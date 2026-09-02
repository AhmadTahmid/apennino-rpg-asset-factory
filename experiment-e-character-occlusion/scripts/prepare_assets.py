"""Build and verify Experiment E's deterministic gameplay art derivatives.

The image model returned visually convincing sprite sheets with a baked
checkerboard instead of alpha.  Both originals remain untouched under
``assets/source``.  This script performs the disclosed mechanical work:

1. flood-fill the border-connected near-neutral checkerboard;
2. normalize the twelve frames into a 3 x 4 atlas of 48 x 64 cells;
3. extract one sparse, full-canvas foreground layer from the locked scene;
4. emit fail-capable structural and pixel-provenance diagnostics.
"""

from __future__ import annotations

from collections import deque
import colorsys
import hashlib
import json
import math
from pathlib import Path

from PIL import Image, ImageDraw


ROOT = Path(__file__).resolve().parent.parent
SOURCE_SHEET = ROOT / "assets" / "source" / "traveler_generated_checkerboard.png"
SCENE = ROOT / "assets" / "control_01.png"
ATLAS = ROOT / "assets" / "traveler_walk_sheet.png"
CONTACT_SHEET = ROOT / "diagnostics" / "traveler_contact_sheet.png"
MASK = ROOT / "assets" / "southwest_planter_mask.png"
FOREGROUND = ROOT / "assets" / "southwest_planter_foreground.png"
OCCLUDER_REVIEW = ROOT / "diagnostics" / "southwest_planter_mask_review.png"
OCCLUSION_REVIEW = ROOT / "diagnostics" / "occlusion_design_review.png"
REPORT = ROOT / "diagnostics" / "asset_preflight.json"

CELL_SIZE = (48, 64)
GRID = (3, 4)
ROW_LABELS = ("down / south", "left / west", "right / east", "up / north")
FOOT_BASELINE_Y = 60
MAX_SUBJECT_SIZE = (40, 52)
# The generator honored three columns but left asymmetric vertical canvas
# margins.  These boundaries are preregistered whitespace midlines between
# complete rows; equal-height slicing would clip the north-facing hair.
SOURCE_ROW_EDGES = (0, 397, 754, 1106, 1578)

OCCLUDER_POLYGON = (
    (668, 645),
    (681, 638),
    (697, 640),
    (710, 648),
    (720, 661),
    (722, 676),
    (717, 691),
    (708, 703),
    (691, 706),
    (677, 697),
    (669, 684),
    (665, 663),
)
OCCLUSION_ANCHOR = (704, 675)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest().upper()


def flood_checkerboard(image: Image.Image) -> Image.Image:
    """Return RGBA pixels with border-connected checkerboard made transparent."""

    rgb = image.convert("RGB")
    width, height = rgb.size
    pixels = rgb.load()
    alpha = Image.new("L", rgb.size, 255)
    alpha_pixels = alpha.load()
    seen = bytearray(width * height)
    queue: deque[tuple[int, int]] = deque()

    def candidate(x: int, y: int) -> bool:
        red, green, blue = pixels[x, y]
        # The generated background is a connected 239-254 neutral checkerboard.
        # A relaxed threshold also removes its pale edge fringe; the character's
        # one-pixel dark contour prevents this fill entering cream clothing.
        return min(red, green, blue) >= 178 and max(red, green, blue) - min(red, green, blue) <= 30

    for x in range(width):
        if candidate(x, 0):
            queue.append((x, 0))
        if candidate(x, height - 1):
            queue.append((x, height - 1))
    for y in range(height):
        if candidate(0, y):
            queue.append((0, y))
        if candidate(width - 1, y):
            queue.append((width - 1, y))

    while queue:
        x, y = queue.popleft()
        offset = y * width + x
        if seen[offset] or not candidate(x, y):
            continue
        seen[offset] = 1
        alpha_pixels[x, y] = 0
        if x:
            queue.append((x - 1, y))
        if x + 1 < width:
            queue.append((x + 1, y))
        if y:
            queue.append((x, y - 1))
        if y + 1 < height:
            queue.append((x, y + 1))

    result = rgb.convert("RGBA")
    result.putalpha(alpha)
    return result


