from flask import render_template, request, jsonify, make_response
from automoops.browser import get_context
from automoops.extraction.moops_order import extract_order
from automoops.workflows.itf import run_itf

WORKFLOWS = {
    "itf": ("ITF Form", run_itf),
}

_active_page = None


def init_routes(app):

    @app.route("/")
    def index():
        workflows = {k: v[0] for k, v in WORKFLOWS.items()}
        resp = make_response(render_template("index.html", workflows=workflows))
        resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        return resp

    @app.route("/extract", methods=["POST"])
    def extract():
        global _active_page
        try:
            ctx = get_context()
            # Find the MOOPS order page currently open in the browser
            page = None
            for p in ctx.pages:
                if "moops.mitechisys.com/order" in p.url:
                    page = p
                    break
            if page is None:
                return jsonify({"error": "No MOOPS order page found. Navigate to an order in the Playwright browser first."}), 400
            _active_page = page
            return jsonify(extract_order(page))
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.route("/workflow/<name>", methods=["POST"])
    def run_workflow(name):
        if name not in WORKFLOWS:
            return jsonify({"error": f"Unknown workflow: {name}"}), 400
        if _active_page is None or _active_page.is_closed():
            return jsonify({"error": "Extract an order first."}), 400
        try:
            order = request.json
            _, fn = WORKFLOWS[name]
            fn(_active_page, order)
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
