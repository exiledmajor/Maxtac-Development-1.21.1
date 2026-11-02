#!/usr/bin/env python3
"""Convert Blockbench generic meshes to triangulated, UV-mapped runtime geometry.

Faces are triangulated with ear clipping (including concave polygons), preserving
per-vertex UVs. Geometry remains in source coordinates; hierarchy transforms are
reported as warnings because they must be applied in Blockbench's group space.
"""
import argparse
import json
from pathlib import Path


def cross2(a, b, c):
    return (b[0]-a[0])*(c[1]-a[1]) - (b[1]-a[1])*(c[0]-a[0])


def triangulate(poly):
    """Ear-clip a simple polygon. poly entries are (3D point, UV)."""
    if len(poly) < 3:
        return []
    if len(poly) == 3:
        return [tuple(poly)]

    # Project onto the plane with the largest normal component.
    pts = [v[0] for v in poly]
    nx = ny = nz = 0.0
    for i, p in enumerate(pts):
        q = pts[(i + 1) % len(pts)]
        nx += (p[1]-q[1])*(p[2]+q[2])
        ny += (p[2]-q[2])*(p[0]+q[0])
        nz += (p[0]-q[0])*(p[1]+q[1])
    axis = max(range(3), key=lambda k: abs((nx, ny, nz)[k]))
    if axis == 0:
        xy = [(p[1], p[2]) for p in pts]
    elif axis == 1:
        xy = [(p[0], p[2]) for p in pts]
    else:
        xy = [(p[0], p[1]) for p in pts]

    area = sum(xy[i][0]*xy[(i+1)%len(xy)][1] -
               xy[(i+1)%len(xy)][0]*xy[i][1] for i in range(len(xy)))
    if abs(area) < 1e-9:
        return [(poly[0], poly[i], poly[i+1]) for i in range(1, len(poly)-1)]
    orient = 1.0 if area > 0 else -1.0
    remaining = list(range(len(poly)))
    result = []

    def inside(p, a, b, c):
        c1 = orient * cross2(a, b, p)
        c2 = orient * cross2(b, c, p)
        c3 = orient * cross2(c, a, p)
        return c1 >= -1e-8 and c2 >= -1e-8 and c3 >= -1e-8

    guard = len(remaining) * len(remaining)
    while len(remaining) > 3 and guard > 0:
        guard -= 1
        found = False
        for j, cur in enumerate(remaining):
            prev = remaining[(j-1) % len(remaining)]
            nxt = remaining[(j+1) % len(remaining)]
            a, b, c = xy[prev], xy[cur], xy[nxt]
            if orient * cross2(a, b, c) <= 1e-9:
                continue
            if any(inside(xy[k], a, b, c) for k in remaining
                   if k not in (prev, cur, nxt)):
                continue
            result.append((poly[prev], poly[cur], poly[nxt]))
            del remaining[j]
            found = True
            break
        if not found:
            # Degenerate/self-intersecting polygon: retain a deterministic fallback.
            return [(poly[0], poly[i], poly[i+1]) for i in range(1, len(poly)-1)]
    if len(remaining) == 3:
        result.append(tuple(poly[i] for i in remaining))
    return result


def add_face(points, uvs, material, triangles):
    for tri in triangulate(list(zip(points, uvs))):
        positions = [float(c) for point, _ in tri for c in point]
        tex = [float(c) for _, uv in tri for c in uv]
        a, b, c = tri
        p, q, r = a[0], b[0], c[0]
        ax, ay, az = q[0]-p[0], q[1]-p[1], q[2]-p[2]
        bx, by, bz = r[0]-p[0], r[1]-p[1], r[2]-p[2]
        nx, ny, nz = ay*bz-az*by, az*bx-ax*bz, ax*by-ay*bx
        length = (nx*nx + ny*ny + nz*nz) ** 0.5
        if length > 1e-9:
            nx, ny, nz = nx/length, ny/length, nz/length
        triangles.append({"positions": positions, "uv": tex,
                          "normal": [nx, ny, nz], "material": material})


