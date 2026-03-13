# pip install openreview-py

import openreview
from urllib.parse import urlparse, parse_qs

# Insert login information.
client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net",
    username="EMAIL",
    password="PASSWORD"
)

in_csv = "WoProc 2026 Submission Status.csv"
out_csv = "WoProc 2026 Submission Status (modality + areas_and_methods + reviews).csv"

def forum_to_id(s):
    s = s.strip()
    if s.startswith("http"):
        return parse_qs(urlparse(s).query).get("id", [""])[0]
    return s

# keep exact same style in the csv
def csv_escape(x):
    x = "" if x is None else str(x)
    return '"' + x.replace('"', '""') + '"'

def content_value(content, key):
    v = content.get(key, {})
    return v.get("value", "") if isinstance(v, dict) else v

def first_signature(note):
    sigs = getattr(note, "signatures", None)
    if isinstance(sigs, list) and len(sigs) > 0:
        return sigs[0].split("/")[-1]
    return ""

# read original lines
with open(in_csv, "r", encoding="utf-8-sig", newline="") as f:
    lines = f.read().splitlines()

header = lines[0]
rows = lines[1:]

# add columns to header (quoted, matching your file style)
new_header = header + (
    ',"modality","areas_and_methods"'
    ',"review1_reviewer","review1_research_objectives","review1_methods_and_analysis","review1_impact_and_innovation","review1_overall_recommendation","review1_presentation_modality"'
    ',"review2_reviewer","review2_research_objectives","review2_methods_and_analysis","review2_impact_and_innovation","review2_overall_recommendation","review2_presentation_modality"'
)
new_lines = [new_header]

for line in rows:
    if not line.strip():
        continue

    # forum is column 2: "3","https://openreview.net/forum?id=...","Title",...
    parts = line.split('","', 3)
    forum_field = parts[1]
    forum_field = forum_field.lstrip('"').rstrip('"')
    forum_id = forum_to_id(forum_field)

    # submission fields
    note = client.get_note(forum_id)
    c = note.content
    modality = content_value(c, "modality")
    areas = content_value(c, "areas_and_methods")

    # get all notes in the forum, keep only official reviews
    forum_notes = client.get_all_notes(forum=forum_id)
    official_reviews = [
        n for n in forum_notes
        if any("/-/Official_Review" in inv for inv in (getattr(n, "invitations", None) or []))
    ]

    # stable ordering: oldest first
    official_reviews.sort(key=lambda n: getattr(n, "cdate", 0) or 0)

    # prepare 2 slots for two reviwers
    slot = []
    for i in range(2):
        if i < len(official_reviews):
            r = official_reviews[i]
            rc = r.content

            slot.append(first_signature(r))
            slot.append(content_value(rc, "research_objectives"))
            slot.append(content_value(rc, "methods_and_analysis"))
            slot.append(content_value(rc, "impact_and_innovation"))
            slot.append(content_value(rc, "overall_recommendation"))
            slot.append(content_value(rc, "presentation_modality"))
        else:
            slot.extend(["", "", "", "", "", ""])

    new_lines.append(
        line
        + "," + csv_escape(modality)
        + "," + csv_escape(areas)
        + "," + ",".join(csv_escape(x) for x in slot)
    )

# writing the file
with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
    f.write("\n".join(new_lines))