# dytx/__init__.py
# DYTX — Dynamic Type eXchange Core Runtime v2.0
# PolyPy paradigm library for Thonny IDE + MicroPython
# Supports: rp2040, esp32, esp8266, stm32, avr, nrf52, generic
# Install in Thonny REPL: import upip; upip.install('dytx')
# GitHub: chuckyLeeVIII/PolyPy

# ── Runtime state ───────────────────────────────────────────────────────────
_mode        = None   # 'micropython' | 'python'
_ide         = None   # 'thonny' (enforced)
_target      = None   # board identifier string
_initialized = False
_runtime_log = []     # ordered log of every init call this session

# Supported values (for validation & IDE hints)
_VALID_MODES   = ('micropython', 'python')
_VALID_IDES    = ('thonny',)
_VALID_TARGETS = ('rp2040', 'generic', 'esp32', 'esp8266', 'stm32', 'avr', 'nrf52')

# ── Core init ───────────────────────────────────────────────────────────────
def init(mode="micropython", ide="thonny", target=None):
    """
    Initialize the DYTX runtime.
    Must be called at the top of every PolyPy file.

    Args:
        mode   : 'micropython' (default) or 'python'
        ide    : Must be 'thonny'  — PolyPy is a Thonny-only paradigm
        target : 'rp2040' | 'generic' | 'esp32' | 'esp8266'
                 'stm32'  | 'avr'     | 'nrf52' | None

    Raises:
        RuntimeError if ide is not 'thonny'
        ValueError   if mode or target are unrecognised

    Example:
        import dytx
        dytx.init(mode='micropython', ide='thonny', target='rp2040')
    """
    global _mode, _ide, _target, _initialized, _runtime_log

    # ── IDE guard (hard requirement) ─────────────────────────────────────
    if ide not in _VALID_IDES:
        raise RuntimeError(
            "[DYTX] ERROR: PolyPy requires Thonny IDE. "
            "Do not run in VS Code, PyCharm, or IDLE."
        )

    # ── Mode validation ──────────────────────────────────────────────────
    if mode not in _VALID_MODES:
        raise ValueError(
            f"[DYTX] ERROR: Invalid mode '{mode}'. "
            f"Choose from: {_VALID_MODES}"
        )

    # ── Target validation (None is allowed = unspecified) ────────────────
    if target is not None and target not in _VALID_TARGETS:
        raise ValueError(
            f"[DYTX] ERROR: Unknown target '{target}'. "
            f"Valid targets: {_VALID_TARGETS}"
        )

    _mode        = mode
    _ide         = ide
    _target      = target
    _initialized = True

    entry = {"mode": mode, "ide": ide, "target": target}
    _runtime_log.append(entry)

    print(f"[DYTX] Runtime initialised | mode={mode} | ide={ide} | target={target}")
    print(f"[DYTX] Sub-modules ready   | machine | binary | firmware | web | asm")


# ── Guard helper (call at top of every sub-module public function) ───────────
def _check_init():
    """Raise if dytx.init() has not been called yet."""
    if not _initialized:
        raise RuntimeError(
            "[DYTX] ERROR: dytx.init() must be called before "
            "using any DYTX sub-module."
        )


# ── Runtime introspection ────────────────────────────────────────────────────
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


def get_runtime_info():
    """Return the current runtime configuration as a dict."""
    return {
        "version"     : __version__,
        "initialised" : _initialized,
        "mode"        : _mode,
        "ide"         : _ide,
        "target"      : _target,
        "init_calls"  : len(_runtime_log),
    }


def reset():
    """Reset the DYTX runtime state (useful in test harnesses)."""
    global _mode, _ide, _target, _initialized, _runtime_log
    _mode        = None
    _ide         = None
    _target      = None
    _initialized = False
    _runtime_log = []
    print("[DYTX] Runtime reset.")


# ── Sub-module imports ───────────────────────────────────────────────────────
# Lazy-loaded so this package survives on bare MicroPython boards that
# may not have all standard library modules available at import time.
from dytx import machine, binary, firmware, web, asm


# ── Global session report ────────────────────────────────────────────────────
def report_all():
    """
    Print a full session report across ALL DYTX sub-engines.
    Call at program end to summarise what was executed.
    """
    print("\n" + "=" * 52)
    print(" DYTX Full Session Report")
    print("=" * 52)
    machine.report()
    binary.report()
    firmware.report()
    web.report()
    asm.report()
    print("=" * 52 + "\n")


