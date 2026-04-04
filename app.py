import json
import os
import time
import threading
import webbrowser
from playwright.sync_api import sync_playwright
from flask import Flask
from automoops.browser import set_browser
from automoops.web.routes import init_routes

app = Flask(__name__, template_folder="automoops/web/templates")
init_routes(app)

PROFILE_DIR = os.path.join(os.path.dirname(__file__), "chrome_profile")


def clean_profile_locks():
    for fname in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            fpath = os.path.join(PROFILE_DIR, fname)
            if os.path.exists(fpath):
                os.remove(fpath)
        except Exception:
            pass

    prefs_path = os.path.join(PROFILE_DIR, "Default", "Preferences")
    if os.path.exists(prefs_path):
        try:
            with open(prefs_path, "r", encoding="utf-8") as f:
                prefs = json.load(f)
            prefs.setdefault("profile", {})["exit_type"] = "Normal"
            prefs.setdefault("profile", {})["exited_cleanly"] = True
            with open(prefs_path, "w", encoding="utf-8") as f:
                json.dump(prefs, f)
        except Exception:
            pass


if __name__ == "__main__":
    clean_profile_locks()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--start-maximized"],
        )
        # Store context only — pages are created fresh per request
        set_browser(context, None)

        dashboard_url = f"http://localhost:5000?v={int(time.time())}"
        threading.Timer(1.5, lambda: webbrowser.open(dashboard_url)).start()

        app.run(debug=False, use_reloader=False, threaded=False)
