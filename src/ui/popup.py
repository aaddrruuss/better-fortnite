import tkinter as tk

popup_root = None
popup_label = None

def create_popup():
    root = tk.Tk()
    root.overrideredirect(True)   # Sin bordes ni barra de título
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.85)
    width = 300
    height = 50
    screen_width = root.winfo_screenwidth()
    x = screen_width - width - 10
    y = 10
    root.geometry(f"{width}x{height}+{x}+{y}")
    label = tk.Label(root, text="Cuenta actual: ", font=("Arial", 12), bg="black", fg="white")
    label.pack(expand=True, fill="both")
    return root, label

def popup_loop():
    global popup_root, popup_label
    popup_root, popup_label = create_popup()
    popup_root.mainloop()

def update_popup(text: str):
    global popup_root, popup_label
    if popup_root is not None:
        popup_root.after(0, lambda: popup_label.config(text=text))
