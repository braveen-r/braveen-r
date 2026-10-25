
import datetime
import os
import json
import urllib.request
import urllib.error
import xml.sax.saxutils


# --- 1. DYNAMIC CALCULATIONS ---
dob = datetime.datetime(2006, 11, 8, 22, 9)
now = datetime.datetime.now()
days_alive = (now - dob).days
years = days_alive // 365
days_remainder = days_alive % 365
uptime_string = f"{years} years, {days_remainder} days (Level {years})"

weekday = now.weekday()

if weekday == 0:
    battery = "[██████████] 100%"
elif weekday == 1:
    battery = "[████████░░] 80%"
elif weekday == 2:
    battery = "[██████░░░░] 60%"
elif weekday == 3:
    battery = "[████░░░░░░] 40%"
elif weekday == 4:
    battery = "[██░░░░░░░░] 20%"
else:
    battery = "[ CHARGING ] 100%"


# --- 2. GITHUB API FETCH ---
github_token = os.getenv("README_STATS_TOKEN")

repos_count = "..."
stars_count = "..."
commits_count = "..."
followers_count = "..."
loc_total = "..."

if github_token:
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
        "User-Agent": "Terminal-SVG-Generator",
    }

    query = """
    {
      viewer {
        repositories(
          first: 100
          ownerAffiliations: OWNER
          privacy: PUBLIC
        ) {
          totalCount
          nodes {
            stargazerCount
          }
        }
        followers {
          totalCount
        }
        contributionsCollection {
          contributionCalendar {
            totalContributions
          }
        }
      }
    }
    """

    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query}).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode("utf-8"))

        if result.get("errors"):
            raise RuntimeError(
                "; ".join(error.get("message", "GraphQL error")
                          for error in result["errors"])
            )

        data = result["data"]["viewer"]

        repos_count = data["repositories"]["totalCount"]
        followers_count = data["followers"]["totalCount"]

        stars_count = sum(
            repo["stargazerCount"]
            for repo in data["repositories"]["nodes"]
        )

        commits_count = (
            data["contributionsCollection"]
                ["contributionCalendar"]["totalContributions"]
        )

        # Estimate only, not actual measured lines of code.
        loc_total = f"{commits_count * 125}++"

    except Exception as e:
        print(f"API Error: {e}")


# --- 3. ASCII LOAD ---
try:
    with open("ascii-art.txt", "r", encoding="utf-8") as f:
        ascii_art = f.read().splitlines()
except FileNotFoundError:
    ascii_art = ["Error: ascii-art.txt not found."]


# --- 4. STRUCTURED DATA ---
lines_data = [
    ("header", "sunraku@archlinux", "-----------------------------------------"),
    ("item", "OS", "Arch Linux, Windows 11, Android"),
    ("item", "Player.Active", uptime_string),
    ("item", "Role", "Cloud & DevOps Eng."),
    ("item", "Desktop", "Hyprland, Win Explorer"),
    ("item", "Shell", "zsh, PowerShell"),
    ("item", "IDE", "Neovim, VS Code, Cursor"),
    ("item", "Battery", battery),
    ("item", "Fuel", "Coffee"),
    ("item", "Audio", "The Life of Ram | Govind Vasantha"),
    ("empty", "", ""),
    ("item", "Languages.Core", "JavaScript, Python, Bash, C"),
    ("item", "Languages.Web", "HTML, Tailwind, React, Node"),
    ("item", "Languages.Real", "English, Tamil, Malayalam"),
    ("item", "DevOps and DB", "Docker, Actions, Vercel, DuckDB"),
    ("item", "Hardware", "ASUS Vivobook (AMD Ryzen 3)"),
    ("item", "Hobbies", "System Ricing, Action RPGs, Anime"),
    ("empty", "", ""),
    ("header", "Contact", "-------------------------------------------------"),
    ("item", "Portfolio", "portfolio-weld-rho-75.vercel.app"),
    ("item", "Email", "braveenrprogrammer811@gmail.com"),
    ("item", "LinkedIn", "Braveen R"),
    ("item", "X (Twitter)", "@braveenruban"),
    ("item", "Instagram", "braveen_r"),
    ("item", "Discord", "itz_sunraku"),
    ("item", "Location", "Bangalore (Study) | Kerala (Home)"),
    ("empty", "", ""),
    ("header", "GitHub Stats", "------------------------------------------"),
    ("item", "Repos", f"{repos_count} | Stars: {stars_count}"),
    ("item", "Commits", f"{commits_count} | Followers: {followers_count}"),
    ("item", "Lines of Code", loc_total),
]


# --- 5. SVG RENDERING WITH DYNAMIC CENTERING ---

# Change these two values freely.
SVG_WIDTH = 950
SVG_HEIGHT = 600

# Layout settings
PADDING_X = 24
PADDING_Y = 24
GAP = 10

ASCII_FONT_SIZE = 10
ASCII_LINE_HEIGHT = 10

TERM_FONT_SIZE = 13
TERM_LINE_HEIGHT = 18

