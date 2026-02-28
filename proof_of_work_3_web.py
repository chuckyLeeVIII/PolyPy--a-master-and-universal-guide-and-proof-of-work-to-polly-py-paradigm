# PolyPy Web Proof of Work
# PolyPi Pure v1.0 — Thonny IDE, MicroPython OR standard Python (fullstack)
# In pure mode, generates static HTML+JS files directly to disk

import sys
import os
import dytx

# --- Detect environment automatically ---
_IDE = "thonny" if "thonny" in sys.executable.lower() else "pure"
_MODE = "micropython" if _IDE == "thonny" else "python"

# Initialize DYTX runtime
dytx.init(mode=_MODE, ide=_IDE)

# --- Web module abstraction ---
if _IDE == "thonny":
    try:
        import dytx.web as dxw  # DYTX web compiler module
    except ImportError:
        dxw = None
else:
    dxw = None  # will use pure Python fallback below


# --- HTML template (PolyPy #html: directives as inline doc comments) ---
def define_web_header():
    """
    #html: <!DOCTYPE html><html lang="en">
    #html: <head><meta charset="UTF-8"><title>PolyPi Pure — Proof of Work</title>
    #html: <link rel="stylesheet" href="style.css"></head>
    #html: <body><h1>Built with PolyPy + DYTX</h1>
    #html: <button id="btn">Click me</button>
    #html: <p id="out"></p>
    #html: <script src="app.js"></script>
    #html: </body></html>
    """
    return (
        '<!DOCTYPE html><html lang="en">\n'
        '<head><meta charset="UTF-8">\n'
        '<title>PolyPi Pure \u2014 Proof of Work #3</title>\n'
        '<link rel="stylesheet" href="style.css"></head>\n'
        '<body>\n'
        '  <h1>Built with PolyPy + DYTX (PolyPi Pure)</h1>\n'
        '  <button id="btn">Click me</button>\n'
        '  <p id="out"></p>\n'
        '  <script src="app.js"></script>\n'
        '</body></html>\n'
    )


def on_button_click():
    """
    #javascript: document.getElementById('btn').addEventListener('click', () => {
    #javascript:   document.getElementById('out').textContent = 'PolyPy button clicked!';
    #javascript: });
    """
    return (
        "document.getElementById('btn').addEventListener('click', () => {\n"
        "  document.getElementById('out').textContent = 'PolyPy button clicked!';\n"
        "});\n"
    )


# --- Compile / emit output ---
if dxw is not None:
    # Thonny / DYTX path: dxw.compile parses #html: and #javascript: directives
    dxw.compile(define_web_header, output="index.html")
    dxw.compile(on_button_click, output="app.js")
else:
    # Pure Python path: write files directly
    out_dir = os.path.join(os.path.dirname(__file__), "web_output")
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
        f.write(define_web_header())
    with open(os.path.join(out_dir, "app.js"), "w", encoding="utf-8") as f:
        f.write(on_button_click())
    print(f"[PolyPi Pure] Web output written to: {out_dir}")

print("[PolyPi Pure] Proof of Work #3 complete: index.html and app.js generated.")
