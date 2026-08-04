#!/usr/bin/env python3
"""
Generate the monthly-compilations chart for the 2026 AWS post.

Data comes from an Athena query over the compile-stats Glue table:

    MSCK REPAIR TABLE default.compile_stats;
    SELECT year, month, count(*) AS compilations
    FROM default.compile_stats
    WHERE (year = 2025 AND month >= 7) OR year = 2026
    GROUP BY year, month ORDER BY year, month;

Note the month column is zero-based (it comes from JavaScript's getMonth()),
so month=7 is August. The labels below are already corrected for that.
"""

# (label, compilations) in calendar order
DATA = [
    ("Aug", 6_492_107),
    ("Sep", 7_174_005),
    ("Oct", 7_770_156),
    ("Nov", 6_999_216),
    ("Dec", 7_286_532),
    ("Jan", 6_961_487),
    ("Feb", 6_554_899),
    ("Mar", 6_636_797),
    ("Apr", 6_237_991),
    ("May", 5_829_706),
    ("Jun", 5_495_860),
    ("Jul", 5_238_210),
]

WIDTH, HEIGHT = 800, 400
MARGIN_L, MARGIN_R, MARGIN_T, MARGIN_B = 70, 30, 40, 55

ACCENT = "#444499"  # matches the site's link/header colour
INK = "#333333"
MUTED = "#777777"
GRID = "#e4e4ea"

Y_MAX = 8_000_000
Y_STEP = 2_000_000


def x_for(i):
    span = WIDTH - MARGIN_L - MARGIN_R
    return MARGIN_L + span * i / (len(DATA) - 1)


def y_for(v):
    span = HEIGHT - MARGIN_T - MARGIN_B
    return MARGIN_T + span * (1 - v / Y_MAX)


def main():
    points = [(x_for(i), y_for(v)) for i, (_, v) in enumerate(DATA)]
    line = " ".join(f"{x:.1f},{y:.1f}" for x, y in points)
    baseline = HEIGHT - MARGIN_B
    area = f"{points[0][0]:.1f},{baseline:.1f} {line} {points[-1][0]:.1f},{baseline:.1f}"

    out = []
    add = out.append
    add(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" font-family="Helvetica, Arial, sans-serif" '
        f'role="img" aria-label="Monthly Compiler Explorer compilations, August 2025 to July 2026, '
        f'declining from 6.5 million to 5.2 million with a peak of 7.8 million in October 2025">'
    )
    add(f'<rect width="{WIDTH}" height="{HEIGHT}" fill="#ffffff"/>')
    add(f'<text x="{MARGIN_L}" y="24" font-size="15" font-weight="bold" fill="{INK}">' f"Compilations per month</text>")

    # Recessive gridlines and y labels
    v = 0
    while v <= Y_MAX:
        y = y_for(v)
        add(
            f'<line x1="{MARGIN_L}" y1="{y:.1f}" x2="{WIDTH - MARGIN_R}" y2="{y:.1f}" '
            f'stroke="{GRID}" stroke-width="1"/>'
        )
        add(
            f'<text x="{MARGIN_L - 10}" y="{y + 4:.1f}" font-size="12" fill="{MUTED}" '
            f'text-anchor="end">{v // 1_000_000}M</text>'
        )
        v += Y_STEP

    add(f'<polygon points="{area}" fill="{ACCENT}" fill-opacity="0.13"/>')
    add(
        f'<polyline points="{line}" fill="none" stroke="{ACCENT}" stroke-width="2" '
        f'stroke-linejoin="round" stroke-linecap="round"/>'
    )

    # Month labels, and a year marker where it rolls over
    for i, (label, _) in enumerate(DATA):
        x = x_for(i)
        add(
            f'<text x="{x:.1f}" y="{baseline + 20:.1f}" font-size="11" fill="{MUTED}" '
            f'text-anchor="middle">{label}</text>'
        )
    add(
        f'<text x="{x_for(0):.1f}" y="{baseline + 36:.1f}" font-size="11" fill="{MUTED}" '
        f'text-anchor="middle">2025</text>'
    )
    add(
        f'<text x="{x_for(5):.1f}" y="{baseline + 36:.1f}" font-size="11" fill="{MUTED}" '
        f'text-anchor="middle">2026</text>'
    )

    # Selective direct labels only: the peak and the two endpoints
    peak = max(range(len(DATA)), key=lambda i: DATA[i][1])
    for i, anchor, dy in ((0, "start", -14), (peak, "middle", -16), (len(DATA) - 1, "end", -14)):
        x, y = points[i]
        add(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{ACCENT}" stroke="#ffffff" stroke-width="2"/>')
        add(
            f'<text x="{x:.1f}" y="{y + dy:.1f}" font-size="12" font-weight="bold" '
            f'fill="{INK}" text-anchor="{anchor}">{DATA[i][1] / 1e6:.2f}M</text>'
        )

    add("</svg>")

    with open("compilations-per-month.svg", "w") as f:
        f.write("\n".join(out))
    print("Wrote compilations-per-month.svg")
    print(f"Range: {DATA[0][1]:,} down to {DATA[-1][1]:,}; total {sum(v for _, v in DATA):,}")


if __name__ == "__main__":
    main()
