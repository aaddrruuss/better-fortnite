import tkinter as tk

popup_root = None
popup_label = None

def create_popup():
    root = tk.Tk()
    root.overrideredirect(True)   # Sin bordes ni barra de título
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0.8)
    width = 350
    height = 30
    screen_width = root.winfo_screenwidth()
    x = screen_width - width - 10
    y = 10
    root.geometry(f"{width}x{height}+{x}+{y}")
    label = tk.Label(root, text="Loading...", font=("Courier New", 12), bg="white", fg="black")
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
