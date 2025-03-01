import asyncio
import threading
import time
import webbrowser
import keyboard
import os

from colorama import init, Fore, Back, Style
init()

from account.manager import load_all_accounts, authenticate, get_display_name_for_account
from commands.refresh import command_leave_party, command_skip, command_play_fortnite
from commands.stw import fast_drop  # Importamos la función fast_drop
from ui.popup import popup_loop, update_popup
from config import display_names
from ui.cmd_interface import cmd_interface, better_fortnite_ascii

# ================================================================
# Variables Globales
# ================================================================
accounts_list = []      # List of tuples (filename, data)
current_account_index = 0
event_loop = None       # Será asignado en run_app()

# ------------------------------------------------
# Variables para manejar el loop continuo de fast drop
# ------------------------------------------------
fast_drop_active = False
fast_drop_thread = None


# ================================================================
# Manejo de cuentas y acciones asociadas
# ================================================================
def on_switch_account_down():
    global current_account_index
    if current_account_index < len(display_names):
        display_name = display_names[current_account_index]
    else:
        display_name = "Unknown"
    text = f"Current account: [{current_account_index + 1}] {display_name}"
    os.system("cls")
    better_fortnite_ascii()
    print(Fore.LIGHTGREEN_EX + f"[+] {text}" + Fore.RESET)
    update_popup(text)
    cmd_interface()

