"""Build do Lotus Elise 111S (Series 1) — constrói a cena completa no Blender.

Uso direto:
    blender --background car-lotus-elise-111s.blend --python scripts/build_lotus_elise_111s.py

Uso via MCP:
    exec(open("scripts/build_lotus_elise_111s.py").read())

O script é idempotente: limpa a cena antes de reconstruir.
"""

from __future__ import annotations

import math
import os
import sys
import time

import bpy
from mathutils import Euler, Matrix, Vector


# ---------------------------------------------------------------------------
# Localização do pacote de helpers (funciona com __file__ ou exec via MCP)
# ---------------------------------------------------------------------------

def _find_base() -> str:
    """Raiz do projeto: exige `scripts/lotus_common.py` e `images/`."""
    candidates = []
    if bpy.data.filepath:
        candidates.append(os.path.dirname(bpy.data.filepath))
    try:
        candidates.append(os.path.dirname(os.path.abspath(__file__)))
    except NameError:
        pass
    candidates.append(os.getcwd())
    for start in candidates:
        node = start
        for _ in range(5):
            if os.path.isfile(os.path.join(node, "scripts", "lotus_common.py")) and os.path.isdir(
                os.path.join(node, "images")
            ):
                return node
            parent = os.path.dirname(node)
            if parent == node:
                break
            node = parent
    return candidates[0]


BASE = _find_base()
if os.path.join(BASE, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(BASE, "scripts"))

import importlib  # noqa: E402

import lotus_common as lc  # noqa: E402  (path ajustado acima)

# Em sessões longas do Blender (MCP) o módulo pode estar em cache: recarregar
# garante que as edições em lotus_common.py tenham efeito.
importlib.reload(lc)

SAVE_BLEND = True
BLEND_PATH = os.path.join(BASE, "car-lotus-elise-111s.blend")
REPORT_PATH = os.path.join(BASE, "docs", "renders", "mesh_report.txt")

# ---------------------------------------------------------------------------
# Dimensões de referência (Lotus Elise Series 1 111S)
# ---------------------------------------------------------------------------

LENGTH = 3.726
WIDTH = 1.718
HEIGHT = 1.117
WHEELBASE = 2.300
TRACK_FRONT = 1.419
TRACK_REAR = 1.454

AXLE_F_X = +WHEELBASE / 2.0     # +1.150
AXLE_R_X = -WHEELBASE / 2.0     # -1.150

TIRE_F_R, RIM_F_R, TIRE_F_HW = 0.292, 0.1905, 0.0925   # 185/55R15
TIRE_R_R, RIM_R_R, TIRE_R_HW = 0.306, 0.2032, 0.1025   # 205/50R16

ARCH_F = (AXLE_F_X, TIRE_F_R, 0.335)
ARCH_R = (AXLE_R_X, TIRE_R_R, 0.350)

BELTLINE = 0.700            # base da cabine (cintura visível ~0,71)
ROOF_TOP = 1.117

BUILT: list[str] = []


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


def base_bottom(x: float) -> float:
    """Fundo da carroceria fora dos vãos de roda."""
    if x >= 1.525:
        return lerp(0.130, 0.190, (x - 1.525) / (1.863 - 1.525))
    if x <= -1.545:
        return lerp(0.205, 0.320, (-x - 1.545) / (1.863 - 1.545))
    return 0.128


def station_bottom(x: float) -> float:
    return lc.arch_bottom(x, base_bottom(x), [ARCH_F, ARCH_R])


# ---------------------------------------------------------------------------
# Materiais
# ---------------------------------------------------------------------------


