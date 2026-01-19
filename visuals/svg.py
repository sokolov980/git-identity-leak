def generate_github_svg(days, output_path):
    CELL = 11
    GAP = 2

    weeks = {}
    for d in days:
        week = d["date"][:7]
        weeks.setdefault(week, []).append(d)

    svg_width = len(weeks) * (CELL + GAP)
    svg_height = 7 * (CELL + GAP)

    def color(c):
        if c == 0: return "#ebedf0"
        if c < 5: return "#9be9a8"
        if c < 10: return "#40c463"
        if c < 20: return "#30a14e"
        return "#216e39"

    svg = [f'<svg width="{svg_width}" height="{svg_height}" xmlns="http://www.w3.org/2000/svg">']

    x = 0
    for week in weeks.values():
        for d in week:
            y = int(d["date"][-2:]) % 7
            svg.append(
                f'<rect x="{x}" y="{y*(CELL+GAP)}" width="{CELL}" height="{CELL}" fill="{color(d["count"])}"/>'
            )
        x += CELL + GAP

    svg.append("</svg>")

    with open(output_path, "w") as f:
        f.write("\n".join(svg))
