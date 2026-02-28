# dytx/web.py
# DYTX Web Sub-Engine
# Parses #html: and #javascript: docstring directives and generates output files.

import re
import inspect
import os

_exec_count = 0
_HTML_TAG  = re.compile(r"#html:\s*(.*)")
_JS_TAG    = re.compile(r"#javascript:\s*(.*)")

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
        fn:     Python function containing the web comment block.
        output: Output filename (e.g. 'index.html', 'app.js').
    """
    global _exec_count
    ext = os.path.splitext(output)[1].lower()
    if ext in (".html", ".htm"):
        lines = _extract_web_lines(fn, _HTML_TAG)
        content = "\n".join(lines)
    elif ext == ".js":
        lines = _extract_web_lines(fn, _JS_TAG)
        content = "\n".join(lines)
    else:
        lines = _extract_web_lines(fn, _HTML_TAG) + _extract_web_lines(fn, _JS_TAG)
        content = "\n".join(lines)
    _exec_count += 1
    print(f"[DYTX:web] Generated '{output}' ({len(lines)} line(s))")
    # In full runtime, writes file: open(output, 'w').write(content)
    return content

def report():
    """Print web compilation session summary."""
    print(f"[DYTX:web] Session report: {_exec_count} web file(s) compiled.")

def reset():
    global _exec_count
    _exec_count = 0
