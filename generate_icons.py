import os
from PIL import Image

ICON_SRC = "assets/icon-only.png"
RES_DIR = "android/app/src/main/res"
BG_COLOR = "#FFFFFF"

DENSITIES = {
    "mipmap-mdpi": (48, 108),
    "mipmap-hdpi": (72, 162),
    "mipmap-xhdpi": (96, 216),
    "mipmap-xxhdpi": (144, 324),
    "mipmap-xxxhdpi": (192, 432),
}

def make_adaptive_foreground(src_img, canvas_size):
    # Safe zone is 66/108 (~61%) of adaptive icon canvas
    safe_size = int(canvas_size * 0.64)
    resized = src_img.resize((safe_size, safe_size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
    offset = (canvas_size - safe_size) // 2
    canvas.paste(resized, (offset, offset), resized)
    return canvas

def make_legacy_square(src_img, size, bg_hex):
    bg = Image.new("RGBA", (size, size), bg_hex)
    resized = src_img.resize((size, size), Image.Resampling.LANCZOS)
    bg.paste(resized, (0, 0), resized)
    return bg

def main():
    if not os.path.exists(ICON_SRC):
        print("Icon source not found, skipping.")
        return

    src = Image.open(ICON_SRC).convert("RGBA")

    for folder, (legacy_px, adaptive_px) in DENSITIES.items():
        out_dir = os.path.join(RES_DIR, folder)
        os.makedirs(out_dir, exist_ok=True)

        legacy = make_legacy_square(src, legacy_px, BG_COLOR)
        legacy.save(os.path.join(out_dir, "ic_launcher.png"), "PNG")
        legacy.save(os.path.join(out_dir, "ic_launcher_round.png"), "PNG")

        fg = make_adaptive_foreground(src, adaptive_px)
        fg.save(os.path.join(out_dir, "ic_launcher_foreground.png"), "PNG")

    values_dir = os.path.join(RES_DIR, "values")
    os.makedirs(values_dir, exist_ok=True)
    with open(os.path.join(values_dir, "ic_launcher_background.xml"), "w", encoding="utf-8") as f:
        f.write(f'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="ic_launcher_background">{BG_COLOR}</color>
</resources>
''')

    anydpi_dir = os.path.join(RES_DIR, "mipmap-anydpi-v26")
    os.makedirs(anydpi_dir, exist_ok=True)
    adaptive_xml = '''<?xml version="1.0" encoding="utf-8"?>
<adaptive-icon xmlns:android="http://schemas.android.com/apk/res/android">
    <background android:drawable="@color/ic_launcher_background"/>
    <foreground android:drawable="@mipmap/ic_launcher_foreground"/>
</adaptive-icon>
'''
    with open(os.path.join(anydpi_dir, "ic_launcher.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_xml)
    with open(os.path.join(anydpi_dir, "ic_launcher_round.xml"), "w", encoding="utf-8") as f:
        f.write(adaptive_xml)

    print("Android Adaptive & Legacy Icons generated successfully.")

if __name__ == "__main__":
    main()