# ── Comprehensive test-coverage tags & use-case catalogue ───────────────────
def test_coverage():
    """
    Canonical tag reference for all DYTX comment-directive types.
    This function is never executed directly — it exists solely as a
    living documentation block and parser-coverage target.

    ── MACHINE directives (MCU register / instruction level) ────────────
    #machine: MOV R0, #1          <- load immediate into register
    #machine: LDR R1, [R0]        <- load register from memory
    #machine: STR R2, [SP, #4]    <- store register to stack
    #machine: BL  0x1234          <- branch-with-link (function call)
    #machine: BX  LR              <- return from function
    #machine: NOP                 <- timing / pipeline no-op
    #machine: CMP R0, #0          <- compare and set flags
    #machine: BEQ 0x0020          <- branch if equal
    #machine: PUSH {R4-R7, LR}    <- save context
    #machine: POP  {R4-R7, PC}    <- restore context
    #machine: ADD R0, R1, R2      <- arithmetic
    #machine: SUB R3, R3, #1      <- decrement
    #machine: MUL R0, R1, R0      <- multiply
    #machine: AND R0, R0, #0xFF   <- bitmask
    #machine: ORR R1, R1, #0x01   <- set bit
    #machine: EOR R2, R2, R2      <- XOR zero
    #machine: LSL R0, R0, #2      <- logical shift left
    #machine: LSR R1, R1, #1      <- logical shift right

    ── BINARY directives (raw byte / bit patterns) ───────────────────────
    #binary: 10101010 01010101        <- pattern A (alternating)
    #binary: 11110000 00001111        <- pattern B (nibble swap)
    #binary: 00000000 : NOP           <- labelled NOP byte
    #binary: 11111111 : BITMASK_ALL   <- all-ones mask
    #binary: 00000001 : BIT0          <- single bit set
    #binary: 10000000 : MSB           <- most-significant bit
    #binary: 01111111 : INT8_MAX      <- max signed 8-bit
    #binary: 11001100 10110011        <- checksum pattern

    ── ASM directives (ARM Thumb / ARMv6-M / ARMv7-M mnemonics) ─────────
    #asm: mov  r0, #42             <- load constant
    #asm: push {r4, lr}            <- save registers
    #asm: pop  {r4, pc}            <- restore & return
    #asm: ldr  r1, =0x20000000     <- load address
    #asm: str  r0, [r1]            <- store to address
    #asm: bl   my_function         <- call subroutine
    #asm: cmp  r0, #0              <- compare
    #asm: beq  .loop_end           <- conditional branch
    #asm: nop                      <- no-operation
    #asm: bkpt #0                  <- breakpoint (debug)
    #asm: svc  #0                  <- supervisor call
    #asm: wfi                      <- wait for interrupt (low power)
    #asm: wfe                      <- wait for event
    #asm: dsb                      <- data synchronisation barrier
    #asm: isb                      <- instruction sync barrier
    #asm: mrs  r0, MSP             <- read Main Stack Pointer
    #asm: msr  PSP, r0             <- write Process Stack Pointer

    ── HTML directives (MicroPython web server / WebREPL output) ─────────
    #html: <html lang='en'>
    #html: <head><meta charset='UTF-8'><title>PolyPy</title></head>
    #html: <body>
    #html: <h1>PolyPy DYTX Web Output</h1>
    #html: <div id='output'></div>
    #html: <button id='refresh' onclick='fetchData()'>Refresh</button>
    #html: <canvas id='chart' width='400' height='200'></canvas>
    #html: </body></html>

    ── JAVASCRIPT directives (browser-side / WebREPL UI logic) ──────────
    #javascript: const ws = new WebSocket('ws://192.168.4.1:8266/');
    #javascript: ws.onmessage = e => document.getElementById('output').innerText = e.data;
    #javascript: function fetchData() { ws.send('status'); }
    #javascript: console.log('[DYTX] web runtime active');
    #javascript: alert('PolyPy connected');
    #javascript: setInterval(fetchData, 1000);

    ── FIRMWARE directives (C/C++ blocks for cross-compilation) ─────────
    //firmware:c++
    // #include <Arduino.h>
    // void setup() { pinMode(13, OUTPUT); }
    // void loop()  { digitalWrite(13, HIGH); delay(500);
    //                digitalWrite(13, LOW);  delay(500); }

    //firmware:rp2040
    // #include "pico/stdlib.h"
    // int main() { gpio_init(25); gpio_set_dir(25, GPIO_OUT);
    //   while(1){ gpio_put(25,1); sleep_ms(500);
    //             gpio_put(25,0); sleep_ms(500); } }

    //firmware:esp32
    // #include <Arduino.h>
    // void setup() { Serial.begin(115200); }
    // void loop()  { Serial.println("PolyPy ESP32"); delay(1000); }

    //firmware:avr
    // #include <avr/io.h>
    // #include <util/delay.h>
    // int main(void) { DDRB |= (1<<PB5);
    //   while(1){ PORTB^=(1<<PB5); _delay_ms(500); } }

    //firmware:stm32
    // #include "stm32f4xx_hal.h"
    // HAL_GPIO_TogglePin(GPIOA, GPIO_PIN_5);
    // HAL_Delay(500);

    //firmware:nrf52
    // #include <zephyr.h>
    // #include <drivers/gpio.h>
    // // Toggle LED0 every 500 ms via Zephyr RTOS
    """
    pass


# ── Package metadata ─────────────────────────────────────────────────────────
__version__ = "2.0.0"
__author__  = "PolyPy / chuckyLeeVIII"
__license__ = "MIT"
__all__ = [
    # Core lifecycle
    "init", "reset", "status", "get_runtime_info", "report_all",
    # Sub-modules
    "machine", "binary", "firmware", "web", "asm",
    # Coverage / docs
    "test_coverage",
    # Internal guard (advanced use)
    "_check_init",
]
