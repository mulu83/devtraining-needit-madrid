"""
Run once to generate the PWA icons: python static/generate_icons.py
Requires: pip install Pillow
"""
from pathlib import Path
from PIL import Image, ImageDraw

SIZES = [192, 512]
OUT = Path(__file__).parent / "icons"
OUT.mkdir(exist_ok=True)

for size in SIZES:
    img = Image.new("RGB", (size, size), "#003087")
    draw = ImageDraw.Draw(img)
    # Simple "AI" text mark
    font_size = size // 3
    draw.text((size * 0.18, size * 0.28), "AI", fill="white",
              font=None)  # uses default bitmap font — replace with TTF for production
    img.save(OUT / f"icon-{size}.png")
    print(f"Created icon-{size}.png")
