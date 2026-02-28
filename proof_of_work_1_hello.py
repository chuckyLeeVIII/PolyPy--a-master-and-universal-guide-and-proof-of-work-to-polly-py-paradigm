# PolyPy Hello World
# PolyPi Pure v1.0 — Runs in Thonny IDE (MicroPython) OR standard Python
# IDE mode: set ide="thonny" for MicroPython, ide="pure" for CPython/fullstack

import sys
import dytx

# --- Detect environment automatically ---
_IDE = "thonny" if "thonny" in sys.executable.lower() else "pure"
_MODE = "micropython" if _IDE == "thonny" else "python"

# Initialize DYTX runtime
dytx.init(mode=_MODE, ide=_IDE)

# Standard Python output
print("Hello from PolyPy! (PolyPi Pure v1.0)")

# Machine-code comment directives (parsed by DYTX in Thonny/MicroPython mode)
# #machine: MOV R0, #72  ; ASCII 'H'
# #machine: MOV R1, #101 ; ASCII 'e'
# #machine: MOV R2, #108 ; ASCII 'l'
# #machine: STR R0, [SP] ; push to stack
# #machine: BL UART_WRITE ; write to UART (Thonny REPL output)

# In pure/fullstack mode, dytx.machine is a simulation stub — no hardware required
try:
    import dytx.machine as dxm
    dxm.flush()  # flush machine code buffer to MicroPython runtime (no-op in pure mode)
except (ImportError, AttributeError):
    pass  # pure Python fallback

print("[PolyPi Pure] Proof of Work #1 complete.")
