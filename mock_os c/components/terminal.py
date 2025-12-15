import os
import tkinter as tk


def open_terminal(app):
    print('[MOCKOS] open_terminal (component)')
    w = app._make_window('Terminal', (700, 400))
    txt = tk.Text(w, bg='#000000', fg='#00ff00', insertbackground='#00ff00')
    txt.pack(fill='both', expand=True)
    entry = tk.Entry(w)
    entry.pack(fill='x')
    def on_enter(e=None):
        cmd = entry.get().strip()
        entry.delete(0, 'end')
        if not cmd:
            return
        txt.insert('end', f"> {cmd}\n")
        if cmd in ('clear', 'cls'):
            txt.delete('1.0', 'end')
        elif cmd.startswith('echo '):
            txt.insert('end', cmd[5:] + '\n')
        elif cmd == 'list':
            for fn in os.listdir(app.workspace_root):
                txt.insert('end', fn + '\n')
        else:
            txt.insert('end', f"Unknown command: {cmd}\n")
        txt.see('end')
    entry.bind('<Return>', on_enter)
