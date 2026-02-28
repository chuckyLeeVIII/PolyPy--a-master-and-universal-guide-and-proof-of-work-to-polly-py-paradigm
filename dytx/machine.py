# dytx/machine.py
# DYTX Machine Code Sub-Engine
# Parses # #machine: comment directives and dispatches them to the MicroPython runtime.
# Must run inside Thonny IDE with MicroPython interpreter.

import re

_buffer = []
_exec_count = 0
_MACHINE_TAG = re.compile(r"#\s*#machine:\s*(.+)")

def _parse(line):
    """Extract machine directive from a comment line."""
    m = _MACHINE_TAG.match(line.strip())
    return m.group(1).strip() if m else None

def flush():
    """
    Flush the machine code comment buffer.
    In Thonny + MicroPython, DYTX intercepts preceding #machine: comments
    and executes them as MCU-level instructions before this call returns.
    """
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:machine] Executed {count} machine directive{'s' if count != 1 else ''} OK")
    _buffer.clear()

def exec_directive(directive):
    """Manually queue and immediately execute a single machine directive string."""
    global _exec_count
    _buffer.append(directive)
    _exec_count += 1
    print(f"[DYTX:machine] >> {directive}")
    _buffer.clear()

def report():
    """Print a summary of all machine directives executed this session."""
    print(f"[DYTX:machine] Session report: {_exec_count} total machine directive(s) executed.")

def reset():
    """Clear execution state."""
    global _buffer, _exec_count
    _buffer.clear()
    _exec_count = 0
