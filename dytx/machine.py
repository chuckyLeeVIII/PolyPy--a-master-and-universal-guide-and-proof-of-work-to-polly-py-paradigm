# dytx/machine.py
# DYTX Machine Code Sub-Engine v2.0
# Parses #machine: comment directives and simulates MCU register access.

import re
from typing import Any
from dytx import _check_init

# ── State ─────────────────────────────────────────────────────────────────────
_buffer: list[str] = []
_exec_count: int = 0
_MACHINE_TAG = re.compile(r"#\s*#machine:\s*(.+)")

# Simulated register file (ARM Cortex-M style)
_registers: dict[str, int] = {f'R{i}': 0 for i in range(16)}
_registers['SP'] = 0x20000000  # R13 - stack pointer
_registers['LR'] = 0           # R14 - link register
_registers['PC'] = 0           # R15 - program counter

# Simulated memory (dict: address -> value)
_memory: dict[int, int] = {}

# Peripheral register addresses (RP2040 / Generic ARM)
_PERIPHERALS = {
    'GPIO_OUT': 0x40014000,
    'GPIO_IN':  0x40014004,
    'GPIO_DIR': 0x40014008,
    'UART_DR':  0x40034000,
    'UART_FR':  0x40034018,
    'SPI_DR':   0x40040000,
    'I2C_DAT':  0x40044000,
}

def _parse(line: str) -> str | None:
    """Extract machine directive from a comment line."""
    m = _MACHINE_TAG.match(line.strip())
    return m.group(1).strip() if m else None

def read_register(reg: str) -> int:
    """Read a simulated ARM register value."""
    reg = reg.upper()
    if reg not in _registers:
        print(f"[DYTX:machine] WARNING: Unknown register '{reg}'")
        return 0
    return _registers[reg]

def write_register(reg: str, value: int):
    """Write to a simulated ARM register."""
    reg = reg.upper()
    if reg not in _registers:
        print(f"[DYTX:machine] WARNING: Unknown register '{reg}'")
        return
    _registers[reg] = value & 0xFFFFFFFF
    print(f"[DYTX:machine] {reg} ← 0x{value:08X}")

def read_memory(address: int) -> int:
    """Read a 32-bit word from simulated memory."""
    return _memory.get(address, 0)

def write_memory(address: int, value: int):
    """Write a 32-bit word to simulated memory."""
    _memory[address] = value & 0xFFFFFFFF
    print(f"[DYTX:machine] MEM[0x{address:08X}] ← 0x{value:08X}")

def read_peripheral(name: str) -> int:
    """Read from a named peripheral register."""
    if name not in _PERIPHERALS:
        print(f"[DYTX:machine] WARNING: Unknown peripheral '{name}'")
        return 0
    return read_memory(_PERIPHERALS[name])

def write_peripheral(name: str, value: int):
    """Write to a named peripheral register."""
    if name not in _PERIPHERALS:
        print(f"[DYTX:machine] WARNING: Unknown peripheral '{name}'")
        return
    write_memory(_PERIPHERALS[name], value)

def get_register_map() -> dict[str, int]:
    """Return a copy of the current register state."""
    return dict(_registers)

def dump_registers():
    """Print all register values in a formatted table."""
    print("=" * 40)
    print("      DYTX Machine Register Dump")
    print("=" * 40)
    for i in range(13):
        print(f" R{i:<2} = 0x{_registers[f'R{i}']:08X}")
    print(f" SP  = 0x{_registers['SP']:08X}")
    print(f" LR  = 0x{_registers['LR']:08X}")
    print(f" PC  = 0x{_registers['PC']:08X}")
    print("=" * 40)

def dump_memory(start: int = 0x20000000, count: int = 16):
    """Print a memory dump."""
    print(f"
[DYTX:machine] Memory dump from 0x{start:08X}:")
    for i in range(count):
        addr = start + (i * 4)
        val = read_memory(addr)
        print(f"  0x{addr:08X}: 0x{val:08X}")

def flush():
    """Flush the machine code comment buffer."""
    _check_init()
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:machine] Executed {count} machine directive(s) OK")
    _buffer.clear()

def exec_directive(directive: str):
    """Execute a single machine directive string."""
    _check_init()
    global _exec_count
    _exec_count += 1
    print(f"[DYTX:machine] >> {directive}")

def report():
    """Print a summary report."""
    print(f"[DYTX:machine] Session report: {_exec_count} machine directive(s) executed.")

def reset():
    """Reset execution state."""
    global _exec_count, _registers, _memory
    _exec_count = 0
    for key in _registers: _registers[key] = 0
    _registers['SP'] = 0x20000000
    _memory.clear()
    print("[DYTX:machine] Reset complete.")

# ── Instruction Simulation ───────────────────────────────────────────────────

def _resolve_val(op: Any) -> int:
    if isinstance(op, int): return op
    if isinstance(op, str):
        op = op.strip()
        if op.startswith('#'):
            try: return int(op[1:], 0)
            except ValueError: return 0
        if op.upper() in _registers:
            return read_register(op)
    return 0

def simulate_mov(dest: str, src: Any):
    """Simulate MOV dest, src."""
    write_register(dest, _resolve_val(src))

def simulate_add(dest: str, op1: Any, op2: Any):
    """Simulate ADD dest, op1, op2."""
    write_register(dest, _resolve_val(op1) + _resolve_val(op2))

def simulate_sub(dest: str, op1: Any, op2: Any):
    """Simulate SUB dest, op1, op2."""
    write_register(dest, _resolve_val(op1) - _resolve_val(op2))
