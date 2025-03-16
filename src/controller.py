import asyncio
import threading
import time
import webbrowser
import keyboard
import os

from colorama import init, Fore, Back, Style
init()

from account.manager import load_all_accounts, authenticate, get_display_name_for_account
from commands.refresh import command_leave_party, command_skip, command_play_fortnite, refresh_access_token
from commands.stw import fast_drop
from commands.auto_kick import toggle_auto_kick, toggle_claim_rewards, update_account, claim_rewards
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
fast_drop_monitor_thread = None
keep_monitoring_keys = True  # Para controlar el ciclo del monitor de teclas

# Auto kick variables - We'll use this flag to track UI status only
auto_kick_active = False


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
    cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list), 
                  auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)

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
        
        # Actualizar Auto Kick con la nueva cuenta si está activo
        if auto_kick_active:
            device_auth_data = accounts_list[current_account_index][1]
            update_account(device_auth_data)
        
        clear_screen()
        better_fortnite_ascii()
        
        text = f"Current account: [{idx}] {display_name}"
        print_status(text, "success")
        update_popup(text)
        cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list),
                      auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)

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
        
        # Actualizar Auto Kick con la nueva cuenta si está activo
        if auto_kick_active:
            device_auth_data = accounts_list[current_account_index][1]
            update_account(device_auth_data)
        
        clear_screen()
        better_fortnite_ascii()
        
        text = f"Current account: [{idx}] {display_name}"
        print_status(text, "success")
        update_popup(text)
        cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list),
                      auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)


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
# Auto Kick Functions
# ================================================================
def on_toggle_auto_kick():
    """Toggle Auto Kick functionality on/off"""
    global auto_kick_active, accounts_list, current_account_index
    
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts available to execute command.", "error")
        cmd_interface(accounts_count=len(accounts_list), auto_kick_status=False, claim_rewards=claim_rewards)
        return
    
    # Toggle the UI indicator flag explicitly - this is the only place we change it
    auto_kick_active = not auto_kick_active
    
    if auto_kick_active:
        clear_screen()
        better_fortnite_ascii()
        print_status("Activando Auto Kick...", "info")
        
        # Get the complete device_auth_data for current account
        device_auth_data = accounts_list[current_account_index][1]
        
        # Execute in separate thread to avoid blocking
        def start_auto_kick():
            # Need to declare auto_kick_active as global here too
            global auto_kick_active
            
            # Pass full device_auth_data to toggle_auto_kick
            try:
                # Call the backend function
                toggle_auto_kick(device_auth_data)
                
                # Update UI after finished - show auto_kick_active=True regardless of backend
                idx, display_name = get_current_account_info()
                clear_screen()
                better_fortnite_ascii()
                text = f"Auto Kick ACTIVADO para cuenta [{idx}] {display_name}"
                print_status(text, "success")
                update_popup(text, "success")
                cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list),
                              auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)
            except Exception as e:
                # On error, revert the UI flag
                auto_kick_active = False
                clear_screen()
                better_fortnite_ascii()
                print_status(f"Error al activar Auto Kick: {str(e)}", "error")
                cmd_interface(current_account=get_current_account_info(), accounts_count=len(accounts_list),
                              auto_kick_status=False, claim_rewards=claim_rewards)
        
        threading.Thread(target=start_auto_kick, daemon=True).start()
    else:
        # Just turn off the backend function
        toggle_auto_kick()
        idx, display_name = get_current_account_info()
        clear_screen()
        better_fortnite_ascii()
        text = f"Auto Kick DESACTIVADO para cuenta [{idx}] {display_name}"
        print_status(text, "info")
        update_popup(text)
        cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list),
                      auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)

def on_toggle_claim_rewards():
    """Toggle claim rewards option for Auto Kick"""
    if not accounts_list:
        clear_screen()
        better_fortnite_ascii()
        print_status("No accounts available to execute command.", "error")
        cmd_interface(accounts_count=len(accounts_list))
        return
    
    toggle_claim_rewards()
    from commands.auto_kick import claim_rewards
    idx, display_name = get_current_account_info()
    clear_screen()
    better_fortnite_ascii()
    print_status(f"Reclamar recompensas: {'ACTIVADO' if claim_rewards else 'DESACTIVADO'}", 
                 "success" if claim_rewards else "info")
    cmd_interface(current_account=(idx, display_name), accounts_count=len(accounts_list),
                  auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)


# ================================================================
# Fast Drop Functions
# ================================================================
def fast_drop_loop():
    """Loop for fast drop function execution"""
    while fast_drop_active:
        fast_drop()
        # Very small sleep to prevent CPU overload
        time.sleep(0.01)

def monitor_fast_drop_keys():
    """Monitor if both AltGr and P keys are pressed"""
    global fast_drop_active, fast_drop_thread
    
    while keep_monitoring_keys:
        # Verificar si ambas teclas están presionadas
        if keyboard.is_pressed('alt gr') and keyboard.is_pressed('p'):
            # Si no está activo, activar Fast Drop
            if not fast_drop_active:
                fast_drop_active = True
                update_popup("Fast Drop ACTIVE", "busy")
                
                fast_drop_thread = threading.Thread(target=fast_drop_loop, daemon=True)
                fast_drop_thread.start()
        else:
            # Si alguna tecla se suelta y Fast Drop está activo, desactivarlo
            if (fast_drop_active):
                fast_drop_active = False
                update_popup("Fast Drop DEACTIVATED", "success")
                
                # Después de un breve retraso, mostrar la cuenta actual de nuevo
                def show_account_after_delay():
                    time.sleep(1.5)
                    idx, name = get_current_account_info()
                    update_popup(f"Current account: [{idx}] {name}")
                    
                threading.Thread(target=show_account_after_delay, daemon=True).start()
        
        # Breve pausa para no consumir CPU excesivamente
        time.sleep(0.05)


# ================================================================
# Initialization and Helper Functions
# ================================================================
def start_event_loop(loop: asyncio.AbstractEventLoop):
    """Start asyncio event loop"""
    asyncio.set_event_loop(loop)
    loop.run_forever()

def register_hotkeys():
    """Register all hotkeys with more descriptive comments"""
    global fast_drop_monitor_thread
    
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

    # Auto Kick: Alt Gr + K
    keyboard.add_hotkey('alt gr+k', on_toggle_auto_kick)
    
    # Toggle Claim Rewards: Alt Gr + R
    keyboard.add_hotkey('alt gr+r', on_toggle_claim_rewards)

    # Para Fast Drop usamos un enfoque diferente basado en monitoreo continuo
    # en lugar de hotkeys tradicionales
    fast_drop_monitor_thread = threading.Thread(target=monitor_fast_drop_keys, daemon=True)
    fast_drop_monitor_thread.start()

def close_program():
    """Exit the application gracefully"""
    global keep_monitoring_keys
    
    # Detener el hilo de monitoreo de teclas
    keep_monitoring_keys = False
    
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
    cmd_interface(current_account=(idx, name), accounts_count=len(accounts_list),
                  auto_kick_status=auto_kick_active, claim_rewards=claim_rewards)

    # Wait for exit hotkey
    keyboard.wait('f+g+h+t+y+d+s+q+d+u+i+p')
    print("Exiting...")
    event_loop.call_soon_threadsafe(event_loop.stop)
    ui.popup.popup_root.destroy()


if __name__ == "__main__":
    run_app()