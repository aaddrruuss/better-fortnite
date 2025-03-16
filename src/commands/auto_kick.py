import aiohttp
import time
import threading
import asyncio

from commands.refresh import command_skip, refresh_access_token
from commands.party import getPartyId, leaveParty

# Variables para Auto Kick
auto_kick_enabled = False
auto_kick_thread = None
claim_rewards = True
check_interval = 1.0  # Intervalo en segundos para verificar el estado de la misión
last_mission_status = False  # Almacena si el jugador estaba en misión en la última verificación
current_device_auth = None  # Almacenar los datos de autenticación completos
account_switch_lock = threading.Lock()  # Bloqueo para actualizaciones seguras de cuenta
force_reset_mission_status = False  # Bandera para forzar reset del estado de misión

async def get_matchmaking_status(access_token: str, account_id: str):
    """
    Verifica el estado de la misión actual del jugador.
    
    Returns:
        bool: True si el jugador está en misión, False en caso contrario
    """
    url = f"https://fngw-mcp-gc-livefn.ol.epicgames.com/fortnite/api/matchmaking/session/findPlayer/{account_id}"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Determinar si está en misión
                    is_in_mission = False
                    if isinstance(data, list):
                        for item in data:
                            if isinstance(item, dict):
                                if ("matchmaking" in item and item["matchmaking"].get("started", False)) or item.get("started", False):
                                    is_in_mission = True
                                    break
                    elif isinstance(data, dict):
                        if ("matchmaking" in data and data["matchmaking"].get("started", False)) or data.get("started", False):
                            is_in_mission = True
                            
                    return is_in_mission
                elif response.status == 404:
                    # No está en ninguna misión
                    return False
                elif response.status == 401:
                    # Error de autenticación, necesitamos refrescar el token
                    print("⚠️ Error 401: Token expirado o inválido, refrescando...")
                    return None  # Valor especial para indicar error de autenticación
                else:
                    print(f"Error al verificar estado de misión: {response.status}")
                    return False
    except Exception as e:
        print(f"Error en get_matchmaking_status: {e}")
        return False

async def execute_auto_kick(device_auth_data: dict, with_rewards: bool):
    """
    Ejecuta el auto kick: abandona la party y opcionalmente reclama recompensas
    
    Args:
        device_auth_data: Datos completos de autenticación del dispositivo
        with_rewards: Si debe reclamar recompensas o no
    """
    try:
        print("Ejecutando Auto Kick...")
        
        if with_rewards:
            # Si se activa la reclamación de recompensas, usamos command_skip directamente
            # que se encarga de abandonar la party Y reclamar todas las recompensas
            print("Usando command_skip para abandonar la party y reclamar recompensas...")
            await command_skip(device_auth_data)
            print("✅ Auto Kick completado con éxito (con recompensas)")
        else:
            # Si solo queremos abandonar la party sin reclamar recompensas
            # usamos el mismo patrón que command_leave_party
            print("Abandonando la party sin reclamar recompensas...")
            try:
                # Refrescamos el token usando el device_auth_data completo
                access_token = await refresh_access_token(device_auth_data)
                account_id = device_auth_data["account_id"]
                
                # Obtenemos el ID de la party y la abandonamos
                party_id = await getPartyId(access_token, account_id)
                if party_id:
                    leave_result = await leaveParty(access_token, party_id, account_id)
                    if leave_result:
                        print("✅ Party abandonada correctamente")
                    else:
                        print("❌ Error al abandonar la party")
                else:
                    print("ℹ️ No se encontró ninguna party activa")
            except Exception as e:
                print(f"❌ Error al abandonar la party: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Error en execute_auto_kick: {e}")
        return False

