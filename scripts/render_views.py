"""Renderiza as vistas de verificação do Lotus Elise 111S.

Uso:
    blender --background car-lotus-elise-111s.blend --python scripts/render_views.py

Gera PNGs em docs/renders/ para comparação visual com images/*.jpeg.
"""

from __future__ import annotations

import os
import sys
import time

import bpy

VIEWS = [
    ("CAM_Frontal", "01_frontal.png", "frontal.jpeg"),
    ("CAM_Superior", "02_superior.png", "superior_branco.jpeg"),
    ("CAM_Lateral", "03_lateral.png", "lateral.jpeg"),
    ("CAM_Traseira", "04_traseira.png", "traseira1.jpeg"),
    ("CAM_TresQuartos", "05_three_quarter.png", "car.jpeg"),
    ("CAM_TresQuartos_Tr", "06_three_quarter_rear.png", "traseira2.jpeg"),
    ("CAM_WheelDetail", "07_wheel_closeup.png", None),
]

CLAY_VIEWS = [
    ("CAM_Lateral", "10_clay_lateral.png"),
    ("CAM_TresQuartos", "11_clay_three_quarter.png"),
]


def _find_base() -> str:
    """Raiz do projeto: exige `images/` e o arquivo `.blend` do modelo."""
    nodes = []
    if bpy.data.filepath:
        nodes.append(os.path.dirname(bpy.data.filepath))
    try:
        nodes.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    nodes.append(os.getcwd())
    for node in nodes:
        start = node
        for _ in range(5):
            if os.path.isdir(os.path.join(start, "images")) and os.path.isfile(
                os.path.join(start, "car-lotus-elise-111s.blend")
            ):
                return start
            parent = os.path.dirname(start)
            if parent == start:
                break
            start = parent
    return nodes[0]


BASE = _find_base()
OUT_DIR = os.path.join(BASE, "docs", "renders")
CLAY = os.environ.get("LOTUS_CLAY", "1") == "1"


def clay_material():
    mat = bpy.data.materials.get("MAT_Clay_Check")
    if mat:
        return mat
    mat = bpy.data.materials.new("MAT_Clay_Check")
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.inputs["Base Color"].default_value = (0.62, 0.62, 0.62, 1.0)
    bsdf.inputs["Roughness"].default_value = 0.34
    bsdf.inputs["Metallic"].default_value = 0.0
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat


def render(camera_name: str, filename: str) -> float:
    scene = bpy.context.scene
    cam = bpy.data.objects.get(camera_name)
    if cam is None:
        print(f"[aviso] câmera ausente: {camera_name}")
        return 0.0
    scene.camera = cam
    scene.render.filepath = os.path.join(OUT_DIR, filename)
    t0 = time.time()
    bpy.ops.render.render(write_still=True)
    return time.time() - t0


def main() -> None:
    os.makedirs(OUT_DIR, exist_ok=True)
    scene = bpy.context.scene
    for attr, value in (("taa_render_samples", 64), ("use_raytracing", True)):
        if hasattr(scene.eevee, attr):
            try:
                setattr(scene.eevee, attr, value)
            except Exception:
                pass

    total = 0.0
    print(f"BASE={BASE}")
    print(f"OUT_DIR={OUT_DIR}")
    print("RENDERS DE VERIFICAÇÃO")
    for cam, filename, ref in VIEWS:
        dt = render(cam, filename)
        total += dt
        print(f"  {filename:24s} {dt:5.1f}s  ref={ref}")

    if CLAY:
        vl = scene.view_layers[0]
        previous = vl.material_override
        vl.material_override = clay_material()
        try:
            for cam, filename in CLAY_VIEWS:
                dt = render(cam, filename)
                total += dt
                print(f"  {filename:24s} {dt:5.1f}s  (clay)")
        finally:
            vl.material_override = previous

    print(f"Tempo total de render: {total:.1f}s")


main()
