"""Emite o relatório de malha do modelo já construído.

Uso:
    blender --background car-lotus-elise-111s.blend --python scripts/mesh_report.py

Escreve docs/renders/mesh_report.txt e imprime o resumo no console. Não altera a cena.
"""

from __future__ import annotations

import os
import sys

import bpy
from mathutils import Vector

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
if os.path.join(BASE, "scripts") not in sys.path:
    sys.path.insert(0, os.path.join(BASE, "scripts"))

import bmesh  # noqa: E402

ALVOS = {"X": 3.726, "Y": 1.718, "Z": 1.117}


def stats(obj) -> dict:
    me = obj.data
    bm = bmesh.new()
    bm.from_mesh(me)
    non_manifold = sum(1 for e in bm.edges if len(e.link_faces) not in (1, 2))
    boundary = sum(1 for e in bm.edges if len(e.link_faces) == 1)
    bm.free()
    return dict(
        verts=len(me.vertices),
        faces=len(me.polygons),
        quads=sum(1 for p in me.polygons if len(p.vertices) == 4),
        tris=sum(1 for p in me.polygons if len(p.vertices) == 3),
        ngons=sum(1 for p in me.polygons if len(p.vertices) > 4),
        non_manifold=non_manifold,
        boundary=boundary,
    )


def bounds() -> dict:
    lo = Vector((1e9, 1e9, 1e9))
    hi = Vector((-1e9, -1e9, -1e9))
    for obj in bpy.data.objects:
        if obj.type != "MESH":
            continue
        for corner in obj.bound_box:
            p = obj.matrix_world @ Vector(corner)
            lo = Vector((min(lo.x, p.x), min(lo.y, p.y), min(lo.z, p.z)))
            hi = Vector((max(hi.x, p.x), max(hi.y, p.y), max(hi.z, p.z)))
    return dict(min=lo, max=hi, size=hi - lo)


def main() -> None:
    linhas = ["# Relatório de malha — Lotus Elise 111S", ""]
    total = dict(faces=0, quads=0, tris=0, ngons=0, non_manifold=0, boundary=0)
    linhas += [
        "| Objeto | Vértices | Faces | Quads | Tris | N-gons | Non-manifold | Borda |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for obj in sorted(bpy.data.objects, key=lambda o: o.name):
        if obj.type != "MESH":
            continue
        s = stats(obj)
        for k in total:
            total[k] += s[k]
        linhas.append(
            f"| {obj.name} | {s['verts']} | {s['faces']} | {s['quads']} | {s['tris']} | "
            f"{s['ngons']} | {s['non_manifold']} | {s['boundary']} |"
        )

    bb = bounds()
    linhas += [
        "",
        "## Totais (malha base, sem subdivisão)",
        "",
        f"- Faces: {total['faces']} (quads {total['quads']}, tris {total['tris']}, n-gons {total['ngons']})",
        f"- Arestas non-manifold: {total['non_manifold']}",
        f"- Arestas de borda: {total['boundary']}",
        "",
        "## Envelope",
        "",
        f"- Comprimento (X): {bb['size'][0]:.3f} m (alvo {ALVOS['X']:.3f})",
        f"- Largura (Y): {bb['size'][1]:.3f} m (alvo {ALVOS['Y']:.3f})",
        f"- Altura (Z): {bb['size'][2]:.3f} m (alvo {ALVOS['Z']:.3f})",
        f"- Solo (Z mín): {bb['min'][2]:.4f} m",
        f"- Centro Y: {(bb['min'][1] + bb['max'][1]) / 2:.4f} m",
    ]

    texto = "\n".join(linhas)
    destino = os.path.join(BASE, "docs", "renders", "mesh_report.txt")
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as fh:
        fh.write(texto + "\n")

    print(f"Faces: {total['faces']} | n-gons: {total['ngons']} | non-manifold: {total['non_manifold']}")
    print(
        f"Envelope: X {bb['size'][0]:.3f} | Y {bb['size'][1]:.3f} | Z {bb['size'][2]:.3f} | "
        f"Zmin {bb['min'][2]:.4f}"
    )
    print(f"Relatório escrito em {destino}")


main()
