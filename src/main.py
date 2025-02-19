import asyncio
import threading
import time
import keyboard
import subprocess
import os

from account.manager import load_all_accounts, authenticate, get_display_name_for_account
from commands.refresh import command_leave_party, command_skip, command_play_fortnite
from ui.popup import popup_loop, update_popup
from config import display_names

# Variables globales
accounts_list = []      # Lista de tuplas (filename, data)
current_account_index = 0
event_loop = None       # Se asignará el loop en main

def on_switch_account_down():
    global accounts_list, current_account_index, event_loop
    if current_account_index < len(display_names):
        display_name = display_names[current_account_index]
    else:
        display_name = "Unknown"
    text = f"Cuenta actual: [{current_account_index + 1}] {display_name}"
    print(f"[+] {text}")
    update_popup(text)

def on_switch_account_right():
    global current_account_index, accounts_list, event_loop
    if not accounts_list:
        print("[!] No hay cuentas guardadas.")
        return
    if current_account_index == len(accounts_list) - 1:
        respuesta = input("¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = f"device_auths{len(accounts_list) + 1}.json"
            try:
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                
                new_display = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
                display_names.append(new_display)
                
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
    global current_account_index, accounts_list, event_loop
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

def start_event_loop(loop: asyncio.AbstractEventLoop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

loop = asyncio.new_event_loop()
event_loop = loop
loop_thread = threading.Thread(target=start_event_loop, args=(loop,), daemon=True)
loop_thread.start()

def on_leave_party():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_leave_party(device_auth_data), loop)

def on_skip():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_skip(device_auth_data), loop)

def on_play_fortnite():
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_play_fortnite(device_auth_data), loop)

def close_program():
    print("Saliendo del programa")
    time.sleep(1)
    os.system("exit")


def main():
    global accounts_list, current_account_index, event_loop

    # Iniciar la ventana popup en un hilo separado
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()
    # Esperar hasta que se cree la ventana popup
    import ui.popup
    while ui.popup.popup_root is None:
        time.sleep(0.1)
    

    # Cargar cuentas existentes
    accounts_list = load_all_accounts()
    if not accounts_list:
        respuesta = input("No se encontraron cuentas guardadas. ¿Desea agregar una nueva cuenta? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), loop).result()
            accounts_list.append((new_filename, data))
            current_account_index = 0

            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), loop).result()
            display_names.append(display_name)
        else:
            print("No se agregó ninguna cuenta. Saliendo...")
            return
    else:
        for fname, data in accounts_list:
            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), loop).result()
            display_names.append(display_name)
        print(f"[*] Se encontraron {len(accounts_list)} cuenta(s).")
        print(f"[*] Cuenta actual: {display_name}")
        update_popup(f"Cuenta actual: [{current_account_index + 1}] {display_name}")

    # Registrar hotkeys
    keyboard.add_hotkey('alt gr+l', on_leave_party)
    keyboard.add_hotkey('alt gr+s', on_skip)
    keyboard.add_hotkey('alt gr+up', on_play_fortnite)
    keyboard.add_hotkey('alt gr+right', on_switch_account_right)
    keyboard.add_hotkey('alt gr+left', on_switch_account_left)
    keyboard.add_hotkey('alt gr+down', on_switch_account_down)
    keyboard.add_hotkey('alt gr + esc', close_program)

    # Mostrar instrucciones en consola
    print("========================================")
    print("Instrucciones y Hotkeys:")
    print("  - AltGr+L: Ejecuta 'Leave Party' con la cuenta actual")
    print("  - AltGr+S: Ejecuta 'Skip' con la cuenta actual")
    print("  - AltGr+Up: Lanza Fortnite con la cuenta actual (si ya está abierto, se cierra y relanza)")
    print("  - AltGr+Right: Cambia a la siguiente cuenta (o pregunta para agregar una nueva)")
    print("  - AltGr+Left: Cambia a la cuenta anterior")
    print("  - AltGr+Down: Muestra en consola la cuenta actual")
    print("========================================")
    print("Presione ALTGR+ESC para salir.")
    
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Saliendo...")
    loop.call_soon_threadsafe(loop.stop)
    import ui.popup
    ui.popup.popup_root.destroy()

if __name__ == "__main__":
    main()
