"""
Redraw the 28 Cromwell Road floorplan as a clean, to-scale SVG.

Layout, fixtures and room labels follow the original agent plan (plan.png);
the geometry is rebuilt at one consistent scale from the labelled dimensions,
because the original is not drawn to scale (~91 px/m across, 82-105 px/m down).

All geometry below is in METRES. Front (Cromwell Road) is at the bottom of each
plan, rear garden at the top.
"""
import io
from math import cos, sin, radians

S = 44.0          # svg units per metre
MARGIN = 34.0
GAP = 1.45        # metres between the three plans
TITLE_SPACE = 62.0

EW = 0.25         # external / party wall
IW = 0.10         # internal wall

# ---------------------------------------------------------------- envelope --
MB_X0, MB_X1 = 0.00, 5.35          # main body, outer
mb_x0, mb_x1 = 0.25, 5.10          # main body, inner   (4.85 wide)
MB_Y0, MB_Y1 = 5.48, 14.25         # main body, outer
mb_y0, mb_y1 = 5.73, 14.00         # main body, inner   (8.27 deep)

BA_X0, BA_X1 = 2.31, 5.35          # back addition, outer
ba_x0, ba_x1 = 2.56, 5.10          # back addition, inner (2.54 wide)
BA_Y0 = 0.00
ba_y0, ba_y1 = 0.25, 5.48          # back addition, inner (5.23 deep)

BAY_Y = 14.85                      # front bay projection

PLAN_W = MB_X1 - MB_X0
FLOOR_DX = PLAN_W + GAP

W = 3 * PLAN_W * S + 2 * GAP * S + 2 * MARGIN
H = BAY_Y * S + MARGIN + TITLE_SPACE

out = []
_dx = 0.0


def X(m): return round(MARGIN + _dx + m * S, 2)
def Y(m): return round(MARGIN + m * S, 2)
def L(m): return round(m * S, 2)


def rect(x0, y0, x1, y1, cls):
    out.append(f'<rect class="{cls}" x="{X(x0)}" y="{Y(y0)}" '
               f'width="{L(x1-x0)}" height="{L(y1-y0)}"/>')


def wall(x0, y0, x1, y1):    rect(x0, y0, x1, y1, "w")
def room(x0, y0, x1, y1, c): rect(x0, y0, x1, y1, c)
def gap(x0, y0, x1, y1):     rect(x0, y0, x1, y1, "op")
def punch(x0, y0, x1, y1, c): rect(x0, y0, x1, y1, c)


def win_h(x0, x1, y0, y1):
    """Window in a horizontal (east-west) wall."""
    gap(x0, y0, x1, y1, )
    m = (y0 + y1) / 2
    out.append(f'<line class="gl" x1="{X(x0)}" y1="{Y(m)}" x2="{X(x1)}" y2="{Y(m)}"/>')
    out.append(f'<rect class="wl" x="{X(x0)}" y="{Y(y0)}" width="{L(x1-x0)}" height="{L(y1-y0)}"/>')


def win_v(y0, y1, x0, x1):
    """Window in a vertical (north-south) wall."""
    gap(x0, y0, x1, y1)
    m = (x0 + x1) / 2
    out.append(f'<line class="gl" x1="{X(m)}" y1="{Y(y0)}" x2="{X(m)}" y2="{Y(y1)}"/>')
    out.append(f'<rect class="wl" x="{X(x0)}" y="{Y(y0)}" width="{L(x1-x0)}" height="{L(y1-y0)}"/>')


def door(x0, y0, x1, y1, hx, hy, a0, a1, r=None):
    """Erase the wall between (x0,y0)-(x1,y1) and swing a leaf from (hx,hy)."""
    gap(x0, y0, x1, y1)
    if r is None:
        r = max(x1 - x0, y1 - y0)
    px0, py0 = hx + r * cos(radians(a0)), hy + r * sin(radians(a0))
    px1, py1 = hx + r * cos(radians(a1)), hy + r * sin(radians(a1))
    sweep = 1 if a1 > a0 else 0
    out.append(f'<path class="dr" d="M {X(hx)} {Y(hy)} L {X(px0)} {Y(py0)} '
               f'A {L(r)} {L(r)} 0 0 {sweep} {X(px1)} {Y(py1)}"/>')


