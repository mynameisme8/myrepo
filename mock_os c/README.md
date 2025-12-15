MockOS — fullscreen mock desktop (Tkinter)

Files created:
- mock_os/main.py

Quick start

1) Install Python 3.8+ (Windows).
2) From a terminal run:

```bash
python "mock_os\main.py"
```

Behavior

- The app opens fullscreen (F11 toggles fullscreen, Escape exits).
- Click Start (bottom-left) to open the app menu.
- Desktop icons: Terminal, Files, Settings.
- Terminal supports simple fake commands: `echo`, `clear`/`cls`, `list` (lists files in parent workspace).
- File Explorer double-click files to view contents.

Notes

- The mock OS is a minimal demo to prototype a fullscreen UI. It intentionally fakes functionality.
- You can expand apps by editing `mock_os/main.py`.
