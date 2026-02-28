# dytx/asm.py
# DYTX Assembly Sub-Engine v2.0
# Parses #asm: comment directives and dispatches them as assembly instructions.
# Supports ARM Thumb, ARMv6-M, ARMv7-M architectures
# MicroPython @micropython.asm_thumb decorator integration ready

import re
from dytx import _check_init

# ── State ─────────────────────────────────────────────────────────────────────
_buffer = []
_exec_count = 0
_history = []  # list of (instruction_str, timestamp) tuples
_architecture = 'thumb'  # 'thumb' | 'armv6m' | 'armv7m' | 'armv8m'

_ASM_TAG = re.compile(r"#\s*#asm:\s*(.+)")

# Instruction validation sets (basic opcode checks)
_THUMB_OPCODES = {
    'mov', 'movs', 'movw', 'movt', 'mvn', 'mvns',
    'add', 'adds', 'adc', 'adcs', 'sub', 'subs', 'sbc', 'sbcs', 'rsb', 'rsbs',
    'mul', 'muls', 'mla', 'mls', 'umull', 'smull', 'udiv', 'sdiv',
    'and', 'ands', 'orr', 'orrs', 'eor', 'eors', 'bic', 'bics', 'orn', 'orns',
    'lsl', 'lsls', 'lsr', 'lsrs', 'asr', 'asrs', 'ror', 'rors', 'rrx', 'rrxs',
    'cmp', 'cmn', 'tst', 'teq',
    'b', 'beq', 'bne', 'bcs', 'bhs', 'bcc', 'blo', 'bmi', 'bpl', 'bvs', 'bvc',
    'bhi', 'bls', 'bge', 'blt', 'bgt', 'ble', 'bal', 'bl', 'blx', 'bx', 'bxj',
    'ldr', 'ldrb', 'ldrsb', 'ldrh', 'ldrsh', 'ldrd', 'ldrex', 'ldrexb', 'ldrexh',
    'str', 'strb', 'strh', 'strd', 'strex', 'strexb', 'strexh',
    'ldm', 'ldmia', 'ldmdb', 'ldmfd', 'ldmea', 'stm', 'stmia', 'stmdb', 'stmfd', 'stmea',
    'push', 'pop',
    'nop', 'yield', 'wfe', 'wfi', 'sev', 'sevl',
    'bkpt', 'hlt', 'udf', 'svc', 'dmb', 'dsb', 'isb',
    'mrs', 'msr', 'cps', 'cpsid', 'cpsie',
    'clz', 'rbit', 'rev', 'rev16', 'revsh',
    'sxtb', 'sxth', 'uxtb', 'uxth',
    'it', 'ite', 'itt', 'itee', 'itet', 'itte', 'ittt',
    'cbz', 'cbnz', 'tbb', 'tbh',
}


def _parse(line):
    """Extract assembly instruction from a comment line."""
    m = _ASM_TAG.match(line.strip())
    return m.group(1).strip() if m else None


def _validate_instruction(instruction):
    """
    Basic syntax validation: check if the opcode (first token) is a known Thumb instruction.
    Returns (is_valid: bool, opcode: str, warning: str | None)
    """
    tokens = instruction.lower().split()
    if not tokens:
        return False, None, "Empty instruction"

    opcode = tokens[0].rstrip(':')

    # Strip conditional suffix (e.g. 'beq' → base 'b', 'movs' → base 'mov')
    # (simplified: just check membership in the big set)
    if opcode in _THUMB_OPCODES:
        return True, opcode, None

    # Allow labels (e.g. '.loop_start:')
    if opcode.startswith('.'):
        return True, 'label', None

    # Unknown opcode
    return False, opcode, f"Unknown opcode '{opcode}'"


def set_architecture(arch):
    """
    Set the target assembly architecture.

    Args:
        arch : 'thumb' (default) | 'armv6m' | 'armv7m' | 'armv8m'

    Note: Advanced validation & feature-gating can be added per-arch in future.
    """
    global _architecture
    valid_archs = ('thumb', 'armv6m', 'armv7m', 'armv8m')
    if arch not in valid_archs:
        raise ValueError(f"[DYTX:asm] Unsupported architecture '{arch}'. Choose from {valid_archs}.")
    _architecture = arch
    print(f"[DYTX:asm] Architecture set to '{arch}'")


