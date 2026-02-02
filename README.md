# daWAREHOUSE – Inventory & Sales Manager

Simple inventory and sales manager built with **Python, SQLite, Flask and Flet**.  
Includes:
- Desktop GUI (Flet) for warehouse management.
- Web sales portal with email‑based login and 2FA token.

## Features

- Manage **products**, **suppliers**, and **clients**.
- Track **sales** and **purchases** with stock updates.
- Web login via email token (Flask + Flask-Mail + Gmail SMTP).
- Dark/light theme toggle in the GUI.

## Tech stack

- Python 3.x
- SQLite (file‑based DB)
- Flask (web backend)
- Flask-Mail (Gmail SMTP)
- Flet (GUI desktop app)

## How to run

1. Install dependencies:
   ```bash
   pip install -r requirements.txt

2. Run the Flask web app:
   '''bash
   python app.py

4. Run the Flet GUI:
   '''bash
   python warehouse_gui.py