def stairs(x0, x1, y0, y1, n, arrow):
    """Vertical flight; treads run east-west. arrow = 'up' | 'down'."""
    rect(x0, y0, x1, y1, "st")
    for i in range(1, n):
        y = y0 + (y1 - y0) * i / n
        out.append(f'<line class="stl" x1="{X(x0)}" y1="{Y(y)}" x2="{X(x1)}" y2="{Y(y)}"/>')
    cx = (x0 + x1) / 2
    ay0, ay1 = (y1 - 0.25, y0 + 0.25) if arrow == "up" else (y0 + 0.25, y1 - 0.25)
    out.append(f'<line class="ar" x1="{X(cx)}" y1="{Y(ay0)}" x2="{X(cx)}" y2="{Y(ay1)}"/>')
    d = 0.20 if arrow == "up" else -0.20
    out.append(f'<path class="ar" d="M {X(cx-0.13)} {Y(ay1+d)} L {X(cx)} {Y(ay1)} '
               f'L {X(cx+0.13)} {Y(ay1+d)}"/>')


def label(cx, cy, name, metric=None, imperial=None, small=False):
    fs = 11.0 if small else 12.5
    out.append(f'<text class="rn" x="{X(cx)}" y="{Y(cy)}" font-size="{fs}">{name}</text>')
    if metric:
        out.append(f'<text class="rd" x="{X(cx)}" y="{Y(cy)+13}">{metric}</text>')
    if imperial:
        out.append(f'<text class="rd" x="{X(cx)}" y="{Y(cy)+25}">{imperial}</text>')


def label2(cx, cy, l1, l2):
    out.append(f'<text class="rn" x="{X(cx)}" y="{Y(cy)}" font-size="11">{l1}</text>')
    out.append(f'<text class="rn" x="{X(cx)}" y="{Y(cy)+13}" font-size="11">{l2}</text>')


def floor_title(t):
    cx = (MB_X0 + MB_X1) / 2
    out.append(f'<text class="ft" x="{X(cx)}" y="{Y(BAY_Y)+34}">{t}</text>')


def bay(inner_fill):
    """Canted bay projecting beyond the front wall, glazed on three faces."""
    outer = [(0.95, MB_Y1), (1.55, BAY_Y), (2.55, BAY_Y), (3.15, MB_Y1)]
    inner = [(1.20, MB_Y1), (1.72, BAY_Y - 0.25), (2.38, BAY_Y - 0.25), (2.90, MB_Y1)]
    mid   = [(1.075, MB_Y1), (1.635, BAY_Y - 0.125), (2.465, BAY_Y - 0.125), (3.025, MB_Y1)]

    punch(1.20, mb_y1 - 0.01, 2.90, MB_Y1 + 0.01, inner_fill)   # open to the room
    pts = lambda p: " ".join(f"{X(x)},{Y(y)}" for x, y in p)
    out.append(f'<polygon class="w" points="{pts(outer)}"/>')
    out.append(f'<polygon class="{inner_fill}" points="{pts(inner)}"/>')
    out.append(f'<polyline class="bayglass" points="{pts(mid)}"/>')
    out.append(f'<polyline class="gl" points="{pts(mid)}"/>')
    out.append(f'<polyline class="wl2" points="{pts(outer)}"/>')


def envelope_walls():
    """Outer shell shared by the ground and first floors."""
    wall(BA_X0, BA_Y0, BA_X1, ba_y0)          # addition rear
    wall(BA_X0, BA_Y0, ba_x0, MB_Y0 + EW)     # addition left
    wall(ba_x1, BA_Y0, BA_X1, MB_Y0 + EW)     # addition right
    wall(MB_X0, MB_Y0, MB_X1, mb_y0)          # main rear band
    wall(MB_X0, MB_Y0, mb_x0, MB_Y1)          # main left
    wall(mb_x1, MB_Y0, MB_X1, MB_Y1)          # main right
    wall(MB_X0, mb_y1, MB_X1, MB_Y1)          # front


def chimney(x_from, y0, y1):
    rect(x_from, y0, x_from + 0.45, y1, "ch")


