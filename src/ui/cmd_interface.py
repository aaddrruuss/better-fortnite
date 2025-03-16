from colorama import init, Fore, Back, Style
import os
import platform
import time
import sys

init()

def clear_screen():
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def better_fortnite_ascii():
    print(Fore.CYAN + """
 ██████╗ ███████╗████████╗████████╗███████╗██████╗     ███████╗ ██████╗ ██████╗ ████████╗███╗   ██╗██╗████████╗███████╗
 ██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝████╗  ██║██║╚══██╔══╝██╔════╝
 ██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝    █████╗  ██║   ██║██████╔╝   ██║   ██╔██╗ ██║██║   ██║   █████╗  
 ██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗    ██╔══╝  ██║   ██║██╔══██╗   ██║   ██║╚██╗██║██║   ██║   ██╔══╝  
 ██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║    ██║     ╚██████╔╝██║  ██║   ██║   ██║ ╚████║██║   ██║   ███████╗
 ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝
""" + Fore.RESET)
    print(Fore.YELLOW + "⭐ " + Fore.LIGHTBLUE_EX + "Version 1.1" + Fore.YELLOW + " ⭐" + Fore.RESET)
    print(Fore.MAGENTA + "═" * 90 + Fore.RESET)

def print_status(message, status_type="info"):
    """Prints a formatted status message with appropriate colors"""
    prefix_map = {
        "info": (Fore.LIGHTYELLOW_EX + "[*]" + Fore.RESET),
        "success": (Fore.LIGHTGREEN_EX + "[+]" + Fore.RESET),
        "error": (Fore.LIGHTRED_EX + "[!]" + Fore.RESET),
        "warning": (Fore.LIGHTYELLOW_EX + "[!]" + Fore.RESET)
    }
    prefix = prefix_map.get(status_type, prefix_map["info"])
    print(f"{prefix} {message}")

def show_loading(message="Loading", duration=1.5, steps=3):
    """Shows a loading animation without clearing the screen (eliminates flicker)"""
    # Imprime un mensaje inicial para dejar espacio para la animación
    print("")
    
    # Calculamos el tiempo para cada estado de la animación
    step_duration = duration / steps / 4
    
    # Realizamos la animación sin limpiar la pantalla
    for _ in range(steps):
        for i in range(4):
            # Volvemos al inicio de la línea con \r
            dots = "." * i + " " * (3-i)
            sys.stdout.write(f"\r{Fore.LIGHTYELLOW_EX}{message}{dots}{Fore.RESET}")
            sys.stdout.flush()
            time.sleep(step_duration)
    
    # Limpia la línea de carga al finalizar
    sys.stdout.write("\r" + " " * (len(message) + 5) + "\r")
    sys.stdout.flush()
    print("")

def cmd_interface(current_account=None, accounts_count=0):
    """Display an improved command interface with account info"""
    # Display account status if available
    if current_account:
        print("\n" + Fore.WHITE + Back.BLUE + f" CURRENT ACCOUNT: [{current_account[0]}] {current_account[1]} " + Back.RESET)
        print(Fore.BLUE + f" Total Accounts: {accounts_count} " + Fore.RESET)
    
    # Commands section
    print("\n" + Fore.WHITE + Back.GREEN + " AVAILABLE COMMANDS " + Back.RESET)
    
    # Create a neat table for commands
    commands = [
        ("AltGr+L", "Leave Party", "Exits your current Fortnite party"),
        ("AltGr+K", "Auto Kick", "Enables or disables auto kick feature"),
        ("AltGr+S", "Skip", "Skip mission animation"),
        ("AltGr+Up", "Launch Fortnite", "Opens Fortnite with current account"),
        ("AltGr+Right", "Next Account", "Switch to next account or add new"),
        ("AltGr+Left", "Previous Account", "Switch to previous account"),
        ("AltGr+Down", "Check Account", "Show current account details"),
        ("AltGr+Q", "FortniteDB", "Open FortniteDB.com in browser"),
        ("AltGr+P", "Fast Drop", "Hold to activate fast drop script"),
        ("AltGr+ESC", "Exit", "Close Better Fortnite")
    ]
    
    # Define column widths for a consistent look
    col_widths = [13, 20, 40]
    
    # Print header
    print(Fore.CYAN + "┌" + "─" * col_widths[0] + "┬" + "─" * col_widths[1] + "┬" + "─" * col_widths[2] + "┐" + Fore.RESET)
    print(Fore.CYAN + f"│{Fore.WHITE} {'HOTKEY':^{col_widths[0]-2}}{Fore.CYAN} │{Fore.WHITE} {'COMMAND':^{col_widths[1]-2}}{Fore.CYAN} │{Fore.WHITE} {'DESCRIPTION':^{col_widths[2]-2}}{Fore.CYAN} │" + Fore.RESET)
    print(Fore.CYAN + "├" + "─" * col_widths[0] + "┼" + "─" * col_widths[1] + "┼" + "─" * col_widths[2] + "┤" + Fore.RESET)
    
    # Print each command with alternating row colors
    for i, (hotkey, command, description) in enumerate(commands):
        bg_color = Back.BLACK if i % 2 == 0 else ""
        print(Fore.CYAN + f"│{bg_color} {Fore.LIGHTYELLOW_EX}{hotkey:<{col_widths[0]-2}}{Fore.RESET}{bg_color} {Fore.CYAN}│{bg_color} {Fore.LIGHTGREEN_EX}{command:<{col_widths[1]-2}}{Fore.RESET}{bg_color} {Fore.CYAN}│{bg_color} {Fore.WHITE}{description:<{col_widths[2]-2}}{Fore.RESET}{bg_color} {Fore.CYAN}│" + Fore.RESET)
    
    # Print footer
    print(Fore.CYAN + "└" + "─" * col_widths[0] + "┴" + "─" * col_widths[1] + "┴" + "─" * col_widths[2] + "┘" + Fore.RESET)
    
    # Tips section
    print("\n" + Fore.WHITE + Back.MAGENTA + " TIPS " + Back.RESET)
    print(Fore.MAGENTA + "• " + Fore.WHITE + "For fast account switching, use " + Fore.LIGHTYELLOW_EX + "AltGr+Left" + Fore.WHITE + " and " + Fore.LIGHTYELLOW_EX + "AltGr+Right" + Fore.RESET)
    print(Fore.MAGENTA + "• " + Fore.WHITE + "Hold " + Fore.LIGHTYELLOW_EX + "AltGr+P" + Fore.WHITE + " to quickly drop items" + Fore.RESET)
    
    # Footer
    print("\n" + Fore.MAGENTA + "═" * 90 + Fore.RESET)
    print(Fore.LIGHTBLUE_EX + "Better Fortnite" + Fore.RESET + " - Made with " + Fore.RED + "♥" + Fore.RESET + " by @adrusss")