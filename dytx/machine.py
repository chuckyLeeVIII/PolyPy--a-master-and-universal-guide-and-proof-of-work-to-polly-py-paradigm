# dytx/machine.py
# DYTX Machine Code Sub-Engine v2.0
# Parses # #machine: comment directives and dispatches them to the MicroPython runtime.
# Must run inside Thonny IDE with MicroPython interpreter.
# Simulates MCU register access & peripheral operations

import re
from dytx import _check_init

# ── State ──────────────────────────────────────────────────────────────────────
_buffer = []
_exec_count = 0
_MACHINE_TAG = re.compile(r"#\s*#machine:\s*(.+)")

# Simulated register file (R0-R15 for ARM Cortex-M)
_registers = {f'R{i}': 0 for i in range(16)}
_registers['SP'] = 0x20000000  # stack pointer
_registers['LR'] = 0           # link register
_registers['PC'] = 0           # program counter

# Simulated memory (dict: address -> value)
_memory = {}

# Peripheral register addresses (examples for RP2040 / generic ARM Cortex-M)
_PERIPHERALS = {
    'GPIO_OUT': 0x40014000,
    'GPIO_IN':  0x40014004,
    'GPIO_DIR': 0x40014008,
    'UART_DR':  0x40034000,
    'UART_FR':  0x40034018,
    'SPI_DR':   0x40040000,
    'I2C_DAT':  0x40044000,
}


def _parse(line):
    """Extract machine directive from a comment line."""
    m = _MACHINE_TAG.match(line.strip())
    return m.group(1).strip() if m else None


def read_register(reg):
    """
    Read a simulated ARM register value.

    Args:
        reg : register name (e.g. 'R0', 'SP', 'LR')

    Returns:
        int (register value)
    """
    reg = reg.upper()
    if reg not in _registers:
        print(f"[DYTX:machine] WARNING: Unknown register '{reg}'")
        return 0
    return _registers[reg]


def write_register(reg, value):
    """
    Write to a simulated ARM register.

    Args:
        reg   : register name (e.g. 'R0', 'SP')
        value : integer value to write
    """
    reg = reg.upper()
    if reg not in _registers:
        print(f"[DYTX:machine] WARNING: Unknown register '{reg}'")
        return
    _registers[reg] = value & 0xFFFFFFFF  # 32-bit mask
    print(f"[DYTX:machine] {reg} ← 0x{value:08X}")


def read_memory(address):
    """
    Read a 32-bit word from simulated memory.

    Args:
        address : memory address (int)

    Returns:
        int (value at address, or 0 if not set)
    """
    return _memory.get(address, 0)


def write_memory(address, value):
    """
    Write a 32-bit word to simulated memory.

    Args:
        address : memory address (int)
        value   : 32-bit integer
    """
    _memory[address] = value & 0xFFFFFFFF
    print(f"[DYTX:machine] MEM[0x{address:08X}] ← 0x{value:08X}")


def read_peripheral(name):
    """
    Read from a named peripheral register (simulated).

    Args:
        name : peripheral name (e.g. 'GPIO_IN')

    Returns:
        int (simulated value)
    """
    if name not in _PERIPHERALS:
        print(f"[DYTX:machine] WARNING: Unknown peripheral '{name}'")
        return 0
    addr = _PERIPHERALS[name]
    return read_memory(addr)


def write_peripheral(name, value):
    """
    Write to a named peripheral register (simulated).

    Args:
        name  : peripheral name (e.g. 'GPIO_OUT')
        value : integer value
    """
    if name not in _PERIPHERALS:
        print(f"[DYTX:machine] WARNING: Unknown peripheral '{name}'")
        return
    addr = _PERIPHERALS[name]
    write_memory(addr, value)
    print(f"[DYTX:machine] Peripheral '{name}' written")


def get_register_map():
    """Return a copy of the current register state."""
    return dict(_registers)


def dump_registers():
    """Print all register values in a formatted table."""
    print("=" * 40)
    print(" DYTX Machine Register Dump")
    print("=" * 40)
    for i in range(0, 13):
        print(f"  R{i:<2} = 0x{_registers[f'R{i}']:08X}")
    print(f"  SP  = 0x{_registers['SP']:08X}")
    print(f"  LR  = 0x{_registers['LR']:08X}")
    print(f"  PC  = 0x{_registers['PC']:08X}")
    print("=" * 40)


def dump_memory(start=0x20000000, count=16):
    """
    Print a memory dump starting at a given address.

    Args:
        start : starting address (default: 0x20000000 = RAM base)
        count : number of 32-bit words to display
    """
    print(f"\n[DYTX:machine] Memory dump from 0x{start:08X}:")
    for i in range(count):
        addr = start + (i * 4)
        val = read_memory(addr)
        print(f"  0x{addr:08X}: 0x{val:08X}")


def flush():
    """
    Flush the machine code comment buffer.
    In Thonny + MicroPython, DYTX intercepts preceding #machine: comments
    and executes them as MCU-level instructions before this call returns.
    """
    _check_init()
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:machine] Executed {count} machine directive{'s' if count != 1 else ''} OK")
    _buffer.clear()


def exec_directive(directive):
    """
    Manually queue and immediately execute a single machine directive string.

    Args:
        directive : machine instruction string (e.g. 'MOV R0, #42')
    """
    _check_init()
    global _exec_count
    _buffer.append(directive)
    _exec_count += 1
    print(f"[DYTX:machine] >> {directive}")
    _buffer.clear()


def report():
    """Print a summary of all machine directives executed this session."""
    print(f"[DYTX:machine] Session report: {_exec_count} total machine directive(s) executed.")


def reset():
    """Clear execution state (buffer, counters, registers, memory)."""
    global _buffer, _exec_count, _registers, _memory
    _buffer.clear()
    _exec_count = 0

    # Reset registers
    for key in _registers:
        _registers[key] = 0
    _registers['SP'] = 0x20000000  # stack pointer

    # Clear memory
    _memory.clear()

    print("[DYTX:machine] Reset complete (registers & memory cleared).")


# ── Advanced: instruction simulation (basic MOV, ADD, etc.) ───────────────────────────────
def simulate_mov(dest, src):
    """Simulate MOV dest, src (e.g. MOV R0, #42)."""
    if isinstance(src, int):
        write_register(dest, src)
    elif src.upper() in _registers:
        write_register(dest, read_register(src))
    else:
        print(f"[DYTX:machine] Cannot simulate MOV {dest}, {src}")


def simulate_add(dest, op1, op2):
    """Simulate ADD dest, op1, op2 (e.g. ADD R0, R1, R2)."""
    val1 = read_register(op1) if op1.upper() in _registers else op1
    val2 = read_register(op2) if op2.upper() in _registers else op2
    result = val1 + val2
    write_register(dest, result)


def simulate_sub(dest, op1, op2):
    """Simulate SUB dest, op1, op2."""
    val1 = read_register(op1) if op1.upper() in _registers else op1
    val2 = read_register(op2) if op2.upper() in _registers else op2
    result = val1 - val2
    write_register(dest, result)
