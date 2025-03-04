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
from commands.stw import fast_drop
from ui.popup import popup_loop, update_popup
from config import display_names
from ui.cmd_interface import cmd_interface, better_fortnite_ascii, clear_screen, print_status, show_loading

# ================================================================
# Variables Globales
# ================================================================
accounts_list = []      # List of tuples (filename, data)
current_account_index = 0
event_loop = None       # Assigned in run_app()
display_names_cache = {}  # Cache for display names to reduce API calls

# Fast drop variables
fast_drop_active = False
fast_drop_thread = None


# ================================================================
# Efficient Account Management Functions
# ================================================================
def get_current_account_info():
    """Returns a tuple with current account index and name for display"""
    if not accounts_list or current_account_index >= len(display_names):
        return (current_account_index + 1, "Unknown")
    
    return (current_account_index + 1, display_names[current_account_index])

def on_switch_account_down():
    """Display current account information"""
    global current_account_index
    
    idx, display_name = get_current_account_info()
    text = f"Current account: [{idx}] {display_name}"
    
    clear_screen()
    better_fortnite_ascii()
    print_status(text, "success")
    update_popup(text)
    cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list))

def on_switch_account_right():
    """Switch to next account or add a new one"""
    global current_account_index, accounts_list
    
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts saved.", "error")
        cmd_interface()
        return
        
    if current_account_index == len(accounts_list) - 1:
        clear_screen()
        better_fortnite_ascii()
        respuesta = input(Fore.LIGHTYELLOW_EX + "No more accounts found. Would you like to add a new account? (y/n): " + Fore.RESET).strip().lower()
        
        if respuesta == 'y':
            clear_screen()
            better_fortnite_ascii()
            print_status("Adding new account, please wait...", "info")
            
            new_filename = f"device_auths{len(accounts_list) + 1}.json"
            try:
                # Authenticate and add the new account
                print_status("Authenticating...", "info")
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                
                # Get the display name for the new account and add it to the cache
                print_status("Getting display name...", "info")
                new_display = asyncio.run_coroutine_threadsafe(
                    get_display_name_for_account(data), event_loop
                ).result()
                display_names.append(new_display)
                current_account_index = len(accounts_list) - 1
                
                text = f"Current account: [{current_account_index + 1}] {new_display}"
                clear_screen()
                better_fortnite_ascii()
                print_status(f"New account added: {text}", "success")
                update_popup(text)
                cmd_interface(current_account=(current_account_index + 1, new_display), accounts_count=len(accounts_list))
            except Exception as ex:
                clear_screen()
                better_fortnite_ascii()
                print_status(f"Error adding new account: {ex}", "error")
                cmd_interface(accounts_count=len(accounts_list))
        else:
            clear_screen()
            better_fortnite_ascii()
            print_status("Staying on the current account.", "info")
            idx, name = get_current_account_info()
            cmd_interface(current_account=(idx, name), accounts_count=len(accounts_list))
    else:
        current_account_index += 1
        idx, display_name = get_current_account_info()
        
        # Mostramos solo un mensaje de cambio, sin animaciones que parpadeen
        clear_screen()
        better_fortnite_ascii()
        print_status(f"Switching to account [{idx}] {display_name}...", "info")
        time.sleep(0.5)  # Una pequeña pausa para dar feedback visual
        
        clear_screen()
        better_fortnite_ascii()
        
        text = f"Current account: [{idx}] {display_name}"
        print_status(text, "success")
        update_popup(text)
        cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list))

def on_switch_account_left():
    """Switch to previous account"""
    global current_account_index, accounts_list
    
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts saved.", "error")
        cmd_interface()
        return
        
    if current_account_index == 0:
        clear_screen()
        better_fortnite_ascii()
        print_status("You are already at the first account. No previous account.", "error")
        idx, name = get_current_account_info()
        cmd_interface(current_account=(idx, name), accounts_count=len(accounts_list))
    else:
        current_account_index -= 1
        idx, display_name = get_current_account_info()
        
        # Mostramos solo un mensaje de cambio, sin animaciones que parpadeen
        clear_screen()
        better_fortnite_ascii()
        print_status(f"Switching to account [{idx}] {display_name}...", "info")
        time.sleep(0.5)  # Una pequeña pausa para dar feedback visual
        
        clear_screen()
        better_fortnite_ascii()
        
        text = f"Current account: [{idx}] {display_name}"
        print_status(text, "success")
        update_popup(text)
        cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list))


