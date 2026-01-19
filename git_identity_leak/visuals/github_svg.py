def generate_github_svg(days, out="contributions.svg"):
    CELL = 11
    GAP = 2

    weeks = {}
    for d in days:
        week = d["date"][:7]
        weeks.setdefault(week, []).append(d)

    def color(c):
        if c == 0: return "#ebedf0"
        if c < 5: return "#9be9a8"
        if c < 10: return "#40c463"
        if c < 20: return "#30a14e"
        return "#216e39"

    width = len(weeks) * (CELL + GAP)
    height = 7 * (CELL + GAP)

    svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">']

    x = 0
    for week in weeks.values():
        for d in week:
            y = datetime.strptime(d["date"], "%Y-%m-%d").weekday()
            svg.append(
                f'<rect x="{x}" y="{y*(CELL+GAP)}" width="{CELL}" height="{CELL}" fill="{color(d["count"])}"/>'
            )
        x += CELL + GAP

    svg.append("</svg>")

    with open(out, "w") as f:
        f.write("\n".join(svg))
