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
        title_label = ctk.CTkLabel(parent, text="Better Fortnite", font=("General Sans Font"))        