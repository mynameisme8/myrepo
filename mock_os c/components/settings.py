import tkinter as tk
from tkinter import ttk, messagebox


def open_settings(app):
    """Open settings window. Expects `app` to be the MockOS instance."""
    print('[MOCKOS] open_settings (component)')
    w = app._make_window('Settings', (420, 300))
    f = tk.Frame(w)
    f.pack(fill='both', expand=True, padx=8, pady=8)
    ttk.Label(f, text='MockOS Settings').pack(pady=6)
    ttk.Button(f, text='About', command=lambda: messagebox.showinfo('About', 'MockOS demo')).pack(pady=6)
    ttk.Button(f, text='Profiles', command=lambda: app.open_profile_manager(w)).pack(pady=6)
