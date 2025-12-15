import tkinter as tk
import time


class SplashScreen:
    def __init__(self, root, duration=5):
        self.root = root
        self.duration = duration
        self.start_time = None
        self._aborted = False
        self._bios_open = False

        self.win = tk.Toplevel(root)
        self.win.overrideredirect(True)
        sw = root.winfo_screenwidth()
        sh = root.winfo_screenheight()
        self.win.geometry(f"{sw}x{sh}+0+0")
        self.win.configure(bg='black')
        try:
            self.win.focus_force()
        except Exception:
            pass

        frm = tk.Frame(self.win, bg='black')
        frm.place(relx=0.5, rely=0.4, anchor='center')
        logo = tk.Label(frm, text='MockOS', fg='white', bg='black', font=('Segoe UI', 40))
        logo.pack()

        self.spinner_label = tk.Label(self.win, text='', fg='white', bg='black', font=('Consolas', 24))
        self.spinner_label.place(relx=0.5, rely=0.55, anchor='center')

        self.console = tk.Text(self.win, height=8, bg='black', fg='#66ff66', bd=0, highlightthickness=0)
        self.console.place(relx=0.5, rely=0.75, anchor='center', relwidth=0.8)
        self.console.insert('end', 'Initializing system...\n')
        self.console.config(state='disabled')

        self.win.bind('<Key>', self._on_key)

        self.spinner_chars = ['|', '/', '-', '\\']
        self.spin_index = 0
        self.messages = [
            'POST: All systems nominal',
            'Checking devices... done',
            'Loading firmware...',
            'Initializing network: none',
            'Bootloader ready'
        ]

    def _on_key(self, event):
        if event.keysym == 'Return' and not self._bios_open:
            self.open_bios()

    def open_bios(self):
        self._bios_open = True
        bio = tk.Toplevel(self.win)
        bio.title('BIOS')
        bio.geometry('640x360+100+100')
        bio.transient(self.win)
        tk.Label(bio, text='Mock BIOS', font=('Consolas', 16)).pack(pady=8)
        tk.Label(bio, text='Press F10 to boot, Esc to resume').pack()
        def on_f10(e=None):
            bio.destroy()
            self._bios_open = False
            self._aborted = False
        def on_esc(e=None):
            bio.destroy()
            self._bios_open = False
        bio.bind('<F10>', on_f10)
        bio.bind('<Escape>', on_esc)

    def run(self, callback_after):
        self.start_time = time.time()
        self._tick_messages_index = 0
        self._last_msg_time = time.time()

        def loop():
            if self._aborted:
                self.win.destroy()
                callback_after()
                return
            elapsed = time.time() - self.start_time
            self.spinner_label.config(text=self.spinner_chars[self.spin_index % len(self.spinner_chars)])
            self.spin_index += 1
            if time.time() - self._last_msg_time > 0.8 and self._tick_messages_index < len(self.messages):
                self.console.config(state='normal')
                self.console.insert('end', self.messages[self._tick_messages_index] + '\n')
                self.console.see('end')
                self.console.config(state='disabled')
                self._tick_messages_index += 1
                self._last_msg_time = time.time()
            if elapsed >= self.duration and not self._bios_open:
                self.win.destroy()
                callback_after()
                return
            self.win.after(120, loop)

        loop()
