"""
dytx/__init__.py
DYTX — Dynamic Type eXchange Core Runtime v2.1.0 (PolyPi Pure)
PolyPy paradigm library — Thonny IDE + MicroPython + Standard Python (fullstack)

GitHub: chuckyLeeVIII/PolyPy
"""

__version__ = "2.1.0"
__author__ = "PolyPy / chuckyLeeVIII"
__license__ = "MIT"

# ── Runtime state ────────────────────────────────────────────────────────────
_mode = None        # 'micropython' | 'python'
_ide = None         # 'thonny' | 'pure' (pure = standard CPython / fullstack)
_target = None      # board identifier string
_initialized = False
_runtime_log = []   # ordered log of every init call this session

# Supported values
_VALID_MODES = ('micropython', 'python')
_VALID_IDES = ('thonny', 'pure')           # 'pure' = CPython / fullstack / FastAPI
_VALID_TARGETS = ('rp2040', 'generic', 'esp32', 'esp8266', 'stm32', 'avr', 'nrf52', None)

# ── Core init ────────────────────────────────────────────────────────────────
def init(mode="micropython", ide="thonny", target=None):
    """
    Initialize the DYTX runtime.
    Must be called at the top of every PolyPy file.

    Args:
        mode   : 'micropython' (default) or 'python'
        ide    : 'thonny' (embedded/MicroPython) or 'pure' (standard CPython / fullstack)
        target : 'rp2040' | 'generic' | 'esp32' | 'esp8266' |
                 'stm32' | 'avr' | 'nrf52' | None
    """
    global _mode, _ide, _target, _initialized, _runtime_log

    if ide not in _VALID_IDES:
        raise RuntimeError(
            f"[DYTX] ERROR: Invalid ide '{ide}'. "
            "Use 'thonny' for MicroPython or 'pure' for standard Python/fullstack."
        )

    if mode not in _VALID_MODES:
        raise ValueError(f"[DYTX] ERROR: Invalid mode '{mode}'.")

    if target is not None and target not in _VALID_TARGETS:
        raise ValueError(f"[DYTX] ERROR: Unknown target '{target}'.")

    _mode = mode
    _ide = ide
    _target = target
    _initialized = True

    _runtime_log.append({"mode": mode, "ide": ide, "target": target})
    print(f"[DYTX] Runtime initialised | mode={mode} | ide={ide} | target={target}")
    print("[DYTX] Sub-modules ready | machine | binary | firmware | web | asm")


def _check_init():
    """Raise if dytx.init() has not been called yet."""
    if not _initialized:
        raise RuntimeError("[DYTX] ERROR: dytx.init() must be called first.")


# ── Runtime introspection ─────────────────────────────────────────────────────
def status():
    """Print a human-readable summary of the current DYTX runtime state."""
    print("=" * 52)
    print(" DYTX Runtime Status")
    print("=" * 52)
    print(f"  initialised : {_initialized}")
    print(f"  mode        : {_mode}")
    print(f"  ide         : {_ide}")
    print(f"  target      : {_target}")
    print(f"  init calls  : {len(_runtime_log)}")
    print("=" * 52)


def get_runtime_info() -> dict:
    """Return the current runtime configuration as a dict."""
    return {
        "version": __version__,
        "initialised": _initialized,
        "mode": _mode,
        "ide": _ide,
        "target": _target,
        "init_calls": len(_runtime_log),
    }


def reset():
    """Reset the DYTX runtime state (useful in test harnesses)."""
    global _mode, _ide, _target, _initialized, _runtime_log
    _mode = None
    _ide = None
    _target = None
    _initialized = False
    _runtime_log = []
    print("[DYTX] Runtime reset.")


# ── Sub-module imports ────────────────────────────────────────────────────────
# Lazy-loaded for MicroPython compatibility
try:
    from dytx import machine, binary, firmware, web, asm
except ImportError:
    pass


def report_all():
    """Print a full session report across ALL DYTX sub-engines."""
    print(" " + "=" * 52)
    print(" DYTX Full Session Report")
    print("=" * 52)
    for module in (machine, binary, firmware, web, asm):
        if hasattr(module, 'report'):
            module.report()
    print("=" * 52 + " ")


__all__ = [
    "init",
    "reset",
    "status",
    "get_runtime_info",
    "report_all",
    "machine",
    "binary",
    "firmware",
    "web",
    "asm",
    "_check_init",
]
