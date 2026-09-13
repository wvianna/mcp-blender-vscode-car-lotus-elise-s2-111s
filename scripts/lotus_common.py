"""Helpers de modelagem compartilhados — Lotus Elise 111S.

Módulo sem efeitos colaterais: importar não altera a cena. Todas as funções de
construção criam e retornam objetos nomeados conforme a convenção `GEO_*`.
"""

from __future__ import annotations

import math

import bpy
import bmesh
from mathutils import Euler, Matrix, Vector

# ---------------------------------------------------------------------------
# Cores
# ---------------------------------------------------------------------------


def srgb_to_linear(c: float) -> float:
    """Converte um canal sRGB (0..1) para linear."""
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def hex_to_linear(hex_str: str) -> tuple[float, float, float]:
    h = hex_str.lstrip("#")
    return tuple(srgb_to_linear(int(h[i : i + 2], 16) / 255.0) for i in (0, 2, 4))


def rgba(hex_str: str, alpha: float = 1.0) -> tuple[float, float, float, float]:
    r, g, b = hex_to_linear(hex_str)
    return (r, g, b, alpha)


# ---------------------------------------------------------------------------
# Cena
# ---------------------------------------------------------------------------


def clear_scene() -> None:
    """Remove todos os objetos e dados órfãos — torna o build idempotente."""
    for obj in list(bpy.data.objects):
        bpy.data.objects.remove(obj, do_unlink=True)
    for coll in list(bpy.data.collections):
        bpy.data.collections.remove(coll)

    for collection in (
        bpy.data.meshes,
        bpy.data.curves,
        bpy.data.materials,
        bpy.data.cameras,
        bpy.data.lights,
        bpy.data.node_groups,
        bpy.data.worlds,
    ):
        for block in list(collection):
            try:
                collection.remove(block)
            except Exception:  # blocos em uso são ignorados
                pass


# ---------------------------------------------------------------------------
# Materiais
# ---------------------------------------------------------------------------


def new_material(name: str):
    """Cria um material com Principled BSDF e retorna (material, node_tree, bsdf)."""
    mat = bpy.data.materials.new(name)
    mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    out.location = (320, 0)
    bsdf = nt.nodes.new("ShaderNodeBsdfPrincipled")
    bsdf.location = (0, 0)
    nt.links.new(bsdf.outputs["BSDF"], out.inputs["Surface"])
    return mat, nt, bsdf


def noise_normal(nt, bsdf, scale=140.0, detail=2.0, strength=0.06, location=(-900, -320)):
    """Liga um Noise -> Bump -> Normal do BSDF (micro-relevo)."""
    noise = nt.nodes.new("ShaderNodeTexNoise")
    noise.location = location
    noise.inputs["Scale"].default_value = scale
    noise.inputs["Detail"].default_value = detail
    bump = nt.nodes.new("ShaderNodeBump")
    bump.location = (location[0] + 260, location[1])
    bump.inputs["Strength"].default_value = strength
    nt.links.new(noise.outputs["Fac"], bump.inputs["Height"])
    nt.links.new(bump.outputs["Normal"], bsdf.inputs["Normal"])
    return noise, bump


# ---------------------------------------------------------------------------
# Finalização de malha
# ---------------------------------------------------------------------------


