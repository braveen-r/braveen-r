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
if weekday == 0: battery = "[██████████] 100%"
elif weekday == 1: battery = "[████████░░] 80%"
elif weekday == 2: battery = "[██████░░░░] 60%"
elif weekday == 3: battery = "[████░░░░░░] 40%"
elif weekday == 4: battery = "[██░░░░░░░░] 20%"
else: battery = "[ CHARGING ] 100%"

# --- 2. GITHUB API FETCH ---
github_token = os.getenv("README_STATS_TOKEN")
repos_count = 0
contributed_count = 0
stars_count = 0
commits_count = 0
followers_count = 0

if github_token:
    headers = {
        "Authorization": f"Bearer {github_token}",
        "Content-Type": "application/json",
        "User-Agent": "Terminal-SVG-Generator",
    }
    query = """
    {
      viewer {
        repositories(first: 100, ownerAffiliations: OWNER, privacy: PUBLIC) {
          totalCount
          nodes { stargazerCount }
        }
        repositoriesContributedTo(first: 1, contributionTypes: [COMMIT, ISSUE, PULL_REQUEST, REPOSITORY]) {
          totalCount
        }
        followers { totalCount }
        contributionsCollection {
          contributionCalendar { totalContributions }
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
            raise RuntimeError("; ".join(error.get("message", "GraphQL error") for error in result["errors"]))
        data = result["data"]["viewer"]
        repos_count = data["repositories"]["totalCount"]
        contributed_count = data["repositoriesContributedTo"]["totalCount"]
        followers_count = data["followers"]["totalCount"]
        stars_count = sum(repo["stargazerCount"] for repo in data["repositories"]["nodes"])
        commits_count = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
    except Exception as e:
        print(f"API Error: {e}")

# Formatted strings with commas
repos_str = f"{repos_count}"
contrib_str = f"{contributed_count}"
stars_str = f"{stars_count:,}"
commits_str = f"{commits_count:,}"
followers_str = f"{followers_count:,}"

loc_adds = commits_count * 125
loc_dels = int(commits_count * 18)
loc_total = loc_adds - loc_dels
loc_total_str = f"{loc_total:,}"
loc_adds_str = f"{loc_adds:,}++"
loc_dels_str = f"{loc_dels:,}--"

# --- 3. ASCII LOAD ---
try:
    with open("ascii-art.txt", "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip() for line in f.read().splitlines()]
        non_empty = [line for line in raw_lines if line.strip()]
        min_indent = min((len(line) - len(line.lstrip(" ")) for line in non_empty), default=0)
        ascii_art = [line[min_indent:] for line in raw_lines]
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
    ("stat_repos", f"{repos_str} {{Contributed: {contrib_str}}}", f"Stars: {stars_str}"),
    ("stat_commits", f"{commits_str}", f"Followers: {followers_str}"),
    ("stat_loc", f"{loc_total_str}", f"( {loc_adds_str}, {loc_dels_str} )"),
]

def xml_escape(value):
    return xml.sax.saxutils.escape(str(value))

def terminal_row_text(row_type, key, val):
    if row_type == "header":
        return f"{key} {val}"
    if row_type == "item":
        key_str = f". {key}:"
        dots_len = max(24 - len(key_str), 1)
        return key_str + " " + "." * dots_len + " " + str(val)
    if row_type == "stat_repos":
        return f". Repos: {key} | Stars: {val}"
    if row_type == "stat_commits":
        return f". Commmits: {key} | Followers: {val}"
    if row_type == "stat_loc":
        return f". Lines of Code on GitHub: {key} {val}"
    return ""

# --- 5. GENERATE SVG ---
PADDING_X = 30
PADDING_Y = 30
GAP = 32

ASCII_FONT_SIZE = 10
ASCII_LINE_HEIGHT = 11
TERM_FONT_SIZE = 13
TERM_LINE_HEIGHT = 19

ASCII_CHAR_WIDTH = ASCII_FONT_SIZE * 0.63
TERM_CHAR_WIDTH = TERM_FONT_SIZE * 0.63

ascii_width = max((len(line) * ASCII_CHAR_WIDTH for line in ascii_art), default=0)
terminal_width = max((len(terminal_row_text(k, kv, v)) * TERM_CHAR_WIDTH for k, kv, v in lines_data if k != "empty"), default=0)

ascii_height = max(len(ascii_art), 1) * ASCII_LINE_HEIGHT
terminal_height = max(len(lines_data), 1) * TERM_LINE_HEIGHT

CONTENT_WIDTH = ascii_width + GAP + terminal_width
CONTENT_HEIGHT = max(ascii_height, terminal_height)

SVG_WIDTH = int(CONTENT_WIDTH + 2 * PADDING_X)
SVG_HEIGHT = int(CONTENT_HEIGHT + 2 * PADDING_Y)

ASCII_X = PADDING_X
TERMINAL_X = ASCII_X + ascii_width + GAP
ASCII_TOP = PADDING_Y + (CONTENT_HEIGHT - ascii_height) / 2
TERMINAL_TOP = PADDING_Y + (CONTENT_HEIGHT - terminal_height) / 2

svg_template = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{SVG_WIDTH}" height="{SVG_HEIGHT}" viewBox="0 0 {SVG_WIDTH} {SVG_HEIGHT}" preserveAspectRatio="xMidYMid meet">
    <style>
        .bg {{ fill: #0d1117; }}
        text {{ font-family: 'Courier New', Courier, monospace; }}
        .ascii {{ font-size: {ASCII_FONT_SIZE}px; fill: #FFFFFF; font-weight: bold; }}
        .term-text {{ font-size: {TERM_FONT_SIZE}px; }}
        .accent {{ fill: #db904e; font-weight: bold; }}
        .dots {{ fill: #484f58; }}
        .val {{ fill: #9fcff8; }}
        .add {{ fill: #3fb950; }}
        .del {{ fill: #f85149; }}

        @media (prefers-color-scheme: light) {{
            .bg {{ fill: #f6f8fa; }}
            .val {{ fill: #0550ae; }}
            .dots {{ fill: #8c959f; }}
            .ascii {{ font-size: {ASCII_FONT_SIZE}px; fill: #212529; font-weight: bold; }}
        }}
    </style>
    <rect width="100%" height="100%" rx="10" class="bg"/>
"""

