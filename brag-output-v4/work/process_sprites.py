import os
from PIL import Image, ImageDraw

WORK_DIR = r"D:\Project\RememberMe\brag-output-v4\work"
os.makedirs(WORK_DIR, exist_ok=True)

# 1. Clean extraction of uploaded mascot
SRC_IMAGE = r"C:\Users\iwank\.gemini\antigravity\brain\750275df-b18a-4256-b242-96c2bb4a98b3\.user_uploaded\media_1790570880531.png"

# Authentic terracotta palette
COLOR_MAIN = (218, 119, 87, 255)       # #DA7757
COLOR_HIGHLIGHT = (235, 142, 112, 255)  # Top highlight
COLOR_SHADOW = (185, 90, 62, 255)       # Underbody / leg shadow
COLOR_EYE_PUPIL = (35, 20, 30, 255)     # When eyes have pupils or dark background
COLOR_GOLD = (255, 215, 0, 255)         # Wizard stars / book
COLOR_PURPLE = (88, 54, 156, 255)       # Wizard hat
COLOR_PURPLE_LIGHT = (120, 80, 200, 255)
COLOR_PURPLE_DARK = (60, 32, 110, 255)
COLOR_BOOK_COVER = (140, 28, 48, 255)   # Crimson leather tome
COLOR_BOOK_GOLD = (245, 195, 60, 255)
COLOR_BOOK_PAGES = (245, 240, 220, 255)
COLOR_MAGIC_CYAN = (64, 224, 255, 255)
COLOR_SWEAT_BLUE = (100, 200, 255, 255)

# Save exact native 16x10 PNG and high-res clean transparent PNG
GRID_16x10 = [
    "..############..",
    "..############..",
    "..##.######.##..",
    "..##.######.##..",
    "################",
    "################",
    "..############..",
    "..############..",
    "...#.#....#.#...",
    "...#.#....#.#..."
]

def make_pixel_image(grid, scale=1, shading=True):
    h = len(grid)
    w = len(grid[0])
    img = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            char = grid[y][x]
            if char == '#':
                col = COLOR_MAIN
                if shading:
                    if y == 0 or (y == 4 and (x < 2 or x > 13)):
                        col = COLOR_HIGHLIGHT
                    elif y >= 6:
                        col = COLOR_SHADOW
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), col)
            elif char == '.':
                pass # transparent
            elif char == 'H': # hat
                col = COLOR_PURPLE
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), col)
            elif char == 'G': # gold
                col = COLOR_GOLD
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), col)
            elif char == 'S': # sweat
                col = COLOR_SWEAT_BLUE
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), col)
    return img

# 1. Native mascot
mascot_1x = make_pixel_image(GRID_16x10, scale=1, shading=False)
mascot_1x.save(os.path.join(WORK_DIR, "claude_16x10_native.png"))

# High-res clean mascot (deliverable 1)
mascot_clean = make_pixel_image(GRID_16x10, scale=20, shading=False)
mascot_clean.save(os.path.join(WORK_DIR, "claude_mascot.png"))
print("Saved clean claude_mascot.png (320x200)")

# 2. Build Animation States (as individual frames and combined spritesheet)
# Standard grid dimensions: 20x16 to allow space for ears/hat/sweat/arm raises
STATES = {}

# Idle 1
STATES["idle_1"] = [
    "....############....",
    "....############....",
    "....##.######.##....",
    "....##.######.##....",
    "..################..",
    "..################..",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "....................",
    "...................."
]

# Idle 2 (1-pixel bob / breathing)
STATES["idle_2"] = [
    "....................",
    "....############....",
    "....############....",
    "....##.######.##....",
    "....##.######.##....",
    "..################..",
    "..################..",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    "....................",
    "...................."
]

# Blink
STATES["blink"] = [
    "....############....",
    "....############....",
    "....############....",
    "....############....",
    "..################..",
    "..################..",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "....................",
    "...................."
]

# Wink (Left eye open, right eye closed/smile)
STATES["wink"] = [
    "....############....",
    "....############....",
    "....##.#########....",
    "....##.#########....",
    "..################..",
    "..################..",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "....................",
    "...................."
]

# Panic Sweat (wide eyes + sweat drop)
STATES["panic"] = [
    "S...############....",
    ".S..############.S..",
    "....##..####..##..S.",
    "....##..####..##....",
    "..################..",
    "..################..",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "....................",
    "...................."
]

