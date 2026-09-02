"""
Generates a clean readable 2.5D player sprite for the Godot validation harness.
"""

from pathlib import Path
from PIL import Image, ImageDraw

GODOT_DIR = Path(__file__).resolve().parent.parent / "godot"
GODOT_DIR.mkdir(parents=True, exist_ok=True)

# 48x64 player sprite
w, h = 48, 64
img = Image.new("RGBA", (w, h), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# 1. Soft contact shadow at feet (centered at x=24, y=58)
draw.ellipse([10, 54, 38, 62], fill=(20, 20, 20, 110))

# 2. Boots & Legs
draw.rectangle([16, 44, 22, 56], fill=(50, 40, 30))
draw.rectangle([26, 44, 32, 56], fill=(50, 40, 30))

# 3. Tunic / Body (Deep navy blue with leather belt)
draw.rectangle([14, 24, 34, 46], fill=(30, 58, 100))
draw.rectangle([13, 36, 35, 40], fill=(130, 85, 45)) # Belt
draw.rectangle([22, 36, 26, 40], fill=(230, 190, 60)) # Buckle

# 4. Red Adventurer Cloak / Scarf
draw.polygon([(12, 22), (36, 22), (38, 38), (10, 38)], fill=(195, 45, 45))

# 5. Head & Hair (Warm skin tone, dark brown hair)
draw.ellipse([16, 8, 32, 24], fill=(240, 200, 160)) # Face
draw.ellipse([15, 6, 33, 16], fill=(70, 45, 30))   # Hair cap
# Eyes
draw.rectangle([19, 14, 21, 17], fill=(30, 30, 30))
draw.rectangle([27, 14, 29, 17], fill=(30, 30, 30))

out_path = GODOT_DIR / "player.png"
img.save(out_path)
print(f"--> Saved {out_path.name}")