def auto_kick_monitor():
    """Función de monitoreo que se ejecuta en segundo plano"""
    global auto_kick_enabled, last_mission_status, current_device_auth, force_reset_mission_status
    
    print("🔄 Monitor de Auto Kick iniciado")
    
    # Crear un nuevo bucle de eventos para las operaciones asíncronas
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Copiar los datos de autenticación localmente para evitar problemas de concurrencia
        with account_switch_lock:
            device_auth = current_device_auth.copy() if current_device_auth else None
            if not device_auth:
                print("❌ Error: No hay datos de autenticación disponibles")
                auto_kick_enabled = False
                return

        # Refrescamos el token antes de comenzar
        access_token = loop.run_until_complete(refresh_access_token(device_auth))
        account_id = device_auth["account_id"]
        
        # Inicializar estado - importante: esperamos un poco antes de verificar el estado
        # para evitar falsos positivos justo después de cambiar de cuenta
        time.sleep(1.0)  # Esperar 1 segundo para estabilizar
        last_mission_status = loop.run_until_complete(get_matchmaking_status(access_token, account_id))
        print(f"Estado inicial de misión: {'En misión' if last_mission_status else 'Fuera de misión'}")
        
        idle_counter = 0
        token_refresh_counter = 0
        auth_error_counter = 0
        
        while auto_kick_enabled:
            try:
                # Si hay un cambio de cuenta, resetear el estado
                if force_reset_mission_status:
                    with account_switch_lock:
                        device_auth = current_device_auth.copy()
                        force_reset_mission_status = False

                    # Refrescar token con la nueva cuenta
                    access_token = loop.run_until_complete(refresh_access_token(device_auth))
                    account_id = device_auth["account_id"]
                    
                    # Reiniciar contadores y estado
                    token_refresh_counter = 0
                    auth_error_counter = 0
                    idle_counter = 0
                    
                    # Esperar un momento para estabilizar
                    time.sleep(1.0)
                    
                    # Obtener el nuevo estado de misión
                    last_mission_status = loop.run_until_complete(get_matchmaking_status(access_token, account_id))
                    print(f"Estado de misión después del cambio de cuenta: {'En misión' if last_mission_status else 'Fuera de misión'}")
                    continue
                
                # Refrescamos el token cada 10 minutos (600 segundos) o si hay errores de autenticación
                token_refresh_counter += 1
                if token_refresh_counter >= 600 or auth_error_counter > 0:
                    try:
                        access_token = loop.run_until_complete(refresh_access_token(device_auth))
                        token_refresh_counter = 0
                        auth_error_counter = 0  # Resetear contador de errores de autenticación
                    except Exception as e:
                        print(f"Error al refrescar token: {e}")
                        auth_error_counter += 1
                        # Si no podemos refrescar después de varios intentos, mejor desactivar
                        if auth_error_counter >= 3:
                            print("❌ Demasiados errores de autenticación, desactivando Auto Kick")
                            auto_kick_enabled = False
                            break
                
                # Verificar estado actual de misión
                current_mission_status = loop.run_until_complete(get_matchmaking_status(access_token, account_id))
                
                # Si recibimos None, indica un error 401, necesitamos refrescar token
                if current_mission_status is None:
                    auth_error_counter += 1
                    if auth_error_counter < 3:  # Intentar refrescar al siguiente ciclo
                        time.sleep(check_interval)
                        continue
                    else:  # Demasiados errores, desactivar
                        print("❌ Demasiados errores de autenticación, desactivando Auto Kick")
                        auto_kick_enabled = False
                        break
                
                # Detectar la transición específica: de estar en misión a ya no estar en misión
                # Solo si antes estábamos seguros de que estaba en misión
                if last_mission_status and not current_mission_status:
                    print("¡Misión completada detectada!")
                    # Asegurarse de que los datos de autenticación sean los más recientes
                    with account_switch_lock:
                        device_auth = current_device_auth.copy()
                        
                    # Ejecutar el auto kick
                    loop.run_until_complete(execute_auto_kick(device_auth, claim_rewards))
                    
                    # Dar un pequeño descanso después del auto kick
                    time.sleep(2)
                    
                    # Refrescamos el token después del auto-kick
                    access_token = loop.run_until_complete(refresh_access_token(device_auth))
                    token_refresh_counter = 0
                
                # Actualizar estado para próxima iteración
                last_mission_status = current_mission_status
                
                # Gestión de inactividad
                if not current_mission_status:
                    idle_counter += 1
                    if idle_counter >= 1800:  # 30 minutos (a 1 segundo por verificación)
                        print("Auto Kick desactivado por inactividad (30 minutos)")
                        auto_kick_enabled = False
                        break
                else:
                    idle_counter = 0
                
            except Exception as e:
                print(f"Error en ciclo de monitoreo: {e}")
            
            # Esperar antes de la próxima verificación
            time.sleep(check_interval)
    except Exception as e:
        print(f"Error en auto_kick_monitor: {e}")
    finally:
        loop.close()
        print("🛑 Monitor de Auto Kick detenido")