# =============================================================== BASEMENT ===
def basement():
    cel_rear = 6.47          # cellar 2 rear inner face
    div0, div1 = 9.79, 9.89  # wall between the two cellars
    st_x0, st_x1 = 3.97, mb_x1
    st_top = 5.73            # stair well projects behind cellar 2

    room(mb_x0, cel_rear, 3.87, div0, "cel")           # cellar 2
    room(mb_x0, div1, mb_x1, mb_y1, "cel")             # cellar (full width)
    room(st_x0, st_top, mb_x1, div1, "circ")           # stair well

    # shell
    wall(MB_X0, cel_rear - EW, 4.12, cel_rear)         # cellar 2 rear
    wall(3.87, MB_Y0, 4.12, cel_rear)                  # stair well left (outer)
    wall(3.87, cel_rear, st_x0, div0)                  # stair well left (inner)
    wall(3.72, MB_Y0, MB_X1, st_top)                   # stair well rear
    wall(MB_X0, cel_rear - EW, mb_x0, MB_Y1)           # left
    wall(mb_x1, MB_Y0, MB_X1, MB_Y1)                   # right
    wall(MB_X0, mb_y1, MB_X1, MB_Y1)                   # front
    wall(mb_x0, div0, 3.87, div1)                      # between cellars

    punch(3.87, 8.55, st_x0, 9.45, "cel")              # opening to the stair well
    bay("cel")
    chimney(mb_x0, 11.15, 12.55)

    stairs(st_x0 + 0.06, mb_x1 - 0.06, 6.15, 8.45, 9, "up")
    label(2.06, 8.00, "Cellar 2", "3.40m × 3.32m", "(11&#8242;2&#8243; × 10&#8242;11&#8243;)")
    label(2.68, 11.90, "Cellar", "3.50m × 4.11m", "(11&#8242;6&#8243; × 13&#8242;6&#8243;)")
    floor_title("Basement")


# ============================================================== GROUND ======
def ground():
    part_x0, part_x1 = 3.87, 3.97       # rooms | hall
    din_lou0, din_lou1 = 9.44, 9.54     # dining | lounge
    por0, por1 = 12.50, 12.60           # hall | porch

    room(ba_x0, ba_y0, ba_x1, ba_y1, "kit")            # kitchen
    room(mb_x0, mb_y0, part_x0, din_lou0, "rec")       # dining
    room(mb_x0, din_lou1, part_x0, mb_y1, "rec")       # lounge
    room(part_x1, mb_y0, mb_x1, por0, "circ")          # hall
    room(part_x1, por1, mb_x1, mb_y1, "circ")          # porch

    envelope_walls()
    wall(part_x0, mb_y0, part_x1, mb_y1)               # rooms | hall
    wall(mb_x0, din_lou0, part_x0, din_lou1)           # dining | lounge
    wall(part_x1, por0, mb_x1, por1)                   # hall | porch

    # -- windows
    win_h(0.85, 2.15, MB_Y0, mb_y0)                    # dining, rear
    win_h(3.30, 4.50, BA_Y0, ba_y0)                    # kitchen, rear
    win_v(0.85, 1.75, BA_X0, ba_x0)                    # kitchen, side
    win_v(2.15, 3.05, BA_X0, ba_x0)
    win_v(3.45, 4.15, BA_X0, ba_x0)
    bay("rec")

    # -- doors
    door(BA_X0, 4.55, ba_x0, 5.30, ba_x0, 5.30, -90, -20, r=0.75)      # back door
    door(3.00, MB_Y0, 3.80, mb_y0, 3.00, mb_y0, 0, 78, r=0.80)         # kitchen > dining
    door(4.22, MB_Y0, mb_x1, mb_y0, 4.22, mb_y0, 0, 72, r=0.88)        # kitchen > hall
    door(part_x0, 8.45, part_x1, 9.25, part_x0, 8.45, 90, 175, r=0.80) # hall > dining
    door(part_x0, 10.55, part_x1, 11.35, part_x0, 11.35, -90, -175, r=0.80)  # hall > lounge
    door(4.20, por0, 5.00, por1, 4.20, por0, 0, -75, r=0.80)           # porch > hall
    door(4.15, mb_y1, 4.90, MB_Y1, 4.15, mb_y1, 0, -72, r=0.75)        # front door

    # -- kitchen fittings
    out.append(f'<rect class="fx" x="{X(ba_x0)}" y="{Y(ba_y0)}" '
               f'width="{L(ba_x1-ba_x0)}" height="{L(0.60)}"/>')                 # rear run
    out.append(f'<rect class="fx" x="{X(ba_x1-0.60)}" y="{Y(ba_y0+0.60)}" '
               f'width="{L(0.60)}" height="{L(1.85)}"/>')                        # side run
    out.append(f'<rect class="fx" x="{X(3.45)}" y="{Y(0.36)}" '
               f'width="{L(0.62)}" height="{L(0.42)}" rx="3"/>')                 # sink bowl
    for i, dx in enumerate((0.18, 0.52)):
        for dy in (0.28, 0.62):
            out.append(f'<circle class="fx" cx="{X(ba_x1-0.60+dx+0.06)}" '
                       f'cy="{Y(ba_y0+0.72+dy)}" r="{L(0.10)}"/>')               # hob rings
    stairs(part_x1 + 0.06, mb_x1 - 0.06, 6.70, 9.40, 10, "up")

    # -- labels
    label(3.83, 3.35, "Kitchen", "5.23m × 2.54m", "(17&#8242;2&#8243; × 8&#8242;4&#8243;)")
    label(2.06, 7.40, "Dining Room", "3.71m × 3.49m", "(12&#8242;2&#8243; × 11&#8242;5&#8243;)")
    label(2.06, 11.60, "Lounge", "4.46m × 3.62m", "(14&#8242;8&#8243; × 11&#8242;11&#8243;)")
    label(4.53, 10.95, "Hall", small=True)
    label(4.53, 13.45, "Porch", small=True)
    chimney(mb_x0, 6.85, 8.25)
    chimney(mb_x0, 11.15, 12.55)

    # orientation notes
    out.append(f'<text class="or" x="{X(1.15)}" y="{Y(BA_Y0)-9}">Garden</text>')
    out.append(f'<text class="or" x="{X(2.67)}" y="{Y(BAY_Y)+15}">Cromwell Road</text>')
    floor_title("Ground Floor")


