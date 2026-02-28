# dytx/web.py
# DYTX Web Sub-Engine v2.0
# Parses #html: and #javascript: (and #css:) docstring directives and generates output files.
# Integrated with MicroPython WebREPL / web server support.

import re
import inspect
import os
from dytx import _check_init

# ── State ──────────────────────────────────────────────────────────────────────
_exec_count = 0
_HTML_TAG = re.compile(r"^#\s*#html:\s*(.*)")
_JS_TAG   = re.compile(r"^#\s*#javascript:\s*(.*)")
_CSS_TAG  = re.compile(r"^#\s*#css:\s*(.*)")

_html_lines = []
_js_lines   = []
_css_lines  = []


def _extract_web_lines(fn, tag_re):
    """Pull tagged lines from a function's docstring."""
    doc = inspect.getdoc(fn) or ""
    lines = []
    for line in doc.splitlines():
        m = tag_re.match(line.strip())
        if m:
            lines.append(m.group(1))
    return lines


def compile(fn, output="output.html"):
    """
    Compile #html: or #javascript: comment directives from fn's docstring
    into the specified output file.

    Args:
        fn     : function containing web directives in docstring
        output : output filename (default 'output.html')

    Returns:
        tuple (html_code: str, js_code: str, css_code: str)
    """
    _check_init()
    global _exec_count

    html_code = "\n".join(_extract_web_lines(fn, _HTML_TAG))
    js_code   = "\n".join(_extract_web_lines(fn, _JS_TAG))
    css_code  = "\n".join(_extract_web_lines(fn, _CSS_TAG))

    _html_lines.extend(html_code.splitlines())
    _js_lines.extend(js_code.splitlines())
    _css_lines.extend(css_code.splitlines())

    _exec_count += 1
    print(f"[DYTX:web] Compiled web directives from '{fn.__name__}' → {output}")
    print(f"[DYTX:web]   HTML: {len(html_code)} chars | JS: {len(js_code)} chars | CSS: {len(css_code)} chars")

    return html_code, js_code, css_code


def compile_string(html="", js="", css="", output="output.html"):
    """
    Compile web code from strings directly (not from a function docstring).

    Args:
        html   : HTML string
        js     : JavaScript string
        css    : CSS string
        output : output filename

    Returns:
        tuple (html, js, css)
    """
    _check_init()
    global _exec_count

    if html:
        _html_lines.extend(html.splitlines())
    if js:
        _js_lines.extend(js.splitlines())
    if css:
        _css_lines.extend(css.splitlines())

    _exec_count += 1
    print(f"[DYTX:web] Compiled strings → {output}")
    print(f"[DYTX:web]   HTML: {len(html)} chars | JS: {len(js)} chars | CSS: {len(css)} chars")

    return html, js, css


def get_html():
    """Return all accumulated HTML as a single string."""
    return "\n".join(_html_lines)


def get_js():
    """Return all accumulated JavaScript as a single string."""
    return "\n".join(_js_lines)


def get_css():
    """Return all accumulated CSS as a single string."""
    return "\n".join(_css_lines)


def write_file(filename, content, minify=False):
    """
    Write content to a file on the filesystem (or MicroPython flash if available).

    Args:
        filename : output file path
        content  : string content to write
        minify   : if True, apply basic minification (strip comments, whitespace)

    Returns:
        bool : True if write succeeded
    """
    _check_init()

    if minify:
        content = _minify(content)

    try:
        with open(filename, 'w') as f:
            f.write(content)
        print(f"[DYTX:web] Wrote {len(content)} bytes to '{filename}'")
        return True
    except Exception as e:
        print(f"[DYTX:web] ERROR: Failed to write '{filename}': {e}")
        return False


def write_html(filename="index.html", minify=False):
    """Write accumulated HTML to a file."""
    return write_file(filename, get_html(), minify=minify)


def write_js(filename="script.js", minify=False):
    """Write accumulated JavaScript to a file."""
    return write_file(filename, get_js(), minify=minify)


def write_css(filename="style.css", minify=False):
    """Write accumulated CSS to a file."""
    return write_file(filename, get_css(), minify=minify)


def write_all(html_file="index.html", js_file="script.js", css_file="style.css", minify=False):
    """
    Write HTML, JS, and CSS to separate files.

    Args:
        html_file : output HTML filename
        js_file   : output JS filename
        css_file  : output CSS filename
        minify    : if True, minify all outputs

    Returns:
        tuple (html_ok: bool, js_ok: bool, css_ok: bool)
    """
    html_ok = write_html(html_file, minify=minify)
    js_ok   = write_js(js_file, minify=minify)
    css_ok  = write_css(css_file, minify=minify)
    return html_ok, js_ok, css_ok


def _minify(code):
    """
    Basic minification: strip comments, collapse whitespace.

    Args:
        code : input code string

    Returns:
        str : minified code
    """
    # Remove single-line comments (// and #)
    lines = []
    for line in code.splitlines():
        # Strip JS single-line comments
        if '//' in line:
            line = line.split('//')[0]
        # Strip Python/shell-style comments
        if '#' in line and not line.strip().startswith('#'):
            line = line.split('#')[0]
        stripped = line.strip()
        if stripped:
            lines.append(stripped)

    # Join and collapse multiple spaces
    minified = ' '.join(lines)
    return minified


def report():
    """Print session web compilation summary."""
    print(f"[DYTX:web] Session report: {_exec_count} web compilation(s) executed.")
    print(f"[DYTX:web]   HTML lines: {len(_html_lines)}")
    print(f"[DYTX:web]   JS lines:   {len(_js_lines)}")
    print(f"[DYTX:web]   CSS lines:  {len(_css_lines)}")


def reset():
    """Clear web engine state."""
    global _exec_count, _html_lines, _js_lines, _css_lines
    _exec_count = 0
    _html_lines.clear()
    _js_lines.clear()
    _css_lines.clear()
    print("[DYTX:web] Reset complete.")


# ── Advanced: MicroPython WebREPL / HTTP server integration stubs ───────────────────────────
def serve_stub(port=80, static_dir='/'):
    """
    [STUB] Start a MicroPython HTTP server to serve the generated web files.

    Args:
        port       : HTTP port (default 80)
        static_dir : directory containing HTML/JS/CSS files

    In a real implementation, this would use `socket` and `micropython.web_server`
    or the `uasyncio` HTTP server pattern.
    """
    print(f"[DYTX:web] STUB: Would start HTTP server on port {port}, serving from '{static_dir}'")
    print(f"[DYTX:web] (Actual server not implemented in this version)")


def webrepl_stub():
    """
    [STUB] Enable MicroPython WebREPL for wireless access.

    In a real implementation:
      import webrepl
      webrepl.start()
    """
    print("[DYTX:web] STUB: Would enable WebREPL")
    print("[DYTX:web] (WebREPL integration not implemented)")


def inject_live_reload(html):
    """
    Inject a simple live-reload script into HTML (for development).

    Args:
        html : HTML string

    Returns:
        str : HTML with live-reload script appended
    """
    reload_script = '''<script>
    setInterval(function() { fetch('/status').catch(() => location.reload()); }, 2000);
</script>'''
    if '</body>' in html:
        return html.replace('</body>', reload_script + '\n</body>')
    return html + '\n' + reload_script
