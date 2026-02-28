# PolyPy Hello World — Run in Thonny IDE only (MicroPython)

import dytx
import dytx.machine as dxm

# Initialize DYTX runtime — must be called first
dytx.init(mode="micropython", ide="thonny")

# Standard Python
print("Hello from PolyPy!")

# #machine: MOV R0, #72 ; ASCII 'H'
# #machine: MOV R1, #101 ; ASCII 'e'
# #machine: MOV R2, #108 ; ASCII 'l'
# #machine: STR R0, [SP] ; push to stack
# #machine: BL UART_WRITE ; write to UART (Thonny REPL output)

# DYTX executes the above machine comments automatically
dxm.flush()  # flush machine code buffer to MicroPython runtime
