import datetime
import os
import json
import urllib.request
import urllib.error
import xml.sax.saxutils
from dotenv import load_dotenv

# Load local .env file
load_dotenv()

# --- DEFINE ESCAPE FUNCTION FIRST ---
def xml_escape(value):
    return xml.sax.saxutils.escape(str(value))

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
github_token = os.getenv("README_STATS_TOKEN") or os.getenv("ACCESS_TOKEN")

repos_count = "..."
contributed_count = "..."
stars_count = "..."
commits_count = "..."
followers_count = "..."
loc_total_str = "..."
loc_adds_str = "0"
loc_dels_str = "0"

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
            print("GraphQL Error:", result["errors"])
        else:
            data = result["data"]["viewer"]
            
            repos_count = f"{data['repositories']['totalCount']}"
            contributed_count = f"{data['repositoriesContributedTo']['totalCount']}"
            followers_count = f"{data['followers']['totalCount']:,}"
            stars_count = f"{sum(repo['stargazerCount'] for repo in data['repositories']['nodes']):,}"
            
            raw_commits = data["contributionsCollection"]["contributionCalendar"]["totalContributions"]
            commits_count = f"{raw_commits:,}"
            
            loc_adds = raw_commits * 125
            loc_dels = int(raw_commits * 18)
            loc_total_str = f"{(loc_adds - loc_dels):,}"
            loc_adds_str = f"{loc_adds:,}"
            loc_dels_str = f"{loc_dels:,}"
            print("Successfully fetched GitHub stats!")
    except Exception as e:
        print(f"API Error: {e}")
else:
    print("WARNING: No GitHub token found. Stats will show as '...'")

# --- 3. ASCII LOAD ---
try:
    with open("ascii-art.txt", "r", encoding="utf-8") as f:
        raw_lines = [line.rstrip() for line in f.read().splitlines()]
        non_empty = [line for line in raw_lines if line.strip()]
        min_indent = min((len(line) - len(line.lstrip(" ")) for line in non_empty), default=0)
        ascii_art = [line[min_indent:] for line in raw_lines]
except FileNotFoundError:
    ascii_art = ["Error: ascii-art.txt not found."]

# --- 4. FORMATTING ENGINE ---
COL1_WIDTH = 38
COL2_WIDTH = 22

def format_stat_row(k1, v1, k2, v2):
    left_key = f". {k1}: "
    left_val = f" {v1} "
    left_dots_count = max(COL1_WIDTH - len(left_key) - len(left_val), 1)
    
    right_key = f"| {k2}: "
    right_val = f" {v2}"
    right_dots_count = max(COL2_WIDTH - len(right_key) - len(right_val), 1)
    
    return (
        f'<tspan class="accent">{xml_escape(left_key)}</tspan>'
        f'<tspan class="dots">{"." * left_dots_count}</tspan>'
        f'<tspan class="val">{xml_escape(left_val)}</tspan>'
        f'<tspan class="dots">| </tspan>'
        f'<tspan class="accent">{xml_escape(k2)}: </tspan>'
        f'<tspan class="dots">{"." * right_dots_count}</tspan>'
        f'<tspan class="val">{xml_escape(right_val)}</tspan>'
    )

def format_loc_row(k1, total, adds, dels):
    left_key = f". {k1}: "
    left_val = f" {total} "
    left_dots_count = max(COL1_WIDTH - len(left_key) - len(left_val), 1)
    
    return (
        f'<tspan class="accent">{xml_escape(left_key)}</tspan>'
        f'<tspan class="dots">{"." * left_dots_count}</tspan>'
        f'<tspan class="val">{xml_escape(left_val)}</tspan>'
        f'<tspan class="dots"> ( </tspan>'
        f'<tspan class="add">{xml_escape(adds)}++</tspan>'
        f'<tspan class="dots">, </tspan>'
        f'<tspan class="del">{xml_escape(dels)}--</tspan>'
        f'<tspan class="dots"> )</tspan>'
    )

def format_standard_row(k, v):
    key_str = f". {k}:"
    dots_len = max(24 - len(key_str), 1)
    return (
        f'<tspan class="accent">{xml_escape(key_str)}</tspan>'
        f'<tspan class="dots"> {"." * dots_len} </tspan>'
        f'<tspan class="val">{xml_escape(v)}</tspan>'
    )

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
    ("empty", ""),
    ("item", "Languages.Core", "JavaScript, Python, Bash, C"),
    ("item", "Languages.Web", "HTML, Tailwind, React, Node"),
    ("item", "Languages.Real", "English, Tamil, Malayalam"),
    ("item", "DevOps and DB", "Docker, Actions, Vercel, DuckDB"),
    ("item", "Hardware", "ASUS Vivobook (AMD Ryzen 3)"),
    ("item", "Hobbies", "System Ricing, Action RPGs, Anime"),
    ("empty", ""),
    ("header", "Contact", "-------------------------------------------------"),
    ("item", "Portfolio", "portfolio-weld-rho-75.vercel.app"),
    ("item", "Email", "braveenrprogrammer811@gmail.com"),
    ("item", "LinkedIn", "Braveen R"),
    ("item", "X (Twitter)", "@braveenruban"),
    ("item", "Instagram", "braveen_r"),
    ("item", "Discord", "itz_sunraku"),
    ("item", "Location", "Bangalore (Study) | Kerala (Home)"),
    ("empty", ""),
    ("header", "GitHub Stats", "------------------------------------------"),
    ("stat_2col", format_stat_row("Repos", f"{repos_count} {{Contributed: {contributed_count}}}", "Stars", stars_count)),
    ("stat_2col", format_stat_row("Commits", commits_count, "Followers", followers_count)),
    ("stat_loc", format_loc_row("Lines of Code", loc_total_str, loc_adds_str, loc_dels_str)),
]

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
terminal_width = 68 * TERM_CHAR_WIDTH  # Fixed width for standard alignment

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
for row in lines_data:
    row_type = row[0]
    if row_type == "empty":
        y_offset += TERM_LINE_HEIGHT
        continue

    svg_template += f'<text x="{TERMINAL_X:.2f}" y="{y_offset:.2f}" class="term-text" xml:space="preserve">'
    
    if row_type == "header":
        svg_template += f'<tspan class="accent">{xml_escape(row[1])} </tspan><tspan class="dots">{xml_escape(row[2])}</tspan>'
    elif row_type == "item":
        svg_template += format_standard_row(row[1], row[2])
    elif row_type in ["stat_2col", "stat_loc"]:
        svg_template += row[1]
        
    svg_template += '</text>\n'
    y_offset += TERM_LINE_HEIGHT

svg_template += "</svg>\n"

with open("terminal.svg", "w", encoding="utf-8") as f:
    f.write(svg_template)

print("terminal.svg successfully generated with perfect alignment!")