# Courier New is a monospace font: each character has a predictable width.
ASCII_CHAR_WIDTH = ASCII_FONT_SIZE * 0.602
GAP = -120
TERM_CHAR_WIDTH = TERM_FONT_SIZE * 0.602


def xml_escape(value):
    """Escape text safely for SVG/XML."""
    return xml.sax.saxutils.escape(str(value))


def terminal_row_text(row_type, key, val):
    """Return the full visible text for width measurement."""
    if row_type == "header":
        return f"{key} {val}"

    if row_type == "item":
        key_str = f". {key}:"
        dots_len = max(24 - len(key_str), 1)
        dots_str = " " + "." * dots_len + " "
        return key_str + dots_str + str(val)

    return ""


# Measure the ASCII art, preserving leading spaces.
ascii_width = max(
    (len(line) * ASCII_CHAR_WIDTH for line in ascii_art),
    default=0,
)

# Measure the longest terminal row.
terminal_width = max(
    (
        len(terminal_row_text(row_type, key, val)) * TERM_CHAR_WIDTH
        for row_type, key, val in lines_data
        if row_type != "empty"
    ),
    default=0,
)

# Heights use actual rendered row counts.
ascii_height = max(len(ascii_art), 1) * ASCII_LINE_HEIGHT
terminal_height = max(len(lines_data), 1) * TERM_LINE_HEIGHT

# Overall bounding box of the complete two-column layout.
CONTENT_WIDTH = ascii_width + GAP + terminal_width
CONTENT_HEIGHT = max(ascii_height, terminal_height)

# Center the complete group horizontally and vertically.
# If the content is larger than the canvas, align it to the padding.
CONTENT_X = max((SVG_WIDTH - CONTENT_WIDTH) / 2, PADDING_X)
CONTENT_Y = max((SVG_HEIGHT - CONTENT_HEIGHT) / 2, PADDING_Y)

ASCII_X = CONTENT_X
TERMINAL_X = ASCII_X + ascii_width + GAP

# SVG text y-coordinates are baselines, not top edges.
ASCII_START_Y = CONTENT_Y + ASCII_FONT_SIZE
TERMINAL_START_Y = CONTENT_Y + TERM_FONT_SIZE


svg_template = f"""<svg
    xmlns="http://www.w3.org/2000/svg"
    width="{SVG_WIDTH}"
    height="{SVG_HEIGHT}"
    viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}"
    preserveAspectRatio="xMidYMid meet"
>
    <style>
        .bg {{ fill: #0d1117; }}
        text {{ font-family: 'Courier New', Courier, monospace; }}
        .ascii {{ font-size: {ASCII_FONT_SIZE}px; fill: #FFFFFF; font-weight: bold; }}
        .term-text {{ font-size: {TERM_FONT_SIZE}px; }}
        .accent {{ fill: #db904e; font-weight: bold; }}
        .dots {{ fill: #484f58; }}
        .val {{ fill: #9fcff8; }}

        @media (prefers-color-scheme: light) {{
            .bg {{ fill: #f6f8fa; }}
            .val {{ fill: #0550ae; }}
            .dots {{ fill: #8c959f; }}
            .ascii {{ font-size: {ASCII_FONT_SIZE}px; fill: #212529; font-weight: bold; }}
        }}
    </style>

    <rect width="100%" height="100%" rx="10" class="bg"/>
"""


# Render ASCII art.
y_offset = ASCII_START_Y

for line in ascii_art:
    line_escaped = xml_escape(line)

    svg_template += (
        f'    <text x="{ASCII_X:.2f}" y="{y_offset:.2f}" '
        f'class="ascii" xml:space="preserve">{line_escaped}</text>\n'
    )

    y_offset += ASCII_LINE_HEIGHT


# Render terminal text.
y_offset = TERMINAL_START_Y

for row_type, key, val in lines_data:
    if row_type == "empty":
        y_offset += TERM_LINE_HEIGHT
        continue

    key_escaped = xml_escape(key)
    val_escaped = xml_escape(val)

    if row_type == "header":
        svg_template += (
            f'    <text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">{key_escaped} </tspan>'
            f'<tspan class="dots">{val_escaped}</tspan>'
            f'</text>\n'
        )

    elif row_type == "item":
        key_str = f". {key}:"
        dots_len = max(24 - len(key_str), 1)
        dots_str = " " + "." * dots_len + " "

        svg_template += (
            f'    <text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">{xml_escape(key_str)}</tspan>'
            f'<tspan class="dots">{xml_escape(dots_str)}</tspan>'
            f'<tspan class="val">{val_escaped}</tspan>'
            f'</text>\n'
        )

    y_offset += TERM_LINE_HEIGHT


svg_template += "</svg>\n"


# --- 6. SAVE SVG ---
with open("terminal.svg", "w", encoding="utf-8") as f:
    f.write(svg_template)

print("terminal.svg successfully generated!")
print(f"Canvas: {SVG_WIDTH} x {SVG_HEIGHT}")
print(f"Content origin: x={CONTENT_X:.2f}, y={CONTENT_Y:.2f}")
print(f"Estimated content size: {CONTENT_WIDTH:.2f} x {CONTENT_HEIGHT:.2f}")