def _folded_fan_cap(bm, verts, mat_index: int, smooth: bool = True):
    """Tampa um laço fechado usando apenas quads (n par).

    O laço é dobrado sobre si mesmo: cada quad liga v[i]..v[i+1] aos espelhos
    v[n-1-i]..v[n-2-i]. Não gera triângulos nem n-gons.
    """
    n = len(verts)
    if n < 4:
        return []
    if n % 2:
        n -= 1  # ignora o excedente; o laço resultante segue fechado
    created = []
    for i in range(n // 2 - 1):
        a, b = verts[i], verts[i + 1]
        c, d = verts[n - 2 - i], verts[n - 1 - i]
        if len({a, b, c, d}) < 4:
            continue
        try:
            face = bm.faces.new((a, b, c, d))
        except ValueError:
            continue
        face.material_index = mat_index
        face.smooth = smooth
        created.append(face)
    return created


def quad_caps(bm) -> int:
    """Substitui faces n-gon (tampas de cilindro) por malha de quads."""
    replaced = 0
    for face in list(bm.faces):
        n = len(face.verts)
        if n <= 4:
            continue
        verts = list(face.verts)
        mat_index = face.material_index
        smooth = face.smooth
        bmesh.ops.delete(bm, geom=[face], context="FACES_ONLY")
        _folded_fan_cap(bm, verts, mat_index, smooth)
        replaced += 1
    return replaced


def finalize(
    name: str,
    bm: bmesh.types.BMesh,
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    smooth: bool = True,
    recalc: bool = True,
):
    """Converte um bmesh em objeto, aplica material/subsurf e grava metadados."""
    quad_caps(bm)
    if recalc:
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if smooth:
        for f in bm.faces:
            f.smooth = True
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    me.validate()

    obj = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(obj)

    if material is not None:
        me.materials.append(material)
    if subsurf is not None:
        mod = obj.modifiers.new("Subdivision", "SUBSURF")
        mod.levels = subsurf[0]
        mod.render_levels = subsurf[1]
    if tag_info:
        tag(obj, **tag_info)
    return obj


def tag(obj, cat: str, part: str, swap: str) -> None:
    """Metadados para troca automatizada de material via MCP."""
    obj["cat"] = cat
    obj["part"] = part
    obj["mat_swap_key"] = swap


def add_subsurf(obj, view: int = 1, render: int = 3) -> None:
    mod = obj.modifiers.new("Subdivision", "SUBSURF")
    mod.levels = view
    mod.render_levels = render


def shade_smooth(obj, angle: float | None = 0.61) -> None:
    for poly in obj.data.polygons:
        poly.use_smooth = True
    if angle is not None:
        try:
            obj.data.set_sharp_from_angle(angle=angle)
        except AttributeError:
            pass


# ---------------------------------------------------------------------------
# Loft de seções transversais
# ---------------------------------------------------------------------------


def build_loft(
    name: str,
    stations: list[tuple[float, list[tuple[float, float]]]],
    mat_grid=None,
    cap_mats=(0, 0),
    materials: list | None = None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = (1, 3),
    smooth: bool = True,
    caps: bool = True,
):
    """Constrói uma superfície fechada por loft de anéis ao longo de X.

    stations: lista de (x, ring) onde `ring` é um laço fechado de (y, z) com o
    mesmo número de pontos em todas as estações.
    mat_grid: matriz [n_bandas][n_segmentos] com índices de material.
    """
    bm = bmesh.new()
    rings = []
    for x, ring in stations:
        rings.append([bm.verts.new((x, y, z)) for (y, z) in ring])
    bm.verts.ensure_lookup_table()

    nseg = len(rings[0])
    bands: list[list[bmesh.types.BMFace]] = []
    for i in range(len(rings) - 1):
        row = []
        for j in range(nseg):
            k = (j + 1) % nseg
            face = bm.faces.new((rings[i][j], rings[i][k], rings[i + 1][k], rings[i + 1][j]))
            row.append(face)
        bands.append(row)

    if mat_grid is not None:
        for i, row in enumerate(bands):
            for j, face in enumerate(row):
                face.material_index = mat_grid[i][j]

    if caps:
        for end, ring_index in ((0, 0), (1, len(rings) - 1)):
            _folded_fan_cap(bm, list(rings[ring_index]), cap_mats[end], smooth)

    obj = finalize(
        name,
        bm,
        material=materials[0] if materials else None,
        tag_info=tag_info,
        subsurf=subsurf,
        smooth=smooth,
    )
    if materials:
        for mat in materials[1:]:
            obj.data.materials.append(mat)
        # redefine os índices salvos no bmesh (o finalize já criou a malha)
    return obj


# ---------------------------------------------------------------------------
# Primitivas
# ---------------------------------------------------------------------------


def _cone(bm, segments, r1, r2, depth, cap_ends=True, matrix=None):
    kwargs = dict(
        cap_ends=cap_ends,
        cap_tris=False,
        segments=segments,
        depth=depth,
        matrix=matrix or Matrix(),
    )
    try:
        return bmesh.ops.create_cone(bm, radius1=r1, radius2=r2, **kwargs)
    except TypeError:
        return bmesh.ops.create_cone(bm, diameter1=r1 * 2, diameter2=r2 * 2, **kwargs)


def cylinder(
    name: str,
    radius: float,
    depth: float,
    segments: int = 32,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    radius2: float | None = None,
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    caps: bool = True,
    bevel: float = 0.0,
):
    """Cilindro/cone criado ao longo de Z e então posicionado."""
    bm = bmesh.new()
    mat = (
        Matrix.Translation(Vector(location))
        @ Euler(rotation, "XYZ").to_matrix().to_4x4()
        @ Matrix.Translation(Vector((0, 0, depth * 0.5)))
    )
    _cone(bm, segments, radius, radius2 if radius2 is not None else radius, depth, caps, mat)
    if bevel:
        bmesh.ops.bevel(
            bm, geom=list(bm.verts) + list(bm.edges), offset=bevel, segments=3, affect="EDGES"
        )
    return finalize(name, bm, material, tag_info, subsurf)


def box(
    name: str,
    size=(1, 1, 1),
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    bevel: float = 0.0,
):
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=Vector(size), verts=bm.verts)
    if bevel:
        bmesh.ops.bevel(
            bm, geom=list(bm.verts) + list(bm.edges), offset=bevel, segments=3, affect="EDGES"
        )
    bmesh.ops.transform(
        bm,
        matrix=Matrix.Translation(Vector(location)) @ Euler(rotation, "XYZ").to_matrix().to_4x4(),
        verts=bm.verts,
    )
    return finalize(name, bm, material, tag_info, subsurf)