def keep_largest_alpha_component(frame: Image.Image) -> Image.Image:
    """Discard disconnected checkerboard remnants while preserving one figure."""

    alpha = frame.getchannel("A")
    width, height = alpha.size
    alpha_pixels = alpha.load()
    seen = bytearray(width * height)
    largest: list[tuple[int, int]] = []
    for start_y in range(height):
        for start_x in range(width):
            offset = start_y * width + start_x
            if seen[offset] or alpha_pixels[start_x, start_y] == 0:
                continue
            component: list[tuple[int, int]] = []
            queue: deque[tuple[int, int]] = deque([(start_x, start_y)])
            while queue:
                x, y = queue.popleft()
                offset = y * width + x
                if seen[offset] or alpha_pixels[x, y] == 0:
                    continue
                seen[offset] = 1
                component.append((x, y))
                for dx, dy in (
                    (-1, -1), (0, -1), (1, -1),
                    (-1, 0),           (1, 0),
                    (-1, 1),  (0, 1),  (1, 1),
                ):
                    nx = x + dx
                    ny = y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        queue.append((nx, ny))
            if len(component) > len(largest):
                largest = component

    cleaned_alpha = Image.new("L", frame.size, 0)
    cleaned_pixels = cleaned_alpha.load()
    for x, y in largest:
        cleaned_pixels[x, y] = alpha_pixels[x, y]
    cleaned = frame.copy()
    cleaned.putalpha(cleaned_alpha)
    return cleaned


def build_atlas() -> tuple[Image.Image, list[dict]]:
    source = flood_checkerboard(Image.open(SOURCE_SHEET))
    source_width, source_height = source.size
    atlas = Image.new("RGBA", (CELL_SIZE[0] * GRID[0], CELL_SIZE[1] * GRID[1]), (0, 0, 0, 0))
    frame_reports: list[dict] = []

    for row in range(GRID[1]):
        if source_height != SOURCE_ROW_EDGES[-1]:
            raise RuntimeError(
                f"Generated sheet height changed: {source_height}; expected {SOURCE_ROW_EDGES[-1]}"
            )
        top = SOURCE_ROW_EDGES[row]
        bottom = SOURCE_ROW_EDGES[row + 1]
        for column in range(GRID[0]):
            left = round(column * source_width / GRID[0])
            right = round((column + 1) * source_width / GRID[0])
            frame = keep_largest_alpha_component(source.crop((left, top, right, bottom)))
            bbox = frame.getchannel("A").getbbox()
            if bbox is None:
                raise RuntimeError(f"Empty generated frame at row {row}, column {column}")
            subject = frame.crop(bbox)
            scale = min(MAX_SUBJECT_SIZE[0] / subject.width, MAX_SUBJECT_SIZE[1] / subject.height)
            resized_size = (
                max(1, round(subject.width * scale)),
                max(1, round(subject.height * scale)),
            )
            subject = subject.resize(resized_size, Image.Resampling.NEAREST)
            paste_x = column * CELL_SIZE[0] + (CELL_SIZE[0] - subject.width) // 2
            paste_y = row * CELL_SIZE[1] + FOOT_BASELINE_Y - subject.height
            atlas.alpha_composite(subject, (paste_x, paste_y))

            frame_cell = atlas.crop(
                (
                    column * CELL_SIZE[0],
                    row * CELL_SIZE[1],
                    (column + 1) * CELL_SIZE[0],
                    (row + 1) * CELL_SIZE[1],
                )
            )
            final_bbox = frame_cell.getchannel("A").getbbox()
            assert final_bbox is not None
            frame_reports.append(
                {
                    "row": row,
                    "column": column,
                    "semantic_row": ROW_LABELS[row],
                    "source_cell": [left, top, right, bottom],
                    "source_subject_bbox": list(bbox),
                    "final_subject_bbox": list(final_bbox),
                    "foot_baseline_y": final_bbox[3] - 1,
                    "pixel_sha256": hashlib.sha256(frame_cell.tobytes()).hexdigest().upper(),
                }
            )

    ATLAS.parent.mkdir(parents=True, exist_ok=True)
    atlas.save(ATLAS, optimize=False)
    return atlas, frame_reports


