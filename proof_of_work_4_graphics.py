# PolyPy Graphics Engine — Full Proof of Work
# PolyPi Pure v1.0 — Thonny IDE / MicroPython OR standard Python (fullstack sim)
# In pure mode, all rendering calls are printed as a text simulation

import sys
import math
import dytx

# --- Detect environment automatically ---
_IDE = "thonny" if "thonny" in sys.executable.lower() else "pure"
_MODE = "micropython" if _IDE == "thonny" else "python"

# Initialize DYTX runtime
dytx.init(mode=_MODE, ide=_IDE, target="generic" if _IDE == "thonny" else None)

# --- DYTX sub-module stubs for pure Python mode ---
if _IDE == "thonny":
    try:
        import dytx.machine as dxm
        import dytx.binary as dxb
        import dytx.firmware as dxf
        import dytx.asm as dxa
    except ImportError:
        dxm = dxb = dxf = dxa = None
else:
    class _Stub:
        def __getattr__(self, name):
            return lambda *a, **k: print(f"  [sim] {name}({', '.join(str(x) for x in a)})")
    dxm = dxb = dxf = dxa = _Stub()


# --- Load 3D model via Python ---
def load_3d_model(filename: str) -> dict:
    """Load a 3D model (simulated in pure mode)."""
    print(f"[PolyPy] Loading model: {filename}")
    return {"file": filename, "verts": 1024, "polys": 512}


class Camera:
    """Simple flythrough camera with DYTX machine-code register comments."""

    def __init__(self):
        self.x, self.y, self.z = 0.0, 0.0, -5.0
        # #machine: MOV R5, #0 ; camera X register
        # #machine: MOV R6, #0 ; camera Y register
        # #machine: MOV R7, #5 ; camera Z register (negative = behind)
        dxm.flush()

    def update(self):
        self.z += 0.01
        # #asm: FADD S7, S7, #0.01 ; increment Z in float register
        dxa.exec("FADD S7, S7, #0.01")


class Renderer:
    """Software rasteriser stub with DYTX firmware directives."""

    def __init__(self, width: int = 320, height: int = 240):
        self.width = width
        self.height = height
        self.frame = 0
        # #firmware: INIT_FRAMEBUFFER 320 240
        dxf.directive("INIT_FRAMEBUFFER", width, height)

    def clear(self):
        # #binary: 11001100 00000000 ; clear framebuffer opcode
        dxb.exec_comment("clear framebuffer")
        if _IDE == "pure":
            print(f"  [sim] frame {self.frame}: framebuffer cleared")

    def draw_model(self, model: dict, camera: Camera):
        # Perspective projection (simplified)
        fov = math.pi / 3
        aspect = self.width / self.height
        near, far = 0.1, 100.0
        f = 1.0 / math.tan(fov / 2)
        # #asm: FDIV S8, S9, S10 ; perspective divide
        dxa.exec(f"FDIV S8, S9, S10  ; fov={fov:.3f} aspect={aspect:.3f}")
        if _IDE == "pure":
            print(f"  [sim] drew {model['polys']} polys | cam_z={camera.z:.3f} | near={near} far={far}")

    def present(self):
        # #firmware: SWAP_BUFFERS
        dxf.directive("SWAP_BUFFERS")
        self.frame += 1
        if _IDE == "pure":
            print(f"  [sim] frame {self.frame} presented")


# --- Main render loop ---
model = load_3d_model("cube.obj")
cam = Camera()
renderer = Renderer(width=320, height=240)

print("[PolyPi Pure] Starting render loop (5 frames)...")
for _ in range(5):
    renderer.clear()
    cam.update()
    renderer.draw_model(model, cam)
    renderer.present()

print(f"[PolyPi Pure] Proof of Work #4 complete. {renderer.frame} frames rendered.")
