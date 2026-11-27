"""Write docs/trip-data.js and docs/kaimanawa-kaweka-2026.gpx from data/trip_geo.json.

Usage: python -I scripts/build_site.py <repo root>
"""
import json
import sys
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(sys.argv[1])
geo = json.load(open(ROOT / "data" / "trip_geo.json"))

DOC = "https://www.doc.govt.nz/parks-and-recreation/places-to-go"
KAI = DOC + "/central-north-island/places/kaimanawa-forest-park"
KAW = DOC + "/hawkes-bay/places/kaweka-forest-park"
URLS = {
    "makahu": KAW + "/things-to-do/huts/makahu-saddle-hut/",
    "poronui": KAI + "/things-to-do/tracks/boyd-oamaru-and-cascade-hut-tracks/",
    "oamaru": KAI + "/things-to-do/huts/oamaru-hut/",
    "boyd": KAI + "/things-to-do/huts/boyd-hut/",
    "tussock": KAW + "/things-to-do/huts/tussock-hut/",
    "harkness": KAW + "/things-to-do/huts/harkness-hut/",
    "venison": KAW + "/things-to-do/huts/venison-tops-hut-tira-lodge/",
    "kawekaj": KAW + "/",
    "tepuke": KAW + "/things-to-do/huts/te-pukeohikarua-te-puke-hut/",
    "mangaturutu": KAW + "/things-to-do/huts/mangaturutu-hut/",
    "ford_oamaru": "https://flowrate.co.nz/river/mohaka-river/poronui-station",
    "ford_ngaruroro": "https://flowrate.co.nz/river/ngaruroro-river/kuripapango",
    "ford_ngaawapurua": "https://flowrate.co.nz/river/ngaruroro-river/kuripapango",
    "ford_harkness": "https://flowrate.co.nz/river/ngaruroro-river/kuripapango",
    "ballard": KAW + "/things-to-do/huts/ballard-hut/",
}

POINTS = [
    # id, name, lat, lon, kind, note
    ("seatoun", "Seatoun (Car 1 leaves)", -41.3260, 174.8320, "town", "Tom K, Henry, Jonathan and Gils"),
    ("palmy", "Palmerston North (pick up Leo)", -40.3560, 175.6110, "town", "Car 2 collects Leo"),
    ("napier", "Napier", -39.4928, 176.9120, "town", "Fuel, food and supplies; about 1 h 15 from Makahu Saddle. Option for Friday night."),
    ("taupo", "Taupō", -38.6857, 176.0702, "town", "Nearest town to the Poronui start, on the Napier–Taupō road (SH5)."),
    ("makahu", "Makahu Saddle car park", -39.2869, 176.4078, "car", "Cars wait here all week. Merv collects us at 10:00 on Sat 12 Dec; Kate meets us here on Wed 16 Dec."),
    ("poronui", "Taharua road end, Poronui (Helisika hangar)", -38.9978, 176.2950, "start", "Start of the walk. Poled route through private Poronui Station: foot traffic only, no hunting, no dogs."),
    ("oamaru", "Oamaru Hut", -39.0763, 176.2649, "hut", "Day 1 passes here; the camp is about an hour further up the Oamaru River."),
    ("camp1", "Camp 1: Oamaru River", -39.09318, 176.23712, "camp", "Night 1 (Sat 12 Dec). The best campsites, about an hour (3.5 km) past Oamaru Hut up the Oamaru River. Position approximate."),
    ("boyd", "Boyd Hut", -39.1545, 176.1694, "hut", "Day 2 passes here: serviced hut, 16 bunks, airstrip. The camp is about 45 min further on."),
    ("camp2", "Camp 2: Ngaruroro River", -39.17424, 176.17997, "camp", "Night 2 (Sun 13 Dec). A great spot on the Ngaruroro, about 45 min (2.6 km) past Boyd Hut, past the ford. Position approximate."),
    ("ford_oamaru", "River crossing: Kaipō/Oamaru River", -39.0726, 176.2683, "ford", "Day 1, just before Oamaru Hut (position approximate). Fine at normal flow; don't cross if it's up. Nearest gauge: Mohaka at Poronui Station."),
    ("ford_ngaruroro", "River crossing: Ngaruroro River", -39.1692, 176.1794, "ford", "End of day 2, about 2 km past Boyd Hut, with two smaller channels in the next km. Usually below knee deep; floods quickly after rain. If it's up, camp at Boyd Hut. Gauge downstream: Ngaruroro at Kuripapango."),
    ("ford_ngaawapurua", "Stream crossings: Ngaawapurua Stream", -39.1958, 176.2296, "ford", "Day 3, the last 3 km into Harkness Hut: about 30 crossings through scrub. Easy at normal flow. No gauge on the stream; the Ngaruroro at Kuripapango shows how wet the catchment is."),
    ("ford_harkness", "Stream crossings past Harkness Hut", -39.1954, 176.2430, "ford", "Start of day 4: five crossings in the first 600 m before the climb. Same stream system as day 3."),
    ("tussock", "Tussock Hut", -39.1656, 176.2153, "hut", "Lunch or morning-tea stop on day 3, at the top of the climb from the Ngaruroro."),
    ("harkness", "Harkness Hut", -39.1955, 176.2392, "camp", "Night 3 (Mon 14 Dec). Wood stove, rain tank, long drop."),
    ("venison", "Venison Tops Hut (Tira Lodge)", -39.2472, 176.3217, "camp", "Night 4 (Tue 15 Dec). On the edge of the Kaweka tops. DOC alert: broken water tap; a crew is due to fix it on 14 Dec. If it isn't fixed, take the tank lid off and reach in."),
    ("kawekaj", "Kaweka J, 1724 m", -39.2762, 176.3819, "peak", "Highest point of the trip; memorial cairn. Exposed tops."),
    ("tepuke", "Te Pukeohikarua (Te Puke) Hut", -39.1935, 176.2766, "hut", "Day 4 passes here after about 4 km: a good first break."),
    ("mangaturutu", "Mangaturutu Hut", -39.2192, 176.3299, "hut", "Other hut nearby (shelter option)."),
    ("ballard", "Ballard Hut", -39.2380, 176.3698, "hut", "Other hut nearby (shelter option)."),
]

data = {
    "points": [dict(zip(["id", "name", "lat", "lon", "kind", "note"], p), url=URLS.get(p[0], ""),
                    link="River level on FlowRate" if p[4] == "ford" else "DOC page") for p in POINTS],
    "walk": geo["walk"],
    "drive": geo["drive"],
}
docs = ROOT / "docs"
docs.mkdir(exist_ok=True)
(docs / "trip-data.js").write_text(
    "window.TRIP = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8")

# GPX: one track per walking day, plus the waypoints, for offline phone apps.
DAY_NAMES = {
    "d1": "Day 1 Sat 12 Dec: Taharua road end past Oamaru Hut to camp on the Oamaru River",
    "d2": "Day 2 Sun 13 Dec: Oamaru River camp past Boyd Hut to camp on the Ngaruroro",
    "d3": "Day 3 Mon 14 Dec: Ngaruroro camp to Tussock Hut to Harkness Hut",
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