def build_materials() -> dict:
    mats = {}

    # --- Pintura azul metálica multicamada --------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Blue_Metallic")
    base_blue = lc.rgba("#0C1A96")
    deep_blue = lc.rgba("#050A3C")

    layer = nt.nodes.new("ShaderNodeLayerWeight")
    layer.location = (-1100, 120)
    layer.inputs["Blend"].default_value = 0.45
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.location = (-900, 120)
    ramp.color_ramp.elements[0].position = 0.30
    ramp.color_ramp.elements[1].position = 0.85
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.location = (-650, 160)
    mix.inputs["A"].default_value = base_blue
    mix.inputs["B"].default_value = deep_blue
    nt.links.new(layer.outputs["Facing"], ramp.inputs["Fac"])
    nt.links.new(ramp.outputs["Color"], mix.inputs["Factor"])
    nt.links.new(mix.outputs["Result"], bsdf.inputs["Base Color"])

    flake = nt.nodes.new("ShaderNodeTexNoise")
    flake.location = (-1100, -260)
    flake.inputs["Scale"].default_value = 380.0
    flake.inputs["Detail"].default_value = 2.0
    flake.inputs["Roughness"].default_value = 0.5
    flake_ramp = nt.nodes.new("ShaderNodeValToRGB")
    flake_ramp.location = (-880, -260)
    flake_ramp.color_ramp.elements[0].position = 0.38
    flake_ramp.color_ramp.elements[1].position = 0.62
    nt.links.new(flake.outputs["Fac"], flake_ramp.inputs["Fac"])

    met_mix = nt.nodes.new("ShaderNodeMapRange")
    met_mix.location = (-620, -420)
    met_mix.inputs["From Min"].default_value = 0.0
    met_mix.inputs["From Max"].default_value = 1.0
    met_mix.inputs["To Min"].default_value = 0.22
    met_mix.inputs["To Max"].default_value = 0.48
    nt.links.new(flake_ramp.outputs["Color"], met_mix.inputs["Value"])
    nt.links.new(met_mix.outputs["Result"], bsdf.inputs["Metallic"])

    rough_mix = nt.nodes.new("ShaderNodeMapRange")
    rough_mix.location = (-620, -640)
    rough_mix.inputs["To Min"].default_value = 0.16
    rough_mix.inputs["To Max"].default_value = 0.32
    nt.links.new(flake_ramp.outputs["Color"], rough_mix.inputs["Value"])
    nt.links.new(rough_mix.outputs["Result"], bsdf.inputs["Roughness"])

    flake_bump = nt.nodes.new("ShaderNodeBump")
    flake_bump.location = (-360, -300)
    flake_bump.inputs["Strength"].default_value = 0.03
    nt.links.new(flake.outputs["Fac"], flake_bump.inputs["Height"])
    nt.links.new(flake_bump.outputs["Normal"], bsdf.inputs["Normal"])

    bsdf.inputs["Coat Weight"].default_value = 0.65
    bsdf.inputs["Coat Roughness"].default_value = 0.02
    bsdf.inputs["Coat IOR"].default_value = 1.55
    bsdf.inputs["IOR"].default_value = 1.50
    bsdf.inputs["Specular IOR Level"].default_value = 0.55
    mats["blue"] = mat

    # --- Vidro / policarbonato -------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Glass_Polycarbonate")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#8FA6B4")
    bsdf.inputs["Roughness"].default_value = 0.02
    bsdf.inputs["IOR"].default_value = 1.58
    bsdf.inputs["Transmission Weight"].default_value = 1.0
    mat.use_backface_culling = False
    mats["glass"] = mat

    # --- Borracha do pneu -------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Rubber_Tire")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#141416")
    bsdf.inputs["Roughness"].default_value = 0.85
    bsdf.inputs["Metallic"].default_value = 0.0
    lc.noise_normal(nt, bsdf, scale=90.0, strength=0.30)
    mats["rubber"] = mat

    # --- Alumínio escovado ------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Aluminum_Brushed")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#B4B8BC")
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.32
    bsdf.inputs["Anisotropic"].default_value = 0.7
    lc.noise_normal(nt, bsdf, scale=14.0, strength=0.12)
    mats["aluminum"] = mat

    # --- Plástico preto texturizado --------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Black_Trim")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#0E0E10")
    bsdf.inputs["Roughness"].default_value = 0.72
    lc.noise_normal(nt, bsdf, scale=55.0, strength=0.10)
    mats["black"] = mat

    # --- Grade / mesh metálico -------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Grille_Mesh")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#17191B")
    bsdf.inputs["Metallic"].default_value = 0.35
    bsdf.inputs["Roughness"].default_value = 0.62
    mats["mesh"] = mat

    # --- Cromado ----------------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Chrome_Trim")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#D6DADE")
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.08
    mats["chrome"] = mat

    # --- Lente vermelha / âmbar ------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Lens_Red")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#7A0A12")
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Transmission Weight"].default_value = 0.85
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Emission Color"].default_value = lc.rgba("#FF1A22")
    bsdf.inputs["Emission Strength"].default_value = 0.35
    mats["lens_red"] = mat

    mat, nt, bsdf = lc.new_material("MAT_Lens_Amber")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#B85A05")
    bsdf.inputs["Roughness"].default_value = 0.05
    bsdf.inputs["Transmission Weight"].default_value = 0.80
    bsdf.inputs["IOR"].default_value = 1.52
    bsdf.inputs["Emission Color"].default_value = lc.rgba("#FF9A20")
    bsdf.inputs["Emission Strength"].default_value = 0.20
    mats["lens_amber"] = mat

    # --- Lente do farol ---------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Headlamp_Lens")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#DCE6EA")
    bsdf.inputs["Roughness"].default_value = 0.03
    bsdf.inputs["Transmission Weight"].default_value = 0.95
    bsdf.inputs["IOR"].default_value = 1.52
    mats["headlamp_lens"] = mat

    # --- Interior ---------------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Interior_Fabric")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#0E0E11")
    bsdf.inputs["Roughness"].default_value = 0.90
    lc.noise_normal(nt, bsdf, scale=160.0, strength=0.20)
    mats["interior"] = mat

    # --- Emblema ----------------------------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Badge_Chrome")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#C8CC50")
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.22
    mats["badge"] = mat

    # --- Refletor / fundo de farol ---------------------------------------
    mat, nt, bsdf = lc.new_material("MAT_Reflector_Chrome")
    bsdf.inputs["Base Color"].default_value = lc.rgba("#EEF1F4")
    bsdf.inputs["Metallic"].default_value = 1.0
    bsdf.inputs["Roughness"].default_value = 0.05
    mats["reflector"] = mat

    return mats


# ---------------------------------------------------------------------------
# Carroceria
# ---------------------------------------------------------------------------

