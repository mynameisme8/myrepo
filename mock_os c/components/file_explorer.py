import os
import tkinter as tk
from tkinter import messagebox


def open_file_explorer(app):
    print('[MOCKOS] open_file_explorer (component)')
    w = app._make_window('File Explorer', (600, 400))
    frame = tk.Frame(w)
    frame.pack(fill='both', expand=True)
    lb = tk.Listbox(frame)
    lb.pack(side='left', fill='both', expand=True)
    scrollbar = tk.Scrollbar(frame, command=lb.yview)
    scrollbar.pack(side='right', fill='y')
    lb.config(yscrollcommand=scrollbar.set)
    path = app.workspace_root
    try:
        files = os.listdir(path)
    except Exception:
        files = []
    for f in files:
        lb.insert('end', f)
    def on_open(e=None):
        sel = lb.curselection()
        if not sel:
            return
        name = lb.get(sel[0])
        full = os.path.join(path, name)
        if os.path.isdir(full):
            try:
                lb.delete(0, 'end')
                for nf in os.listdir(full):
                    lb.insert('end', nf)
            except Exception as e:
                messagebox.showerror('Error', str(e))
        else:
            try:
                with open(full, 'r', encoding='utf-8', errors='ignore') as fh:
                    content = fh.read()
                vw = app._make_window(name, (700, 500))
                t = tk.Text(vw)
                t.insert('1.0', content)
                t.pack(fill='both', expand=True)
            except Exception as e:
                messagebox.showerror('Open file', f"Cannot open file: {e}")
    lb.bind('<Double-Button-1>', on_open)
