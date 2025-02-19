import os
import sys
import threading
import asyncio
import tkinter as tk
from tkinter import filedialog

# ======================================================
# SOLUCIÓN RÁPIDA PARA PODER IMPORTAR config.py DESDE EL DIRECTORIO PADRE (src/)
# ======================================================
parent_dir = os.path.join(os.path.dirname(__file__), '..')
sys.path.append(parent_dir)

import customtkinter as ctk
import tkinter.ttk as ttk  # Usaremos ttk.Separator
import config  # Para acceder a display_names y FORTNITE_DIR

from account.manager import load_all_accounts, get_display_name_for_account

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class BetterFortniteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Better Fortnite")
        self.geometry("800x600")

        # Cargar las cuentas guardadas (si existen)
        self.accounts_list = load_all_accounts()  # Lista de tuplas (filename, data)
        config.display_names.clear()
        if self.accounts_list:
            for fname, data in self.accounts_list:
                display = asyncio.run(get_display_name_for_account(data))
                config.display_names.append(display)
            self.current_account_index = 0
            self.current_display_name = config.display_names[0]
        else:
            self.accounts_list = []
            self.current_account_index = -1
            self.current_display_name = ""

        self._create_widgets()
        self.setup_hotkeys()

    def _create_widgets(self):
        """Crea la estructura principal: sidebar y área de contenido."""
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(fill="both", expand=True)

        # Sidebar
        self.sidebar_frame = ctk.CTkFrame(
            self.main_frame,
            width=200,
            fg_color="#4e7f94",
            corner_radius=0
        )
        self.sidebar_frame.pack(side="left", fill="y")

        # Área de contenido
        self.content_frame = ctk.CTkFrame(self.main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self._create_sidebar(self.sidebar_frame)
        self.show_home()

    def _create_sidebar(self, parent):
        """Crea la barra lateral con título, botones y OptionMenu para cuentas."""
        title_label = ctk.CTkLabel(
            parent,
            text="Better Fortnite",
            font=("Arial", 20, "bold")
        )
        title_label.pack(pady=20, padx=10)

        self.btn_home = ctk.CTkButton(
            parent,
            text="Home",
            command=self.show_home,
            width=180,
            height=40,
            corner_radius=10
        )
        self.btn_home.pack(pady=10, padx=10)

        self.btn_settings = ctk.CTkButton(
            parent,
            text="Settings",
            command=self.show_settings,
            width=180,
            height=40,
            corner_radius=10
        )
        self.btn_settings.pack(pady=10, padx=10)

        self.btn_placeholder = ctk.CTkButton(
            parent,
            text="Placeholder",
            command=self.show_placeholder,
            width=180,
            height=40,
            corner_radius=10
        )
        self.btn_placeholder.pack(pady=10, padx=10)

        separator = ttk.Separator(parent, orient="horizontal")
        separator.pack(fill="x", pady=20, padx=10)

        # Sub-frame para "Change Account"
        self.account_frame = ctk.CTkFrame(parent, fg_color="transparent")
        self.account_frame.place(relx=0.8, rely=1.0, anchor="se", x=-10, y=-10)

        change_account_label = ctk.CTkLabel(
            self.account_frame,
            text="Change Account:",
            font=("Arial", 14, "bold")
        )
        change_account_label.pack(pady=(0, 5), anchor="e")

        account_values = config.display_names.copy()
        if not account_values:
            account_values = ["No account"]
        account_values.append("Add new account...")
        default_account = self.current_display_name if self.current_display_name else account_values[0]

        self.account_optionmenu = ctk.CTkOptionMenu(
            self.account_frame,
            values=account_values,
            command=self.on_select_account
        )
        self.account_optionmenu.set(default_account)
        self.account_optionmenu.pack(anchor="e")

    def on_select_account(self, choice):
        """Si se selecciona 'Add new account...' inicia autenticación; si no, cambia la cuenta."""
        if choice == "Add new account...":
            self.add_new_account()
        else:
            try:
                idx = config.display_names.index(choice)
                self.current_account_index = idx
                self.current_display_name = choice
                self.update_welcome(choice)
                self.account_optionmenu.set(choice)
                self.append_log(f"[+] Cuenta cambiada a: {choice}")
            except Exception as e:
                self.append_log(f"[!] Error al cambiar de cuenta: {e}")

    def add_new_account(self):
        import threading
        threading.Thread(target=self._authenticate_new_account, daemon=True).start()

    def _authenticate_new_account(self):
        try:
            from account.manager import authenticate, get_display_name_for_account
            new_filename = f"device_auths{len(self.accounts_list) + 1}.json"
            data = asyncio.run(authenticate(new_filename))
            new_display = asyncio.run(get_display_name_for_account(data))
            self.after(0, lambda: self._update_after_new_account(new_display, data))
            self.after(0, lambda: self.append_log(f"[+] Nueva cuenta agregada: {new_display}"))
        except Exception as e:
            self.after(0, lambda: self.append_log(f"[!] Error al agregar nueva cuenta: {e}"))

    def _update_after_new_account(self, new_display, data):
        self.accounts_list.append(("nuevo", data))  # "nuevo" es un placeholder
        config.display_names.append(new_display)
        self.current_account_index = len(self.accounts_list) - 1
        self.current_display_name = new_display
        self.update_welcome(new_display)
        new_values = config.display_names.copy()
        new_values.append("Add new account...")
        self.account_optionmenu.configure(values=new_values)
        self.account_optionmenu.set(new_display)

    def switch_account_right(self):
        if not self.accounts_list:
            self.append_log("[!] No hay cuentas guardadas.")
            return
        self.current_account_index = (self.current_account_index + 1) % len(self.accounts_list)
        new_display = config.display_names[self.current_account_index]
        self.current_display_name = new_display
        self.update_welcome(new_display)
        self.account_optionmenu.set(new_display)
        self.append_log(f"[+] Cuenta cambiada a: {new_display}")

    def switch_account_left(self):
        if not self.accounts_list:
            self.append_log("[!] No hay cuentas guardadas.")
            return
        self.current_account_index = (self.current_account_index - 1) % len(self.accounts_list)
        new_display = config.display_names[self.current_account_index]
        self.current_display_name = new_display
        self.update_welcome(new_display)
        self.account_optionmenu.set(new_display)
        self.append_log(f"[+] Cuenta cambiada a: {new_display}")

    def setup_hotkeys(self):
        try:
            import keyboard
            keyboard.add_hotkey('alt gr+left', lambda: self.switch_account_left())
            keyboard.add_hotkey('alt gr+right', lambda: self.switch_account_right())
        except Exception as e:
            self.append_log(f"[!] Error configurando hotkeys: {e}")

    def show_home(self):
        """Muestra la pantalla Home sin borrar el log."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.variable_frame = ctk.CTkFrame(self.content_frame)
        self.variable_frame.pack(side="top", fill="both", expand=True)
        self.log_frame = ctk.CTkFrame(self.content_frame)
        self.log_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        if not hasattr(self, 'log_text'):
            self.log_text = ctk.CTkTextbox(
                self.log_frame,
                width=400,
                height=200,
                corner_radius=0,
                border_width=2,
                border_color="black",
                fg_color="white",
                text_color="black"
            )
            self.log_text.pack(fill="x")
            self.log_text.configure(state="disabled")
        welcome_text = "WELCOME"
        if self.current_display_name:
            welcome_text += " " + self.current_display_name
        self.welcome_label = ctk.CTkLabel(
            self.variable_frame,
            text=welcome_text,
            font=("General Sans Font", 20, "bold")
        )
        self.welcome_label.pack(pady=20)
        # Botón "Open Fortnite" debajo del welcome
        open_btn = ctk.CTkButton(
            self.variable_frame,
            text="Open Fortnite",
            command=self.open_fortnite,
            width=150,
            height=40,
            corner_radius=10
        )
        open_btn.pack(pady=10)

    def show_settings(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.variable_frame = ctk.CTkFrame(self.content_frame)
        self.variable_frame.pack(side="top", fill="both", expand=True)
        self.log_frame = ctk.CTkFrame(self.content_frame)
        self.log_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        settings_label = ctk.CTkLabel(
            self.variable_frame,
            text="Settings",
            font=("General Sans Font", 20, "bold")
        )
        settings_label.pack(pady=20)
        self.mode_switch = ctk.CTkSwitch(
            self.variable_frame,
            text="Light Mode",
            command=self.toggle_mode
        )
        self.mode_switch.pack(pady=10)
        if ctk.get_appearance_mode() == "Dark":
            self.mode_switch.deselect()
        else:
            self.mode_switch.select()
        # Nuevo: Botón para seleccionar el directorio de Fortnite
        select_dir_btn = ctk.CTkButton(
            self.variable_frame,
            text="Select Fortnite Directory",
            command=self.select_fortnite_dir,
            width=220,
            height=40,
            corner_radius=10
        )
        select_dir_btn.pack(pady=10)
        # Label para mostrar el directorio actual
        self.dir_label = ctk.CTkLabel(
            self.variable_frame,
            text=f"Current Fortnite Directory:\n{config.FORTNITE_DIR}",
            font=("Arial", 12)
        )
        self.dir_label.pack(pady=10)
        btn_back = ctk.CTkButton(
            self.variable_frame,
            text="Back",
            command=self.show_home
        )
        btn_back.pack(pady=10)

    def select_fortnite_dir(self):
        """Abre el explorador de archivos para seleccionar la carpeta que contiene FortniteLauncher.exe."""
        selected = filedialog.askdirectory(initialdir=config.FORTNITE_DIR, title="Select Fortnite Directory")
        if selected:
            config.FORTNITE_DIR = selected
            self.append_log(f"[+] Fortnite directory updated: {selected}")
            if hasattr(self, 'dir_label'):
                self.dir_label.configure(text=f"Current Fortnite Directory:\n{config.FORTNITE_DIR}")

    def show_placeholder(self):
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        self.variable_frame = ctk.CTkFrame(self.content_frame)
        self.variable_frame.pack(side="top", fill="both", expand=True)
        self.log_frame = ctk.CTkFrame(self.content_frame)
        self.log_frame.pack(side="bottom", fill="x", padx=20, pady=20)
        placeholder_label = ctk.CTkLabel(
            self.variable_frame,
            text="Placeholder Screen",
            font=("General Sans Font", 20, "bold")
        )
        placeholder_label.pack(pady=20)
        btn_back = ctk.CTkButton(
            self.variable_frame,
            text="Back",
            command=self.show_home
        )
        btn_back.pack(pady=10)

    def toggle_mode(self):
        current_mode = ctk.get_appearance_mode()
        if current_mode == "Dark":
            ctk.set_appearance_mode("Light")
            self.mode_switch.configure(text="Light Mode")
            self.mode_switch.select()
        else:
            ctk.set_appearance_mode("Dark")
            self.mode_switch.configure(text="Dark Mode")
            self.mode_switch.deselect()

    def open_fortnite(self):
        """Cierra Fortnite si está abierto y lo abre en la cuenta activa."""
        if self.current_account_index == -1 or not self.accounts_list:
            self.append_log("[!] No hay cuenta activa.")
            return
        device_auth_data = self.accounts_list[self.current_account_index][1]
        import threading
        threading.Thread(target=lambda: asyncio.run(self._async_open_fortnite(device_auth_data)), daemon=True).start()

    async def _async_open_fortnite(self, device_auth_data: dict):
        try:
            from commands.refresh import command_play_fortnite
            await command_play_fortnite(device_auth_data)
        except Exception as e:
            self.append_log(f"[!] Error al lanzar Fortnite: {e}")

    def update_welcome(self, display_name: str):
        self.current_display_name = display_name
        if hasattr(self, 'welcome_label'):
            self.welcome_label.configure(text="WELCOME " + display_name)

    def append_log(self, message: str):
        if hasattr(self, 'log_text'):
            self.log_text.configure(state="normal")
            self.log_text.insert("end", message + "\n")
            self.log_text.configure(state="disabled")
            self.log_text.see("end")

    def setup_hotkeys(self):
        try:
            import keyboard
            keyboard.add_hotkey('alt gr+left', lambda: self.switch_account_left())
            keyboard.add_hotkey('alt gr+right', lambda: self.switch_account_right())
        except Exception as e:
            self.append_log(f"[!] Error configurando hotkeys: {e}")

if __name__ == "__main__":
    app = BetterFortniteApp()
    app.mainloop()