# (x, w, wt, zs, zte, zt)
# (x, w, wt, zs, zte, zt)
# (x, w, wt, zs, zte, zt)
BODY_STATIONS = [
    (1.863, 0.625, 0.500, 0.470, 0.560, 0.592),
    (1.848, 0.712, 0.580, 0.490, 0.578, 0.610),
    (1.806, 0.775, 0.630, 0.512, 0.600, 0.632),
    (1.740, 0.792, 0.646, 0.530, 0.618, 0.650),
    (1.680, 0.802, 0.656, 0.545, 0.632, 0.664),
    (1.610, 0.806, 0.660, 0.558, 0.646, 0.678),
    (1.545, 0.808, 0.660, 0.570, 0.658, 0.690),
    (1.530, 0.808, 0.660, 0.572, 0.660, 0.692),
    (1.520, 0.808, 0.660, 0.574, 0.662, 0.694),
    (1.470, 0.810, 0.660, 0.590, 0.676, 0.708),
    (1.380, 0.814, 0.660, 0.618, 0.700, 0.730),
    (1.280, 0.818, 0.660, 0.648, 0.720, 0.748),
    (1.200, 0.820, 0.660, 0.668, 0.735, 0.760),
    (1.150, 0.820, 0.660, 0.680, 0.742, 0.766),
    (1.100, 0.818, 0.660, 0.676, 0.738, 0.762),
    (1.020, 0.812, 0.655, 0.656, 0.726, 0.754),
    (0.930, 0.806, 0.650, 0.634, 0.716, 0.750),
    (0.860, 0.800, 0.642, 0.616, 0.712, 0.752),
    (0.790, 0.795, 0.636, 0.600, 0.706, 0.748),
    (0.775, 0.794, 0.634, 0.596, 0.704, 0.746),
    (0.700, 0.792, 0.630, 0.592, 0.700, 0.742),
    (0.550, 0.790, 0.624, 0.598, 0.700, 0.740),
    (0.380, 0.790, 0.622, 0.610, 0.702, 0.740),
    (0.200, 0.793, 0.624, 0.626, 0.706, 0.744),
    (0.020, 0.797, 0.626, 0.640, 0.712, 0.748),
    (-0.160, 0.803, 0.630, 0.652, 0.720, 0.756),
    (-0.340, 0.815, 0.638, 0.670, 0.762, 0.816),
    (-0.520, 0.832, 0.648, 0.692, 0.812, 0.872),
    (-0.680, 0.848, 0.654, 0.710, 0.856, 0.900),
    (-0.755, 0.852, 0.656, 0.716, 0.866, 0.906),
    (-0.765, 0.852, 0.656, 0.716, 0.866, 0.906),
    (-0.850, 0.855, 0.656, 0.720, 0.870, 0.908),
    (-0.950, 0.859, 0.657, 0.726, 0.872, 0.910),
    (-1.050, 0.859, 0.657, 0.734, 0.874, 0.911),
    (-1.150, 0.859, 0.657, 0.740, 0.874, 0.911),
    (-1.250, 0.858, 0.656, 0.740, 0.872, 0.909),
    (-1.350, 0.855, 0.652, 0.736, 0.868, 0.905),
    (-1.450, 0.850, 0.646, 0.726, 0.860, 0.897),
    (-1.545, 0.843, 0.638, 0.714, 0.850, 0.886),
    (-1.558, 0.841, 0.636, 0.710, 0.846, 0.882),
    (-1.640, 0.836, 0.632, 0.700, 0.836, 0.870),
    (-1.720, 0.822, 0.618, 0.686, 0.818, 0.848),
    (-1.790, 0.802, 0.600, 0.660, 0.790, 0.814),
    (-1.838, 0.775, 0.570, 0.634, 0.752, 0.778),
    (-1.863, 0.735, 0.520, 0.606, 0.706, 0.732),
]


def build_body(mats):
    stations = []
    for x, w, wt, zs, zte, zt in BODY_STATIONS:
        zb = station_bottom(x)
        stations.append((x, lc.body_ring(w, wt, zb, max(zs, zb + 0.02), zte, zt)))
    obj = lc.build_loft(
        "GEO_Body_Hull",
        stations,
        materials=[mats["blue"]],
        tag_info=dict(cat="GEO", part="body", swap="paint_primary"),
        subsurf=(1, 3),
    )
    BUILT.append(obj.name)
    _scoop_dent(obj)
    _headlamp_recess(obj)
    return obj


def _scoop_dent(obj) -> None:
    """Abertura real das entradas de ar laterais (sem boolean, sem normal map)."""
    me = obj.data
    cx, cz = -0.235, 0.520
    rx, rz = 0.215, 0.165
    depth = 0.062
    for v in me.vertices:
        if abs(v.co.y) < 0.35:
            continue
        nx = (v.co.x - cx) / rx
        nz = (v.co.z - cz) / rz
        r = math.sqrt(nx * nx + nz * nz)
        if r >= 1.0:
            continue
        fade = 1.0 if r <= 0.62 else 1.0 - ((r - 0.62) / 0.38) ** 1.5
        sign = 1.0 if v.co.y > 0 else -1.0
        v.co.y -= sign * depth * fade


def _falloff(value: float, inner: float, outer: float) -> float:
    """1 no interior, 0 no exterior, com transição suave."""
    if value <= inner:
        return 1.0
    if value >= outer:
        return 0.0
    t = (value - inner) / (outer - inner)
    return 1.0 - t * t * (3.0 - 2.0 * t)


def _headlamp_recess(obj) -> None:
    """Escava o alojamento dos faróis no clamshell dianteiro."""
    for v in obj.data.vertices:
        if v.co.x < 1.44 or abs(v.co.z - 0.598) > 0.16:
            continue
        for cy in (0.470, -0.470):
            nx = (v.co.x - 1.646) / 0.190
            ny = (abs(v.co.y) - abs(cy)) / 0.150
            r = math.sqrt(nx * nx + ny * ny)
            if r >= 1.0:
                continue
            v.co.z -= 0.030 * _falloff(r, 0.50, 1.0)


def build_cabin(mats):
    zc = BELTLINE
    # (x, wb, wt, altura acima da cintura)
    stations_def = [
        (0.790, 0.560, 0.500, 0.014),
        (0.720, 0.530, 0.480, 0.076),
        (0.630, 0.492, 0.440, 0.164),
        (0.520, 0.468, 0.408, 0.262),
        (0.420, 0.458, 0.398, 0.345),
        (0.330, 0.452, 0.392, 0.417),
        (0.180, 0.452, 0.392, 0.413),
        (0.020, 0.452, 0.392, 0.407),
        (-0.120, 0.454, 0.390, 0.390),
        (-0.230, 0.458, 0.386, 0.347),
        (-0.330, 0.462, 0.378, 0.288),
        (-0.430, 0.467, 0.366, 0.217),
        (-0.520, 0.474, 0.350, 0.140),
        (-0.590, 0.480, 0.326, 0.064),
        (-0.625, 0.482, 0.306, 0.017),
    ]
    stations = [(x, lc.cabin_ring(wb, wt, zc, h)) for x, wb, wt, h in stations_def]

    # zonas: 0..4 para-brisa, 5..7 teto, 8..10 janela traseira, 11+ buttress
    windshield = set(range(0, 5))
    roof = set(range(5, 8))
    rear = {8, 9, 10}
    side_glass = {5, 6, 7, 8}

    top_segments = {3, 4, 5, 6}
    side_segments = {0, 1, 7, 8}

    mat_grid = []
    for band in range(len(stations) - 1):
        row = []
        for seg in range(10):
            if band in windshield and seg in top_segments:
                row.append(1)
            elif band in rear and seg in top_segments:
                row.append(1)
            elif band in side_glass and seg in side_segments:
                row.append(1)
            else:
                row.append(0)
        mat_grid.append(row)

    obj = lc.build_loft(
        "GEO_Cabin_Hull",
        stations,
        mat_grid=mat_grid,
        materials=[mats["blue"], mats["glass"]],
        cap_mats=(0, 0),
        tag_info=dict(cat="GEO", part="cabin", swap="paint_primary"),
        subsurf=(1, 3),
    )
    BUILT.append(obj.name)
    return obj


