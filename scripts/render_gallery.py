"""Gera as imagens de apresentação do modelo em `images/modelo3d-*.png`.

Vistas: superior, traseira, lateral, isométrica e com efeito de luz (hero shot com
rim lights, faróis acesos e bloom no compositor).

Uso:
    blender --background car-lotus-elise-111s.blend --python scripts/render_gallery.py

O script não salva o .blend: o rig neutro é restaurado ao final, de modo que os
renders de verificação (`render_views.py`) continuam idênticos.
"""

from __future__ import annotations

import os
import time

import bpy
from mathutils import Vector

GALLERY = [
    ("CAM_Superior", "modelo3d-superior.png"),
    ("CAM_Traseira", "modelo3d-traseira.png"),
    ("CAM_Lateral", "modelo3d-lateral.png"),
    ("CAM_Isometrica", "modelo3d-isometrica.png"),
]

HERO = ("CAM_Hero", "modelo3d-efeitoluz.png")

# rig dramático do hero shot: (nome, tipo, local, tamanho, energia)
HERO_LIGHTS = [
    ("LGT_Hero_Rim_L", "AREA", (0.20, 5.20, 1.35), (0.16, 5.40), 2600.0),
    ("LGT_Hero_Rim_R", "AREA", (0.20, -5.20, 1.35), (0.16, 5.40), 2600.0),
    ("LGT_Hero_Key", "AREA", (3.40, 2.10, 3.60), (2.20, 2.20), 1100.0),
    ("LGT_Hero_Top", "AREA", (-0.40, 0.20, 4.60), (3.00, 2.40), 700.0),
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
OUT_DIR = os.path.join(BASE, "images")

# ---------------------------------------------------------------------------
# Compositor: bloom (o EEVEE do Blender 5.x não tem mais use_bloom)
# ---------------------------------------------------------------------------


def build_bloom() -> None:
    scene = bpy.context.scene
    ng = bpy.data.node_groups.get("NG_Bloom_Hero")
    if ng is None:
        ng = bpy.data.node_groups.new("NG_Bloom_Hero", "CompositorNodeTree")
    ng.nodes.clear()
    ng.interface.clear()
    ng.interface.new_socket("Image", in_out="OUTPUT", socket_type="NodeSocketColor")

    rl = ng.nodes.new("CompositorNodeRLayers")
    rl.location = (-420, 0)
    glare = ng.nodes.new("CompositorNodeGlare")
    glare.location = (-160, 0)
    out = ng.nodes.new("NodeGroupOutput")
    out.location = (180, 0)

    for tipo in ("BLOOM", "FOG_GLOW", "GHOSTS"):
        try:
            glare.inputs["Type"].default_value = tipo
            break
        except Exception:
            continue

    def set_input(nome, valor):
        if nome in glare.inputs:
            try:
                glare.inputs[nome].default_value = valor
            except Exception:
                pass

    set_input("Quality", "HIGH")
    set_input("Threshold", 0.85)
    set_input("Strength", 0.055)
    set_input("Size", 0.55)
    set_input("Saturation", 0.9)
    set_input("Clamp", 0.0)

    ng.links.new(rl.outputs["Image"], glare.inputs["Image"])
    ng.links.new(glare.outputs["Image"], out.inputs["Image"])
    scene.compositing_node_group = ng


# ---------------------------------------------------------------------------
# Rig do hero shot
# ---------------------------------------------------------------------------


def _aim(obj, target) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def setup_hero() -> dict:
    """Iluminação dramática + faróis acesos. Retorna o estado para restauração."""
    scene = bpy.context.scene
    estado = {"world": None, "lights": [], "emissao": [], "compositor": scene.compositing_node_group}

    world = scene.world
    if world and world.use_nodes:
        for node in world.node_tree.nodes:
            if node.bl_idname == "ShaderNodeBackground":
                estado["world"] = (
                    node,
                    tuple(node.inputs["Color"].default_value),
                    node.inputs["Strength"].default_value,
                )
                node.inputs["Color"].default_value = (0.010, 0.012, 0.018, 1.0)
                node.inputs["Strength"].default_value = 0.6

    for obj in bpy.data.objects:
        if obj.type == "LIGHT":
            estado["lights"].append((obj, obj.hide_render))
            obj.hide_render = True

    for nome, tipo, loc, size, energia in HERO_LIGHTS:
        data = bpy.data.lights.new(name=nome, type=tipo)
        data.shape = "RECTANGLE"
        data.size = size[0]
        data.size_y = size[1]
        data.energy = energia
        data.color = (0.92, 0.95, 1.0)
        obj = bpy.data.objects.new(nome, data)
        obj.location = loc
        scene.collection.objects.link(obj)
        _aim(obj, (0.0, 0.0, 0.55))

    # faróis e lanternas acesos
    for mat_name, strength, cor in (
        ("MAT_Headlamp_Lens", 8.0, "#E8F0FF"),
            ("MAT_Lens_Red", 4.0, "#FF2A22"),
        ("MAT_Lens_Amber", 3.0, "#FFA030"),
    ):
        mat = bpy.data.materials.get(mat_name)
        if mat is None or not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.bl_idname == "ShaderNodeBsdfPrincipled":
                prev = node.inputs["Emission Strength"].default_value
                estado["emissao"].append((node, prev))
                node.inputs["Emission Strength"].default_value = strength
                r, g, b = (
                    int(cor[1:3], 16) / 255.0,
                    int(cor[3:5], 16) / 255.0,
                    int(cor[5:7], 16) / 255.0,
                )
                node.inputs["Emission Color"].default_value = (r, g, b, 1.0)

    build_bloom()
    return estado


def restore(estado: dict) -> None:
    scene = bpy.context.scene
    if estado["world"]:
        node, cor, forca = estado["world"]
        node.inputs["Color"].default_value = cor
        node.inputs["Strength"].default_value = forca
    for obj, hide in estado["lights"]:
        obj.hide_render = hide
    for node, valor in estado["emissao"]:
        node.inputs["Emission Strength"].default_value = valor
    for nome, *_ in HERO_LIGHTS:
        obj = bpy.data.objects.get(nome)
        if obj:
            bpy.data.objects.remove(obj, do_unlink=True)
    scene.compositing_node_group = estado["compositor"]


# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------


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
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1000
    for attr, value in (("taa_render_samples", 96), ("use_raytracing", True)):
        if hasattr(scene.eevee, attr):
            try:
                setattr(scene.eevee, attr, value)
            except Exception:
                pass

    print(f"GALERIA → {OUT_DIR}")
    total = 0.0
    for cam, filename in GALLERY:
        dt = render(cam, filename)
        total += dt
        print(f"  {filename:26s} {dt:5.1f}s")

    estado = setup_hero()
    try:
        dt = render(*HERO)
        total += dt
        print(f"  {HERO[1]:26s} {dt:5.1f}s  (efeito de luz)")
    finally:
        restore(estado)

    print(f"Tempo total: {total:.1f}s")


main()
