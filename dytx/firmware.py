# dytx/firmware.py
# DYTX Firmware Sub-Engine v2.0
# Parses //firmware:c++ docstring blocks and compiles them to target firmware.
# Supports multi-target cross-compilation: rp2040, avr, esp32, stm32, nrf52

import re
import inspect
from dytx import _check_init

# ── State ──────────────────────────────────────────────────────────────────────
_exec_count = 0
_FIRMWARE_TAG = re.compile(r"^//firmware:(\w+)")
_compiled_blocks = {}  # {target: [code_strings]}

# Supported targets
_VALID_TARGETS = ('c++', 'rp2040', 'avr', 'esp32', 'esp8266', 'stm32', 'nrf52')


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
        fn     : function containing firmware code in docstring
        target : target architecture ('c++', 'rp2040', 'avr', 'esp32', etc.)

    Returns:
        str : extracted firmware source code
    """
    _check_init()
    global _exec_count

    if target not in _VALID_TARGETS:
        print(f"[DYTX:firmware] WARNING: Unknown target '{target}'")

    code = _extract_block(fn)
    if not code:
        print(f"[DYTX:firmware] No firmware block found in function '{fn.__name__}'")
        return ""

    if target not in _compiled_blocks:
        _compiled_blocks[target] = []
    _compiled_blocks[target].append(code)

    _exec_count += 1
    print(f"[DYTX:firmware] Compiled block for target '{target}' ({len(code)} chars)")
    return code


def compile_string(code, target='c++', output_file=None):
    """
    Compile a firmware code string directly (not from a function docstring).

    Args:
        code        : C/C++ source code string
        target      : target architecture
        output_file : optional output filename (e.g. 'blink.ino', 'main.c')

    Returns:
        str : the input code (for chaining)
    """
    _check_init()
    global _exec_count

    if target not in _VALID_TARGETS:
        print(f"[DYTX:firmware] WARNING: Unknown target '{target}'")

    if target not in _compiled_blocks:
        _compiled_blocks[target] = []
    _compiled_blocks[target].append(code)

    _exec_count += 1
    print(f"[DYTX:firmware] Compiled string for target '{target}' ({len(code)} chars)")

    if output_file:
        print(f"[DYTX:firmware] Output would be written to: {output_file}")
        # In a real impl, write to file here: with open(output_file, 'w') as f: f.write(code)

    return code


def get_compiled(target=None):
    """
    Retrieve all compiled firmware blocks for a given target.

    Args:
        target : target name (e.g. 'rp2040'), or None to get all

    Returns:
        dict {target: [code_strings]} if target is None, else list of code strings
    """
    if target is None:
        return dict(_compiled_blocks)
    return _compiled_blocks.get(target, [])


def flash_stub(target, binary_path=None):
    """
    [STUB] Simulate flashing firmware to a connected device.

    Args:
        target      : target board identifier
        binary_path : path to compiled binary (e.g. 'firmware.uf2')

    In a real implementation, this would invoke tools like:
      - RP2040: picotool, drag-drop UF2
      - ESP32:  esptool.py
      - AVR:    avrdude
      - STM32:  st-flash, dfu-util
      - nRF52:  nrfjprog, pyOCD
    """
    print(f"[DYTX:firmware] STUB: Would flash '{binary_path or 'compiled firmware'}' to {target}")
    print(f"[DYTX:firmware] (Actual flashing not implemented in this version)")


def report():
    """Print session firmware compilation summary."""
    total_blocks = sum(len(blocks) for blocks in _compiled_blocks.values())
    print(f"[DYTX:firmware] Session report: {_exec_count} total firmware block(s) compiled.")
    for target, blocks in _compiled_blocks.items():
        print(f"[DYTX:firmware]   {target}: {len(blocks)} block(s)")


def reset():
    """Clear firmware compilation state."""
    global _exec_count, _compiled_blocks
    _exec_count = 0
    _compiled_blocks.clear()
    print("[DYTX:firmware] Reset complete.")


# ── Advanced: toolchain detection & invocation stubs ────────────────────────────────────────
def detect_toolchain(target):
    """
    [STUB] Check if the appropriate cross-compilation toolchain is installed.

    Args:
        target : target name (e.g. 'avr', 'rp2040')

    Returns:
        dict with keys: 'available' (bool), 'compiler' (str | None), 'version' (str | None)
    """
    # TODO: Actually invoke 'which arm-none-eabi-gcc', 'esptool.py version', etc.
    print(f"[DYTX:firmware] STUB: Detecting toolchain for '{target}'...")
    return {'available': False, 'compiler': None, 'version': None}


def build(target, source_file, output_file):
    """
    [STUB] Invoke the compiler/linker to build firmware.

    Args:
        target      : target name
        source_file : input C/C++ source file
        output_file : output binary/hex/uf2 file

    Returns:
        bool : True if build succeeded
    """
    print(f"[DYTX:firmware] STUB: Building {source_file} → {output_file} for {target}")
    print(f"[DYTX:firmware] (Actual compilation not implemented)")
    return False