# ---------------------------------------------------------------------------
# Rodas
# ---------------------------------------------------------------------------


def build_wheel(name: str, x: float, y_signed: float, r_tire: float, r_rim: float,
                hw: float, mats, side: int):
    yc = y_signed
    zc = r_tire
    r_b = r_rim + 0.004

    def ax(offset: float) -> float:
        return yc + side * offset

    # --- pneu (revolução de um perfil fechado) ---------------------------
    r_inner = r_rim - 0.018
    profile = [
        (r_b, hw),
        (r_b + 0.30 * (r_tire - r_b), hw),
        (r_b + 0.66 * (r_tire - r_b), hw * 0.99),
        (r_tire - 0.012, hw * 0.94),
        (r_tire, hw * 0.82),
        (r_tire, hw * 0.45),
        (r_tire, 0.0),
        (r_tire, -hw * 0.45),
        (r_tire, -hw * 0.82),
        (r_tire - 0.012, -hw * 0.94),
        (r_b + 0.66 * (r_tire - r_b), -hw * 0.99),
        (r_b + 0.30 * (r_tire - r_b), -hw),
        (r_b, -hw),
        (r_inner, -hw * 0.86),
        (r_inner, hw * 0.86),
    ]
    tire = lc.revolve(
        f"{name}_Tire",
        profile,
        segments=48,
        center=(x, yc, zc),
        axis=(0, side, 0),
        material=mats["rubber"],
        tag_info=dict(cat="GEO", part="tire", swap="rubber"),
        subsurf=(1, 2),
    )
    BUILT.append(tire.name)

    # --- aro (barrel, casca fechada) -------------------------------------
    barrel_profile = [
        (r_rim, hw * 0.88),
        (r_rim, -hw * 0.88),
        (r_rim - 0.034, -hw * 0.88),
        (r_rim - 0.034, hw * 0.88),
    ]
    barrel = lc.revolve(
        f"{name}_Rim_Barrel",
        barrel_profile,
        segments=44,
        center=(x, yc, zc),
        axis=(0, side, 0),
        material=mats["aluminum"],
        tag_info=dict(cat="GEO", part="rim_barrel", swap="aluminum_brushed"),
    )
    BUILT.append(barrel.name)

    # --- prato escavado atrás dos raios ---------------------------------
    dish_profile = [
        (r_rim - 0.010, hw * 0.86),
        (0.062, hw * 0.06),
        (0.045, hw * 0.03),
        (r_rim - 0.030, hw * 0.86),
    ]
    dish = lc.revolve(
        f"{name}_Rim_Dish",
        dish_profile,
        segments=44,
        center=(x, yc, zc),
        axis=(0, side, 0),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="rim_dish", swap="black_trim"),
        subsurf=(1, 1),
    )
    BUILT.append(dish.name)

    # --- 6 raios ---------------------------------------------------------
    for k in range(6):
        ang = math.radians(60.0 * k + 15.0)
        dx, dz = math.cos(ang), math.sin(ang)
        spoke = lc.box(
            f"{name}_Spoke_{k + 1}",
            size=(0.150, 0.046, 0.030),
            location=(x + dx * 0.118, ax(hw * 0.70), zc + dz * 0.118),
            rotation=(0.0, -ang, 0.0),
            material=mats["aluminum"],
            tag_info=dict(cat="GEO", part="wheel_spoke", swap="aluminum_brushed"),
            bevel=0.006,
            subsurf=(1, 2),
        )
        BUILT.append(spoke.name)

    hub = lc.cylinder(
        f"{name}_Hub",
        radius=0.052,
        depth=0.055,
        segments=24,
        location=(x, ax(hw * 0.70), zc),
        rotation=(math.pi / 2, 0, 0),
        material=mats["aluminum"],
        tag_info=dict(cat="GEO", part="wheel_hub", swap="aluminum_brushed"),
        bevel=0.006,
        subsurf=(1, 2),
    )
    BUILT.append(hub.name)

    cap = lc.cylinder(
        f"{name}_CenterCap",
        radius=0.030,
        depth=0.020,
        segments=20,
        location=(x, ax(hw * 0.80), zc),
        rotation=(math.pi / 2, 0, 0),
        material=mats["chrome"],
        tag_info=dict(cat="GEO", part="wheel_centercap", swap="chrome"),
        bevel=0.004,
        subsurf=(1, 2),
    )
    BUILT.append(cap.name)

    disc = lc.cylinder(
        f"{name}_BrakeDisc",
        radius=r_rim * 0.82,
        depth=0.020,
        segments=32,
        location=(x, ax(0.0), zc),
        rotation=(math.pi / 2, 0, 0),
        material=mats["aluminum"],
        tag_info=dict(cat="GEO", part="brake_disc", swap="aluminum_brushed"),
        caps=True,
    )
    BUILT.append(disc.name)

    caliper = lc.box(
        f"{name}_BrakeCaliper",
        size=(0.090, 0.045, 0.075),
        location=(x - 0.115, ax(0.0), zc + 0.10),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="brake_caliper", swap="black_trim"),
        bevel=0.006,
        subsurf=(1, 1),
    )
    BUILT.append(caliper.name)


def build_wheels(mats):
    build_wheel("GEO_Wheel_FL", AXLE_F_X, +TRACK_FRONT / 2, TIRE_F_R, RIM_F_R, TIRE_F_HW, mats, +1)
    build_wheel("GEO_Wheel_FR", AXLE_F_X, -TRACK_FRONT / 2, TIRE_F_R, RIM_F_R, TIRE_F_HW, mats, -1)
    build_wheel("GEO_Wheel_RL", AXLE_R_X, +TRACK_REAR / 2, TIRE_R_R, RIM_R_R, TIRE_R_HW, mats, +1)
    build_wheel("GEO_Wheel_RR", AXLE_R_X, -TRACK_REAR / 2, TIRE_R_R, RIM_R_R, TIRE_R_HW, mats, -1)


