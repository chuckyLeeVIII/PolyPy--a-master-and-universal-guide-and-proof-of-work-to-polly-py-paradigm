# PolyPy LED Blink Proof of Work
# PolyPi Pure v1.0 — Thonny/MicroPython (RP2040) OR CPython simulation
# In pure mode, hardware calls are simulated — no physical board required

import sys
import dytx
import time

# --- Detect environment automatically ---
_IDE = "thonny" if "thonny" in sys.executable.lower() else "pure"
_MODE = "micropython" if _IDE == "thonny" else "python"

# Initialize PolyPy DYTX runtime
dytx.init(mode=_MODE, ide=_IDE, target="rp2040" if _IDE == "thonny" else None)

# --- Hardware abstraction layer ---
if _IDE == "thonny":
    # Real MicroPython hardware path
    from machine import Pin  # type: ignore
    import dytx.binary as dxb
    import dytx.machine as dxm
    led = Pin(25, Pin.OUT)
else:
    # Pure Python simulation stub
    class _PinStub:
        def __init__(self, pin, mode=None): self._pin = pin; self._val = 0
        def value(self, v=None):
            if v is not None:
                self._val = v
                print(f"  [sim] GPIO{self._pin} = {'HIGH' if v else 'LOW'}")
            return self._val
    class _DxbStub:
        def exec_comment(self, label): print(f"  [sim] binary exec: {label}")
    class _DxmStub:
        def flush(self): print("  [sim] machine flush")
    led = _PinStub(25)
    dxb = _DxbStub()
    dxm = _DxmStub()

# #binary: 00100101 00000001 ; GPIO25 HIGH — machine binary comment directive
# #binary: 00100101 00000000 ; GPIO25 LOW
# #machine: MOV R3, #25 ; load GPIO pin number into register
# #machine: MOV R4, #1  ; HIGH
# #machine: STR R4, [GPIO_BASE, R3] ; write HIGH to GPIO25

print("[PolyPi Pure] Starting LED blink sequence (10 cycles)...")
for i in range(10):
    led.value(1)
    dxb.exec_comment("GPIO25 HIGH")  # DYTX executes the #binary HIGH directive
    time.sleep(0.5)
    led.value(0)
    dxb.exec_comment("GPIO25 LOW")   # DYTX executes the #binary LOW directive
    time.sleep(0.5)

if _IDE == "thonny":
    dxm.flush()  # flush machine code buffer to MicroPython runtime

print("[PolyPi Pure] Proof of Work #2 complete.")