def sphere(
    name: str,
    radius: float = 1.0,
    u_segments: int = 24,
    v_segments: int = 12,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    scale=(1, 1, 1),
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    smooth: bool = True,
):
    bm = bmesh.new()
    try:
        bmesh.ops.create_uvsphere(
            bm, u_segments=u_segments, v_segments=v_segments, radius=radius
        )
    except TypeError:
        bmesh.ops.create_uvsphere(
            bm, u_segments=u_segments, v_segments=v_segments, diameter=radius * 2
        )
    mat = (
        Matrix.Translation(Vector(location))
        @ Euler(rotation, "XYZ").to_matrix().to_4x4()
        @ Matrix.Diagonal(Vector(scale).to_4d())
    )
    bmesh.ops.transform(bm, matrix=mat, verts=bm.verts)
    return finalize(name, bm, material, tag_info, subsurf, smooth=smooth)


def revolve(
    name: str,
    profile: list[tuple[float, float]],
    segments: int = 48,
    center=(0, 0, 0),
    axis=(0, 1, 0),
    ref=(1, 0, 0),
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    smooth: bool = True,
):
    """Revolve um perfil fechado (raio, posição_axial) em torno de um eixo."""
    c = Vector(center)
    ax = Vector(axis).normalized()
    ref_v = Vector(ref)
    u = (ref_v - ax * ref_v.dot(ax)).normalized()
    v = ax.cross(u)

    bm = bmesh.new()
    rings = []
    n = len(profile)
    for s in range(segments):
        ang = 2.0 * math.pi * s / segments
        direction = u * math.cos(ang) + v * math.sin(ang)
        rings.append([bm.verts.new(c + direction * r + ax * a) for (r, a) in profile])

    for s in range(segments):
        s2 = (s + 1) % segments
        for j in range(n):
            j2 = (j + 1) % n
            bm.faces.new((rings[s][j], rings[s][j2], rings[s2][j2], rings[s2][j]))

    return finalize(name, bm, material, tag_info, subsurf, smooth=smooth)


def extrude_profile(
    name: str,
    profile: list[tuple[float, float]],
    axis: str = "y",
    location=(0, 0, 0),
    thickness: float = 0.0,
    material=None,
    tag_info: dict | None = None,
    subsurf: tuple[int, int] | None = None,
    smooth: bool = True,
):
    """Cria um sólido extrudando um polígono (x, z) no eixo indicado."""
    bm = bmesh.new()
    verts = [bm.verts.new((x, 0.0, z)) for (x, z) in profile]
    face = bm.faces.new(verts)
    if thickness:
        bmesh.ops.solidify(bm, geom=[face], thickness=thickness)
    if axis == "y":
        pass
    elif axis == "x":
        bmesh.ops.rotate(
            bm, verts=bm.verts, cent=(0, 0, 0), matrix=Matrix.Rotation(math.pi / 2, 3, "Z")
        )
    bmesh.ops.transform(bm, matrix=Matrix.Translation(Vector(location)), verts=bm.verts)
    return finalize(name, bm, material, tag_info, subsurf, smooth=smooth)