# ---------------------------------------------------------------------------
# Conjuntos ópticos
# ---------------------------------------------------------------------------


def build_headlamps(mats):
    for side, tag in ((+1, "L"), (-1, "R")):
        # carcaça escura (housing) ligeiramente maior que a lente
        housing = lc.sphere(
            f"GEO_Headlamp_Housing_{tag}",
            radius=1.0,
            location=(1.646, side * 0.470, 0.596),
            rotation=(0.0, math.radians(-26.0), math.radians(-6.0 * side)),
            scale=(0.118, 0.190, 0.088),
            material=mats["black"],
            tag_info=dict(cat="GEO", part="headlamp_housing", swap="black_trim"),
            subsurf=(1, 2),
        )
        BUILT.append(housing.name)

        reflector = lc.sphere(
            f"GEO_Headlamp_Reflector_{tag}",
            radius=1.0,
            location=(1.640, side * 0.470, 0.598),
            rotation=(0.0, math.radians(-26.0), math.radians(-6.0 * side)),
            scale=(0.108, 0.176, 0.080),
            material=mats["reflector"],
            tag_info=dict(cat="GEO", part="headlamp_reflector", swap="reflector_chrome"),
            subsurf=(1, 2),
        )
        BUILT.append(reflector.name)

        lens = lc.sphere(
            f"GEO_Headlamp_Lens_{tag}",
            radius=1.0,
            location=(1.666, side * 0.470, 0.594),
            rotation=(0.0, math.radians(-26.0), math.radians(-6.0 * side)),
            scale=(0.114, 0.184, 0.084),
            material=mats["headlamp_lens"],
            tag_info=dict(cat="GEO", part="headlamp_lens", swap="headlamp_lens"),
            subsurf=(1, 2),
        )
        BUILT.append(lens.name)

        # óptica interna: dois elementos redondos dentro da carcaça
        for i, (dx, dy, dz, r) in enumerate(
            ((-0.030, -0.030, 0.004, 0.058), (0.026, 0.048, 0.014, 0.052))
        ):
            lamp = lc.cylinder(
                f"GEO_Headlamp_Bulb_{tag}_{i + 1}",
                radius=r,
                depth=0.022,
                segments=24,
                location=(1.624 + dx, side * (0.470 + dy), 0.598 + dz),
                rotation=(0.0, math.radians(64.0), math.radians(-6.0 * side)),
                material=mats["reflector"],
                tag_info=dict(cat="GEO", part="headlamp_bulb", swap="reflector_chrome"),
                bevel=0.003,
            )
            BUILT.append(lamp.name)

        # indicador âmbar: seção frontal-externa do conjunto
        amber = lc.sphere(
            f"GEO_Indicator_Lens_{tag}",
            radius=1.0,
            location=(1.744, side * 0.566, 0.562),
            rotation=(0.0, math.radians(-30.0), 0.0),
            scale=(0.048, 0.052, 0.036),
            material=mats["lens_amber"],
            tag_info=dict(cat="GEO", part="indicator_lens", swap="lens_amber"),
            subsurf=(1, 2),
        )
        BUILT.append(amber.name)


def build_front_grille(mats):
    # vão escuro da grade, assentado sobre a face frontal
    recess = lc.box(
        "GEO_Grille_Recess",
        size=(0.030, 0.560, 0.210),
        location=(1.836, 0.0, 0.420),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="grille_recess", swap="black_trim"),
        bevel=0.014,
        subsurf=(1, 2),
    )
    BUILT.append(recess.name)

    for i in range(5):
        z = 0.334 + i * 0.043
        bar = lc.box(
            f"GEO_Grille_Bar_{i + 1}",
            size=(0.022, 0.510, 0.017),
            location=(1.850 - 0.010 * abs(i - 2), 0.0, z),
            material=mats["mesh"],
            tag_info=dict(cat="GEO", part="grille_bar", swap="grille_mesh"),
            bevel=0.003,
        )
        BUILT.append(bar.name)

    # faróis auxiliares redondos do para-choque
    for side in (+1, -1):
        for i, (xx, yy, zz, r) in enumerate(
            ((1.836, 0.360, 0.425, 0.056), (1.812, 0.596, 0.398, 0.048))
        ):
            lamp = lc.cylinder(
                f"GEO_DrivingLamp_{'L' if side > 0 else 'R'}_{i + 1}",
                radius=r,
                depth=0.032,
                segments=28,
                location=(xx, side * yy, zz),
                rotation=(0.0, math.radians(90.0), 0.0),
                material=mats["reflector"],
                tag_info=dict(cat="GEO", part="driving_lamp", swap="reflector_chrome"),
                bevel=0.004,
            )
            BUILT.append(lamp.name)

    badge = lc.sphere(
        "GEO_Badge_Front",
        radius=1.0,
        location=(1.836, 0.0, 0.556),
        rotation=(0.0, math.radians(-36.0), 0.0),
        scale=(0.020, 0.040, 0.030),
        material=mats["badge"],
        tag_info=dict(cat="GEO", part="badge_front", swap="badge_chrome"),
        subsurf=(1, 2),
    )
    BUILT.append(badge.name)


