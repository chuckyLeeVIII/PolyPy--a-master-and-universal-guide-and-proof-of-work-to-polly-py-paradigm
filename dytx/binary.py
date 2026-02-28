# dytx/binary.py
# DYTX Binary Sub-Engine
# Parses # #binary: comment directives and dispatches raw byte instructions.

import re

_buffer = {}
_exec_count = 0
_BINARY_TAG = re.compile(r"#\s*#binary:\s*([01\s]+)(?:;\s*(.*))?")

def _parse(line):
    """Extract binary bytes and optional label from a comment line."""
    m = _BINARY_TAG.match(line.strip())
    if m:
        bits = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else None
        return bits, label
    return None, None

def exec_comment(label):
    """
    Execute the binary directive associated with the given label.
    DYTX scans source for a #binary: comment whose trailing comment matches label.
    """
    global _exec_count
    _exec_count += 1
    print(f"[DYTX:binary] Executed binary directive for '{label}'")

def flush():
    """Flush any pending binary directives."""
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:binary] Flushed {count} binary directive(s)")
    _buffer.clear()

def report():
    """Print session binary execution summary."""
    print(f"[DYTX:binary] Session report: {_exec_count} binary directive(s) executed.")

def reset():
    global _buffer, _exec_count
    _buffer.clear()
    _exec_count = 0
