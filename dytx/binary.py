# dytx/binary.py
# DYTX Binary Sub-Engine v2.0
# Parses # #binary: comment directives and dispatches raw byte instructions.
# Supports binary string parsing, conversion utilities, and endianness control.

import re
from dytx import _check_init

# ── State ───────────────────────────────────────────────────────────────────────
_buffer = {}
_exec_count = 0
_BINARY_TAG = re.compile(r"#\s*#binary:\s*([01\s]+)(?::\s*(.+))?")

# Endianness setting
_endianness = 'big'  # 'big' | 'little'


def _parse(line):
    """Extract binary bytes and optional label from a comment line."""
    m = _BINARY_TAG.match(line.strip())
    if m:
        bits = m.group(1).strip()
        label = m.group(2).strip() if m.group(2) else None
        return bits, label
    return None, None


def _validate_bits(bits_str):
    """
    Validate that a binary string contains only '0', '1', and whitespace.

    Args:
        bits_str : string of binary digits (e.g. '10101010 01010101')

    Returns:
        (is_valid: bool, error_msg: str | None)
    """
    clean = bits_str.replace(' ', '').replace('\t', '')
    if not clean:
        return False, "Empty binary string"
    if any(c not in '01' for c in clean):
        return False, f"Invalid characters in binary string: '{bits_str}'"
    if len(clean) % 8 != 0:
        return False, f"Binary string length ({len(clean)} bits) is not a multiple of 8"
    return True, None


def to_int(bits_str, signed=False):
    """
    Convert a binary string to an integer.

    Args:
        bits_str : string of binary digits (e.g. '10101010')
        signed   : if True, interpret as two's complement signed integer

    Returns:
        int
    """
    clean = bits_str.replace(' ', '').replace('\t', '')
    if not clean:
        return 0

    value = int(clean, 2)

    if signed:
        # Two's complement: if MSB is 1, interpret as negative
        bit_len = len(clean)
        if value >= (1 << (bit_len - 1)):
            value -= (1 << bit_len)

    return value


def to_hex(bits_str, prefix=True):
    """
    Convert a binary string to hexadecimal representation.

    Args:
        bits_str : string of binary digits (e.g. '11110000')
        prefix   : if True, prepend '0x'

    Returns:
        str (hex representation)
    """
    val = to_int(bits_str, signed=False)
    hex_str = hex(val) if prefix else hex(val)[2:]
    return hex_str


def to_bytes(bits_str, byteorder=None):
    """
    Convert a binary string to a bytes object.

    Args:
        bits_str  : binary string (e.g. '10101010 01010101')
        byteorder : 'big' (default) | 'little' | None (uses global _endianness)

    Returns:
        bytes
    """
    if byteorder is None:
        byteorder = _endianness

    val = to_int(bits_str, signed=False)
    byte_len = (len(bits_str.replace(' ', '').replace('\t', '')) + 7) // 8
    return val.to_bytes(byte_len, byteorder=byteorder)


def from_int(value, bit_width=8):
    """
    Convert an integer to a binary string of specified width.

    Args:
        value     : integer
        bit_width : number of bits (default 8)

    Returns:
        str (binary representation, e.g. '00001010')
    """
    return format(value & ((1 << bit_width) - 1), f'0{bit_width}b')


def from_bytes(byte_data, byteorder=None):
    """
    Convert a bytes object to a binary string.

    Args:
        byte_data : bytes
        byteorder : 'big' | 'little' | None (uses global _endianness)

    Returns:
        str (binary representation, space-separated bytes)
    """
    if byteorder is None:
        byteorder = _endianness

    val = int.from_bytes(byte_data, byteorder=byteorder)
    bit_width = len(byte_data) * 8
    bits = format(val, f'0{bit_width}b')

    # Space-separate into bytes for readability
    return ' '.join(bits[i:i+8] for i in range(0, len(bits), 8))


