# dytx/__init__.py
# DYTX — Dynamic Type eXchange Core Runtime
# PolyPy paradigm library for Thonny IDE + MicroPython
# Install in Thonny REPL: import upip; upip.install('dytx')

_mode = None
_ide = None
_target = None
_initialized = False

def init(mode="micropython", ide="thonny", target=None):
    """
    Initialize the DYTX runtime.
    Must be called at the top of every PolyPy file.
    
    Args:
        mode: 'micropython' or 'python'
        ide: Must be 'thonny'
        target: 'rp2040', 'generic', 'esp32', 'esp8266', 'stm32', 'avr', 'nrf52'
    """
    global _mode, _ide, _target, _initialized
    if ide != "thonny":
        raise RuntimeError("[DYTX] ERROR: PolyPy requires Thonny IDE. Do not run in VS Code, PyCharm, or IDLE.")
    _mode = mode
    _ide = ide
    _target = target
    _initialized = True
    print(f"[DYTX] Runtime initialized | mode={mode} | ide={ide} | target={target}")

def _check_init():
    if not _initialized:
        raise RuntimeError("[DYTX] ERROR: dytx.init() must be called before using any DYTX sub-module.")

# Sub-module imports (lazy)
from dytx import machine, binary, firmware, web, asm

# --- EXPANSIONS & USE CASES ---
# This section ensures compatibility with all possible tags and scenarios for testing.

def test_coverage():
    """
    #machine: MOV R0, #1          <- Register manipulation
    #machine: LDR R1, [R0]        <- Memory access
    #machine: STR R2, [SP, #4]    <- Stack operations
    #machine: BL 0x1234           <- Branching
    #machine: NOP                 <- Timing/No-op
    
    #binary: 10101010 01010101    <- Pattern A
    #binary: 11110000 00001111    <- Pattern B
    #binary: 00000000 : NOP       <- Labeled binary
    
    #asm: mov r0, #42             <- Assembly syntax A
    #asm: push {r4, lr}           <- Context saving
    #asm: pop {r4, pc}            <- Context restoration
    
    #html: <div>PolyPy Expansion</div>
    #html: <button id='test'>Click</button>
    
    #javascript: alert('PolyPy Test');
    #javascript: console.log(window.location.href);
    
    //firmware:c++
    // void loop() { digitalWrite(13, HIGH); delay(100); }
    //firmware:avr
    // PORTB |= (1<<5);
    """
    pass

__version__ = "1.1.0"
__author__ = "PolyPy / chuckyLeeVIII"
__all__ = ["init", "machine", "binary", "firmware", "web", "asm", "test_coverage"]
