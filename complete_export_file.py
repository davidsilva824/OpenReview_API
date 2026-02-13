import openreview
from urllib.parse import urlparse, parse_qs

# Insert login information.
client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net",
    username="EMAIL",
    password="PASSWORD"
)

in_csv = "WoProc 2026 Submission Status.csv"
out_csv = "WoProc 2026 Submission Status (modality + areas_and_methods).csv"

def forum_to_id(s):
    s = s.strip()
    if s.startswith("http"):
        return parse_qs(urlparse(s).query).get("id", [""])[0]
    return s

# keep exact same style in the csv
def csv_escape(x):
    x = "" if x is None else str(x)
    return '"' + x.replace('"', '""') + '"'

# read original lines
with open(in_csv, "r", encoding="utf-8-sig", newline="") as f:
    lines = f.read().splitlines()

header = lines[0]
rows = lines[1:]

# add columns to header (quoted, matching your file style)
new_lines = [header + ',"modality","areas_and_methods"']

for line in rows:
    if not line.strip():
        continue

    parts = line.split('","', 3)
    forum_field = parts[1]  # second column, without the outer quotes removed fully
    forum_field = forum_field.lstrip('"').rstrip('"')
    forum_id = forum_to_id(forum_field)

    note = client.get_note(forum_id)
    c = note.content

    modality = c.get("modality", {}).get("value", "")
    areas = c.get("areas_and_methods", {}).get("value", "")

    new_lines.append(line + "," + csv_escape(modality) + "," + csv_escape(areas))

# write back
with open(out_csv, "w", encoding="utf-8-sig", newline="") as f:
    f.write("\n".join(new_lines))
