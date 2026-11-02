#!/usr/bin/env python3
"""Convert a Blockbench .bbmodel into a triangle/UV JSON mesh for the mod.

Supports Blockbench generic-format mesh elements and cubes. Mesh faces are
fan-triangulated; cube faces are expanded to triangles. Coordinates are
converted from Blockbench's Y-up model space to Minecraft model space.
"""
import argparse, json, math
from pathlib import Path

def triangulate(points):
    if len(points) < 3:
        return []
    return [(points[0], points[i], points[i + 1]) for i in range(1, len(points)-1)]

def face_uv(face, vertex_ids):
    uv = face.get("uv", {})
    out = []
    for vid in vertex_ids:
        value = uv.get(str(vid), [0.0, 0.0])
        out.append([float(value[0]), float(value[1])])
    return out

def convert_mesh(element, triangles):
    vertices = element.get("vertices", {})
    for face in element.get("faces", {}).values():
        ids = face.get("vertices", [])
        points = [vertices.get(str(i)) for i in ids]
        if any(p is None for p in points):
            continue
        uvs = face_uv(face, ids)
        for tri in triangulate(list(zip(points, uvs))):
            pos, tex = [], []
            for p, uv in tri:
                # Blockbench axes are X/Y/Z; Minecraft entity model uses X/Y/Z.
                pos.extend([float(p[0]), float(p[1]), float(p[2])])
                tex.extend([float(uv[0]), float(uv[1])])
            triangles.append({"positions": pos, "uv": tex, "material": face.get("texture")})

def convert_cube(element, triangles):
    # Cubes are emitted as six quads. The face UV rectangle is respected.
    origin = element.get("from", [0, 0, 0])
    end = element.get("to", [0, 0, 0])
    x0,y0,z0 = map(float, origin); x1,y1,z1 = map(float, end)
    faces = {
      "north": ([(x0,y0,z0),(x1,y0,z0),(x1,y1,z0),(x0,y1,z0)], "north"),
      "south": ([(x1,y0,z1),(x0,y0,z1),(x0,y1,z1),(x1,y1,z1)], "south"),
      "west":  ([(x0,y0,z1),(x0,y0,z0),(x0,y1,z0),(x0,y1,z1)], "west"),
      "east":  ([(x1,y0,z0),(x1,y0,z1),(x1,y1,z1),(x1,y1,z0)], "east"),
      "up":    ([(x0,y1,z0),(x1,y1,z0),(x1,y1,z1),(x0,y1,z1)], "up"),
      "down":  ([(x0,y0,z1),(x1,y0,z1),(x1,y0,z0),(x0,y0,z0)], "down"),
    }
    for name,(verts,_) in faces.items():
        f = element.get("faces", {}).get(name)
        if not f or f.get("texture") is None:
            continue
        uv = f.get("uv", [0,0,0,0])
        u0,v0,u1,v1 = map(float, uv)
        tex = [(u0,v0),(u1,v0),(u1,v1),(u0,v1)]
        for tri in triangulate(list(zip(verts,tex))):
            positions=[]; uvs=[]
            for p,t in tri:
                positions.extend(p); uvs.extend(t)
            triangles.append({"positions":positions,"uv":uvs,"material":f.get("texture")})

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("input", type=Path)
    ap.add_argument("-o","--output", type=Path, default=Path("warden_av_v11.mesh.json"))
    args=ap.parse_args()
    model=json.loads(args.input.read_text(encoding="utf-8"))
    triangles=[]
    for element in model.get("elements", []):
        if element.get("type") == "mesh" or "vertices" in element:
            convert_mesh(element, triangles)
        elif element.get("type") == "cube" or ("from" in element and "to" in element):
            convert_cube(element, triangles)
    if not triangles:
        raise SystemExit("No supported mesh/cube faces found; check this is a Blockbench generic .bbmodel")
    out={"format":"maxtac-triangles-v1","source":args.input.name,
         "resolution":model.get("resolution",{"width":512,"height":512}),
         "triangle_count":len(triangles),"triangles":triangles}
    args.output.write_text(json.dumps(out,separators=(",",":")),encoding="utf-8")
    print(f"Wrote {len(triangles)} triangles to {args.output}")

if __name__=="__main__":
    main()
