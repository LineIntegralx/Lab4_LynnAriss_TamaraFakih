# gui/choose_gui.py
"""Launcher module to choose between PyQt5 and Tkinter GUI applications."""

import sys
import tkinter as tk
from tkinter import messagebox

def launch_pyqt():
    """Launch the PyQt5 GUI application.

    :raises ImportError: If PyQt5 or the PyQt5 application module cannot be imported.
    :returns: None
    """
    try:
        from Pyqt5 import SchoolManagementSystem
        from PyQt5.QtWidgets import QApplication
    except ImportError:
        messagebox.showerror("Error", "PyQt5 module not found!")
        return

    root.destroy()
    app = QApplication(sys.argv)
    window = SchoolManagementSystem()
    window.show()
    sys.exit(app.exec_())

def launch_tkinter():
    """Launch the Tkinter GUI application.

    :raises ImportError: If Tkinter or the Tkinter application module cannot be imported.
    :returns: None
    """
    try:
        from tkinter_app_db import App
    except ImportError:
        messagebox.showerror("Error", "Tkinter app module not found!")
        return
    try:
        import tkinter
    except ImportError:
        messagebox.showerror("Error", "Tkinter module not installed in your Python environment!")
        return

    root.destroy()
    app = App()
    app.mainloop()

root = tk.Tk()
root.title("Choose GUI Library")
root.geometry("320x150")
root.resizable(False, False)

label = tk.Label(root, text="Select GUI Library to Launch", font=("Segoe UI", 12))
label.pack(pady=15)

btn_pyqt = tk.Button(root, text="PyQt5", width=25, command=launch_pyqt)
btn_pyqt.pack(pady=5)

btn_tk = tk.Button(root, text="Tkinter", width=25, command=launch_tkinter)
btn_tk.pack(pady=5)

root.mainloop()
