import tkinter as tk
from tkinter import ttk
import platform
import threading
import time

popup_root = None
popup_label = None
popup_account_label = None
popup_status_indicator = None

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
    
    # Set transparency (platform specific)
    if platform.system() == "Windows":
        root.attributes("-alpha", 0.9)
    
    # Use a nicer theme if available
    try:
        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")
    except:
        pass
    
    # Configure size and position
    width = 380
    height = 40
    screen_width = root.winfo_screenwidth()
    x = screen_width - width - 20
    y = 20
    root.geometry(f"{width}x{height}+{x}+{y}")
    
    # Create a frame with gradient-like effect
    frame = tk.Frame(root, bg="#2C3E50")  # Dark blue background
    frame.pack(expand=True, fill="both")
    
    # Status indicator (colored circle)
    status_indicator = tk.Canvas(frame, width=10, height=10, bg="#2C3E50", highlightthickness=0)
    status_indicator.place(x=10, y=15)
    status_indicator.create_oval(0, 0, 10, 10, fill="#2ECC71", outline="")  # Green circle
    
    # Better Fortnite label
    title_label = tk.Label(frame, text="Better Fortnite", font=("Arial", 9, "bold"), 
                           bg="#2C3E50", fg="#3498DB")  # Light blue text
    title_label.place(x=25, y=3)
    
    # Account status label
    account_label = tk.Label(frame, text="Loading...", font=("Arial", 9), 
                             bg="#2C3E50", fg="#ECF0F1")  # White text
    account_label.place(x=25, y=20)
    
    # Add a close button
    close_btn = tk.Button(frame, text="×", font=("Arial", 12), bg="#2C3E50", fg="#ECF0F1",
                         relief="flat", command=root.destroy, cursor="hand2")
    close_btn.place(x=width-25, y=8)
    
    # Bind mouse events for dragging
    frame.bind("<ButtonPress-1>", on_drag_start)
    frame.bind("<B1-Motion>", on_drag_motion)
    
    return root, account_label, status_indicator

def popup_loop():
    global popup_root, popup_label, popup_status_indicator
    popup_root, popup_label, popup_status_indicator = create_popup()
    popup_root.mainloop()

def fade_text_effect(new_text, label, steps=5, delay=0.02):
    """Crea un efecto de transición suave para el texto"""
    current_fg = label.cget("fg")
    
    # Primero desvanecemos el texto actual
    for i in range(steps):
        alpha = 1.0 - (i / steps)
        # Calculamos el color con transparencia
        label.config(fg=f"#{int(int(current_fg[1:3], 16) * alpha):02x}{int(int(current_fg[3:5], 16) * alpha):02x}{int(int(current_fg[5:7], 16) * alpha):02x}")
        label.update()
        time.sleep(delay)
    
    # Establecemos el nuevo texto
    label.config(text=new_text)
    
    # Hacemos aparecer el nuevo texto
    for i in range(steps):
        alpha = i / steps
        # Calculamos el color con transparencia aumentando
        label.config(fg=f"#{int(int(current_fg[1:3], 16) * alpha):02x}{int(int(current_fg[3:5], 16) * alpha):02x}{int(int(current_fg[5:7], 16) * alpha):02x}")
        label.update()
        time.sleep(delay)
    
    # Restauramos el color original
    label.config(fg=current_fg)

def update_popup(text: str, status="online"):
    """Update popup text and status indicator color with smooth transition"""
    global popup_root, popup_label, popup_status_indicator
    
    if popup_root is not None:
        # Actualizamos el texto con una transición suave en un hilo separado
        threading.Thread(target=lambda: popup_root.after(0, lambda: fade_text_effect(text, popup_label)), daemon=True).start()
        
        # Update status indicator color
        color = "#2ECC71"  # Green (default/online)
        if status == "busy":
            color = "#E74C3C"  # Red
        elif status == "away":
            color = "#F39C12"  # Orange
        elif status == "loading":
            color = "#3498DB"  # Blue
            
        popup_root.after(0, lambda: popup_status_indicator.itemconfig(1, fill=color))