def set_endianness(order):
    """
    Set the global endianness for binary <-> bytes conversions.

    Args:
        order : 'big' | 'little'
    """
    global _endianness
    if order not in ('big', 'little'):
        raise ValueError(f"[DYTX:binary] Invalid endianness '{order}'. Choose 'big' or 'little'.")
    _endianness = order
    print(f"[DYTX:binary] Endianness set to '{order}'")


def get_endianness():
    """Return the current global endianness setting."""
    return _endianness


def exec_comment(label, bits=None):
    """
    Execute the binary directive associated with the given label.
    DYTX scans source for a #binary: comment whose trailing comment matches label.

    Args:
        label : string label to match (e.g. 'NOP', 'BITMASK_ALL')
        bits  : optional binary string override (if not scanning from source)
    """
    _check_init()
    global _exec_count

    if bits is not None:
        valid, err = _validate_bits(bits)
        if not valid:
            print(f"[DYTX:binary] ERROR: {err}")
            return
        _buffer[label] = bits

    _exec_count += 1
    print(f"[DYTX:binary] Executed binary directive for '{label}'")


def flush():
    """Flush any pending binary directives."""
    _check_init()
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:binary] Flushed {count} binary directive(s)")
    _buffer.clear()


def get_buffer():
    """Return the current buffer of binary directives as a dict {label: bits_str}."""
    return dict(_buffer)


def report():
    """Print session binary execution summary."""
    print(f"[DYTX:binary] Session report: {_exec_count} binary directive(s) executed. | endianness={_endianness}")


def reset():
    """Reset binary engine state."""
    global _buffer, _exec_count
    _buffer.clear()
    _exec_count = 0
    print("[DYTX:binary] Reset complete.")


# ── Utility: bitwise operations ────────────────────────────────────────────────────
def bitwise_and(bits_a, bits_b):
    """Perform bitwise AND on two binary strings of equal length."""
    a = to_int(bits_a)
    b = to_int(bits_b)
    result = a & b
    width = max(len(bits_a.replace(' ', '')), len(bits_b.replace(' ', '')))
    return from_int(result, bit_width=width)


def bitwise_or(bits_a, bits_b):
    """Perform bitwise OR on two binary strings of equal length."""
    a = to_int(bits_a)
    b = to_int(bits_b)
    result = a | b
    width = max(len(bits_a.replace(' ', '')), len(bits_b.replace(' ', '')))
    return from_int(result, bit_width=width)


def bitwise_xor(bits_a, bits_b):
    """Perform bitwise XOR on two binary strings of equal length."""
    a = to_int(bits_a)
    b = to_int(bits_b)
    result = a ^ b
    width = max(len(bits_a.replace(' ', '')), len(bits_b.replace(' ', '')))
    return from_int(result, bit_width=width)


def bitwise_not(bits, width=None):
    """
    Perform bitwise NOT (invert all bits).

    Args:
        bits  : binary string
        width : bit width (default: infer from bits string length)

    Returns:
        binary string (inverted)
    """
    if width is None:
        width = len(bits.replace(' ', '').replace('\t', ''))
    val = to_int(bits)
    mask = (1 << width) - 1
    result = val ^ mask
    return from_int(result, bit_width=width)


# ── Advanced: checksum / parity utilities (future expansion) ─────────────────────────────
def parity(bits_str):
    """
    Calculate even parity bit (1 if odd number of 1s, else 0).

    Args:
        bits_str : binary string (e.g. '10101010')

    Returns:
        int (0 or 1)
    """
    clean = bits_str.replace(' ', '').replace('\t', '')
    ones = clean.count('1')
    return ones % 2


def hamming_distance(bits_a, bits_b):
    """
    Calculate Hamming distance between two binary strings (number of differing bits).

    Args:
        bits_a, bits_b : binary strings of equal length

    Returns:
        int (distance)
    """
    xor_result = bitwise_xor(bits_a, bits_b)
    return xor_result.count('1')
