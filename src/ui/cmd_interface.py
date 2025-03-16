from colorama import init, Fore, Back, Style
import os
import platform
import time
import sys

init()

def clear_screen():
    """Clears the console screen in a cross-platform way"""
    os.system('cls' if platform.system() == 'Windows' else 'clear')

def better_fortnite_ascii():
    """Display the Better Fortnite ASCII art title"""
    print(Fore.CYAN + """
╔══════════════════════════════════════════════════════════════════════╗
║  ██████╗ ███████╗████████╗████████╗███████╗██████╗                   ║
║  ██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗                  ║
║  ██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝                  ║
║  ██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗                  ║
║  ██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║                  ║
║  ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝                  ║
║  ███████╗ ██████╗ ██████╗ ████████╗███╗   ██╗██╗████████╗███████╗    ║
║  ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝████╗  ██║██║╚══██╔══╝██╔════╝    ║
║  █████╗  ██║   ██║██████╔╝   ██║   ██╔██╗ ██║██║   ██║   █████╗      ║
║  ██╔══╝  ██║   ██║██╔══██╗   ██║   ██║╚██╗██║██║   ██║   ██╔══╝      ║
║  ██║     ╚██████╔╝██║  ██║   ██║   ██║ ╚████║██║   ██║   ███████╗    ║
║  ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝    ║
╚══════════════════════════════════════════════════════════════════════╝""" + Style.RESET_ALL)
    print()  # Add a blank line for spacing

def print_status(message, status_type="info"):
    """Prints a formatted status message with appropriate colors"""
    prefix = ""
    if status_type == "success":
        prefix = Fore.LIGHTGREEN_EX + "[✓] " + Style.RESET_ALL
    elif status_type == "error":
        prefix = Fore.LIGHTRED_EX + "[✗] " + Style.RESET_ALL
    elif status_type == "warning":
        prefix = Fore.LIGHTYELLOW_EX + "[!] " + Style.RESET_ALL
    elif status_type == "info":
        prefix = Fore.LIGHTCYAN_EX + "[i] " + Style.RESET_ALL
    elif status_type == "busy":
        prefix = Fore.LIGHTMAGENTA_EX + "[⟳] " + Style.RESET_ALL
        
    print(f"{prefix}{message}")

def show_loading(message="Loading", duration=1.5, steps=3):
    """Shows a loading animation without clearing the screen (eliminates flicker)"""
    for i in range(steps):
        sys.stdout.write(f"\r{message}" + "." * (i + 1) + " " * (3 - i))
        sys.stdout.flush()
        time.sleep(duration / steps)
    sys.stdout.write("\r" + " " * (len(message) + 4) + "\r")
    sys.stdout.flush()

def cmd_interface(current_account=None, accounts_count=0, auto_kick_status=False, claim_rewards=True):
    """Display an improved command interface with account info and auto kick status"""
    # Header section with account info and status
    print(Fore.WHITE + "\n" + "╔" + "═" * 68 + "╗")

    # STATUS PANEL
    # Current account info
    if current_account:
        idx, name = current_account
        print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "📝 Current Account: " + 
              Fore.LIGHTGREEN_EX + f"[{idx}] {name}" + 
              Fore.LIGHTCYAN_EX + f" ({accounts_count} total)" +
              " " * (30 - len(f"[{idx}] {name}") - len(f" ({accounts_count} total)")) + Fore.WHITE + "║")
    else:
        print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "📝 Current Account: " + 
              Fore.LIGHTRED_EX + "No account selected" + " " * 35 + Fore.WHITE + "║")

    # Auto Kick Status
    auto_kick_color = Fore.LIGHTGREEN_EX if auto_kick_status else Fore.LIGHTRED_EX
    auto_kick_text = "ON" if auto_kick_status else "OFF"
    auto_kick_emoji = "✅" if auto_kick_status else "❌"
    rewards_text = Fore.LIGHTCYAN_EX + f" (with rewards)" if claim_rewards and auto_kick_status else (
                   Fore.LIGHTCYAN_EX + f" (without rewards)" if auto_kick_status else "")
    
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + f"🤖 Auto Kick: " + 
          auto_kick_color + f"{auto_kick_emoji} {auto_kick_text}" + 
          rewards_text + " " * (48 - len(rewards_text)) + Fore.WHITE + "║")
    
    print(Fore.WHITE + "╠" + "═" * 68 + "╣")
    
    # KEYBOARD SHORTCUTS
    print(Fore.WHITE + "║" + Fore.LIGHTBLUE_EX + " 🎮 KEYBOARD SHORTCUTS " + Fore.WHITE + "═" * 46 + "║")
    
    # Account management section
    print(Fore.WHITE + "║ " + Fore.LIGHTMAGENTA_EX + "┌─ ACCOUNT MANAGEMENT " + "─" * 46 + Fore.WHITE + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTMAGENTA_EX + "│ " + 
          Fore.GREEN + "AltGr+DOWN  " + Fore.WHITE + "→ Show current account" + " " * 32 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTMAGENTA_EX + "│ " + 
          Fore.GREEN + "AltGr+LEFT  " + Fore.WHITE + "→ Previous account" + " " * 36 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTMAGENTA_EX + "│ " + 
          Fore.GREEN + "AltGr+RIGHT " + Fore.WHITE + "→ Next account" + " " * 39 + "║")
    
    # Game actions section
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "┌─ GAME ACTIONS " + "─" * 53 + Fore.WHITE + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "│ " + 
          Fore.GREEN + "AltGr+UP    " + Fore.WHITE + "→ Launch Fortnite" + " " * 37 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "│ " + 
          Fore.GREEN + "AltGr+S     " + Fore.WHITE + "→ Skip mission animation" + " " * 32 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "│ " + 
          Fore.GREEN + "AltGr+L     " + Fore.WHITE + "→ Leave current party" + " " * 35 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTYELLOW_EX + "│ " + 
          Fore.GREEN + "AltGr+P     " + Fore.WHITE + "→ Fast Drop (hold keys together)" + " " * 23 + "║")
    
    # Auto Kick controls - highlight based on current status
    print(Fore.WHITE + "║ " + Fore.LIGHTGREEN_EX + "┌─ AUTO KICK CONTROLS " + "─" * 47 + Fore.WHITE + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTGREEN_EX + "│ " + 
          Fore.GREEN + "AltGr+K     " + Fore.WHITE + "→ Toggle Auto Kick " + 
          auto_kick_color + f"{auto_kick_emoji} {auto_kick_text}" + " " * 26 + Fore.WHITE + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTGREEN_EX + "│ " + 
          Fore.GREEN + "AltGr+R     " + Fore.WHITE + "→ Toggle rewards claiming" + " " * 31 + "║")
    
    # Utilities section
    print(Fore.WHITE + "║ " + Fore.LIGHTCYAN_EX + "┌─ UTILITIES " + "─" * 56 + Fore.WHITE + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTCYAN_EX + "│ " + 
          Fore.GREEN + "AltGr+Q     " + Fore.WHITE + "→ Open FortniteDB website" + " " * 31 + "║")
    print(Fore.WHITE + "║ " + Fore.LIGHTCYAN_EX + "│ " + 
          Fore.GREEN + "AltGr+ESC   " + Fore.WHITE + "→ Exit Better Fortnite" + " " * 34 + "║")
    
    print(Fore.WHITE + "╚" + "═" * 68 + "╝" + Style.RESET_ALL)