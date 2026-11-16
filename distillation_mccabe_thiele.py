"""
McCabe-Thiele Distillation Column Calculator (ethanol-water)
-------------------------------------------------------------
Works out how many trays (stages) a distillation column needs to separate
a weak ethanol-water mixture into strong ethanol (top) and almost pure
water (bottom), and draws the McCabe-Thiele diagram.

Assumptions (stated so a reader knows the limits of the model):
  - 1 atm pressure, ethanol-water equilibrium taken from tabulated data
  - Constant molar overflow (flows are constant within each section)
  - Feed is a saturated liquid (q = 1)
  - Ideal stages (every tray reaches equilibrium)
  - Product purity must stay below the azeotrope (about 0.894 mole fraction)

All strengths are mole fractions of ethanol (0.85 means 85%).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.interpolate import PchipInterpolator

# ----------------------------------------------------------------------
# 1. INPUTS - change these and re-run
# ----------------------------------------------------------------------
product = 0.85          # strength of the product at the top
feed = 0.30             # strength of the liquid entering the middle
leftover = 0.02         # strength of the leftover water at the bottom
reflux_multiple = 1.5   # actual reflux ratio = this x the minimum reflux ratio

# ----------------------------------------------------------------------
# 2. NATURE'S RULE: equilibrium data (the blue curve)
#    Each row: a liquid of this strength gives steam of that strength.
#    Check these values against a textbook table and cite it in your report.
# ----------------------------------------------------------------------
liquid_ethanol = [0, 0.019, 0.0721, 0.0966, 0.1238, 0.1661, 0.2337, 0.2608,
                  0.3273, 0.3965, 0.5079, 0.5198, 0.5732, 0.6763, 0.7472,
                  0.8943, 1.0]
vapour_ethanol = [0, 0.17, 0.3891, 0.4375, 0.4704, 0.5089, 0.5445, 0.558,
                  0.5826, 0.6122, 0.6564, 0.6599, 0.6841, 0.7385, 0.7815,
                  0.8943, 1.0]

# Smooth lookups through the table (a curve instead of straight segments)
steam_from_liquid = PchipInterpolator(liquid_ethanol, vapour_ethanol)
liquid_from_steam = PchipInterpolator(vapour_ethanol, liquid_ethanol)  # table read backwards

# ----------------------------------------------------------------------
# 3. CHECK THE INPUTS
# ----------------------------------------------------------------------
if not (0 < leftover < feed < product < 0.8943):
    raise ValueError("Need 0 < leftover < feed < product < 0.8943 (the azeotrope limit).")


# ----------------------------------------------------------------------
# 4. FUNCTIONS
# ----------------------------------------------------------------------
def top_line(x, R):
    """Orange line: steam strength between trays in the top section."""
    return R / (R + 1) * x + product / (R + 1)


def minimum_reflux():
    """Smallest reflux ratio that still works (the line just touches the blue curve)."""
    xs = np.linspace(feed, product - 1e-4, 2000)
    slope = ((product - steam_from_liquid(xs)) / (product - xs)).max()
    return slope / (1 - slope)


def count_trays(R):
    """Step down the tower from the top. Returns (steps, feed_tray, meeting_point)
    or None if R is too low to ever reach the target."""
    # Where the top line meets the feed (also the start of the bottom line)
    meet_x = feed
    meet_y = top_line(meet_x, R)
    bottom_slope = (meet_y - leftover) / (meet_x - leftover)

    def bottom_line(x):
        """Green line: steam strength between trays in the bottom section."""
        return leftover + bottom_slope * (x - leftover)

    steps = []
    x, y = product, product      # start at the top: steam leaving the top tray
    feed_tray = None

    for tray in range(1, 201):
        new_x = float(liquid_from_steam(y))            # sideways to the blue curve
        in_top_section = new_x > meet_x
        if in_top_section:
            new_y = top_line(new_x, R)                 # down to the orange line
        else:
            new_y = bottom_line(new_x)                 # down to the green line
            if feed_tray is None:
                feed_tray = tray                       # first tray below the feed point
        steps.append((x, y, new_x, new_y))
        if abs(x - new_x) < 1e-6:                      # steps shrank to nothing: R too low
            return None
        x, y = new_x, new_y
        if x <= leftover:                              # reached the leftover strength
            return steps, feed_tray, (meet_x, meet_y)
    return None


# ----------------------------------------------------------------------
# 5. RUN THE DESIGN
# ----------------------------------------------------------------------
R_min = minimum_reflux()
R = reflux_multiple * R_min
steps, feed_tray, meet = count_trays(R)

print("Minimum reflux ratio :", round(R_min, 2))
print("Reflux ratio used    :", round(R, 2), "(", reflux_multiple, "x minimum )")
print("Trays needed         :", len(steps), "(counting the bottom heater as one stage)")
print("Feed enters at tray  :", feed_tray, "counting from the top")

# ----------------------------------------------------------------------
# 6. DRAW THE McCABE-THIELE DIAGRAM
# ----------------------------------------------------------------------
xs = np.linspace(0, 1, 400)
plt.figure(figsize=(7, 7))
plt.plot(xs, steam_from_liquid(xs), label="Equilibrium curve (nature's rule)")
plt.plot(xs, xs, "k--", lw=1, label="y = x")
plt.plot([meet[0], product], [meet[1], product], label="Top operating line")
plt.plot([leftover, meet[0]], [leftover, meet[1]], label="Bottom operating line")
for x0, y0, x1, y1 in steps:
    plt.plot([x0, x1], [y0, y0], "r", lw=1)    # sideways
    plt.plot([x1, x1], [y0, y1], "r", lw=1)    # down
plt.xlabel("x: ethanol in liquid")
plt.ylabel("y: ethanol in steam")
plt.title("McCabe-Thiele: R = " + str(round(R, 2)) + ", " + str(len(steps)) +
          " trays, feed at tray " + str(feed_tray))
plt.legend()
plt.grid(alpha=0.3)
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.savefig("mccabe_thiele_diagram.png", dpi=150)
plt.show()

# ----------------------------------------------------------------------
# 7. TRADE-OFF: trays needed vs reflux ratio
# ----------------------------------------------------------------------
multiples = [1.05, 1.1, 1.2, 1.3, 1.5, 2, 3, 5]
tray_counts = []
print("\nReflux trade-off:")
for m in multiples:
    result = count_trays(m * R_min)
    n = len(result[0]) if result else None
    tray_counts.append(n)
    print("  R =", round(m * R_min, 2), "(", m, "x min ) ->", n, "trays")

plt.figure(figsize=(7, 4.5))
plt.plot([m * R_min for m in multiples], tray_counts, "o-")
plt.axvline(R_min, color="gray", linestyle="--", label="Minimum reflux")
plt.xlabel("Reflux ratio R")
plt.ylabel("Trays needed")
plt.title("More reflux = fewer trays, but more energy")
plt.legend()
plt.grid(alpha=0.3)
plt.savefig("trays_vs_reflux.png", dpi=150)
plt.show()
