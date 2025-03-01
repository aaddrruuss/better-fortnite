from colorama import init, Fore
init()


def better_fortnite_ascii():
    print(Fore.CYAN + """
██████╗ ███████╗████████╗████████╗███████╗██████╗     ███████╗ ██████╗ ██████╗ ████████╗███╗   ██╗██╗████████╗███████╗
██╔══██╗██╔════╝╚══██╔══╝╚══██╔══╝██╔════╝██╔══██╗    ██╔════╝██╔═══██╗██╔══██╗╚══██╔══╝████╗  ██║██║╚══██╔══╝██╔════╝
██████╔╝█████╗     ██║      ██║   █████╗  ██████╔╝    █████╗  ██║   ██║██████╔╝   ██║   ██╔██╗ ██║██║   ██║   █████╗  
██╔══██╗██╔══╝     ██║      ██║   ██╔══╝  ██╔══██╗    ██╔══╝  ██║   ██║██╔══██╗   ██║   ██║╚██╗██║██║   ██║   ██╔══╝  
██████╔╝███████╗   ██║      ██║   ███████╗██║  ██║    ██║     ╚██████╔╝██║  ██║   ██║   ██║ ╚████║██║   ██║   ███████╗
╚═════╝ ╚══════╝   ╚═╝      ╚═╝   ╚══════╝╚═╝  ╚═╝    ╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝  ╚═══╝╚═╝   ╚═╝   ╚══════╝

    """ + Fore.RESET)

def cmd_interface():

    print("\n" + Fore.CYAN +"==================================================================================")
    print("Instructions and Hotkeys:")
    print("  - AltGr+L\t->\tExecutes 'Leave Party' with the current account")
    print("  - AltGr+S\t->\tExecutes 'Skip' with the current account")
    print("  - AltGr+Up\t->\tLaunches Fortnite with the current account")
    print("  - AltGr+Right ->\tSwitches to the next account (or prompts to add a new one)")
    print("  - AltGr+Left\t->\tSwitches to the previous account")
    print("  - AltGr+Down\t->\tDisplays the current account in the console")
    print("  - AltGr+Q\t->\tOpens FortniteDB.com in the browser")
    print("  - AltGr+P\t->\tWhile holding, you will activate fast drop script")
    print("==================================================================================")
    print("Press ALTGR+ESC to exit." + Fore.RESET)