def build_rear_lights(mats):
    for side in (+1, -1):
        for i, (yy, r) in enumerate(((0.285, 0.062), (0.560, 0.062))):
            ring = lc.cylinder(
                f"GEO_TailLamp_Ring_{'L' if side > 0 else 'R'}_{i + 1}",
                radius=r + 0.012,
                depth=0.028,
                segments=28,
                location=(-1.852, side * yy, 0.665),
                rotation=(0.0, math.radians(90.0), 0.0),
                material=mats["chrome"],
                tag_info=dict(cat="GEO", part="taillamp_ring", swap="chrome"),
                bevel=0.004,
            )
            BUILT.append(ring.name)

            lens = lc.cylinder(
                f"GEO_TailLamp_Lens_{'L' if side > 0 else 'R'}_{i + 1}",
                radius=r,
                depth=0.030,
                segments=28,
                location=(-1.860, side * yy, 0.665),
                rotation=(0.0, math.radians(90.0), 0.0),
                material=mats["lens_red"],
                tag_info=dict(cat="GEO", part="taillamp_lens", swap="lens_red"),
                bevel=0.003,
            )
            BUILT.append(lens.name)

    # refletores vermelhos no difusor
    for side in (+1, -1):
        ref = lc.cylinder(
            f"GEO_Diffuser_Reflector_{'L' if side > 0 else 'R'}",
            radius=0.036,
            depth=0.024,
            segments=24,
            location=(-1.800, side * 0.330, 0.245),
            rotation=(0.0, math.radians(90.0), 0.0),
            material=mats["lens_red"],
            tag_info=dict(cat="GEO", part="diffuser_reflector", swap="lens_red"),
            bevel=0.003,
        )
        BUILT.append(ref.name)


# ---------------------------------------------------------------------------
# Ventilações e aerodinâmica
# ---------------------------------------------------------------------------


def build_vents(mats):
    # louvers do engine cover (aletas reais, orientação longitudinal)
    for side in (+1, -1):
        for i in range(6):
            y = side * (0.075 + i * 0.042)
            bar = lc.box(
                f"GEO_EngineCover_Louver_{'L' if side > 0 else 'R'}_{i + 1}",
                size=(0.300, 0.020, 0.026),
                location=(-0.790, y, 0.918),
                rotation=(math.radians(-3.0), 0.0, 0.0),
                material=mats["black"],
                tag_info=dict(cat="GEO", part="engine_cover_louver", swap="black_trim"),
                bevel=0.003,
            )
            BUILT.append(bar.name)

    recess = lc.box(
        "GEO_EngineCover_Recess",
        size=(0.340, 0.500, 0.030),
        location=(-0.790, 0.0, 0.898),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="engine_cover_recess", swap="black_trim"),
        bevel=0.006,
    )
    BUILT.append(recess.name)

    # grade de saída atrás do cockpit
    for i in range(9):
        y = -0.18 + i * 0.045
        bar = lc.box(
            f"GEO_Rear_Vent_Slat_{i + 1}",
            size=(0.240, 0.024, 0.020),
            location=(-0.400, y, 0.845),
            rotation=(math.radians(-16.0), 0.0, 0.0),
            material=mats["black"],
            tag_info=dict(cat="GEO", part="rear_vent_slat", swap="black_trim"),
            bevel=0.002,
        )
        BUILT.append(bar.name)

    # entrada de ar do capô (frente da cabine)
    hood_vent = lc.box(
        "GEO_Hood_Vent",
        size=(0.120, 0.230, 0.020),
        location=(0.905, 0.0, 0.746),
        rotation=(math.radians(6.0), 0.0, 0.0),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="hood_vent", swap="black_trim"),
        bevel=0.004,
    )
    BUILT.append(hood_vent.name)


def build_aero(mats):
    splitter = lc.box(
        "GEO_Front_Splitter",
        size=(0.240, 1.020, 0.026),
        location=(1.712, 0.0, 0.124),
        rotation=(math.radians(-4.0), 0.0, 0.0),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="front_splitter", swap="black_trim"),
        bevel=0.006,
    )
    BUILT.append(splitter.name)

    diffuser = lc.box(
        "GEO_Rear_Diffuser",
        size=(0.300, 1.100, 0.080),
        location=(-1.700, 0.0, 0.220),
        rotation=(math.radians(7.0), 0.0, 0.0),
        material=mats["black"],
        tag_info=dict(cat="GEO", part="rear_diffuser", swap="black_trim"),
        bevel=0.008,
    )
    BUILT.append(diffuser.name)

    for side in (+1, -1):
        fin = lc.box(
            f"GEO_Diffuser_Fin_{'L' if side > 0 else 'R'}",
            size=(0.320, 0.016, 0.115),
            location=(-1.690, side * 0.390, 0.250),
            rotation=(math.radians(7.0), 0.0, 0.0),
            material=mats["black"],
            tag_info=dict(cat="GEO", part="diffuser_fin", swap="black_trim"),
            bevel=0.004,
        )
        BUILT.append(fin.name)

    # escapes centrais duplos
    for side in (+1, -1):
        tip = lc.cylinder(
            f"GEO_Exhaust_Tip_{'L' if side > 0 else 'R'}",
            radius=0.052,
            depth=0.130,
            segments=28,
            location=(-1.790, side * 0.130, 0.285),
            rotation=(0.0, math.radians(90.0), 0.0),
            material=mats["aluminum"],
            tag_info=dict(cat="GEO", part="exhaust_tip", swap="aluminum_brushed"),
            bevel=0.006,
            subsurf=(1, 1),
        )
        BUILT.append(tip.name)


def build_mirrors(mats):
    for side in (-1, +1):
        stalk = lc.box(
            f"GEO_Mirror_Stalk_{'L' if side > 0 else 'R'}",
            size=(0.055, 0.062, 0.070),
            location=(0.762, side * 0.752, 0.748),
            rotation=(math.radians(-14.0), 0.0, math.radians(-10.0 * side)),
            material=mats["black"],
            tag_info=dict(cat="GEO", part="mirror_stalk", swap="black_trim"),
            bevel=0.008,
            subsurf=(1, 2),
        )
        BUILT.append(stalk.name)

        shell = lc.sphere(
            f"GEO_Mirror_Shell_{'L' if side > 0 else 'R'}",
            radius=1.0,
            location=(0.722, side * 0.782, 0.796),
            rotation=(0.0, math.radians(-8.0), math.radians(-12.0 * side)),
            scale=(0.092, 0.030, 0.052),
            material=mats["blue"],
            tag_info=dict(cat="GEO", part="mirror_shell", swap="paint_primary"),
            subsurf=(1, 2),
        )
        BUILT.append(shell.name)