def on_switch_account_right():
    global current_account_index, accounts_list
    if not accounts_list:
        print(Fore.LIGHTRED_EX + "[!] No accounts saved." + Fore.RESET)
        cmd_interface()
        return
    if current_account_index == len(accounts_list) - 1:
        respuesta = input("No accounts found. Would you like to add a new account? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = f"device_auths{len(accounts_list) + 1}.json"
            try:
                # Authenticate and add the new account
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                # Get the display name for the new account and add it to the cache
                new_display = asyncio.run_coroutine_threadsafe(
                    get_display_name_for_account(data), event_loop
                ).result()
                display_names.append(new_display)
                current_account_index = len(accounts_list) - 1
                text = f"Current account: [{current_account_index + 1}] {new_display}"
                os.system("cls")
                better_fortnite_ascii()
                print(Fore.LIGHTGREEN_EX + f"[+] New account added: {text}" + Fore.RESET)
                update_popup(text)
                cmd_interface()
            except Exception as ex:
                os.system("cls")
                better_fortnite_ascii()
                print(Fore.LIGHTRED_EX + "[!] Error adding new account:" + Fore.RESET, ex)
                cmd_interface()
        else:
            os.system("cls")
            better_fortnite_ascii()
            print(Fore.LIGHTYELLOW_EX + "[*] Staying on the current account.")
            cmd_interface()
    else:
        current_account_index += 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Current account: [{current_account_index + 1}] {display_name}"
        os.system("cls")
        better_fortnite_ascii()
        print(Fore.LIGHTGREEN_EX + f"[+] {text}" + Fore.RESET)
        update_popup(text)
        cmd_interface()

def on_switch_account_left():
    global current_account_index, accounts_list
    if not accounts_list:
        os.system("cls")
        better_fortnite_ascii()
        print(Fore.LIGHTRED_EX + "[!] No accounts saved." + Fore.RESET)
        cmd_interface()
        return
    if current_account_index == 0:
        os.system("cls")
        better_fortnite_ascii()
        print(Fore.LIGHTRED_EX + "[!] You are already at the first account. No previous account." + Fore.RESET)
        cmd_interface()
    else:
        current_account_index -= 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Current account: [{current_account_index + 1}] {display_name}"
        os.system("cls")
        better_fortnite_ascii()
        print(Fore.LIGHTGREEN_EX + f"[+] {text}" + Fore.RESET)
        update_popup(text)
        cmd_interface()

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
    os.system("cls")
    better_fortnite_ascii()
    print(Fore.LIGHTGREEN_EX + "[+] Opening FortniteDB.com in the browser..." + Fore.RESET)
    url = "https://fortniteDB.com"
    webbrowser.open(url)
    cmd_interface()


# ================================================================
# Funciones para el fast drop continuo
# ================================================================
def fast_drop_loop():
    """
    Mientras 'fast_drop_active' sea True, llamamos repetidamente a 'fast_drop()'
    con un retardo mínimo. 
    """
    while fast_drop_active:
        # Llamamos a la corrutina asíncrona usando run_coroutine_threadsafe
        # para no bloquear el hilo principal.
        fast_drop()
        # Ajusta este sleep a tu gusto (demasiado bajo puede saturar CPU)
        

def on_fast_drop_press():
    """
    Se invoca cuando detectamos que se presionó Alt Gr + P. 
    Inicia el hilo que llama fast_drop_loop() repetidamente.
    """
    global fast_drop_active, fast_drop_thread
    if fast_drop_active:
        return  # Ya estaba activo, no hacemos nada.
    fast_drop_active = True

    fast_drop_thread = threading.Thread(target=fast_drop_loop, daemon=True)
    fast_drop_thread.start()

def on_fast_drop_release():
    """
    Se invoca cuando se suelta la tecla 'P' (o el combo).
    Detiene el bucle de fast drop.
    """
    global fast_drop_active
    fast_drop_active = False


# ================================================================
# Funciones auxiliares de inicialización
# ================================================================
def start_event_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

def register_hotkeys():
    """
    Registra la mayoría de hotkeys para funciones que se disparan 1 sola vez.
    Además, configuramos 'on_press_key' y 'on_release_key' para Alt Gr + P.
    """
    keyboard.add_hotkey('alt gr+l', on_leave_party)
    keyboard.add_hotkey('alt gr+s', on_skip)
    keyboard.add_hotkey('alt gr+up', on_play_fortnite)
    keyboard.add_hotkey('alt gr+right', on_switch_account_right)
    keyboard.add_hotkey('alt gr+left', on_switch_account_left)
    keyboard.add_hotkey('alt gr+down', on_switch_account_down)
    keyboard.add_hotkey('alt gr+esc', close_program)
    keyboard.add_hotkey('alt gr+q', open_fortniteDB)

    # -----------------------------------------------
    # REGISTRO DE TECLAS PARA FAST DROP EN BUCLE
    # -----------------------------------------------
    # Al presionar la tecla P, verificamos si Alt Gr está pulsado 
    # (hay casos donde se detecta alt_r en vez de alt gr).
    keyboard.on_press_key("p", lambda e: on_fast_drop_press() if keyboard.is_pressed('alt gr') else None)

    # Cuando se suelte la tecla P, paramos la repetición.
    keyboard.on_release_key("p", lambda e: on_fast_drop_release())


def close_program():
    os.system("cls")
    better_fortnite_ascii()
    print(Fore.LIGHTYELLOW_EX + "Exiting the program" + Fore.RESET)
    time.sleep(1)
    os.system("exit")

def load_accounts_and_update_popup():
    global accounts_list, current_account_index
    from account.manager import load_all_accounts, authenticate, get_display_name_for_account
    # Load existing accounts
    accounts_list = load_all_accounts()
    if not accounts_list:
        respuesta = input("No accounts found. Would you like to add a new account? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
            accounts_list.append((new_filename, data))
            current_account_index = 0
            display_name = asyncio.run_coroutine_threadsafe(
                get_display_name_for_account(data), event_loop
            ).result()
            display_names.append(display_name)
        else:
            print(Fore.LIGHTYELLOW_EX + "[*] No account added. Exiting..." + Fore.RESET)
            exit(0)
    else:
        for fname, data in accounts_list:
            display_name = asyncio.run_coroutine_threadsafe(
                get_display_name_for_account(data), event_loop
            ).result()
            display_names.append(display_name)
        os.system("cls")
        better_fortnite_ascii()
        print(Fore.LIGHTYELLOW_EX + "[*] Found " + Fore.RESET + Style.BRIGHT  + f"{len(accounts_list)}" + Style.RESET_ALL + Fore.LIGHTYELLOW_EX + " account(s)." + Fore.RESET)
        print(Fore.LIGHTGREEN_EX + f"[+] Current account: [1] {display_names[current_account_index]}" + Fore.RESET)
        update_popup(f"Current account: [{current_account_index + 1}] {display_names[current_account_index]}")


# ================================================================
# Main function
# ================================================================
def run_app():
    global event_loop

    # Iniciar un nuevo loop de asyncio en un hilo separado
    event_loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_event_loop, args=(event_loop,), daemon=True)
    loop_thread.start()

    # Iniciar la ventana popup en un hilo separado
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()

    # Esperamos a que la ventana popup se inicialice
    import ui.popup
    while ui.popup.popup_root is None:
        time.sleep(0.1)

    print(Fore.LIGHTYELLOW_EX + "[*] Application loading, please wait..." + Fore.RESET)

    # Cargamos cuentas y actualizamos la ventana popup
    load_accounts_and_update_popup()

    # Registramos todos los atajos de teclado
    register_hotkeys()

    # Mostramos las instrucciones en consola
    cmd_interface()

    # Esperar hasta que se active la hotkey de salida
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Exiting...")
    event_loop.call_soon_threadsafe(event_loop.stop)
    ui.popup.popup_root.destroy()


if __name__ == "__main__":
    run_app()