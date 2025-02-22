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
from ui.cmd_interface import cmd_interface

# Global variables for managing accounts and the event loop
accounts_list = []      # List of tuples (filename, data)
current_account_index = 0
event_loop = None       # Will be assigned in run_app()

# ================================================================
# Account switching functions and associated actions
# ================================================================
def on_switch_account_down():
    global current_account_index
    if current_account_index < len(display_names):
        display_name = display_names[current_account_index]
    else:
        display_name = "Unknown"
    text = f"Current account: [{current_account_index + 1}] {display_name}"
    os.system("cls")
    print(f"[+] {text}")
    update_popup(text)
    cmd_interface()

def on_switch_account_right():
    global current_account_index, accounts_list
    if not accounts_list:
        print("[!] No accounts saved.")
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
                new_display = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
                display_names.append(new_display)
                # Update the index to the last position (the new account)
                current_account_index = len(accounts_list) - 1
                text = f"Current account: [{current_account_index + 1}] {new_display}"
                os.system("cls")
                print(f"[+] New account added: {text}")
                update_popup(text)
                cmd_interface()
            except Exception as ex:
                os.system("cls")
                print("[!] Error adding new account:", ex)
                cmd_interface()
        else:
            os.system("cls")
            print("[*] Staying on the current account.")
            cmd_interface()
    else:
        current_account_index += 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Current account: [{current_account_index + 1}] {display_name}"
        os.system("cls")
        print(f"[+] {text}")
        update_popup(text)
        cmd_interface()

def on_switch_account_left():
    global current_account_index, accounts_list
    if not accounts_list:
        os.system("cls")
        print("[!] No accounts saved.")
        cmd_interface()
        return
    if current_account_index == 0:
        os.system("cls")
        print("[!] You are already at the first account. No previous account.")
        cmd_interface()
    else:
        current_account_index -= 1
        if current_account_index < len(display_names):
            display_name = display_names[current_account_index]
        else:
            display_name = "Unknown"
        text = f"Current account: [{current_account_index + 1}] {display_name}"
        os.system("cls")
        print(f"[+] {text}")
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
    print("[+] Opening FortniteDB.com in the browser...")
    url = "https://fortniteDB.com"
    webbrowser.open(url)
    cmd_interface()

# ================================================================
# Auxiliary functions for initializing the event loop, hotkeys, and loading accounts
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
    os.system("cls")
    print("Exiting the program")
    time.sleep(1)
    os.system("exit")

def load_accounts_and_update_popup():
    global accounts_list, current_account_index
    # Load existing accounts
    accounts_list = load_all_accounts()
    if not accounts_list:
        respuesta = input("No accounts found. Would you like to add a new account? (y/n): ").strip().lower()
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
            accounts_list.append((new_filename, data))
            current_account_index = 0
            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
            display_names.append(display_name)
        else:
            print("No account added. Exiting...")
            exit(0)
    else:
        for fname, data in accounts_list:
            display_name = asyncio.run_coroutine_threadsafe(get_display_name_for_account(data), event_loop).result()
            display_names.append(display_name)
        print(f"[*] Found {len(accounts_list)} account(s).")
        print(f"[*] Current account: {display_names[current_account_index]}")
        update_popup(f"Current account: [{current_account_index + 1}] {display_names[current_account_index]}")





# ================================================================
# Main function that starts the application
# ================================================================
def run_app():
    global event_loop

    # Initialize and start the event loop in a separate thread
    event_loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_event_loop, args=(event_loop,), daemon=True)
    loop_thread.start()

    # Start the popup window in a separate thread
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()

    # Wait for the popup window to initialize
    import ui.popup
    while ui.popup.popup_root is None:
        time.sleep(0.1)

    # Load accounts and update the popup with the current account
    load_accounts_and_update_popup()

    # Register all the hotkeys
    register_hotkeys()

    # Display instructions in the console
    cmd_interface()

    # Wait until the exit hotkey is activated
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Exiting...")
    event_loop.call_soon_threadsafe(event_loop.stop)
    import ui.popup
    ui.popup.popup_root.destroy()



if __name__ == "__main__":
    run_app()