# =============================================================== FIRST ======
def first():
    b3_b, sh_t = 3.01, 3.11             # bedroom 3 | shower + landing
    sh_x1, ld_x0 = 4.08, 4.18           # shower | landing strip
    b2_x1, ldm_x0 = 3.14, 3.24          # bedroom 2 | landing
    b2_b, b1_t = 9.21, 9.31             # bedroom 2 + landing | bedroom 1

    room(ba_x0, ba_y0, ba_x1, b3_b, "bed")             # bedroom 3
    room(ba_x0, sh_t, sh_x1, ba_y1, "sh")              # shower room
    room(ld_x0, sh_t, ba_x1, ba_y1, "circ")            # landing, in the addition
    room(ldm_x0, mb_y0, mb_x1, b2_b, "circ")           # landing, in the main body
    room(ld_x0, ba_y1, mb_x1, mb_y0, "circ")           # landing pass-through
    room(mb_x0, mb_y0, b2_x1, b2_b, "bed")             # bedroom 2
    room(mb_x0, b1_t, mb_x1, mb_y1, "bed")             # bedroom 1

    envelope_walls()
    punch(ld_x0, MB_Y0 - 0.01, mb_x1, mb_y0 + 0.01, "circ")  # landing passes the rear wall
    wall(ba_x0, b3_b, ba_x1, sh_t)                     # bedroom 3 | below
    wall(sh_x1, sh_t, ld_x0, ba_y1)                    # shower | landing
    wall(b2_x1, mb_y0, ldm_x0, b2_b)                   # bedroom 2 | landing
    wall(mb_x0, b2_b, mb_x1, b1_t)                     # above | bedroom 1

    # -- windows
    win_h(3.30, 4.50, BA_Y0, ba_y0)                    # bedroom 3, rear
    win_v(3.65, 4.45, BA_X0, ba_x0)                    # shower room, side
    win_h(0.85, 2.15, MB_Y0, mb_y0)                    # bedroom 2, rear
    win_h(1.55, 3.45, mb_y1, MB_Y1)                    # bedroom 1, front

    # -- doors
    door(4.20, b3_b, 5.00, sh_t, 4.20, b3_b, 0, -75, r=0.80)            # landing > bed 3
    door(sh_x1, 3.35, ld_x0, 4.05, sh_x1, 3.35, 90, 170, r=0.70)        # landing > shower
    door(b2_x1, 7.25, ldm_x0, 8.00, b2_x1, 7.25, 90, 172, r=0.75)       # landing > bed 2
    door(4.05, b2_b, 4.85, b1_t, 4.05, b1_t, 0, 75, r=0.80)             # landing > bed 1

    # -- shower room fittings
    out.append(f'<ellipse class="fx" cx="{X(3.45)}" cy="{Y(3.50)}" '
               f'rx="{L(0.24)}" ry="{L(0.30)}"/>')                                # wc
    out.append(f'<rect class="fx" x="{X(ba_x0)}" y="{Y(3.85)}" '
               f'width="{L(0.52)}" height="{L(0.62)}" rx="3"/>')                  # basin
    out.append(f'<rect class="fx" x="{X(ba_x0)}" y="{Y(4.58)}" '
               f'width="{L(0.90)}" height="{L(0.90)}"/>')                         # shower tray
    out.append(f'<path class="fx" d="M {X(ba_x0+0.90)} {Y(4.58)} '
               f'A {L(0.90)} {L(0.90)} 0 0 1 {X(ba_x0)} {Y(5.48)}"/>')
    stairs(ld_x0 + 0.06, mb_x1 - 0.06, 5.95, 8.35, 9, "down")

    # -- labels
    label(3.83, 1.45, "Bedroom 3", "2.76m × 2.61m", "(9&#8242;1&#8243; × 8&#8242;7&#8243;)")
    label2(3.55, 4.20, "Shower", "Room")
    label(4.17, 6.55, "Landing", small=True)
    label(1.65, 6.95, "Bedroom 2", "3.45m × 2.89m", "(11&#8242;4&#8243; × 9&#8242;6&#8243;)")
    label(2.68, 11.55, "Bedroom 1", "3.66m × 4.69m", "(12&#8242; × 15&#8242;5&#8243;)")
    chimney(mb_x0, 11.15, 12.55)
    floor_title("First Floor")


