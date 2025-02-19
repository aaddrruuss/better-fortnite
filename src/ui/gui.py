import customtkinter as ctk

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("dark-blue")

class BetterFortniteApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Better Fortnite")
        self.geometry("800x600")

        self._create_widgets()

    def _create_widgets(self):
        main_frame = ctk.CTkFrame(self)
        main_frame.pack(fill="both", expand=True)

        sidebar_frame = ctk.CTkFrame(main_frame, width=200)
        sidebar_frame.pack(side="left", fill="y")

        self.content_frame = ctk.CTkFrame(main_frame)
        self.content_frame.pack(side="left", fill="both", expand=True)

        self._create_sidebar(sidebar_frame)
        self._create_content(self.content_frame)

    def _create_content(self, parent):
        # Crear titulo
        title_label = ctk.CTkLabel(parent, text="Better Fortnite", font=("General Sans Font", 16, "bold"))
        title_label.pack(pady=20, padx=10)

        # Boton "Leave Party"
        btn_leave = ctk.CTkButton(parent, text="Leave Party", command=self.leave_party)
        btn_leave.pack(pady=5, padx=10)

        # Boton "Skip"
        btn_skip = ctk.CTkButton(parent, text="Skip", command=self.skip)
        btn_skip.pack(pady=5, padx=10)

        # Boton "Open Fortnite"
        btn_play = ctk.CTkButton(parent, text="Open Fortnite", command=self.play_fortnite)
        btn_play.pack(pady=5, padx=10)

        # Botones para cambiar entre cuentas
        btn_prev = ctk.CTkButton(parent, text="< Previous account", command=self.switch_account_left)
        btn_prev.pack(pady=5, padx=10)

        btn_next = ctk.CTkButton(parent, text="Next account >", command=self.switch_account_right)
        btn_next.pack(pady=5, padx=10)
        
    def _create_content(self, parent):
        label = ctk.CTkLabel(parent, text="Welcome to Better Fortnite", font=("General Sans Font", 20, "bold"))
        label.pack(pady=20)

        self.log_text = ctk.CTkTextbox(parent, width=400, height= 200)
        self.log_text.pack(pady=10)

    def leave_party(self):
        from ..main import on_leave_party
        try:
            on_leave_party()
            self.append_log("Party left") 
        except:
            self.apeend_log("Error leaving party")

    def skip(self):
        from ..main import on_skip
        try:
            on_skip()
            self.append_log("[+] Animation skipped and rewards claimed")
        except:
            self.append_log("[-] Error skipping animation")
    
    def play_fortnite(self):
        from ..main import on_play_fortnite
        try:
            on_play_fortnite()
            self.append_log("[+] Fortnite has been opened")
        except:
            self.append_log("[-] Error executing Fortnite")
    
    def switch_account_left(self):
        from ..main import on_switch_account_left
        try: 
            on_switch_account_left()
            self.append_log("[+] Account switched")
        except:
            self.append_log("[-] Error switching between accounts")
    
    def switch_account_right(self):
        from ..main import on_switch_account_right
        try:
            on_switch_account_right()
            self.append_log("[+] Account switched")
        except:
            self.append_log("[-] Error switching between accounts")
    
    def append_log(self, message: str):
        self.log_text.insert("end", message + "\n")
        self.log_text.see("end")
