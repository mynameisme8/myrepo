import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
import os

# compute profiles path relative to mock_os (parent folder)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
PROFILES_PATH = os.path.join(BASE_DIR, 'profiles.json')


def open_profile_manager(app, parent_win=None):
    profiles = _load_profiles()
    cur = app.profile_id
    pm = tk.Toplevel(app.root)
    pm.title('Profiles')
    pm.geometry('360x300')
    lb = tk.Listbox(pm)
    lb.pack(fill='both', expand=True)
    for pid, info in profiles.items():
        lb.insert('end', f"{pid} - {info.get('display','')}")
    def create():
        if not profiles.get(cur, {}).get('is_admin'):
            messagebox.showwarning('Permissions', 'Only admin can create profiles')
            return
        name = simpledialog.askstring('Create profile', 'Profile id (no spaces):')
        if not name:
            return
        profiles[name] = {'display': name, 'is_admin': False, 'password': ''}
        _save_profiles(profiles)
        lb.insert('end', f"{name} - {name}")
    def delete():
        sel = lb.curselection()
        if not sel:
            return
        item = lb.get(sel[0])
        pid = item.split(' - ')[0]
        if pid == 'admin':
            messagebox.showwarning('Profiles', 'Cannot delete admin')
            return
        if not profiles.get(cur, {}).get('is_admin'):
            messagebox.showwarning('Permissions', 'Only admin can delete profiles')
            return
        profiles.pop(pid, None)
        _save_profiles(profiles)
        lb.delete(sel[0])
    ttk.Button(pm, text='Create', command=create).pack(side='left', padx=8, pady=6)
    ttk.Button(pm, text='Delete', command=delete).pack(side='left', padx=8, pady=6)


def _load_profiles():
    if not os.path.exists(PROFILES_PATH):
        return {}
    try:
        with open(PROFILES_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}


def _save_profiles(profiles):
    with open(PROFILES_PATH, 'w', encoding='utf-8') as f:
        json.dump(profiles, f, indent=2)