def build_badges(mats):
    lotus = lc.text_mesh(
        "GEO_Badge_LOTUS",
        "LOTUS",
        size=0.075,
        extrude=0.006,
        location=(-1.858, 0.0, 0.735),
        rotation=(math.radians(90.0), 0.0, math.radians(-90.0)),
        material=mats["badge"],
        tag_info=dict(cat="GEO", part="badge_lotus", swap="badge_chrome"),
        spacing=2.2,
    )
    BUILT.append(lotus.name)

    elise = lc.text_mesh(
        "GEO_Badge_111S",
        "111S",
        size=0.048,
        extrude=0.005,
        location=(-1.858, -0.330, 0.672),
        rotation=(math.radians(90.0), 0.0, math.radians(-90.0)),
        material=mats["badge"],
        tag_info=dict(cat="GEO", part="badge_111s", swap="badge_chrome"),
        spacing=1.1,
    )
    BUILT.append(elise.name)


# ---------------------------------------------------------------------------
# Interior
# ---------------------------------------------------------------------------


def build_interior(mats):
    liner = lc.box(
        "GEO_Cockpit_Liner",
        size=(1.360, 0.880, 0.030),
        location=(0.130, 0.0, 0.714),
        material=mats["interior"],
        tag_info=dict(cat="GEO", part="cockpit_liner", swap="interior_fabric"),
        bevel=0.008,
    )
    BUILT.append(liner.name)

    for side in (+1, -1):
        cushion = lc.box(
            f"GEO_Seat_Cushion_{'L' if side > 0 else 'R'}",
            size=(0.420, 0.380, 0.110),
            location=(-0.030, side * 0.215, 0.800),
            material=mats["interior"],
            tag_info=dict(cat="GEO", part="seat_cushion", swap="interior_fabric"),
            bevel=0.035,
            subsurf=(1, 2),
        )
        BUILT.append(cushion.name)

        back = lc.box(
            f"GEO_Seat_Backrest_{'L' if side > 0 else 'R'}",
            size=(0.150, 0.380, 0.280),
            location=(-0.235, side * 0.215, 0.930),
            rotation=(math.radians(-14.0), 0.0, 0.0),
            material=mats["interior"],
            tag_info=dict(cat="GEO", part="seat_backrest", swap="interior_fabric"),
            bevel=0.040,
            subsurf=(1, 2),
        )
        BUILT.append(back.name)

    dashboard = lc.box(
        "GEO_Dashboard",
        size=(0.300, 0.870, 0.090),
        location=(0.470, 0.0, 0.828),
        rotation=(math.radians(-12.0), 0.0, 0.0),
        material=mats["interior"],
        tag_info=dict(cat="GEO", part="dashboard", swap="interior_fabric"),
        bevel=0.020,
        subsurf=(1, 2),
    )
    BUILT.append(dashboard.name)

    wheel_profile = [
        (0.152 + 0.016 * math.cos(t), 0.016 * math.sin(t))
        for t in [2.0 * math.pi * i / 16.0 for i in range(16)]
    ]
    steering = lc.revolve(
        "GEO_Steering_Wheel",
        wheel_profile,
        segments=40,
        center=(0.430, 0.235, 0.875),
        axis=(0.94, 0.0, 0.34),
        ref=(0.0, 1.0, 0.0),
        material=mats["interior"],
        tag_info=dict(cat="GEO", part="steering_wheel", swap="interior_fabric"),
        subsurf=(1, 1),
    )
    BUILT.append(steering.name)

    roll_profile = [
        (0.360 + 0.028 * math.cos(t), 0.028 * math.sin(t))
        for t in [2.0 * math.pi * i / 16.0 for i in range(16)]
    ]
    rollbar = lc.revolve(
        "GEO_RollBar",
        roll_profile,
        segments=56,
        center=(-0.330, 0.0, 0.700),
        axis=(1.0, 0.0, 0.0),
        ref=(0.0, 1.0, 0.0),
        material=mats["interior"],
        tag_info=dict(cat="GEO", part="rollbar", swap="interior_fabric"),
        subsurf=(1, 2),
    )
    BUILT.append(rollbar.name)


# ---------------------------------------------------------------------------
# Rig de verificação e câmeras
# ---------------------------------------------------------------------------


def _aim(obj, target=(0.0, 0.0, 0.55)) -> None:
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def build_world() -> None:
    world = bpy.data.worlds.new("W_Studio_Neutral")
    world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputWorld")
    bg = nt.nodes.new("ShaderNodeBackground")
    bg.inputs["Color"].default_value = (0.42, 0.44, 0.47, 1.0)
    bg.inputs["Strength"].default_value = 1.0
    nt.links.new(bg.outputs["Background"], out.inputs["Surface"])
    bpy.context.scene.world = world


def build_lights(mats) -> None:
    specs = [
        ("LGT_Key_Softbox", (2.9, 2.5, 3.4), (3.4, 2.2), 1150.0, 1.0),
        ("LGT_Fill_Card", (-1.2, -3.6, 2.0), (3.0, 1.4), 420.0, 1.0),
        ("LGT_Rim_Strip", (-3.6, 1.6, 3.0), (2.6, 1.1), 780.0, 1.0),
        ("LGT_Card_Long", (0.4, 4.2, 1.1), (5.2, 1.0), 600.0, 1.0),
    ]
    for name, loc, size, energy, _ in specs:
        data = bpy.data.lights.new(name=name, type="AREA")
        data.shape = "RECTANGLE"
        data.size = size[0]
        data.size_y = size[1]
        data.energy = energy
        obj = bpy.data.objects.new(name, data)
        obj.location = Vector(loc)
        bpy.context.scene.collection.objects.link(obj)
        _aim(obj, (0.0, 0.0, 0.6))
        obj["cat"] = "LGT"
        obj["part"] = name.split("_", 2)[-1].lower()
        obj["mat_swap_key"] = "verification_rig"