# Crouch / Anticipation (squashed body, splayed legs)
STATES["crouch"] = [
    "....................",
    "....................",
    "....############....",
    "....##.######.##....",
    "....##.######.##....",
    "####################",
    "####################",
    "....############....",
    "....############....",
    "....##.#....#.##....",
    "....................",
    "...................."
]

# Jump / Stretch (stretched body, arms up, legs trailing)
STATES["jump"] = [
    "..#..............#..",
    "..##............##..",
    "....############....",
    "....############....",
    "....##.######.##....",
    "....##.######.##....",
    "....############....",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "......#......#......"
]

# Casting / Raise Arms (arms raised diagonally to summon magic)
STATES["cast"] = [
    "..#..............#..",
    "..##............##..",
    "..################..",
    "....############....",
    "....##.######.##....",
    "....##.######.##....",
    "....############....",
    "....############....",
    "....############....",
    ".....#.#....#.#.....",
    ".....#.#....#.#.....",
    "...................."
]

# 3. Save each state
SCALE = 8
for name, grid in STATES.items():
    img = make_pixel_image(grid, scale=SCALE, shading=True)
    img.save(os.path.join(WORK_DIR, f"claude_{name}.png"))

# 4. Generate Wizard Hat Sprites (3 physics angles: center, tilt left, tilt right)
HAT_CENTER = [
    "......G.......",
    ".....HHH......",
    ".....HHH......",
    "....HHHHH.....",
    "....HHHHH.....",
    "...HHHHHHH....",
    "..HHHHHHHHH...",
    ".HHHHHHHHHHH..",
    "HHHHHHHHHHHHH."
]

HAT_TILT_LEFT = [
    "G.............",
    ".HH...........",
    "..HHH.........",
    "...HHHH.......",
    "....HHHHH.....",
    "...HHHHHHH....",
    "..HHHHHHHHH...",
    ".HHHHHHHHHHH..",
    "HHHHHHHHHHHHH."
]

HAT_TILT_RIGHT = [
    "............G.",
    "...........HH.",
    ".........HHH..",
    ".......HHHH...",
    ".....HHHHH....",
    "....HHHHHHH...",
    "...HHHHHHHHH..",
    "..HHHHHHHHHHH.",
    ".HHHHHHHHHHHHH"
]

for name, hgrid in [("hat_center", HAT_CENTER), ("hat_left", HAT_TILT_LEFT), ("hat_right", HAT_TILT_RIGHT)]:
    himg = make_pixel_image(hgrid, scale=SCALE, shading=False)
    himg.save(os.path.join(WORK_DIR, f"{name}.png"))

# 5. Generate Spellbook (RememberMe v2 Grimoire)
BOOK_CLOSED = [
    "..GGGGGGGGGG..",
    ".GCCCCCCCCCCG.",
    "GCPPPPPPPPPPCG",
    "GCPPGGGGGGPPGG",
    "GCPPGG..GGPPGG",
    "GCPPGGGGGGPPGG",
    "GCPPPPPPPPPPCG",
    ".GCCCCCCCCCCG.",
    "..GGGGGGGGGG.."
]

BOOK_OPEN = [
    "..GGGGGG..GGGGGG..",
    ".GPPPPPPGGPPPPPPG.",
    "GPFFFFFPGGPFFFFFPG",
    "GPF###FFGGPF###FFG",
    "GPF###FFGGPF###FFG",
    "GPF###FFGGPF###FFG",
    "GPFFFFFPGGPFFFFFPG",
    ".GPPPPPPGGPPPPPPG.",
    "..GGGGGG..GGGGGG.."
]

def make_book_image(grid, scale=SCALE):
    h = len(grid)
    w = len(grid[0])
    img = Image.new("RGBA", (w * scale, h * scale), (0, 0, 0, 0))
    for y in range(h):
        for x in range(w):
            c = grid[y][x]
            col = (0, 0, 0, 0)
            if c == 'G': col = COLOR_BOOK_GOLD
            elif c == 'C': col = (100, 20, 30, 255)
            elif c == 'P': col = COLOR_BOOK_COVER
            elif c == 'F': col = COLOR_BOOK_PAGES
            elif c == '#': col = (60, 60, 80, 255) # page runes
            if col[3] > 0:
                for dy in range(scale):
                    for dx in range(scale):
                        img.putpixel((x * scale + dx, y * scale + dy), col)
    return img

make_book_image(BOOK_CLOSED).save(os.path.join(WORK_DIR, "book_closed.png"))
make_book_image(BOOK_OPEN).save(os.path.join(WORK_DIR, "book_open.png"))

print("All sprites successfully generated and saved to work/")
