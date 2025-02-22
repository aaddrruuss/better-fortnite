import asyncio
import threading
import time
import webbrowser
import keyboard
import subprocess
import os

from account.manager import load_all_accounts, authenticate, get_display_name_for_account
from commands.refresh import command_leave_party, command_skip, command_play_fortnite
from ui.popup import popup_loop, update_popup
from config import display_names

# Variables globales para la gestión de cuentas y el event loop
accounts_list = []      # Lista de tuplas (filename, data)
current_account_index = 0
event_loop = None       # Se asignará el loop en run_app()

# ================================================================
# Funciones de cambio de cuenta y acciones asociadas
# ================================================================
def on_switch_account_down():
    global current_account_index
    if current_account_index < len(display_names):
        display_name = display_names[current_account_index]
    else:
        display_name = "Unknown"
    text = f"Cuenta actual: [{current_account_index + 1}] {display_name}"
    print(f"[+] {text}")
    update_popup(text)

def on_switch_account_right():
    global current_account_index, accounts_list
    if not accounts_list:
        print("[!] No hay cuentas guardadas.")
        return
    if current_account_index == len(accounts_list) - 1:
        respuesta = input("¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = f"device_auths{len(accounts_list) + 1}.json"
            try:
                # Se autentica y agrega la nueva cuenta
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                # Se obtiene el display name de la nueva cuenta y se añade al cache
                new_display = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
                display_names.append(new_display)
                # Se actualiza el índice a la última posición (la nueva cuenta)
                current_account_index = len(accounts_list) - 1
                text = f"Cuenta actual: [{current_account_index + 1}] {new_display}"
                print(f"[+] Nueva cuenta agregada: {text}")
                update_popup(text)
            except Exception as ex:
                print("[!] Error al agregar nueva cuenta:", ex)
        else:
            print("[*] Permaneciendo en la cuenta actual.")
    else:
        current_account_index += 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Cuenta actual: [{current_account_index + 1}] {display_name}"
        print(f"[+] {text}")
        update_popup(text)

def on_switch_account_left():
    global current_account_index, accounts_list
    if not accounts_list:
        print("[!] No hay cuentas guardadas.")
        return
    if current_account_index == 0:
        print("[!] Ya estás en la primera cuenta. No hay cuenta anterior.")
    else:
        current_account_index -= 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Cuenta actual: [{current_account_index + 1}] {display_name}"
        print(f"[+] {text}")
        update_popup(text)

def on_leave_party():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_leave_party(device_auth_data), event_loop)

def on_skip():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_skip(device_auth_data), event_loop)

def on_play_fortnite():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_play_fortnite(device_auth_data), event_loop)

def open_fortniteDB():
    print("Abriendo FortniteDB.com en el navegador...")
    url = "https://fortniteDB.com"
    webbrowser.open(url)

# ================================================================
# Funciones auxiliares para inicializar el event loop, hotkeys y cargar cuentas
# ================================================================
def start_event_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def register_hotkeys():
    keyboard.add_hotkey('alt gr+l', on_leave_party)
    keyboard.add_hotkey('alt gr+s', on_skip)
    keyboard.add_hotkey('alt gr+up', on_play_fortnite)
    keyboard.add_hotkey('alt gr+right', on_switch_account_right)
    keyboard.add_hotkey('alt gr+left', on_switch_account_left)
    keyboard.add_hotkey('alt gr+down', on_switch_account_down)
    keyboard.add_hotkey('alt gr+esc', close_program)
    keyboard.add_hotkey('alt gr+q', open_fortniteDB)

def close_program():
    print("Saliendo del programa")
    time.sleep(1)
    os.system("exit")

def load_accounts_and_update_popup():
    global accounts_list, current_account_index
    # Cargar cuentas existentes
    accounts_list = load_all_accounts()
    if not accounts_list:
        respuesta = input("No se encontraron cuentas guardadas. ¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
            accounts_list.append((new_filename, data))
            current_account_index = 0
            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
            display_names.append(display_name)
        else:
            print("No se agregó ninguna cuenta. Saliendo...")
            exit(0)
    else:
        for fname, data in accounts_list:
            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
            display_names.append(display_name)
        print(f"[*] Se encontraron {len(accounts_list)} cuenta(s).")
        print(f"[*] Cuenta actual: {display_names[current_account_index]}")
        update_popup(f"Cuenta actual: [{current_account_index + 1}] {display_names[current_account_index]}")

# ================================================================
# Función principal que inicia la aplicación
# ================================================================
def run_app():
    global event_loop

    # Inicializar y arrancar el event loop en un hilo aparte
    event_loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_event_loop, args=(event_loop,), daemon=True)
    loop_thread.start()

    # Iniciar la ventana popup en un hilo aparte
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()

    # Esperar a que la ventana popup se inicialice
    import ui.popup
    while ui.popup.popup_root is None:
        time.sleep(0.1)

    # Cargar cuentas y actualizar el popup con la cuenta actual
    load_accounts_and_update_popup()

    # Registrar todas las hotkeys
    register_hotkeys()

    # Mostrar instrucciones en consola
    print("========================================")
    print("Instrucciones y Hotkeys:")
    print("  - AltGr+L: Ejecuta 'Leave Party' con la cuenta actual")
    print("  - AltGr+S: Ejecuta 'Skip' con la cuenta actual")
    print("  - AltGr+Up: Lanza Fortnite con la cuenta actual")
    print("  - AltGr+Right: Cambia a la siguiente cuenta (o pregunta para agregar una nueva)")
    print("  - AltGr+Left: Cambia a la cuenta anterior")
    print("  - AltGr+Down: Muestra en consola la cuenta actual")
    print("========================================")
    print("Presione ALTGR+ESC para salir.")

    # Esperar hasta que se active la hotkey de salida
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Saliendo...")
    event_loop.call_soon_threadsafe(event_loop.stop)
    import ui.popup
    ui.popup.popup_root.destroy()

if __name__ == "__main__":
    run_app()
