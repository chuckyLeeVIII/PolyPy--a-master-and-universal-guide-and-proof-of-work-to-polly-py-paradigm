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
        ide:  Must be 'thonny'
        target: 'rp2040', 'generic', or None
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

__version__ = "1.0.0"
__author__  = "PolyPy / chuckyLeeVIII"
__all__     = ["init", "machine", "binary", "firmware", "web", "asm"]