def toggle_auto_kick(device_auth_data=None):
    """
    Activa o desactiva la función de Auto Kick
    
    Args:
        device_auth_data: Datos completos de autentificación
    """
    global auto_kick_enabled, auto_kick_thread, claim_rewards, current_device_auth
    
    with account_switch_lock:
        auto_kick_enabled = not auto_kick_enabled
        
        if auto_kick_enabled:
            if not device_auth_data:
                print("❌ Error: Se requieren datos de autenticación para activar Auto Kick")
                auto_kick_enabled = False
                return
                
            # Guardamos los datos de autenticación para su uso en el monitor
            current_device_auth = device_auth_data.copy()  # Hacer copia para evitar referencias
                
            print("✅ Auto Kick: ACTIVADO")
            print("  - Se verificará el estado de la misión cada 1 segundo")
            print("  - Se desactivará automáticamente tras 30 minutos de inactividad")
            print("  - Reclamar recompensas: " + ("ACTIVADO" if claim_rewards else "DESACTIVADO"))
            
            # Inicia un hilo para ejecutar el monitoreo
            auto_kick_thread = threading.Thread(target=auto_kick_monitor)
            auto_kick_thread.daemon = True
            auto_kick_thread.start()
        else:
            print("🛑 Auto Kick: DESACTIVADO")
            # El hilo se detendrá cuando auto_kick_enabled sea False

def toggle_claim_rewards():
    """
    Activa o desactiva la reclamación de recompensas en Auto Kick
    """
    global claim_rewards
    claim_rewards = not claim_rewards
    print(f"Reclamar recompensas en Auto Kick: {'ACTIVADO' if claim_rewards else 'DESACTIVADO'}")

def update_account(device_auth_data):
    """
    Actualiza la cuenta que está siendo monitoreada por Auto Kick
    
    Args:
        device_auth_data: Nuevos datos de autenticación para la cuenta activa
    """
    global current_device_auth, auto_kick_enabled, auto_kick_thread, force_reset_mission_status
    
    # Actualizar datos de autenticación usando un bloqueo para evitar condiciones de carrera
    with account_switch_lock:
        # Solo actualizar si es una cuenta diferente
        if current_device_auth and current_device_auth.get("account_id") == device_auth_data.get("account_id"):
            # Misma cuenta, no es necesario actualizar
            return False
            
        # Actualizar a la nueva cuenta
        current_device_auth = device_auth_data.copy()  # Hacer una copia para evitar referencias
        force_reset_mission_status = True  # Indicar que debe resetear el estado de misión
        
        # Si Auto Kick está activo, informar del cambio
        if auto_kick_enabled:
            new_account_id = device_auth_data.get("account_id", "desconocida")
            print(f"🔄 Auto Kick: Cambiando a cuenta {new_account_id}")
            print(f"  - Reclamar recompensas: {'ACTIVADO' if claim_rewards else 'DESACTIVADO'}")
            return True
    
    return False