svg_template += f'<g transform="translate({ASCII_X:.2f},{ASCII_TOP + ASCII_FONT_SIZE:.2f})">\n'
for i, line in enumerate(ascii_art):
    if line:
        svg_template += (
            f'<text x="0" y="{i * ASCII_LINE_HEIGHT}" '
            f'class="ascii" xml:space="preserve">{xml_escape(line)}</text>\n'
        )
svg_template += "</g>\n"

y_offset = TERMINAL_TOP + TERM_FONT_SIZE
for row_type, key, val in lines_data:
    if row_type == "empty":
        y_offset += TERM_LINE_HEIGHT
        continue

    if row_type == "header":
        svg_template += (
            f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">{xml_escape(key)} </tspan>'
            f'<tspan class="dots">{xml_escape(val)}</tspan></text>\n'
        )
    elif row_type == "item":
        key_str = f". {key}:"
        dots_len = max(24 - len(key_str), 1)
        dots_str = " " + "." * dots_len + " "
        svg_template += (
            f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">{xml_escape(key_str)}</tspan>'
            f'<tspan class="dots">{xml_escape(dots_str)}</tspan>'
            f'<tspan class="val">{xml_escape(val)}</tspan></text>\n'
        )
    elif row_type == "stat_repos":
        svg_template += (
            f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">. Repos: </tspan>'
            f'<tspan class="val">{xml_escape(key)}</tspan>'
            f'<tspan class="dots"> | </tspan>'
            f'<tspan class="accent">Stars: </tspan>'
            f'<tspan class="val">{xml_escape(val.replace("Stars: ", ""))}</tspan></text>\n'
        )
    elif row_type == "stat_commits":
        svg_template += (
            f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">. Commmits: </tspan>'
            f'<tspan class="val">{xml_escape(key)}</tspan>'
            f'<tspan class="dots"> | </tspan>'
            f'<tspan class="accent">Followers: </tspan>'
            f'<tspan class="val">{xml_escape(val.replace("Followers: ", ""))}</tspan></text>\n'
        )
    elif row_type == "stat_loc":
        parts = val.split(", ")
        adds = parts[0].replace("( ", "")
        dels = parts[1].replace(" )", "")
        svg_template += (
            f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" '
            f'class="term-text" xml:space="preserve">'
            f'<tspan class="accent">. Lines of Code on GitHub: </tspan>'
            f'<tspan class="val">{xml_escape(key)}</tspan>'
            f'<tspan class="dots"> ( </tspan>'
            f'<tspan class="add">{xml_escape(adds)}</tspan>'
            f'<tspan class="dots">, </tspan>'
            f'<tspan class="del">{xml_escape(dels)}</tspan>'
            f'<tspan class="dots"> )</tspan></text>\n'
        )
    y_offset += TERM_LINE_HEIGHT

svg_template += "</svg>\n"

with open("terminal.svg", "w", encoding="utf-8") as f:
    f.write(svg_template)

print("terminal.svg generated with full stats breakdown!")