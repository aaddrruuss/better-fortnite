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
    """Display the Better Fortnite ASCII art title with a modern look"""
    # Modern gradient colors
    c1 = Fore.LIGHTBLUE_EX
    c2 = Fore.CYAN
    
    print(c1 + """
     ██████╗ ███████╗████████╗████████╗███████╗██████╗ 
     ██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗
     ██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝
     ██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗
     ██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║
     ╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝""" + c2 + """
     ███████╗ ██████╗ ██████╗ ████████╗███╗   ██╗██╗████████╗███████╗
     ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝████╗  ██║██║╚══██╔══╝██╔════╝
     █████╗  ██║   ██║██████╔╝   ██║   ██╔██╗ ██║██║   ██║   █████╗  
     ██╔══╝  ██║   ██║██╔══██╗   ██║   ██║╚██╗██║██║   ██║   ██╔══╝  
     ██║     ╚██████╔╝██║  ██║   ██║   ██║ ╚████║██║   ██║   ███████╗
     ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═══╝╚═╝   ╚══════╝""" + Style.RESET_ALL)

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
    """Display a simplified, borderless interface with stacked elements"""
    # Colors
    blue = Fore.BLUE
    cyan = Fore.CYAN
    yellow = Fore.YELLOW
    green = Fore.LIGHTGREEN_EX
    red = Fore.LIGHTRED_EX
    magenta = Fore.LIGHTMAGENTA_EX
    white = Fore.WHITE
    reset = Style.RESET_ALL
    
    # Status indicators with emojis
    if auto_kick_status:
        kick_status = f"{green}✅ ACTIVE{reset}"
        rewards_status = f"{green}🎁 WITH REWARDS{reset}" if claim_rewards else f"{yellow}📦 WITHOUT REWARDS{reset}"
    else:
        kick_status = f"{red}❌ INACTIVE{reset}"
        rewards_status = ""
    
    # Title and account information
    print()
    print(f"{Back.BLUE}{white} 🎮 BETTER FORTNITE DASHBOARD {reset}")
    print()
    
    # Account information with emoji
    if current_account:
        idx, name = current_account
        print(f"👤 {yellow}ACCOUNT:{reset} {white}[{idx}] {name}{reset} {cyan}({accounts_count} total){reset}")
    else:
        print(f"👤 {yellow}ACCOUNT:{reset} {red}No account selected{reset}")
    
    # Auto-Kick status line
    print(f"🤖 {yellow}AUTO KICK:{reset} {kick_status} {rewards_status}")
    
    print()
    print(f"{yellow}⌨️  KEYBOARD SHORTCUTS:{reset}")
    print()
    
    # Account management section - now in a single column
    print(f"{blue}▌{white} 👥 {yellow}ACCOUNT MANAGEMENT{reset}")
    print(f"   {cyan}AltGr+DOWN{reset}  Show current account")
    print(f"   {cyan}AltGr+LEFT{reset}  Previous account")
    print(f"   {cyan}AltGr+RIGHT{reset} Next account")
    
    print()
    
    # Game actions section 
    print(f"{blue}▌{white} 🎮 {yellow}GAME ACTIONS{reset}")
    print(f"   {cyan}AltGr+UP{reset}    Launch Fortnite")
    print(f"   {cyan}AltGr+S{reset}     Skip mission")
    print(f"   {cyan}AltGr+L{reset}     Leave party")
    
    print()
    
    # Auto kick section
    print(f"{blue}▌{white} 👢 {yellow}AUTO KICK CONTROLS{reset}")
    status_emoji = "✅" if auto_kick_status else "❌"
    print(f"   {cyan}AltGr+K{reset}     Toggle Auto Kick {status_emoji}")
    print(f"   {cyan}AltGr+R{reset}     Toggle rewards claim")
    
    print()
    
    # Tools section
    print(f"{blue}▌{white} 🛠️ {yellow}TOOLS & UTILITIES{reset}")
    print(f"   {cyan}AltGr+P{reset}     Fast Drop (hold)")
    print(f"   {cyan}AltGr+Q{reset}     FortniteDB website")
    print(f"   {cyan}AltGr+ESC{reset}   Exit")
    
    print()