def make_contact_sheet(atlas: Image.Image) -> None:
    scale = 4
    label_height = 26
    panel_width = CELL_SIZE[0] * GRID[0] * scale
    panel_height = (CELL_SIZE[1] * scale + label_height) * GRID[1]
    sheet = Image.new("RGB", (panel_width, panel_height), (28, 30, 32))
    draw = ImageDraw.Draw(sheet)
    checker = Image.new("RGB", (CELL_SIZE[0] * GRID[0], CELL_SIZE[1]), (216, 216, 216))
    checker_pixels = checker.load()
    for y in range(checker.height):
        for x in range(checker.width):
            if ((x // 8) + (y // 8)) % 2:
                checker_pixels[x, y] = (242, 242, 242)
    for row, label in enumerate(ROW_LABELS):
        target_y = row * (CELL_SIZE[1] * scale + label_height)
        draw.text((8, target_y + 6), f"row {row}: {label} | frames 0, 1 (idle), 2", fill=(245, 220, 138))
        row_atlas = atlas.crop((0, row * CELL_SIZE[1], atlas.width, (row + 1) * CELL_SIZE[1]))
        composed = checker.convert("RGBA")
        composed.alpha_composite(row_atlas)
        enlarged = composed.convert("RGB").resize((panel_width, CELL_SIZE[1] * scale), Image.Resampling.NEAREST)
        sheet.paste(enlarged, (0, target_y + label_height))
        for column in range(1, GRID[0]):
            x = column * CELL_SIZE[0] * scale
            draw.line((x, target_y + label_height, x, target_y + label_height + CELL_SIZE[1] * scale), fill=(255, 190, 70), width=1)
    CONTACT_SHEET.parent.mkdir(parents=True, exist_ok=True)
    sheet.save(CONTACT_SHEET)


def point_segment_distance(point: tuple[int, int], start: tuple[int, int], end: tuple[int, int]) -> float:
    px, py = point
    x1, y1 = start
    x2, y2 = end
    dx = x2 - x1
    dy = y2 - y1
    if dx == 0 and dy == 0:
        return math.hypot(px - x1, py - y1)
    t = max(0.0, min(1.0, ((px - x1) * dx + (py - y1) * dy) / (dx * dx + dy * dy)))
    nearest_x = x1 + t * dx
    nearest_y = y1 + t * dy
    return math.hypot(px - nearest_x, py - nearest_y)


def build_occluder() -> dict:
    scene = Image.open(SCENE).convert("RGBA")
    envelope = Image.new("L", scene.size, 0)
    ImageDraw.Draw(envelope).polygon(OCCLUDER_POLYGON, fill=255)
    envelope_pixels = envelope.load()
    source_pixels = scene.load()
    mask = Image.new("L", scene.size, 0)
    mask_pixels = mask.load()

    min_x = min(point[0] for point in OCCLUDER_POLYGON)
    max_x = max(point[0] for point in OCCLUDER_POLYGON)
    min_y = min(point[1] for point in OCCLUDER_POLYGON)
    max_y = max(point[1] for point in OCCLUDER_POLYGON)
    rail_segments = (
        ((665, 652), (716, 683)),
        ((670, 655), (670, 694)),
        ((709, 673), (709, 704)),
    )
    pot_polygon = ((684, 671), (713, 674), (710, 704), (689, 705))
    pot_region = Image.new("L", scene.size, 0)
    ImageDraw.Draw(pot_region).polygon(pot_polygon, fill=255)
    pot_pixels = pot_region.load()

    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if envelope_pixels[x, y] == 0:
                continue
            red, green, blue, _ = source_pixels[x, y]
            high = max(red, green, blue)
            low = min(red, green, blue)
            chroma = high - low
            hue, saturation, _ = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
            hue_degrees = hue * 360
            # Pale limestone and grout are intentionally excluded even when
            # they fall inside the reviewed envelope.  The retained object
            # palette has olive-green or flower/terracotta hue, unlike paving.
            green_object = 42 <= hue_degrees <= 165 and saturation >= 0.28 and high <= 210 and y >= 646
            warm_object = (hue_degrees <= 35 or hue_degrees >= 340) and saturation >= 0.34 and high <= 220 and y >= 648
            dark_foliage = high <= 108 and chroma >= 16 and y >= 652
            pot_pixel = pot_pixels[x, y] and warm_object and high <= 190
            rail_pixel = high <= 142 and any(
                point_segment_distance((x, y), start, end) <= 2.25
                for start, end in rail_segments
            )
            if green_object or warm_object or dark_foliage or pot_pixel or rail_pixel:
                mask_pixels[x, y] = 255

    # One color-aware growth pass retains exact antialiased edge pixels without
    # copying the pale cobblestone through holes in the railing or foliage.
    grown = mask.copy()
    grown_pixels = grown.load()
    for y in range(min_y, max_y + 1):
        for x in range(min_x, max_x + 1):
            if mask_pixels[x, y] or envelope_pixels[x, y] == 0:
                continue
            red, green, blue, _ = source_pixels[x, y]
            high = max(red, green, blue)
            low = min(red, green, blue)
            adjacent = any(
                0 <= x + dx < scene.width
                and 0 <= y + dy < scene.height
                and mask_pixels[x + dx, y + dy]
                for dx, dy in ((-1, 0), (1, 0), (0, -1), (0, 1))
            )
            chroma = high - low
            hue, saturation, _ = colorsys.rgb_to_hsv(red / 255, green / 255, blue / 255)
            hue_degrees = hue * 360
            semantic_color = (
                (42 <= hue_degrees <= 165 and saturation >= 0.20)
                or ((hue_degrees <= 35 or hue_degrees >= 340) and saturation >= 0.27)
            )
            near_rail = any(
                point_segment_distance((x, y), start, end) <= 3.25
                for start, end in rail_segments
            )
            if adjacent and (
                (semantic_color and high <= 225)
                or (high <= 120 and chroma >= 12 and y >= 652)
                or (near_rail and high <= 156)
            ):
                grown_pixels[x, y] = 255
    # Retain the single connected planter/foliage/rail object.  This rejects
    # isolated chromatic compression flecks in the surrounding limestone.
    component_holder = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    component_holder.putalpha(grown)
    mask = keep_largest_alpha_component(component_holder).getchannel("A")

    # Zero RGB under transparent pixels so the full-canvas identity-aligned
    # layer stays compact and does not retain invisible scene data.
    foreground = Image.new("RGBA", scene.size, (0, 0, 0, 0))
    foreground.paste(scene, (0, 0), mask)
    MASK.parent.mkdir(parents=True, exist_ok=True)
    mask.save(MASK, optimize=False)
    foreground.save(FOREGROUND, optimize=False)

    histogram = mask.histogram()
    opaque_count = sum(histogram[1:])
    bbox = mask.getbbox()
    if bbox is None:
        raise RuntimeError("Foreground mask is empty")

    source_rgb = scene.convert("RGB")
    foreground_rgb = foreground.convert("RGB")
    equal_count = 0
    mismatch_count = 0
    for y in range(bbox[1], bbox[3]):
        for x in range(bbox[0], bbox[2]):
            if mask.getpixel((x, y)):
                if source_rgb.getpixel((x, y)) == foreground_rgb.getpixel((x, y)):
                    equal_count += 1
                else:
                    mismatch_count += 1

    make_occluder_review(scene, mask, foreground, bbox)
    return {
        "declared_outer_polygon": [list(point) for point in OCCLUDER_POLYGON],
        "occlusion_anchor": list(OCCLUSION_ANCHOR),
        "alpha_bbox": list(bbox),
        "opaque_pixel_count": opaque_count,
        "full_canvas_pixel_count": scene.width * scene.height,
        "alpha_occupancy_fraction": opaque_count / (scene.width * scene.height),
        "source_equal_nontransparent_pixels": equal_count,
        "source_mismatch_nontransparent_pixels": mismatch_count,
    }


def make_occluder_review(scene: Image.Image, mask: Image.Image, foreground: Image.Image, bbox: tuple[int, int, int, int]) -> None:
    padding = 12
    crop_box = (
        max(0, bbox[0] - padding),
        max(0, bbox[1] - padding),
        min(scene.width, bbox[2] + padding),
        min(scene.height, bbox[3] + padding),
    )
    source_crop = scene.crop(crop_box).convert("RGB")
    mask_crop = mask.crop(crop_box)
    overlay = source_crop.copy()
    overlay_pixels = overlay.load()
    for y in range(overlay.height):
        for x in range(overlay.width):
            red, green, blue = overlay_pixels[x, y]
            if mask_crop.getpixel((x, y)):
                overlay_pixels[x, y] = (min(255, red // 2 + 128), green // 3, min(255, blue // 2 + 128))
            else:
                overlay_pixels[x, y] = (red // 3, green // 3, blue // 3)

    checker = Image.new("RGBA", source_crop.size, (215, 215, 215, 255))
    checker_pixels = checker.load()
    for y in range(checker.height):
        for x in range(checker.width):
            if ((x // 6) + (y // 6)) % 2:
                checker_pixels[x, y] = (245, 245, 245, 255)
    foreground_crop = foreground.crop(crop_box)
    checker.alpha_composite(foreground_crop)

    scale = 5
    panels = [source_crop, overlay, checker.convert("RGB")]
    canvas = Image.new("RGB", (source_crop.width * scale * 3, source_crop.height * scale + 24), (25, 25, 25))
    draw = ImageDraw.Draw(canvas)
    labels = ("locked source crop", "selected alpha pixels", "transparent extraction")
    for index, (panel, label) in enumerate(zip(panels, labels, strict=True)):
        x = index * source_crop.width * scale
        draw.text((x + 5, 5), label, fill=(246, 218, 126))
        enlarged = panel.resize((source_crop.width * scale, source_crop.height * scale), Image.Resampling.NEAREST)
        canvas.paste(enlarged, (x, 24))
    OCCLUDER_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OCCLUDER_REVIEW)


def make_occlusion_design_review(atlas: Image.Image) -> None:
    """Show the preregistered pose with correct and deliberately wrong order."""

    scene = Image.open(SCENE).convert("RGBA")
    foreground = Image.open(FOREGROUND).convert("RGBA")
    idle = atlas.crop((48, 0, 96, 64))
    player_top_left = (OCCLUSION_ANCHOR[0] - 24, OCCLUSION_ANCHOR[1] - 64)

    correct = scene.copy()
    correct.alpha_composite(idle, player_top_left)
    correct.alpha_composite(foreground)
    wrong = scene.copy()
    wrong.alpha_composite(foreground)
    wrong.alpha_composite(idle, player_top_left)

    crop_box = (640, 590, 760, 720)
    panels = [scene.crop(crop_box), correct.crop(crop_box), wrong.crop(crop_box)]
    labels = ("locked source", "correct: planter above", "mutation: player above")
    scale = 4
    label_height = 24
    panel_width = panels[0].width * scale
    panel_height = panels[0].height * scale
    canvas = Image.new("RGB", (panel_width * 3, panel_height + label_height), (24, 24, 24))
    draw = ImageDraw.Draw(canvas)
    for index, (panel, label) in enumerate(zip(panels, labels, strict=True)):
        x = index * panel_width
        draw.text((x + 5, 5), label, fill=(246, 218, 126))
        enlarged = panel.convert("RGB").resize((panel_width, panel_height), Image.Resampling.NEAREST)
        canvas.paste(enlarged, (x, label_height))
    OCCLUSION_REVIEW.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(OCCLUSION_REVIEW)


def verify_atlas(atlas: Image.Image, frames: list[dict]) -> list[str]:
    failures: list[str] = []
    if atlas.mode != "RGBA":
        failures.append(f"Atlas mode is {atlas.mode}, expected RGBA")
    if atlas.size != (144, 256):
        failures.append(f"Atlas size is {atlas.size}, expected (144, 256)")
    alpha = atlas.getchannel("A")
    border_points = []
    for x in range(atlas.width):
        border_points.extend((alpha.getpixel((x, 0)), alpha.getpixel((x, atlas.height - 1))))
    for y in range(atlas.height):
        border_points.extend((alpha.getpixel((0, y)), alpha.getpixel((atlas.width - 1, y))))
    if any(border_points):
        failures.append("Atlas outer border is not fully transparent")
    if len(frames) != 12:
        failures.append(f"Atlas has {len(frames)} reported frames, expected 12")
    for row in range(GRID[1]):
        row_frames = [frame for frame in frames if frame["row"] == row]
        if len({frame["pixel_sha256"] for frame in row_frames}) != 3:
            failures.append(f"Row {row} does not contain three distinct frame hashes")
        baselines = [frame["foot_baseline_y"] for frame in row_frames]
        if max(baselines) - min(baselines) > 1:
            failures.append(f"Row {row} foot baselines differ by more than one pixel: {baselines}")
    return failures


def main() -> int:
    ROOT.joinpath("diagnostics").mkdir(parents=True, exist_ok=True)
    atlas, frames = build_atlas()
    make_contact_sheet(atlas)
    occluder = build_occluder()
    make_occlusion_design_review(atlas)
    failures = verify_atlas(atlas, frames)
    if occluder["source_mismatch_nontransparent_pixels"]:
        failures.append("Foreground contains non-source RGB pixels")
    if not (0 < occluder["alpha_occupancy_fraction"] < 0.002):
        failures.append("Foreground alpha occupancy is empty or implausibly broad")

    report = {
        "passed": not failures,
        "failures": failures,
        "pipeline": "deterministic checkerboard flood extraction + nearest-neighbor atlas normalization + sparse exact-source foreground mask",
        "source_sheet": {
            "path": str(SOURCE_SHEET.relative_to(ROOT)),
            "sha256": digest(SOURCE_SHEET),
            "dimensions": list(Image.open(SOURCE_SHEET).size),
            "mode": Image.open(SOURCE_SHEET).mode,
        },
        "atlas": {
            "path": str(ATLAS.relative_to(ROOT)),
            "sha256": digest(ATLAS),
            "dimensions": list(atlas.size),
            "mode": atlas.mode,
            "grid": list(GRID),
            "cell_size": list(CELL_SIZE),
            "row_semantics": list(ROW_LABELS),
            "idle_column": 1,
            "frame_order": [0, 1, 2, 1],
            "frames": frames,
        },
        "occluder": {
            **occluder,
            "source_scene_sha256": digest(SCENE),
            "mask_path": str(MASK.relative_to(ROOT)),
            "mask_sha256": digest(MASK),
            "foreground_path": str(FOREGROUND.relative_to(ROOT)),
            "foreground_sha256": digest(FOREGROUND),
            "alignment": "full-canvas 1672x941; identity transform; integer aligned",
        },
    }
    REPORT.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
