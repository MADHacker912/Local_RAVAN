#!/usr/bin/env python3
# ravan ke cyber pixel art logo ko generate karne wali script

import os
from PIL import Image, ImageDraw

def create_ravan_pixel_logo(scale: int = 16) -> str:
    # 32 by 32 pixel grid ka canvas setup
    grid_size = 32
    img = Image.new("RGBA", (grid_size, grid_size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # retro cyberpunk color palette ke rgb codes
    TRANSPARENT = (0, 0, 0, 0)
    BG_DARK = (10, 12, 16, 255)
    ARMOR_DARK = (24, 28, 36, 255)
    ARMOR_MID = (45, 52, 64, 255)
    ARMOR_LIGHT = (70, 80, 98, 255)
    GOLD_DARK = (180, 120, 20, 255)
    GOLD_BRIGHT = (255, 195, 40, 255)
    RED_GLOW = (255, 20, 40, 255)
    RED_DARK = (160, 10, 25, 255)
    CYBER_CYAN = (0, 230, 255, 255)
    WHITE_HOT = (255, 240, 240, 255)

    # bahar ka octagon shield background draw kar rahe hain
    for y in range(grid_size):
        for x in range(grid_size):
            # shield ki boundary calculate kar rahe hain
            dx = abs(x - 15.5)
            dy = abs(y - 15.5)
            if dx + dy <= 20 and max(dx, dy) <= 15:
                img.putpixel((x, y), BG_DARK)
            if (dx + dy == 20 and max(dx, dy) <= 15) or (max(dx, dy) == 15 and dx + dy <= 20):
                img.putpixel((x, y), (50, 15, 25, 255))

    # ravan ke 10 siron ko represent karne wale cyber horns draw kar rahe hain
    horns = [
        # beech ke mukhya crown horns
        (15, 3), (16, 3), (15, 4), (16, 4), (14, 5), (17, 5), (15, 5), (16, 5),
        # bayein taraf ke horns
        (11, 4), (12, 5), (13, 6), (11, 5),
        # dayein taraf ke horns
        (20, 4), (19, 5), (18, 6), (20, 5),
        # sabse bahar wale bayein horns
        (7, 6), (8, 7), (9, 8), (10, 9), (7, 7), (8, 8),
        # sabse bahar wale dayein horns
        (24, 6), (23, 7), (22, 8), (21, 9), (24, 7), (23, 8),
        # side ke wing horns
        (4, 9), (5, 10), (6, 11), (4, 10), (5, 11),
        (27, 9), (26, 10), (25, 11), (27, 10), (26, 11)
    ]
    for hx, hy in horns:
        img.putpixel((hx, hy), GOLD_BRIGHT)
        img.putpixel((hx, hy + 1), GOLD_DARK)

    # forehead ka golden crown base
    for x in range(11, 21):
        img.putpixel((x, 7), GOLD_BRIGHT)
        img.putpixel((x, 8), GOLD_DARK)
    # forehead ka red power core
    img.putpixel((15, 7), RED_GLOW)
    img.putpixel((16, 7), RED_GLOW)
    img.putpixel((15, 8), WHITE_HOT)
    img.putpixel((16, 8), WHITE_HOT)

    # cyber mask ka dark metallic armor structure
    for y in range(9, 26):
        # chehre ke hisab se width ko adjust kar rahe hain
        if y < 14:
            x_min, x_max = 8, 23
        elif y < 19:
            x_min, x_max = 9, 22
        elif y < 23:
            x_min, x_max = 11, 20
        else:
            x_min, x_max = 13, 18

        for x in range(x_min, x_max + 1):
            if x == x_min or x == x_max:
                img.putpixel((x, y), ARMOR_LIGHT)
            elif (x + y) % 2 == 0:
                img.putpixel((x, y), ARMOR_MID)
            else:
                img.putpixel((x, y), ARMOR_DARK)

    # glowing red aur white cyber eyes
    # bayin aankh
    left_eye = [(11, 13), (12, 13), (13, 13), (12, 14), (13, 14)]
    for ex, ey in left_eye:
        img.putpixel((ex, ey), RED_GLOW)
    img.putpixel((12, 13), WHITE_HOT)

    # dayin aankh
    right_eye = [(18, 13), (19, 13), (20, 13), (18, 14), (19, 14)]
    for ex, ey in right_eye:
        img.putpixel((ex, ey), RED_GLOW)
    img.putpixel((19, 13), WHITE_HOT)

    # aankhon ke aas paas red glow ka effect
    img.putpixel((10, 13), RED_DARK)
    img.putpixel((21, 13), RED_DARK)
    img.putpixel((14, 13), RED_DARK)
    img.putpixel((17, 13), RED_DARK)

    # mask ka breathing vent
    for y in range(15, 18):
        img.putpixel((15, y), ARMOR_LIGHT)
        img.putpixel((16, y), ARMOR_LIGHT)

    # cyber fangs aur mouth grill
    mouth_y = 20
    for x in range(12, 20):
        img.putpixel((x, mouth_y), (15, 15, 18, 255))
        img.putpixel((x, mouth_y + 1), (25, 25, 30, 255))

    # white sharp cyber teeth
    fangs = [(13, mouth_y + 1), (13, mouth_y + 2), (18, mouth_y + 1), (18, mouth_y + 2),
             (15, mouth_y), (16, mouth_y)]
    for fx, fy in fangs:
        img.putpixel((fx, fy), WHITE_HOT)

    # chin aur jaw ka armor plate
    for x in range(13, 19):
        img.putpixel((x, 24), ARMOR_LIGHT)
        img.putpixel((x, 25), GOLD_DARK)

    # cheeks par cyan color ki cyber circuit lines
    circuits = [(9, 16), (9, 17), (10, 17), (22, 16), (22, 17), (21, 17)]
    for cx, cy in circuits:
        img.putpixel((cx, cy), CYBER_CYAN)

    # image ko 16x upscale kar rahe hain bina blur kiye taaki pixel art crisp rahe
    upscaled = img.resize((grid_size * scale, grid_size * scale), Image.NEAREST)

    out_paths = [
        "/home/obito/hex-cyber-agent/assets/ravan_pixel_logo.png",
        "/home/obito/Desktop/ravan_pixel_logo.png"
    ]
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        upscaled.save(p, "PNG")

    return out_paths[0]

if __name__ == "__main__":
    path = create_ravan_pixel_logo(scale=16)
    print(f"Generated pixel logo at: {path}")
