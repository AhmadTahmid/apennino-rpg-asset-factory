"""Render the manually authored gameplay geometry over the untouched scene art."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "control_01.png"
GEOMETRY = ROOT / "data" / "node_001_geometry.json"
OUTPUT = ROOT / "diagnostics" / "geometry_overlay.png"


def main() -> int:
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    image = Image.open(ART).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default(size=18)

    boundary = [tuple(point) for point in geometry["walkable_boundary"]]
    draw.polygon(boundary, fill=(20, 210, 245, 45), outline=(40, 235, 255, 255), width=4)

    fountain = geometry["obstacles"][0]
    cx, cy = fountain["center"]
    rx, ry = fountain["radii"]
    draw.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), fill=(255, 40, 55, 55), outline=(255, 55, 65, 255), width=4)
    draw.text((cx - 72, cy - 10), "FOUNTAIN SOLID", fill=(255, 255, 255, 255), font=font, stroke_width=2, stroke_fill=(80, 0, 0, 255))

    route = [tuple(point) for point in geometry["tested_route"]["waypoints"]]
    draw.line(route, fill=(255, 220, 35, 255), width=5, joint="curve")
    for index, point in enumerate(route):
        x, y = point
        draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=(255, 220, 35, 255), outline=(30, 30, 30, 255), width=2)
        draw.text((x + 11, y - 13), str(index), fill=(255, 255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0, 255))

    sx, sy = geometry["player"]["spawn"]
    draw.ellipse((sx - 14, sy - 14, sx + 14, sy + 14), fill=(60, 255, 100, 255), outline=(255, 255, 255, 255), width=3)
    draw.text((sx + 18, sy + 8), "SPAWN", fill=(255, 255, 255, 255), font=font, stroke_width=2, stroke_fill=(0, 0, 0, 255))

    for closed in geometry["closed_for_this_experiment"]:
        x, y = closed["anchor"]
        draw.line((x - 12, y - 12, x + 12, y + 12), fill=(255, 80, 190, 255), width=5)
        draw.line((x - 12, y + 12, x + 12, y - 12), fill=(255, 80, 190, 255), width=5)
        draw.text((x + 16, y - 10), "CLOSED: " + closed["id"], fill=(255, 255, 255, 255), font=font, stroke_width=2, stroke_fill=(70, 0, 50, 255))

    output = Image.alpha_composite(image, overlay).convert("RGB")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    output.save(OUTPUT, quality=95)
    print(OUTPUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