def build_cameras() -> None:
    specs = [
        ("CAM_Frontal", (7.6, 0.0, 0.72), 95.0, (0.0, 0.0, 0.62)),
        ("CAM_Lateral", (0.0, 8.2, 0.76), 62.0, (0.0, 0.0, 0.58)),
        ("CAM_Traseira", (-7.6, 0.0, 0.78), 95.0, (0.0, 0.0, 0.62)),
        ("CAM_Superior", (0.0, 0.0, 10.5), 50.0, (0.0, 0.0, 0.0)),
        ("CAM_WheelDetail", (2.05, 1.35, 0.50), 78.0, (1.15, 0.71, 0.30)),
        ("CAM_TresQuartos", (4.95, 4.15, 1.95), 72.0, (0.0, 0.0, 0.58)),
        ("CAM_TresQuartos_Tr", (-4.95, 4.15, 1.95), 72.0, (0.0, 0.0, 0.62)),
        ("CAM_Isometrica", (5.40, 5.40, 3.90), 70.0, (0.0, 0.0, 0.55)),
        ("CAM_Hero", (4.90, 3.80, 1.00), 50.0, (0.30, 0.0, 0.52)),
    ]
    for name, loc, lens, target in specs:
        data = bpy.data.cameras.new(name)
        data.lens = lens
        obj = bpy.data.objects.new(name, data)
        obj.location = Vector(loc)
        bpy.context.scene.collection.objects.link(obj)
        if name == "CAM_Superior":
            obj.rotation_euler = Euler((0.0, 0.0, math.radians(-90.0)), "XYZ")
        else:
            _aim(obj, target)
        obj["cat"] = "CAM"
        obj["part"] = name.split("_", 1)[1].lower()
        obj["mat_swap_key"] = "camera"


def setup_render() -> None:
    scene = bpy.context.scene
    scene.render.engine = "BLENDER_EEVEE"
    scene.render.resolution_x = 1500
    scene.render.resolution_y = 1000
    scene.render.resolution_percentage = 100
    scene.render.image_settings.file_format = "PNG"
    scene.render.film_transparent = False
    scene.view_settings.view_transform = "AgX"
    for look in ("AgX - Medium High Contrast", "AgX - Base Contrast", "None"):
        try:
            scene.view_settings.look = look
            break
        except Exception:
            continue
    scene.view_settings.exposure = -0.18

    eevee = scene.eevee
    for attr, value in (
        ("taa_render_samples", 96),
        ("use_raytracing", True),
        ("use_shadows", True),
        ("use_volumetric_lights", False),
    ):
        if hasattr(eevee, attr):
            try:
                setattr(eevee, attr, value)
            except Exception:
                pass
    for attr in ("ray_tracing_options",):
        opts = getattr(eevee, attr, None)
        if opts is not None and hasattr(opts, "use_denoise"):
            opts.use_denoise = True


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def report() -> str:
    lines = ["# Relatório de malha — Lotus Elise 111S", ""]
    deps = bpy.context.evaluated_depsgraph_get()

    total = dict(faces=0, quads=0, tris=0, ngons=0, non_manifold=0, boundary=0)
    rows = []
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH":
            continue
        stats = lc.mesh_stats(obj)
        rows.append((obj.name, stats))
        for key in total:
            total[key] += stats[key]

    lines.append(f"Objetos de malha: {len(rows)}")
    lines.append("")
    lines.append("| Objeto | Vértices | Faces | Quads | Tris | N-gons | Non-manifold | Borda |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for name, s in rows:
        lines.append(
            f"| {name} | {s['verts']} | {s['faces']} | {s['quads']} | {s['tris']} | "
            f"{s['ngons']} | {s['non_manifold']} | {s['boundary']} |"
        )

    lines += [
        "",
        "## Totais (malha base, sem subdivisão)",
        "",
        f"- Faces: {total['faces']} (quads {total['quads']}, tris {total['tris']}, n-gons {total['ngons']})",
        f"- Arestas non-manifold: {total['non_manifold']}",
        f"- Arestas de borda: {total['boundary']}",
        "",
    ]

    bb = lc.world_bounds()
    lines += [
        "## Envelope",
        "",
        f"- Comprimento (X): {bb['size'][0]:.3f} m (alvo {LENGTH:.3f})",
        f"- Largura (Y): {bb['size'][1]:.3f} m (alvo {WIDTH:.3f})",
        f"- Altura (Z): {bb['size'][2]:.3f} m (alvo {HEIGHT:.3f})",
        f"- Solo (Z mín): {bb['min'][2]:.4f} m",
        f"- Centro Y: {(bb['min'][1] + bb['max'][1]) / 2:.4f} m",
        "",
        "## N-gons por objeto",
        "",
    ]
    ngon_objs = [f"- {name}: {s['ngons']}" for name, s in rows if s["ngons"]]
    lines += ngon_objs or ["- nenhum"]
    lines.append("")

    text = "\n".join(lines)
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as fh:
        fh.write(text)
    return text


def main() -> None:
    t0 = time.time()
    lc.clear_scene()
    mats = build_materials()
    build_world()
    build_body(mats)
    build_cabin(mats)
    build_wheels(mats)
    build_headlamps(mats)
    build_front_grille(mats)
    build_rear_lights(mats)
    build_vents(mats)
    build_aero(mats)
    build_mirrors(mats)
    build_badges(mats)
    build_interior(mats)
    build_lights(mats)
    build_cameras()
    setup_render()

    bpy.context.scene.camera = bpy.data.objects["CAM_TresQuartos"]

    text = report()
    body = [ln for ln in text.splitlines() if ln.startswith("| GEO_Body") or ln.startswith("| GEO_Cabin")]
    totals = [ln for ln in text.splitlines() if ln.startswith(("- Faces", "- Arestas"))]
    bb = lc.world_bounds()
    print("RESUMO DO BUILD")
    print("\n".join(totals))
    print("\n".join(body))
    print(
        f"Envelope: X {bb['size'][0]:.3f} | Y {bb['size'][1]:.3f} | Z {bb['size'][2]:.3f} | "
        f"Zmin {bb['min'][2]:.4f} | tempo {time.time() - t0:.1f}s"
    )
    print(f"Objetos construídos: {len(BUILT)} | tempo: {time.time() - t0:.1f}s")

    if SAVE_BLEND:
        bpy.ops.wm.save_as_mainfile(filepath=BLEND_PATH)
        print(f"Salvo em {BLEND_PATH}")


main()
