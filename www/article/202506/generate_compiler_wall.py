#!/usr/bin/env python3
"""
Generate a visual "wall of compilers" from Compiler Explorer API data.
This creates an SVG visualization showing the scale and diversity of compilers.
"""

import json
import math
from collections import Counter

import requests


def fetch_compiler_data():
    """Fetch compiler data from the Compiler Explorer API."""
    headers = {"Accept": "application/json"}
    response = requests.get("https://compiler-explorer.com/api/compilers", headers=headers)
    return response.json()


def generate_treemap_svg(language_counts, total_count):
    """Generate a treemap-style SVG visualization."""
    svg_width = 800
    svg_height = 600

    # Color palette
    colors = [
        "#FF6B6B",
        "#4ECDC4",
        "#45B7D1",
        "#96CEB4",
        "#FECA57",
        "#FF7979",
        "#786FA6",
        "#F8B500",
        "#58B19F",
        "#2C3E50",
        "#CE6F3E",
        "#76B900",
        "#95A5A6",
        "#E74C3C",
        "#3498DB",
    ]

    svg_parts = []
    svg_parts.append(
        f"""<?xml version="1.0" encoding="UTF-8"?>
<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <style>
      .title {{ font: bold 24px sans-serif; fill: #333; }}
      .subtitle {{ font: 16px sans-serif; fill: #666; }}
      .lang-label {{ font: bold 14px sans-serif; fill: white; }}
      .lang-label-small {{ font: bold 12px sans-serif; fill: white; }}
      .count-label {{ font: 12px sans-serif; fill: white; }}
      .percent-label {{ font: 10px sans-serif; fill: white; opacity: 0.9; }}
      .stat-title {{ font: bold 24px sans-serif; fill: white; }}
      .stat-label {{ font: bold 14px sans-serif; fill: white; }}
    </style>
  </defs>

  <rect width="{svg_width}" height="{svg_height}" fill="#f8f9fa"/>

  <text x="{svg_width//2}" y="30" text-anchor="middle" class="title">The Compiler Explorer Wall</text>
  <text x="{svg_width//2}" y="50" text-anchor="middle" class="subtitle">{total_count:,} Compilers Across {len(language_counts)} Languages</text>
"""
    )

    # Create three rows with proper sizing
    margin = 20
    box_margin = 4
    start_y = 80

    # Calculate sizes for a proper treemap
    languages = list(language_counts.most_common(20))  # Show top 20

    # Row 1: Top 5 languages (larger boxes)
    row1_langs = languages[:5]
    # Row 2: Next 10 languages (medium boxes)
    row2_langs = languages[5:15]
    # Row 3: Remaining languages (smaller boxes)
    row3_langs = languages[15:20]

    # Row 1 - Large boxes
    y = start_y
    row_height = 110
    x = margin
    available_width = svg_width - 2 * margin

    # Calculate proportional widths for row 1
    row1_total = sum(count for _, count in row1_langs)
    for i, (lang, count) in enumerate(row1_langs):
        box_width = int((count / row1_total) * available_width) - box_margin
        color = colors[i % len(colors)]

        svg_parts.append(
            f"""
  <g>
    <rect x="{x}" y="{y}" width="{box_width}" height="{row_height}"
          fill="{color}" stroke="white" stroke-width="2" rx="4"/>
    <text x="{x + box_width//2}" y="{y + 35}" text-anchor="middle" class="lang-label">{lang.upper()}</text>
    <text x="{x + box_width//2}" y="{y + 60}" text-anchor="middle" class="count-label">{count}</text>
    <text x="{x + box_width//2}" y="{y + 80}" text-anchor="middle" class="percent-label">{count/total_count*100:.1f}%</text>
  </g>"""
        )

        x += box_width + box_margin

    # Row 2 - Medium boxes
    y += row_height + 10
    row_height = 90
    x = margin

    # Calculate proportional widths for row 2
    row2_total = sum(count for _, count in row2_langs)
    for i, (lang, count) in enumerate(row2_langs):
        box_width = int((count / row2_total) * available_width) - box_margin
        box_width = max(70, box_width)  # Minimum width to show text

        # Check if we need to wrap to next line
        if x + box_width > svg_width - margin:
            y += row_height + 10
            x = margin

        color = colors[(i + 5) % len(colors)]

        # Truncate language name if needed
        display_lang = lang.upper()
        if len(display_lang) > 7 and box_width < 100:
            display_lang = display_lang[:6] + "."

        svg_parts.append(
            f"""
  <g>
    <rect x="{x}" y="{y}" width="{box_width}" height="{row_height}"
          fill="{color}" stroke="white" stroke-width="2" rx="4"/>
    <text x="{x + box_width//2}" y="{y + 30}" text-anchor="middle" class="lang-label-small">{display_lang}</text>
    <text x="{x + box_width//2}" y="{y + 50}" text-anchor="middle" class="count-label">{count}</text>
    <text x="{x + box_width//2}" y="{y + 68}" text-anchor="middle" class="percent-label">{count/total_count*100:.1f}%</text>
  </g>"""
        )

        x += box_width + box_margin

    # Row 3 - Smaller boxes for remaining languages
    if row3_langs:
        y += row_height + 10
        row_height = 70
        x = margin

        for i, (lang, count) in enumerate(row3_langs):
            box_width = 140  # Fixed width for smaller languages

            if x + box_width > svg_width - margin:
                y += row_height + 10
                x = margin

            color = colors[(i + 15) % len(colors)]

            # Truncate language name for small boxes
            display_lang = lang.upper()
            if len(display_lang) > 10:
                display_lang = display_lang[:9] + "."

            svg_parts.append(
                f"""
  <g>
    <rect x="{x}" y="{y}" width="{box_width}" height="{row_height}"
          fill="{color}" stroke="white" stroke-width="2" rx="4"/>
    <text x="{x + box_width//2}" y="{y + 25}" text-anchor="middle" class="lang-label-small">{display_lang}</text>
    <text x="{x + box_width//2}" y="{y + 45}" text-anchor="middle" class="count-label">{count}</text>
    <text x="{x + box_width//2}" y="{y + 60}" text-anchor="middle" class="percent-label">{count/total_count*100:.1f}%</text>
  </g>"""
            )

            x += box_width + box_margin

    # Add statistics at the bottom - positioned dynamically
    stats_y = y + row_height + 30
    # Center the stats boxes
    stats_width = 170 * 4 + 15 * 3  # 4 boxes with gaps
    stats_x = (svg_width - stats_width) // 2

    svg_parts.append(
        f"""
  <g transform="translate({stats_x}, {stats_y})">
    <rect x="0" y="0" width="170" height="80" fill="#2C3E50" rx="4"/>
    <text x="85" y="30" text-anchor="middle" class="stat-label">Total Languages</text>
    <text x="85" y="55" text-anchor="middle" class="stat-title">{len(language_counts)}</text>

    <rect x="185" y="0" width="170" height="80" fill="#E74C3C" rx="4"/>
    <text x="270" y="30" text-anchor="middle" class="stat-label">Total Compilers</text>
    <text x="270" y="55" text-anchor="middle" class="stat-title">{total_count:,}</text>

    <rect x="370" y="0" width="170" height="80" fill="#3498DB" rx="4"/>
    <text x="455" y="30" text-anchor="middle" class="stat-label">Storage Size</text>
    <text x="455" y="55" text-anchor="middle" class="stat-title">3.9 TB</text>

    <rect x="555" y="0" width="170" height="80" fill="#27AE60" rx="4"/>
    <text x="640" y="30" text-anchor="middle" class="stat-label">Daily Builds</text>
    <text x="640" y="55" text-anchor="middle" class="stat-title">Trunk</text>
  </g>

  <text x="{svg_width//2}" y="{svg_height-10}" text-anchor="middle" style="font: 12px sans-serif; fill: #666;">
    godbolt.org - Making assembly accessible since 2012
  </text>
</svg>"""
    )

    return "".join(svg_parts)


def main():
    print("Fetching compiler data from Compiler Explorer API...")
    compilers = fetch_compiler_data()

    # Count compilers by language
    language_counts = Counter(compiler["lang"] for compiler in compilers)
    total_count = len(compilers)

    print(f"Found {total_count} compilers across {len(language_counts)} languages")
    print("\nTop 10 languages:")
    for lang, count in language_counts.most_common(10):
        print(f"  {lang}: {count} ({count/total_count*100:.1f}%)")

    # Generate SVG
    svg_content = generate_treemap_svg(language_counts, total_count)

    output_file = "compiler-wall-dynamic.svg"
    with open(output_file, "w") as f:
        f.write(svg_content)

    print(f"\nVisualization saved to {output_file}")

    # Also generate a simple text version for embedding
    print("\nGenerating embeddable stats...")
    stats = {
        "total_compilers": total_count,
        "total_languages": len(language_counts),
        "top_languages": list(language_counts.most_common(10)),
        "storage_size": "3.9TB",
    }

    with open("compiler-stats.json", "w") as f:
        json.dump(stats, f, indent=2)

    print("Stats saved to compiler-stats.json")


if __name__ == "__main__":
    main()