def text_mesh(
    name: str,
    body: str,
    size: float,
    extrude: float,
    location=(0, 0, 0),
    rotation=(0, 0, 0),
    material=None,
    tag_info: dict | None = None,
    align_x: str = "CENTER",
    align_y: str = "CENTER",
    spacing: float = 1.0,
):
    """Cria um texto 3D e o converte em malha."""
    curve = bpy.data.curves.new(name=name, type="FONT")
    curve.body = body
    curve.size = size
    curve.extrude = extrude
    curve.align_x = align_x
    curve.align_y = align_y
    curve.offset = 0.0
    curve.space_character = spacing
    obj = bpy.data.objects.new(name, curve)
    bpy.context.scene.collection.objects.link(obj)

    bpy.context.view_layer.objects.active = obj
    for o in bpy.context.selected_objects:
        o.select_set(False)
    obj.select_set(True)
    bpy.ops.object.convert(target="MESH")
    obj = bpy.context.view_layer.objects.active

    obj.rotation_euler = Euler(rotation, "XYZ")
    obj.location = Vector(location)
    if material is not None:
        obj.data.materials.append(material)
    if tag_info:
        tag(obj, **tag_info)
    return obj


# ---------------------------------------------------------------------------
# Perfis de carroceria
# ---------------------------------------------------------------------------


def body_ring(w, wt, zb, zs, zte, zt) -> list[tuple[float, float]]:
    """Meio-perfil da carroceria espelhado — 16 pontos, laço fechado."""
    span = zs - zb
    zm = zb + 0.58 * span
    half = [
        (0.00, zb),
        (0.40 * w, zb + 0.02 * span),
        (0.80 * w, zb + 0.22 * span),
        (0.97 * w, zb + 0.46 * span),
        (1.00 * w, zm),
        (0.96 * w, zs),
        (0.80 * w, zte - 0.030 * (zt - zte)),
        (0.42 * wt, zte),
        (0.00, zt),
    ]
    return half + [(-y, z) for (y, z) in reversed(half[1:-1])]


def cabin_ring(wb, wt, zc, h) -> list[tuple[float, float]]:
    """Perfil da cabine — topo plano e laterais quase verticais (10 pontos)."""
    half = [
        (wb, zc),
        (0.99 * wb, zc + 0.30 * h),
        (0.97 * wb, zc + 0.62 * h),
        (0.90 * wb, zc + 0.88 * h),
        (0.66 * wt, zc + 0.985 * h),
        (0.00, zc + h),
    ]
    return half + [(-y, z) for (y, z) in reversed(half[1:-1])]


def arch_bottom(
    x: float,
    base: float,
    arches: list[tuple[float, float, float]],
) -> float:
    """Fundo da carroceria considerando os vãos de roda.

    arches: lista de (x_axle, z_axle, raio). Dentro do vão o fundo segue a
    circunferência do arco, permitindo o recorte sem boolean.
    """
    z = base
    for x_axle, z_axle, radius in arches:
        dx = x - x_axle
        if abs(dx) < radius:
            z = max(z, z_axle + math.sqrt(radius * radius - dx * dx))
    return z


# ---------------------------------------------------------------------------
# Relatório
# ---------------------------------------------------------------------------


def world_bounds(objects=None) -> dict:
    """Envelope global (mundo) considerando apenas objetos de malha."""
    objs = objects if objects is not None else bpy.data.objects
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    found = False
    for obj in objs:
        if obj.type != "MESH":
            continue
        found = True
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z)))
            hi = Vector((max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z)))
    if not found:
        return dict(min=Vector((0, 0, 0)), max=Vector((0, 0, 0)), size=Vector((0, 0, 0)))
    return dict(min=lo, max=hi, size=hi - lo)


def mesh_stats(obj, evaluated: bool = False) -> dict:
    """Estatísticas de malha para o relatório de build."""
    deps = bpy.context.evaluated_depsgraph_get()
    target = obj.evaluated_get(deps) if evaluated else obj
    me = target.to_mesh() if evaluated else obj.data
    ngons = sum(1 for p in me.polygons if len(p.vertices) > 4)
    tris = sum(1 for p in me.polygons if len(p.vertices) == 3)
    quads = sum(1 for p in me.polygons if len(p.vertices) == 4)
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if len(e.link_faces) not in (1, 2))
    boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    bm.free()
    if evaluated:
        target.to_mesh_clear()
    return dict(
        verts=len(me.vertices),
        faces=len(me.polygons),
        quads=quads,
        tris=tris,
        ngons=ngons,
        non_manifold=non_manifold,
        boundary=boundary,
    )