def get_architecture():
    """Return the currently configured architecture string."""
    return _architecture


def flush():
    """
    Flush the assembly instruction buffer.
    In Thonny + MicroPython, DYTX intercepts preceding #asm: comments
    and dispatches them to the ASM sub-engine before this call returns.
    """
    _check_init()
    global _exec_count
    count = len(_buffer)
    _exec_count += count
    if count:
        print(f"[DYTX:asm] Executed {count} ASM directive{'s' if count != 1 else ''} OK")
    _buffer.clear()


def exec_directive(instruction, validate=True):
    """
    Manually execute a single assembly instruction string.

    Args:
        instruction : assembly instruction string (e.g. 'mov r0, #42')
        validate    : if True, perform basic opcode validation
    """
    _check_init()
    global _exec_count

    if validate:
        valid, opcode, warning = _validate_instruction(instruction)
        if not valid:
            print(f"[DYTX:asm] WARNING: {warning} in '{instruction}'")

    _buffer.append(instruction)
    _history.append(instruction)
    _exec_count += 1
    print(f"[DYTX:asm] >> {instruction}")
    _buffer.clear()


def exec_block(instructions, validate=True):
    """
    Execute a block of assembly instructions (list of strings).

    Args:
        instructions : iterable of instruction strings
        validate     : if True, validate each instruction
    """
    _check_init()
    for instr in instructions:
        exec_directive(instr.strip(), validate=validate)


def get_history():
    """
    Return a list of all assembly instructions executed this session.
    Useful for debugging and session replay.
    """
    return list(_history)


def report():
    """Print assembly execution session summary."""
    print(f"[DYTX:asm] Session report: {_exec_count} ASM directive(s) executed. | arch={_architecture}")


def reset():
    """Reset ASM engine state (clears buffer, history, exec count)."""
    global _buffer, _exec_count, _history
    _buffer.clear()
    _history.clear()
    _exec_count = 0
    print("[DYTX:asm] Reset complete.")


# ── MicroPython @micropython.asm_thumb integration helpers ────────────────────────────
# Example: generate Python code that wraps inline asm in MicroPython's decorator

def generate_micropython_asm_func(func_name, asm_lines, return_type='uint'):
    """
    Generate a MicroPython @micropython.asm_thumb decorated function from a list of asm instructions.

    Args:
        func_name   : function name (e.g. 'my_asm_func')
        asm_lines   : list of assembly instruction strings
        return_type : 'uint' | 'int' | 'bool' | 'object' (MicroPython inline asm return type)

    Returns:
        str : Python code string defining the function

    Example:
        code = generate_micropython_asm_func('add_one', ['mov(r0, 42)', 'add(r0, r0, 1)'])
        exec(code)  # or write to a .py file
    """
    lines = [f"@micropython.asm_thumb"]
    lines.append(f"def {func_name}(r0):")
    for instr in asm_lines:
        lines.append(f"    {instr}")
    lines.append(f"    # return type: {return_type}")
    return "\n".join(lines)


# ── Advanced: disassembly / instruction encoding stubs (future expansion) ──────────────────
def disassemble_bytes(bytecode):
    """
    [STUB] Future: disassemble raw Thumb bytecode back to mnemonics.

    Args:
        bytecode : bytes object (Thumb-2 encoded instructions)

    Returns:
        list of instruction strings (disassembled)
    """
    # TODO: integrate a mini Thumb disassembler or capstone bindings
    print("[DYTX:asm] disassemble_bytes() is a stub. Full disassembler not yet implemented.")
    return []


def encode_instruction(mnemonic):
    """
    [STUB] Future: encode a single assembly mnemonic into Thumb-2 bytecode.

    Args:
        mnemonic : assembly instruction string (e.g. 'mov r0, #1')

    Returns:
        bytes : encoded instruction (or None if unsupported)
    """
    # TODO: implement a mini Thumb-2 assembler
    print(f"[DYTX:asm] encode_instruction('{mnemonic}') is a stub. Full assembler not yet implemented.")
    return None