# ================================================================
# Action Command Functions
# ================================================================
def on_leave_party():
    """Leave current party with loading animation"""
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts available to execute command.", "error")
        cmd_interface(accounts_count=len(accounts_list))
        return
        
    clear_screen()
    better_fortnite_ascii()
    print_status("Executing command: Leave Party", "info")
    
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_leave_party(device_auth_data), event_loop)

def on_skip():
    """Skip mission with animation"""
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts available to execute command.", "error")
        cmd_interface(accounts_count=len(accounts_list))
        return
        
    clear_screen()
    better_fortnite_ascii()
    print_status("Executing command: Skip Mission Animation", "info")
    
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_skip(device_auth_data), event_loop)

def on_play_fortnite():
    """Launch Fortnite with the current account"""
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts available to execute command.", "error")
        cmd_interface(accounts_count=len(accounts_list))
        return
        
    clear_screen()
    better_fortnite_ascii()
    print_status("Preparing to launch Fortnite...", "info")
    
    device_auth_data = accounts_list[current_account_index][1]
    asyncio.run_coroutine_threadsafe(command_play_fortnite(device_auth_data), event_loop)

def open_fortniteDB():
    """Open FortniteDB website"""
    clear_screen()
    better_fortnite_ascii()
    print_status("Opening FortniteDB.com in the browser...", "success")
    url = "https://fortniteDB.com"
    webbrowser.open(url)
    
    idx, name = get_current_account_info()
    cmd_interface(current_account=(idx, name), accounts_count=len(accounts_list))


# ================================================================
# Fast Drop Functions
# ================================================================
def fast_drop_loop():
    """Loop for fast drop function execution"""
    while fast_drop_active:
        fast_drop()
        # Very small sleep to prevent CPU overload
        time.sleep(0.01)

def on_fast_drop_press():
    """Start fast drop when key combo is pressed"""
    global fast_drop_active, fast_drop_thread
    
    if fast_drop_active:
        return  # Already active
        
    fast_drop_active = True
    update_popup("Fast Drop ACTIVE")
    
    fast_drop_thread = threading.Thread(target=fast_drop_loop, daemon=True)
    fast_drop_thread.start()

def on_fast_drop_release():
    """Stop fast drop when key is released"""
    global fast_drop_active
    
    fast_drop_active = False
    idx, name = get_current_account_info()
    update_popup(f"Current account: [{idx}] {name}")