def rotate_point(point, transform):
    import math
    origin = transform.get("origin") or [0.0, 0.0, 0.0]
    rotation = transform.get("rotation") or [0.0, 0.0, 0.0]
    x, y, z = (float(point[i]) - float(origin[i]) for i in range(3))
    rx, ry, rz = (float(rotation[i]) * math.pi / 180.0 for i in range(3))
    if rx:
        c, sn = math.cos(rx), math.sin(rx); y, z = y*c-z*sn, y*sn+z*c
    if ry:
        c, sn = math.cos(ry), math.sin(ry); x, z = x*c+z*sn, -x*sn+z*c
    if rz:
        c, sn = math.cos(rz), math.sin(rz); x, y = x*c-y*sn, x*sn+y*c
    return [x + float(origin[0]), y + float(origin[1]), z + float(origin[2])]

def transformed(point, transforms):
    result = [float(v) for v in point]
    for transform in transforms: result = rotate_point(result, transform)
    return result

def element_transform(element):
    rotation = element.get("rotation") or [0.0, 0.0, 0.0]
    if len(rotation) == 3 and any(abs(float(v)) > 1e-8 for v in rotation):
        return [{"origin": element.get("origin") or [0, 0, 0], "rotation": rotation}]
    return []

def hierarchy_transforms(model):
    by_uuid = {e.get("uuid"): e for e in model.get("elements", []) if e.get("uuid")}
    result = {}
    def walk(nodes, inherited):
        for node in nodes or []:
            if isinstance(node, str):
                if node in by_uuid: result[node] = list(inherited) + element_transform(by_uuid[node])
            elif isinstance(node, dict):
                rotation = node.get("rotation") or [0.0, 0.0, 0.0]
                group = []
                if len(rotation) == 3 and any(abs(float(v)) > 1e-8 for v in rotation):
                    group = [{"origin": node.get("origin") or [0, 0, 0], "rotation": rotation}]
                walk(node.get("children", []), list(inherited) + group)
    walk(model.get("outliner", []), [])
    for element in model.get("elements", []):
        uid = element.get("uuid")
        if uid and uid not in result: result[uid] = element_transform(element)
    return result

def convert_mesh(element, triangles, transforms=()):
    vertices = element.get("vertices", {})
    for face in element.get("faces", {}).values():
        ids = face.get("vertices", [])
        points = [transformed(vertices.get(str(i)), transforms) if vertices.get(str(i)) is not None else None for i in ids]
        if len(points) < 3 or any(p is None for p in points):
            continue
        uvmap = face.get("uv", {})
        uvs = [uvmap.get(str(i), [0.0, 0.0]) for i in ids]
        add_face(points, uvs, face.get("texture"), triangles)


def convert_cube(element, triangles, transforms=()):
    x0,y0,z0 = map(float, element.get("from", [0,0,0]))
    x1,y1,z1 = map(float, element.get("to", [0,0,0]))
    faces = {
      "north": ([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)]),
      "south": ([(x1,y0,z1),(x0,y0,z1),(x0,y1,z1),(x1,y1,z1)]),
      "west":  ([(x0,y0,z1),(x0,y0,z0),(x0,y1,z0),(x0,y1,z1)]),
      "east":  ([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)]),
      "up":    ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)]),
      "down":  ([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)]),
    }
    for name, points in faces.items():
        points = [transformed(point, transforms) for point in points]
        face = element.get("faces", {}).get(name)
        if not face or face.get("texture") is None:
            continue
        u0,v0,u1,v1 = map(float, face.get("uv", [0,0,0,0]))
        add_face(points, [(u0,v0),(u1,v0),(u1,v1),(u0,v1)],
                 face.get("texture"), triangles)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o", "--output", type=Path, default=Path("warden_av_v11.mesh.json"))
    args = ap.parse_args()
    model = json.loads(args.input.read_text(encoding="utf-8"))
    triangles = []
    elements = model.get("elements", [])
    transforms = hierarchy_transforms(model)
    for element in elements:
        element_transforms = transforms.get(element.get("uuid"), element_transform(element))
        if element.get("type") == "mesh" or "vertices" in element:
            convert_mesh(element, triangles, element_transforms)
        elif element.get("type") == "cube" or ("from" in element and "to" in element):
            convert_cube(element, triangles, element_transforms)
    if not triangles:
        raise SystemExit("No supported mesh/cube faces found")
    out = {"format":"maxtac-triangles-v2", "source":args.input.name,
           "resolution":model.get("resolution", {"width":512,"height":512}),
           "triangle_count":len(triangles), "triangles":triangles}
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(out, separators=(",",":")), encoding="utf-8")
    print(f"Wrote {len(triangles)} triangles to {args.output}")


if __name__ == "__main__":
    main()
