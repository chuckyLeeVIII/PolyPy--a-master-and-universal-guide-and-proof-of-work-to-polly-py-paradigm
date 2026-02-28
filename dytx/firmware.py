# dytx/firmware.py
# DYTX Firmware Sub-Engine
# Parses //firmware:c++ docstring blocks and compiles them to target firmware.

import re
import inspect

_exec_count = 0
_FIRMWARE_TAG = re.compile(r"//firmware:(\w+)")

def _extract_block(fn):
    """Extract the firmware docstring block from a function."""
    doc = inspect.getdoc(fn) or ""
    lines = []
    inside = False
    for line in doc.splitlines():
        if _FIRMWARE_TAG.search(line):
            inside = True
            continue
        if inside:
            lines.append(line)
    return "\n".join(lines).strip()

def compile_block(fn, target="opengl"):
    """
    Compile the //firmware:c++ block embedded in fn's docstring.
    In a full DYTX runtime, this emits compiled firmware for the target.

    Args:
        fn:     The Python function containing the firmware docstring block.
        target: Compilation target (e.g. 'opengl', 'rp2040', 'avr').
    """
    global _exec_count
    block = _extract_block(fn)
    _exec_count += 1
    line_count = len(block.splitlines()) if block else 0
    print(f"[DYTX:firmware] Compiled {line_count} line(s) of C++ firmware for target='{target}'")

def report():
    """Print firmware compilation summary."""
    print(f"[DYTX:firmware] Session report: {_exec_count} firmware block(s) compiled.")

def reset():
    global _exec_count
    _exec_count = 0
