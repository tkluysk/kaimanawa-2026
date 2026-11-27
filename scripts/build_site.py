"""Write docs/trip-data.js and docs/kaimanawa-kaweka-2026.gpx from data/trip_geo.json.

Usage: python -I scripts/build_site.py <repo root>
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(sys.argv[1])
geo = json.load(open(ROOT / "data" / "trip_geo.json"))

POINTS = [
    # id, name, lat, lon, kind, note
    ("seatoun", "Seatoun (Car 1 leaves)", -41.3260, 174.8320, "town", "Tom K, Henry, Jonathan and Gils"),
    ("palmy", "Palmerston North (pick up Leo)", -40.3560, 175.6110, "town", "Car 2 collects Leo"),
    ("makahu", "Makahu Saddle car park", -39.2869, 176.4078, "car", "Cars wait here all week. Merv collects us at 10:00 on Sat 12 Dec; Kate meets us here on Wed 16 Dec."),
    ("poronui", "Taharua road end, Poronui (Helisika hangar)", -38.9978, 176.2950, "start", "Start of the walk. Poled route through private Poronui Station: foot traffic only, no hunting, no dogs."),
    ("oamaru", "Oamaru Hut", -39.0763, 176.2649, "camp", "Night 1 (Sat 12 Dec). Grassy flats below the hut."),
    ("boyd", "Boyd Hut", -39.1545, 176.1694, "camp", "Night 2 (Sun 13 Dec). Serviced hut, 16 bunks."),
    ("tussock", "Tussock Hut", -39.1656, 176.2153, "hut", "Lunch stop on day 3, after fording the Ngaruroro River."),
    ("harkness", "Harkness Hut", -39.1955, 176.2392, "camp", "Night 3 (Mon 14 Dec). Wood stove, rain tank, long drop."),
    ("venison", "Venison Tops Hut (Tira Lodge)", -39.2472, 176.3217, "camp", "Night 4 (Tue 15 Dec). On the edge of the Kaweka tops."),
    ("kawekaj", "Kaweka J, 1724 m", -39.2762, 176.3819, "peak", "Highest point of the trip; memorial cairn. Exposed tops."),
    ("tepuke", "Te Pukeohikarua (Te Puke) Hut", -39.1935, 176.2766, "hut", "Other hut nearby (shelter option)."),
    ("mangaturutu", "Mangaturutu Hut", -39.2192, 176.3299, "hut", "Other hut nearby (shelter option)."),
    ("ballard", "Ballard Hut", -39.2380, 176.3698, "hut", "Other hut nearby (shelter option)."),
]

data = {
    "points": [dict(zip(["id", "name", "lat", "lon", "kind", "note"], p)) for p in POINTS],
    "walk": geo["walk"],
    "drive": geo["drive"],
}
docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "trip-data.js").write_text(
    "window.TRIP = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")

# GPX: one track per walking day, plus the waypoints, for offline phone apps.
DAY_NAMES = {
    "d1": "Day 1 Sat 12 Dec: Taharua road end to Oamaru Hut",
    "d2": "Day 2 Sun 13 Dec: Oamaru Hut to Boyd Hut",
    "d3": "Day 3 Mon 14 Dec: Boyd Hut to Tussock Hut to Harkness Hut",
    "d4": "Day 4 Tue 15 Dec: Harkness Hut to Venison Tops Hut",
    "d5": "Day 5 Wed 16 Dec: Venison Tops Hut over Kaweka J to Makahu Saddle",
}
out = ['<?xml version="1.0" encoding="UTF-8"?>',
       '<gpx version="1.1" creator="kaimanawa-2026" xmlns="http://www.topografix.com/GPX/1/1">',
       '<metadata><name>Kaimanawa to Kaweka traverse, 12-16 Dec 2026</name></metadata>']
for p in POINTS:
    if p[4] in ("town",):
        continue
    out.append(f'<wpt lat="{p[2]}" lon="{p[3]}"><name>{escape(p[1])}</name><desc>{escape(p[5])}</desc></wpt>')
for k, name in DAY_NAMES.items():
    out.append(f"<trk><name>{escape(name)}</name><trkseg>")
    out += [f'<trkpt lat="{c[1]}" lon="{c[0]}"><ele>{c[2]}</ele></trkpt>' for c in geo["walk"][k]["coords"]]
    out.append("</trkseg></trk>")
out.append("</gpx>")
(docs / "kaimanawa-kaweka-2026.gpx").write_text("\n".join(out), encoding="utf-8")
print("wrote", docs / "trip-data.js", docs / "kaimanawa-kaweka-2026.gpx")