# ================================================================= build ====
STYLE = """
  .w   { fill: #23201c; }
  .op  { fill: #ffffff; }
  .wl  { fill: none; stroke: #23201c; stroke-width: 1; }
  .gl  { fill: none; stroke: #23201c; stroke-width: 1.1; }
  .wl2 { fill: none; stroke: #23201c; stroke-width: 1.4; stroke-linejoin: round; }
  .bayglass { fill: none; stroke: #ffffff; stroke-width: 11; stroke-linejoin: round; }
  .dr  { fill: none; stroke: #8b8378; stroke-width: 1; }
  .fx  { fill: none; stroke: #8b8378; stroke-width: 1.1; }
  .st  { fill: #ffffff; stroke: #8b8378; stroke-width: 1; }
  .stl { stroke: #8b8378; stroke-width: 1; }
  .ar  { fill: none; stroke: #8b8378; stroke-width: 1.1; }
  .ch  { fill: none; stroke: #8b8378; stroke-width: 1; }
  .rec { fill: #f2e4cb; }
  .kit { fill: #e8d4b4; }
  .bed { fill: #dde7d2; }
  .cel { fill: #e4e2d8; }
  .sh  { fill: #cfe0e6; }
  .circ{ fill: #e6ded1; }
  .rn  { fill: #23201c; font-weight: 600; text-anchor: middle; }
  .rd  { fill: #5c554c; font-size: 10px; text-anchor: middle; }
  .ft  { fill: #23201c; font-size: 16px; font-weight: 600; text-anchor: middle; }
  .or  { fill: #8b8378; font-size: 10px; font-style: italic; text-anchor: middle; }
  .sb  { fill: #5c554c; font-size: 9.5px; text-anchor: middle; }
  text { font-family: "Inter", system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif; }
"""

for i, fn in enumerate((basement, ground, first)):
    _dx = i * FLOOR_DX * S
    out.append(f'<g id="floor-{fn.__name__}">')
    fn()
    out.append("</g>")

# scale bar, bottom left
_dx = 0.0
sb_y = BAY_Y + 0.30
out.append('<g id="scalebar">')
for k in range(5):
    cls = "w" if k % 2 == 0 else "op"
    out.append(f'<rect class="{cls}" x="{X(k*1.0)}" y="{Y(sb_y)}" '
               f'width="{L(1.0)}" height="6"/>')
out.append(f'<rect class="wl" x="{X(0)}" y="{Y(sb_y)}" width="{L(5.0)}" height="6"/>')
out.append(f'<text class="sb" x="{X(0)}" y="{Y(sb_y)+18}">0</text>')
out.append(f'<text class="sb" x="{X(5.0)}" y="{Y(sb_y)+18}">5m</text>')
out.append("</g>")

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {round(W)} {round(H)}"
     width="{round(W)}" height="{round(H)}" role="img"
     aria-labelledby="fp-title fp-desc" preserveAspectRatio="xMidYMid meet">
<title id="fp-title">Floorplan of 28 Cromwell Road, Lancaster</title>
<desc id="fp-desc">Three floors drawn to scale. Basement: two cellar rooms with a stair well. Ground floor: porch, hall, lounge with a front bay window, dining room, and a kitchen in the rear back addition. First floor: three bedrooms, a shower room and a landing. Front of the house and Cromwell Road are at the bottom of each plan; the garden is at the top.</desc>
<style>{STYLE}</style>
<rect width="100%" height="100%" fill="#fdfcfa"/>
{chr(10).join(out)}
</svg>
'''

path = r"C:/Users/alexa/Dropbox/Admin/cromwell_sale/website/images/floorplan.svg"
io.open(path, "w", encoding="utf-8").write(svg)
print(f"wrote {path}  ({len(svg)/1024:.1f} KB, viewBox {round(W)}x{round(H)})")
