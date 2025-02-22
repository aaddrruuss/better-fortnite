import tkinter as tk

popup_root = None
popup_label = None

def on_drag_start(event):
    event.widget._drag_start_x = event.x
    event.widget._drag_start_y = event.y

def on_drag_motion(event):
    x = event.x_root - event.widget._drag_start_x
    y = event.y_root - event.widget._drag_start_y
    event.widget.winfo_toplevel().geometry(f"+{x}+{y}")

def create_popup():
    root = tk.Tk()
    root.overrideredirect(True)   # Borderless window
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
    
    # Bind mouse events to enable dragging
    root.bind("<ButtonPress-1>", on_drag_start)
    root.bind("<B1-Motion>", on_drag_motion)
    
    return root, label

def popup_loop():
    global popup_root, popup_label
    popup_root, popup_label = create_popup()
    popup_root.mainloop()

def update_popup(text: str):
    global popup_root, popup_label
    if popup_root is not None:
        popup_root.after(0, lambda: popup_label.config(text=text))
