import os
import sys
import json
import time
try:
    from PIL import Image, ImageTk
    PIL_AVAILABLE = True
except Exception:
    PIL_AVAILABLE = False
import math
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from components.settings import open_settings as comp_open_settings
from components.splash import SplashScreen as CompSplashScreen 
from components.terminal import open_terminal as comp_open_terminal
from components.file_explorer import open_file_explorer as comp_open_file_explorer
from components.profile_manager import open_profile_manager as comp_open_profile_manager

print("toggle_fullscreen(self, event=None)\nopen_start_menu(self)\non_toggle_max()\non_minimize()\nopen_profile_manager(self, parent_win=None)\nchoose_profile(root, callback) ")
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_ROOT = os.path.abspath(os.path.join(ROOT_DIR, '..'))
PROFILES_PATH = os.path.join(ROOT_DIR, 'profiles.json')


def load_profiles():
    if not os.path.exists(PROFILES_PATH):
        # create default admin profile
        profiles = {
            "admin": {"display": "Administrator", "is_admin": True, "password": "admin", "avatar": None}
        }
        with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
            json.dump(profiles, f, indent=2)
        return profiles
    try:
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {"admin": {"display": "Administrator", "is_admin": True}}


def save_profiles(profiles):
    with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)



class MockOS:
    def __init__(self, root, profile_id='admin'):
        print('[MOCKOS] starting under profile', profile_id)
        self.root = root
        self.profile_id = profile_id
        # expose workspace root for components
        self.workspace_root = WORKSPACE_ROOT
        root.title('MockOS')
        root.configure(bg='#1e1e2f')
        self.fullscreen = True
        root.attributes('-fullscreen', True)
        root.bind('<F11>', self.toggle_fullscreen)
        root.bind('<Escape>', self.exit_fullscreen)

        # desktop area
        self.desktop = tk.Frame(root, bg='#2b2b44')
        self.desktop.pack(fill='both', expand=True)
        # try to load a desktop wallpaper if provided in assets
        try:
            assets_wall = os.path.join(ROOT_DIR, 'assets', 'IMG_3960.png')
            alt_wall = r"C:\Users\monke\Desktop\python code\mock_os\assets\IMG_3960.png"
            wall_path = assets_wall if os.path.exists(assets_wall) else (alt_wall if os.path.exists(alt_wall) else None)
            if wall_path and PIL_AVAILABLE:
                sw = root.winfo_screenwidth()
                sh = root.winfo_screenheight()
                img = Image.open(wall_path)
                iw, ih = img.size
                scale = max(sw / iw, sh / ih)
                nw, nh = int(iw * scale), int(ih * scale)
                img = img.resize((nw, nh), Image.LANCZOS)
                left = (nw - sw) // 2
                top = (nh - sh) // 2
                img = img.crop((left, top, left + sw, top + sh))
                photo = ImageTk.PhotoImage(img)
                self._wall_label = tk.Label(self.desktop, image=photo)
                self._wall_label.image = photo
                self._wall_label.place(x=0, y=0, relwidth=1, relheight=1)
            elif wall_path:
                # fallback: try loading without resizing
                try:
                    photo = tk.PhotoImage(file=wall_path)
                    self._wall_label = tk.Label(self.desktop, image=photo)
                    self._wall_label.image = photo
                    self._wall_label.place(x=0, y=0, relwidth=1, relheight=1)
                except Exception:
                    pass
        except Exception:
            pass

        # taskbar
        self.taskbar = tk.Frame(root, bg='#171725', height=36)
        self.taskbar.pack(side='bottom', fill='x')
        self._build_taskbar()

        # mapping windows -> taskbar buttons
        self.window_buttons = {}
        # mapping app key/title -> window (prevent multiple instances)
        self.app_windows = {}

        # icons
        self.icon_frame = tk.Frame(self.desktop, bg='#2b2b44')
        self.icon_frame.pack(side='left', anchor='nw', padx=20, pady=20)
        self._place_icons()

        # windows tracking
        self.windows = []

    def toggle_fullscreen(self, event=None):
        self.fullscreen = not self.fullscreen
        print('[MOCKOS] toggle_fullscreen ->', self.fullscreen)
        self.root.attributes('-fullscreen', self.fullscreen)

    def exit_fullscreen(self, event=None):
        print('[MOCKOS] exit request -> closing')
        self.root.attributes('-fullscreen', False)
        self.root.quit()

    def _build_taskbar(self):
        self.start_button = tk.Button(self.taskbar, text='Start', command=self._open_start_menu, bg='#262634', fg='white', bd=0, padx=8, pady=4)
        self.start_button.pack(side='left', padx=6, pady=4)
        # task/window list area (expands)
        self.taskbar_window_frame = tk.Frame(self.taskbar, bg='#1f1f2b')
        self.taskbar_window_frame.pack(side='left', fill='x', expand=True, padx=(6,0), pady=4)
        # right-side status area
        clock = tk.Label(self.taskbar, text=f"MockOS - {self.profile_id}", bg='#171725', fg='#ffffff')
        clock.pack(side='right', padx=10)

        # style tweak: subtle top border to separate desktop and taskbar
        self.taskbar.configure(highlightthickness=0)

    def _open_start_menu(self):
        # toggle existing menu
        if getattr(self, 'start_menu', None):
            try:
                self.start_menu.destroy()
            except Exception:
                pass
            self.start_menu = None
            return

        menu = tk.Toplevel(self.root)
        menu.overrideredirect(True)
        # position the menu above the Start button if space allows
        try:
            sx = self.start_button.winfo_rootx()
            sy = self.start_button.winfo_rooty()
            sw = self.start_button.winfo_width()
            mw = 260
            mh = 300
            x = max(4, sx)
            y = max(4, sy - mh - 6)
            menu.geometry(f"{mw}x{mh}+{x}+{y}")
        except Exception:
            menu.geometry('260x300+10+100')
        # keep the Start menu background color consistent with the original theme
        menu.configure(bg='#2b2b44')

        container = tk.Frame(menu, bg='#2b2b44', bd=1, relief='flat')
        container.pack(fill='both', expand=True, padx=6, pady=6)

        header = tk.Label(container, text='Start', bg='#2b2b44', fg='white', font=('Segoe UI', 12, 'bold'))
        header.pack(anchor='w', padx=8, pady=(4,6))

        apps = [
            ('Terminal', self.open_terminal),
            ('File Explorer', self.open_file_explorer),
            ('Settings', self.open_settings),
            ('Profiles', lambda: self.open_profile_manager()),
            ('Exit', self.exit_fullscreen),
        ]

        for name, cmd in apps:
            # make item background match container so there is no separate colored box
            item_bg = container['bg']
            item = tk.Frame(container, bg=item_bg)
            item.pack(fill='x', padx=8, pady=6)
            icon = tk.Frame(item, width=36, height=28, bg=item_bg)
            icon.pack_propagate(False)
            icon.pack(side='left', padx=(4,8))
            # if this is Terminal and we have a loaded terminal icon, show it
            if name == 'Terminal' and getattr(self, 'terminal_icon', None):
                try:
                    img = self.terminal_icon
                    # create a label with the image inside the icon frame
                    il = tk.Label(icon, image=img, bg=icon['bg'])
                    il.image = img
                    il.pack(expand=True)
                except Exception:
                    pass
            lbl = tk.Label(item, text=name, bg=item_bg, fg='white', anchor='w')
            lbl.pack(side='left', fill='x', expand=True)

            def make_cmd(c=cmd, m=menu):
                def _run(e=None):
                    try:
                        m.destroy()
                    except Exception:
                        pass
                    self.start_menu = None
                    try:
                        c()
                    except Exception:
                        pass
                return _run

            # bind clicks and hover
            item.bind('<Button-1>', make_cmd())
            lbl.bind('<Button-1>', make_cmd())
            icon.bind('<Button-1>', make_cmd())

            def on_enter(e, w=item, l=lbl, ic=icon):
                w.config(bg='#3a3a5a')
                l.config(bg='#3a3a5a')
                try:
                    ic.config(bg='#3a3a5a')
                except Exception:
                    pass

            def on_leave(e, w=item, l=lbl, ic=icon):
                w.config(bg=item_bg)
                l.config(bg=item_bg)
                try:
                    ic.config(bg=item_bg)
                except Exception:
                    pass

            item.bind('<Enter>', on_enter)
            item.bind('<Leave>', on_leave)

        # add a footer with a close hint
        footer = tk.Label(container, text='Click outside to close', bg='#2b2b44', fg='#a8a8b8', font=('Segoe UI', 9))
        footer.pack(side='bottom', pady=(6,4))

        # close when focus leaves the menu
        def on_focus_out(e=None):
            try:
                menu.destroy()
            except Exception:
                pass
            self.start_menu = None

        menu.focus_force()
        menu.bind('<FocusOut>', on_focus_out)
        # also close when clicking anywhere else on root
        try:
            self.root.bind_all('<Button-1>', lambda e: on_focus_out(), add='+')
        except Exception:
            pass

        self.start_menu = menu

    def _place_icons(self):
        items = [
            ('Terminal', self.open_terminal),
            ('Files', self.open_file_explorer),
            ('Settings', self.open_settings),
        ]
        # prefer loading an external PNG placed at mock_os/assets/terminal_icon.png
        # If that file isn't present or fails to load, fall back to the programmatic icon.
        icon_bg = '#3a3a5a'
        icon_fg = '#ffffff'
        assets_dir = os.path.join(ROOT_DIR, 'assets')
        os.makedirs(assets_dir, exist_ok=True)
        png_file = os.path.join(assets_dir, 'terminal_icon.png')
        ppm_file = os.path.join(assets_dir, 'terminal_icon.ppm')

        def generate_ppm(path, size=48):
            # produce a simple PPM (ASCII P3) image with a dark background and a white
            # '>' glyph plus an underscore, so the icon is usable immediately.
            cx, cy = size // 2, size // 2 - 2
            bg_r, bg_g, bg_b = (58, 58, 90)  # #3a3a5a
            fg_r, fg_g, fg_b = (255, 255, 255)
            lines = [f"P3\n{size} {size}\n255\n"]
            for y in range(size):
                row = []
                for x in range(size):
                    # simple arrow shape by distance to a line
                    dx = x - cx
                    dy = y - cy
                    # arrow condition: near a diagonal center
                    if abs(dx) < 8 and abs(dy - (dx // 2)) < 3 and dx < 6:
                        r, g, b = fg_r, fg_g, fg_b
                    # underscore
                    elif (cy + 12) <= y <= (cy + 13) and (cx - 10) <= x <= (cx + 10):
                        r, g, b = fg_r, fg_g, fg_b
                    else:
                        r, g, b = bg_r, bg_g, bg_b
                    row.append(f"{r} {g} {b}")
                lines.append(' '.join(row) + '\n')
            with open(path, 'w', encoding='utf-8') as f:
                f.writelines(lines)

        # prefer PNG if user placed it; otherwise use or generate a PPM and load that
        self.terminal_icon = None
        try:
            if os.path.exists(png_file):
                self.terminal_icon = tk.PhotoImage(file=png_file)
            else:
                if not os.path.exists(ppm_file):
                    generate_ppm(ppm_file, size=48)
                self.terminal_icon = tk.PhotoImage(file=ppm_file)
            # ensure icon fits in the button: subsample if too large
            try:
                target_size = 44
                w = self.terminal_icon.width()
                h = self.terminal_icon.height()
                if max(w, h) > target_size:
                    factor = math.ceil(max(w, h) / target_size)
                    self.terminal_icon = self.terminal_icon.subsample(factor, factor)
            except Exception:
                pass
        except Exception:
            # last-resort: create an in-memory image
            size = 48
            self.terminal_icon = tk.PhotoImage(width=size, height=size)
            for yy in range(size):
                for xx in range(size):
                    self.terminal_icon.put(icon_bg, (xx, yy))

        for i, (name, cmd) in enumerate(items):
            cont = tk.Frame(self.icon_frame, width=96, height=120, bg='#2b2b44')
            cont.grid_propagate(False)
            cont.grid(row=i, column=0, pady=8)
            icon_box = tk.Frame(cont, width=96, height=96, bg=icon_bg)
            icon_box.pack_propagate(False)
            icon_box.pack(side='top', fill='x')
            # for Terminal, use the embedded image inside a borderless button
            if name == 'Terminal' and self.terminal_icon:
                # Place the image inside a smaller button so the button area remains visible
                btn = tk.Button(icon_box, text='', command=cmd, image=self.terminal_icon)
                btn.image = self.terminal_icon
                # give the button a subtle border so it's visually a button containing the icon
                btn.config(borderwidth=2, relief='raised', bg=icon_bg, activebackground=icon_bg)
                # center the button inside the icon_box and give a little padding
                btn.pack(expand=True, padx=6, pady=6)
            else:
                btn = tk.Button(icon_box, text='', command=cmd, bg=icon_bg, fg=icon_fg, relief='flat')
                btn.pack(expand=True, fill='both')
            lbl = tk.Label(cont, text=name, bg='#2b2b44', fg='#ffffff')
            lbl.pack(side='top', pady=(6,0))

    def _make_window(self, title='App', size=(640, 360)):
        # if a window with this title (app key) already exists, focus and return it
        existing = self.app_windows.get(title)
        try:
            if existing and getattr(existing, 'winfo_exists', lambda: False)():
                try:
                    existing.deiconify()
                except Exception:
                    pass
                try:
                    existing.lift()
                    existing.focus_force()
                except Exception:
                    pass
                return existing
        except Exception:
            pass

        w = tk.Toplevel(self.root)
        # remove the system window decorations so our custom header is the only chrome
        w.overrideredirect(True)
        w.title(title)
        w.configure(bg='#ffffff')
        w.geometry(f"{size[0]}x{size[1]}+100+100")
        header = tk.Frame(w, bg='#33334a', height=28)
        header.pack(fill='x')
        lbl = tk.Label(header, text=title, bg='#33334a', fg='#ffffff')
        lbl.pack(side='left', padx=6)

        # Window controls: minimize, maximize/restore, close
        def on_minimize():
            try:
                # withdraw the window (acts as minimize for override-redirect windows)
                w.withdraw()
            except Exception:
                pass

        def on_toggle_max():
            try:
                # Windows supports 'zoomed' state; otherwise toggle fullscreen attribute
                if getattr(w, '_is_maximized', False):
                    prev = getattr(w, '_prev_geom', None)
                    if prev:
                        w.geometry(prev)
                    w._is_maximized = False
                else:
                    try:
                        w._prev_geom = w.geometry()
                    except Exception:
                        w._prev_geom = None
                    sw = self.root.winfo_screenwidth()
                    sh = self.root.winfo_screenheight()
                    w.geometry(f"{sw}x{sh}+0+0")
                    w._is_maximized = True
            except Exception:
                pass

        def on_close():
            try:
                w.destroy()
            except Exception:
                pass

        # double-click header toggles maximize/restore
        header.bind('<Double-1>', lambda e: on_toggle_max())

        # buttons on the right
        btn_close = tk.Button(header, text='✕', command=on_close, bg='#33334a', fg='white', bd=0, activebackground='#b04a4a')
        btn_max = tk.Button(header, text='▢', command=on_toggle_max, bg='#33334a', fg='white', bd=0, activebackground='#666666')
        btn_min = tk.Button(header, text='—', command=on_minimize, bg='#33334a', fg='white', bd=0, activebackground='#666666')
        for b in (btn_close, btn_max, btn_min):
            b.config(font=('Segoe UI', 10, 'bold'), padx=6, pady=2)
        btn_close.pack(side='right', padx=(4,6))
        btn_max.pack(side='right')
        btn_min.pack(side='right')
        def start(e):
            w._drag_x = e.x
            w._drag_y = e.y
        def drag(e):
            x = w.winfo_x() + e.x - getattr(w, '_drag_x', 0)
            y = w.winfo_y() + e.y - getattr(w, '_drag_y', 0)
            w.geometry(f"+{x}+{y}")
        header.bind('<Button-1>', start)
        header.bind('<B1-Motion>', drag)
        self.windows.append(w)
        # create and register a taskbar button for this window
        try:
            self._create_task_button(w, title)
            # remember this window by title so duplicate opens focus it
            self.app_windows[title] = w
        except Exception:
            pass
        return w

    def _create_task_button(self, w, title):
        # create a small flat button for the taskbar representing the window
        btn = tk.Button(self.taskbar_window_frame, text=title, command=lambda win=w: self._toggle_window(win), bg='#1f1f2b', fg='white', relief='flat', padx=8, pady=4)
        btn.pack(side='left', padx=4)
        self.window_buttons[w] = btn

        # when the window is destroyed, remove the task button
        def on_destroy(event=None, win=w):
            self._remove_task_button(win)
        w.bind('<Destroy>', on_destroy)

        # also remove from app_windows mapping on destroy
        def on_full_destroy(e=None, win=w, key=title):
            try:
                if self.app_windows.get(key) is win:
                    del self.app_windows[key]
            except Exception:
                pass
        w.bind('<Destroy>', on_full_destroy, add='+')

    def _remove_task_button(self, w):
        btn = self.window_buttons.pop(w, None)
        try:
            if btn:
                btn.destroy()
        except Exception:
            pass

    def _toggle_window(self, w):
        try:
            # if visible, withdraw (minimize); otherwise deiconify and focus
            if w.winfo_viewable():
                try:
                    w.withdraw()
                except Exception:
                    pass
            else:
                try:
                    w.deiconify()
                except Exception:
                    pass
                try:
                    w.lift()
                    w.focus_force()
                except Exception:
                    pass
        except Exception:
            pass

    def open_terminal(self):
        return comp_open_terminal(self)

    def open_file_explorer(self):
        return comp_open_file_explorer(self)

    def open_settings(self):
        # delegate to settings component implementation
        comp_open_settings(self)

    def open_profile_manager(self, parent_win=None):
        return comp_open_profile_manager(self, parent_win)


def choose_profile(root, callback):
    # Fullscreen graphical login with avatars and password entry
    profiles = load_profiles()
    win = tk.Toplevel(root)
    win.overrideredirect(True)
    sw = root.winfo_screenwidth()
    sh = root.winfo_screenheight()
    win.geometry(f"{sw}x{sh}+0+0")
    # try to load the lock screen background image and rotate to landscape
    artwork_path = os.path.join(ROOT_DIR, 'assets', 'Untitled_Artwork.png')
    # if absolute path provided or file in working dir, prefer that
    if not os.path.exists(artwork_path):
        alt = r"C:\Users\monke\Desktop\python code\mock_os\assets\Untitled_Artwork.png"
        if os.path.exists(alt):
            artwork_path = alt

    if PIL_AVAILABLE and os.path.exists(artwork_path):
        try:
            img = Image.open(artwork_path)
            # rotate portrait to landscape (90 degrees clockwise)
            img = img.rotate(-90, expand=True)
            # scale to cover screen while preserving aspect ratio
            iw, ih = img.size
            scale = max(sw / iw, sh / ih)
            nw, nh = int(iw * scale), int(ih * scale)
            img = img.resize((nw, nh), Image.LANCZOS)
            # center-crop to screen size
            left = (nw - sw) // 2
            top = (nh - sh) // 2
            img = img.crop((left, top, left + sw, top + sh))
            photo = ImageTk.PhotoImage(img)
            bg_label = tk.Label(win, image=photo)
            bg_label.image = photo
            bg_label.place(x=0, y=0, width=sw, height=sh)
        except Exception:
            win.configure(bg='black')
    else:
        # fallback: plain black background
        win.configure(bg='black')

    frame = tk.Frame(win, bg='black')
    frame.place(relx=0.5, rely=0.45, anchor='center')

    ttk.Label(frame, text='Sign in', foreground='white', background='black', font=('Segoe UI', 20)).pack(pady=8)

    icons_frame = tk.Frame(frame, bg='black')
    icons_frame.pack()

    # create icon buttons horizontally
    def make_avatar(pid, info):
        c = tk.Frame(icons_frame, width=120, height=140, bg='black')
        c.pack_propagate(False)
        c.pack(side='left', padx=12)
        # avatar: if avatar path present try to load, otherwise draw circle with initials
        avatar_canvas = tk.Canvas(c, width=96, height=96, bg='#2b2b2b', highlightthickness=0)
        avatar_canvas.pack()
        if info.get('avatar') and os.path.exists(info.get('avatar')):
            try:
                img = tk.PhotoImage(file=info.get('avatar'))
                avatar_canvas.create_image(48,48,image=img)
                # keep reference
                avatar_canvas.image = img
            except Exception:
                avatar_canvas.create_oval(8,8,88,88, fill='#4a90e2')
                initials = ''.join([p[0].upper() for p in info.get('display','').split() if p])[:2]
                avatar_canvas.create_text(48,48,text=initials, fill='white', font=('Segoe UI', 20))
        else:
            avatar_canvas.create_oval(8,8,88,88, fill='#4a90e2')
            initials = ''.join([p[0].upper() for p in info.get('display','').split() if p])[:2]
            avatar_canvas.create_text(48,48,text=initials, fill='white', font=('Segoe UI', 20))

        tk.Label(c, text=info.get('display',''), bg='black', fg='white').pack(pady=(6,0))

        def on_click(e=None, pid=pid, info=info):
            # if profile has password, prompt for it; otherwise select immediately
            pw = info.get('password')
            if pw:
                val = simpledialog.askstring('Password', f'Enter password for {info.get("display")}:', show='*', parent=win)
                if val is None:
                    return
                if val != pw:
                    messagebox.showerror('Login failed', 'Incorrect password')
                    return
            win.destroy()
            callback(pid)

        c.bind('<Button-1>', on_click)
        avatar_canvas.bind('<Button-1>', on_click)

    for pid, info in profiles.items():
        make_avatar(pid, info)

    # allow keyboard Esc to cancel (choose default admin)
    def on_key(e):
        if e.keysym == 'Escape':
            win.destroy()
            callback('admin')
    win.bind('<Key>', on_key)


if __name__ == '__main__':
    root = tk.Tk()
    root.withdraw()

    def after_splash():
        # profile selection after splash
        def on_profile_chosen(pid):
            root.deiconify()
            app = MockOS(root, profile_id=pid)
        choose_profile(root, on_profile_chosen)

    splash = CompSplashScreen(root, duration=5)
    splash.run(after_splash)
    root.mainloop()
