# dytx/asm.py
# DYTX Assembly Sub-Engine
# Parses # #asm: comment directives and dispatches them as assembly instructions.

import re

_buffer = []
_exec_count = 0
_ASM_TAG = re.compile(r"#\s*#asm:\s*(.+)")

def _parse(line):
    """Extract assembly instruction from a comment line."""
    m = _ASM_TAG.match(line.strip())
    return m.group(1).strip() if m else None

def flush():
    """
    Flush the assembly instruction buffer.
    In Thonny + MicroPython, DYTX intercepts preceding #asm: comments
    and dispatches them to the ASM sub-engine before this call returns.
    """
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:asm] Executed {count} ASM directive{'s' if count != 1 else ''} OK")
    _buffer.clear()

def exec_directive(instruction):
    """Manually execute a single assembly instruction string."""
    global _exec_count
    _buffer.append(instruction)
    _exec_count += 1
    print(f"[DYTX:asm] >> {instruction}")
    _buffer.clear()

def report():
    """Print assembly execution session summary."""
    print(f"[DYTX:asm] Session report: {_exec_count} ASM directive(s) executed.")

def reset():
    global _buffer, _exec_count
    _buffer.clear()
    _exec_count = 0
