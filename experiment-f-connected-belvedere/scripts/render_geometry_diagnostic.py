"""Render a review overlay for both Experiment F nodes."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont


ROOT = Path(__file__).resolve().parent.parent


def render_node(art_name: str, geometry_name: str, output_name: str, portal: tuple[int, int], portal_radius: int) -> None:
    image = Image.open(ROOT / "assets" / art_name).convert("RGBA")
    geometry = json.loads((ROOT / "data" / geometry_name).read_text(encoding="utf-8"))
    overlay = Image.new("RGBA", image.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    boundary = [tuple(point) for point in geometry["walkable_boundary"]]
    route = [tuple(point) for point in geometry["tested_route"]["waypoints"]]
    draw.polygon(boundary, fill=(20, 205, 240, 45), outline=(20, 230, 255, 255), width=4)
    draw.line(route, fill=(255, 220, 35, 255), width=4, joint="curve")
    for x, y in route:
        draw.ellipse((x - 6, y - 6, x + 6, y + 6), fill=(255, 220, 35, 255))
    x, y = portal
    draw.ellipse((x - portal_radius, y - portal_radius, x + portal_radius, y + portal_radius), fill=(255, 170, 20, 55), outline=(255, 170, 20, 255), width=4)
    draw.text((24, 116), f"{geometry_name}: cyan=walkable, yellow=test route, orange=portal", fill=(255, 255, 255, 255), stroke_width=2, stroke_fill=(0, 0, 0, 255), font=ImageFont.load_default(size=18))
    Image.alpha_composite(image, overlay).convert("RGB").save(ROOT / "diagnostics" / output_name)


def main() -> int:
    (ROOT / "diagnostics").mkdir(parents=True, exist_ok=True)
    render_node("piazza.png", "node_001_geometry.json", "piazza_geometry_overlay.png", (1095, 655), 28)
    render_node("belvedere.png", "node_002_geometry.json", "belvedere_geometry_overlay.png", (836, 902), 28)
    print("Rendered Experiment F geometry overlays")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
