import json
import os
import time
import threading
import webbrowser
import queue

from playwright.sync_api import sync_playwright
from flask import Flask, render_template, request, jsonify, make_response

PROFILE_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "chrome_profile")

app = Flask(__name__, template_folder="automoops/web/templates")

from automoops.extraction.moops_order import extract_order
from automoops.workflows.itf import run_itf
from automoops.workflows.efs import run_efs
from automoops.workflows.intercom import run_intercom

WORKFLOWS = {
    "itf": ("ITF Form", run_itf),
    "efs": ("EFS Order", run_efs),
    "intercom": ("Fortis Email", run_intercom),
}

# All Playwright work is submitted here and executed in the main thread
_task_queue = queue.Queue()
_page = None


def submit_task(fn, timeout=90):
    """Submit a callable to the Playwright worker (main thread). Blocks until done."""
    result_q = queue.Queue()
    _task_queue.put((fn, result_q))
    kind, value = result_q.get(timeout=timeout)
    if kind == "error":
        raise Exception(value)
    return value


@app.route("/")
def index():
    workflows = {k: v[0] for k, v in WORKFLOWS.items()}
    resp = make_response(render_template("index.html", workflows=workflows))
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
    return resp


@app.route("/load", methods=["POST"])
def load():
    url = request.json.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    print(f"[Flask] Load: {url}")
    try:
        def do_load():
            print(f"[PW] goto {url}")
            _page.goto(url, wait_until="domcontentloaded", timeout=30000)
            # Wait for the specific form field — proves the order page has rendered
            _page.wait_for_selector('textarea[name="notes_to_admin"]', timeout=20000)
            print(f"[PW] loaded: {_page.url}")
            data = extract_order(_page)
            print("[PW] extracted")
            return data
        data = submit_task(do_load)
        return jsonify(data)
    except Exception as e:
        print(f"[Flask] Error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/workflow/<name>", methods=["POST"])
def run_workflow(name):
    if name not in WORKFLOWS:
        return jsonify({"error": f"Unknown workflow: {name}"}), 400
    print(f"[Flask] Workflow: {name}")
    try:
        order = request.json
        _, fn = WORKFLOWS[name]
        def do_workflow():
            fn(_page, order)
        submit_task(do_workflow)
        return jsonify({"ok": True})
    except Exception as e:
        print(f"[Flask] Workflow error: {e}")
        return jsonify({"error": str(e)}), 500


def clean_locks():
    for fname in ("SingletonLock", "SingletonCookie", "SingletonSocket"):
        try:
            os.remove(os.path.join(PROFILE_DIR, fname))
        except Exception:
            pass
    prefs = os.path.join(PROFILE_DIR, "Default", "Preferences")
    if os.path.exists(prefs):
        try:
            with open(prefs, "r", encoding="utf-8") as f:
                data = json.load(f)
            data.setdefault("profile", {})["exit_type"] = "Normal"
            data.setdefault("profile", {})["exited_cleanly"] = True
            with open(prefs, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except Exception:
            pass


if __name__ == "__main__":
    clean_locks()

    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            user_data_dir=PROFILE_DIR,
            headless=False,
            args=["--start-maximized"],
        )
        _page = context.new_page()
        print(f"[PW] Page ready: {_page.url}")

        # Flask runs in a daemon thread so it can serve requests concurrently
        flask_thread = threading.Thread(
            target=lambda: app.run(debug=False, use_reloader=False, threaded=True),
            daemon=True,
        )
        flask_thread.start()

        dashboard_url = f"http://localhost:5000?v={int(time.time())}"
        threading.Timer(1.5, lambda: webbrowser.open(dashboard_url)).start()
        print(f"Dashboard: {dashboard_url}")

        # Main thread stays here processing Playwright tasks
        while True:
            try:
                fn, result_q = _task_queue.get(timeout=0.05)
                try:
                    result = fn()
                    result_q.put(("ok", result))
                except Exception as e:
                    print(f"[PW] Task error: {e}")
                    result_q.put(("error", str(e)))
            except queue.Empty:
                continue
