# custom_dialog.py
import tkinter as tk

class CustomDialog(tk.Toplevel):
    def __init__(self, parent, title, question, options):
        super().__init__(parent)
        self.title(title)
        self.transient(parent)
        self.grab_set()
        self.parent = parent
        self.result = None

        self.protocol("WM_DELETE_WINDOW", self.cancel)

        tk.Label(self, text=question, padx=40, pady=100).pack()

        button_frame = tk.Frame(self)
        button_frame.pack(padx=10, pady=10)
        
        self.geometry("350x150")

        for option in options:
            tk.Button(button_frame, text=option, command=lambda o=option: self.on_button_click(o), width=10) \
              .pack(side=tk.LEFT, padx=5, pady=5)
        
        # Opcional: Centrar el diálogo
        self.update_idletasks()
        window_width = self.winfo_width()
        window_height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        position_top = int(screen_height/2 - window_height/2)
        position_right = int(screen_width/2 - window_width/2)
        self.geometry(f"{350}x{350}+{position_right}+{position_top}")


        # Esperar a que la ventana se cierre
        self.wait_window(self)

    def on_button_click(self, choice):
        self.result = choice
        self.destroy()

    def cancel(self):
        self.result = None
        self.destroy()

def show_custom_dialog(parent, title, question, options):
    """Función de utilidad para mostrar el diálogo y devolver el resultado."""
    dialog = CustomDialog(parent, title, question, options)
    return dialog.result