# ================================================================
# Initialization and Helper Functions
# ================================================================
def start_event_loop(loop: asyncio.AbstractEventLoop):
    """Start asyncio event loop"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def register_hotkeys():
    """Register all hotkeys with more descriptive comments"""
    # Action commands
    keyboard.add_hotkey('alt gr+l', on_leave_party)       # Leave party
    keyboard.add_hotkey('alt gr+s', on_skip)              # Skip mission animation
    keyboard.add_hotkey('alt gr+up', on_play_fortnite)    # Launch Fortnite
    
    # Account navigation
    keyboard.add_hotkey('alt gr+right', on_switch_account_right)  # Next account
    keyboard.add_hotkey('alt gr+left', on_switch_account_left)    # Previous account
    keyboard.add_hotkey('alt gr+down', on_switch_account_down)    # Show current account
    
    # Utility commands
    keyboard.add_hotkey('alt gr+esc', close_program)      # Exit program
    keyboard.add_hotkey('alt gr+q', open_fortniteDB)      # Open FortniteDB website

    # Fast drop key handling (with Alt Gr + P)
    keyboard.on_press_key("p", lambda e: on_fast_drop_press() if keyboard.is_pressed('alt gr') else None)
    keyboard.on_release_key("p", lambda e: on_fast_drop_release())

def close_program():
    """Exit the application gracefully"""
    clear_screen()
    better_fortnite_ascii()
    print_status("Exiting Better Fortnite...", "info")
    time.sleep(1)
    os._exit(0)  # More reliable exit than os.system("exit")

def load_accounts_and_update_popup():
    """Load accounts and display names efficiently with caching"""
    global accounts_list, current_account_index, display_names_cache
    
    # Show loading animation
    clear_screen()
    better_fortnite_ascii()
    print_status("Loading accounts, please wait...", "info")
    
    # Load existing accounts
    accounts_list = load_all_accounts()
    
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        respuesta = input(Fore.LIGHTYELLOW_EX + "No accounts found. Would you like to add a new account? (y/n): " + Fore.RESET).strip().lower()
        
        if respuesta == 'y':
            new_filename = "device_auths1.json"
            
            clear_screen()
            better_fortnite_ascii()
            print_status("Starting authentication process...", "info")
            
            try:
                data = asyncio.run_coroutine_threadsafe(authenticate(new_filename), event_loop).result()
                accounts_list.append((new_filename, data))
                current_account_index = 0
                
                display_name = asyncio.run_coroutine_threadsafe(
                    get_display_name_for_account(data), event_loop
                ).result()
                display_names.append(display_name)
                
                clear_screen()
                better_fortnite_ascii()
                print_status(f"Account added successfully: {display_name}", "success")
            except Exception as ex:
                clear_screen()
                better_fortnite_ascii()
                print_status(f"Error adding account: {ex}", "error")
                print_status("Exiting in 3 seconds...", "info")
                time.sleep(3)
                exit(1)
        else:
            print_status("No account added. Exiting...", "info")
            time.sleep(1)
            exit(0)
    else:
        # Get display names for all accounts (with progress indicator)
        total = len(accounts_list)
        display_names.clear()
        
        for i, (fname, data) in enumerate(accounts_list):
            account_id = data["account_id"]
            
            # Use cached display name if available to reduce API calls
            if account_id in display_names_cache:
                display_names.append(display_names_cache[account_id])
                continue
                
            clear_screen()
            better_fortnite_ascii()
            print_status(f"Loading account information ({i+1}/{total})...", "info")
            
            try:
                display_name = asyncio.run_coroutine_threadsafe(
                    get_display_name_for_account(data), event_loop
                ).result()
                display_names.append(display_name)
                display_names_cache[account_id] = display_name  # Cache the result
            except Exception:
                display_names.append(f"Account #{i+1}")
        
        clear_screen()
        better_fortnite_ascii()
        print_status(f"Found {len(accounts_list)} account(s)", "success")
        
        idx, name = get_current_account_info()
        print_status(f"Current account: [{idx}] {name}", "success")
        update_popup(f"Current account: [{idx}] {name}")


# ================================================================
# Main Application Function
# ================================================================
def run_app():
    """Main function to start the application"""
    global event_loop

    clear_screen()
    better_fortnite_ascii()
    print_status("Initializing Better Fortnite...", "info")

    # Start asyncio event loop in separate thread
    event_loop = asyncio.new_event_loop()
    loop_thread = threading.Thread(target=start_event_loop, args=(event_loop,), daemon=True)
    loop_thread.start()

    # Start popup window in separate thread
    popup_thread = threading.Thread(target=popup_loop, daemon=True)
    popup_thread.start()

    # Wait for popup initialization
    import ui.popup
    while ui.popup.popup_root is None:
        time.sleep(0.1)

    # Load accounts and update popup
    load_accounts_and_update_popup()

    # Register all keyboard shortcuts
    register_hotkeys()

    # Show interface with current account info
    idx, name = get_current_account_info()
    cmd_interface(current_account=(idx, name), accounts_count=len(accounts_list))

    # Wait for exit hotkey
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Exiting...")
    event_loop.call_soon_threadsafe(event_loop.stop)
    ui.popup.popup_root.destroy()


if __name__ == "__main__":
    run_app()