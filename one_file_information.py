import openreview
import pandas as pd
from urllib.parse import urlparse, parse_qs

# EXACT SAME LOGIN STYLE THAT YOU CONFIRMED WORKS
client = openreview.api.OpenReviewClient(
    baseurl="https://api2.openreview.net",
    username="EMAIL",
    password="PASSWORD"
)

in_csv = "WoProc 2026 Submission Status.csv"
out_csv = "WoProc 2026 Submission Status (modality + areas_and_methods).csv"

df = pd.read_csv(in_csv)

def to_forum_id(x):
    s = str(x).strip()
    if s.startswith("http"):
        q = parse_qs(urlparse(s).query)
        return q.get("id", [""])[0].strip()
    return s

def get_value(content, key):
    v = content.get(key, {})
    return v.get("value", "") if isinstance(v, dict) else v

modality_col = []
areas_methods_col = []

for raw in df["forum"]:
    forum_id = to_forum_id(raw)

    note = client.get_note(forum_id)
    content = note.content

    modality_col.append(get_value(content, "modality"))
    areas_methods_col.append(get_value(content, "areas_and_methods"))

df["modality"] = modality_col
df["areas_and_methods"] = areas_methods_col

df.to_csv(out_csv, index=False)
print("Saved:", out_csv)
