# dytx/firmware.py
# DYTX Firmware Sub-Engine v2.0
# Parses //firmware: blocks and compiles them to target firmware.

import re
import inspect
from dytx import _check_init

# ── State ─────────────────────────────────────────────────────────────────────────
_exec_count = 0
_FIRMWARE_TAG = re.compile(r"//firmware:(\w+)")
_compiled_blocks = {}  # {target: [code_strings]}
_VALID_TARGETS = ('c++', 'rp2040', 'avr', 'esp32', 'esp8266', 'stm32', 'nrf52')


def _extract_block(fn):
    """Extract firmware docstring block from function."""
    doc = inspect.getdoc(fn) or ""
    lines = []
    inside = False
    for line in doc.splitlines():
        if _FIRMWARE_TAG.search(line):
            inside = True
            continue
        if inside:
            lines.append(line)
    return " ".join(lines).strip()


def compile_block(fn, target="c++"):
    """Compile firmware block from function docstring."""
    global _exec_count
    _check_init()
    if target not in _VALID_TARGETS:
        print(f"[DYTX:firmware] WARNING: Unknown target {target}")
    code = _extract_block(fn)
    if not code:
        return ""
    if target not in _compiled_blocks:
        _compiled_blocks[target] = []
    _compiled_blocks[target].append(code)
    _exec_count += 1
    print(f"[DYTX:firmware] Compiled block for {target}")
    return code


def compile_string(code, target='c++'):
    """Compile code string directly."""
    _check_init()
    global _exec_count
    if target not in _compiled_blocks:
        _compiled_blocks[target] = []
    _compiled_blocks[target].append(code)
    _exec_count += 1
    print(f"[DYTX:firmware] Compiled string for {target}")
    return code


def directive(name, *args):
    """
    Execute a named firmware directive (simulation stub).

    Args:
        name : directive name string (e.g. 'INIT_FRAMEBUFFER', 'SWAP_BUFFERS')
        *args: optional directive arguments
    """
    _check_init()
    global _exec_count
    arg_str = ', '.join(str(a) for a in args)
    print(f"[DYTX:firmware] directive {name}({arg_str})")
    _exec_count += 1


def report():
    """Summary report."""
    print(f"[DYTX:firmware] Session: {_exec_count} blocks compiled.")


def reset():
    """Reset state."""
    global _exec_count, _compiled_blocks
    _exec_count = 0
    _compiled_blocks.clear()
    print("[DYTX:firmware] Reset complete.")
