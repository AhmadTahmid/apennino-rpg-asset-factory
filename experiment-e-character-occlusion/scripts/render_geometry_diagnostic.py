"""Render unchanged gameplay geometry plus Experiment E's local occluder."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent
ART = ROOT / "assets" / "control_01.png"
GEOMETRY = ROOT / "data" / "node_001_geometry.json"
OCCLUSION = ROOT / "data" / "occlusion_spec.json"
OCCLUDER_MASK = ROOT / "assets" / "southwest_planter_mask.png"
OUTPUT = ROOT / "diagnostics" / "geometry_overlay.png"


def main() -> int:
    geometry = json.loads(GEOMETRY.read_text(encoding="utf-8"))
    occlusion = json.loads(OCCLUSION.read_text(encoding="utf-8"))
    image = Image.open(ART).convert("RGBA")
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    font = ImageFont.load_default(size=18)

    boundary = [tuple(point) for point in geometry["walkable_boundary"]]
    draw.polygon(boundary, fill=(20, 210, 245, 45), outline=(40, 235, 255, 255), width=4)

    mask = Image.open(OCCLUDER_MASK).convert("L")
    mask_tint = Image.new("RGBA", image.size, (255, 35, 210, 0))
    mask_tint.putalpha(mask.point(lambda value: 105 if value else 0))
    overlay = Image.alpha_composite(overlay, mask_tint)
    draw = ImageDraw.Draw(overlay)

    occluder_polygon = [tuple(point) for point in occlusion["object"]["review_envelope_polygon"]]
    draw.line(occluder_polygon + [occluder_polygon[0]], fill=(255, 50, 220, 255), width=3, joint="curve")
    anchor_x, anchor_y = occlusion["render_contract"]["preregistered_player_footpoint"]
    draw.ellipse((anchor_x - 9, anchor_y - 9, anchor_x + 9, anchor_y + 9), fill=(255, 40, 220, 255), outline=(255, 255, 255, 255), width=2)
    draw.text((anchor_x + 14, anchor_y + 9), "OCCLUSION POSE", fill=(255, 255, 255, 255), font=font, stroke_width=2, stroke_fill=(70, 0, 55, 255))

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
