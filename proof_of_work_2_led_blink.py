# PolyPy LED Blink Proof of Work
# IDE: Thonny only | Interpreter: MicroPython (Raspberry Pi Pico)

import dytx
import dytx.binary as dxb
import dytx.machine as dxm
from machine import Pin
import time

# Initialize PolyPy DYTX runtime
dytx.init(mode="micropython", ide="thonny", target="rp2040")

# Python-level pin setup
led = Pin(25, Pin.OUT)

# #binary: 00100101 00000001 ; GPIO25 HIGH — machine binary comment directive
# #binary: 00100101 00000000 ; GPIO25 LOW
# #machine: MOV R3, #25 ; load GPIO pin number into register
# #machine: MOV R4, #1 ; HIGH
# #machine: STR R4, [GPIO_BASE, R3] ; write HIGH to GPIO25

for i in range(10):
    led.value(1)
    dxb.exec_comment("GPIO25 HIGH")  # DYTX executes the #binary HIGH directive
    time.sleep(0.5)
    led.value(0)
    dxb.exec_comment("GPIO25 LOW")   # DYTX executes the #binary LOW directive
    time.sleep(0.5)

print("Proof of Work #2 Complete: LED blinked 10 times")
dxm.report()  # prints DYTX machine code execution report
