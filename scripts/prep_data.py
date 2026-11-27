"""Assemble walking-day tracks (BRouter + OSM way for day 2) and driving routes into data/trip_geo.json."""
import json, math, sys, time, urllib.request, urllib.parse
from pathlib import Path

D = Path(sys.argv[1])

def hav(a, b):
    R = 6371.0
    la1, la2 = math.radians(a[1]), math.radians(b[1])
    dla, dlo = la2 - la1, math.radians(b[0] - a[0])
    h = math.sin(dla/2)**2 + math.cos(la1)*math.cos(la2)*math.sin(dlo/2)**2
    return 2*R*math.asin(math.sqrt(h))

def thin(coords, min_km=0.04):
    out = [coords[0]]
    for c in coords[1:-1]:
        if hav(out[-1], c) >= min_km:
            out.append(c)
    out.append(coords[-1])
    return out

def brouter(name):
    f = json.load(open(D / f"walk_{name}.json"))["features"][0]
    return [[round(x[0], 5), round(x[1], 5), round(x[2])] for x in f["geometry"]["coordinates"]]

def elevations(pts):
    out = []
    for i in range(0, len(pts), 100):
        chunk = pts[i:i+100]
        q = urllib.parse.urlencode({"latitude": ",".join(str(p[1]) for p in chunk),
                                    "longitude": ",".join(str(p[0]) for p in chunk)})
        req = urllib.request.Request("https://api.open-meteo.com/v1/elevation?" + q,
                                     headers={"User-Agent": "kaimanawa-trip-planner"})
        out += json.load(urllib.request.urlopen(req, timeout=30))["elevation"]
        time.sleep(1)
    return out

# Day 2: OSM "Oamaru - Boyd Track" way runs Boyd -> Oamaru; reverse it and add the hut ends.
way = json.load(open(D / "ob.json"))[0]["geojson"]["coordinates"][::-1]
d2 = [[176.2649, -39.0763]] + [[round(c[0], 5), round(c[1], 5)] for c in way] + [[176.1694, -39.1545]]
d2 = thin(d2)
cache = D / "d2_elev.json"
if not cache.exists():
    json.dump(elevations(d2), open(cache, "w"))
ev = json.load(open(cache))
# the 90 m DEM is noisy on valley sides: smooth over ~7 points (~300 m) before use
ev = [sum(ev[max(0, i-3):i+4]) / len(ev[max(0, i-3):i+4]) for i in range(len(ev))]
for p, e in zip(d2, ev):
    p.append(round(e))

days = {"d1": thin(brouter("d1")), "d2": d2, "d3": thin(brouter("d3")),
        "d4": thin(brouter("d4")), "d5": thin(brouter("d5"))}

# The legs above run hut to hut. The camps are past the huts (Tom, 28 Nov 2026):
#   night 1: on the Oamaru River, about an hour past Oamaru Hut (~3.5 km up the valley);
#   night 2: on the Ngaruroro, about 45 min past Boyd Hut (~2.6 km), on the flats past the ford.
# Move those stretches from the start of the next day onto the end of the day before.
CAMP1_KM, CAMP2_KM = 3.5, 2.6

def cut(c, km):
    d = 0.0
    for i in range(1, len(c)):
        d += hav(c[i-1], c[i])
        if d >= km:
            return i
    return len(c) - 1

i = cut(days["d2"], CAMP1_KM)
days["d1"] = days["d1"] + days["d2"][1:i+1]
days["d2"] = days["d2"][i:]
i = cut(days["d3"], CAMP2_KM)
seg = [p[:] for p in days["d3"][:i+1]]
# Day 2 elevations (Open-Meteo) and day 3's (BRouter) disagree by tens of metres at Boyd Hut;
# taper the difference out over the moved stretch so the day 2 profile has no false step.
off = days["d2"][-1][2] - seg[0][2]
lens = [0.0]
for a, b in zip(seg, seg[1:]):
    lens.append(lens[-1] + hav(a, b))
for p, l in zip(seg, lens):
    p[2] = round(p[2] + off * (1 - l / lens[-1]))
days["d2"] = days["d2"] + seg[1:]
days["d3"] = days["d3"][i:]
print("camp 1", days["d1"][-1], "camp 2", days["d2"][-1])

def stats(c):
    dist = sum(hav(a, b) for a, b in zip(c, c[1:]))
    # smooth elevation a little before summing climb, like BRouter's "filtered ascend"
    up = down = 0.0
    ref = c[0][2]
    for p in c[1:]:
        d = p[2] - ref
        if abs(d) >= 10:
            up += max(d, 0); down += max(-d, 0); ref = p[2]
    return {"km": round(dist, 1), "up": round(up), "down": round(down),
            "min": min(p[2] for p in c), "max": max(p[2] for p in c)}

out = {"walk": {k: {"coords": v, **stats(v)} for k, v in days.items()}, "drive": {}}
for k in ["seatoun_makahu", "seatoun_palmy_makahu", "makahu_poronui"]:
    r = json.load(open(D / f"drive_{k}.json"))["routes"][0]
    out["drive"][k] = {"km": round(r["distance"]/1000), "min": round(r["duration"]/60),
                       "coords": [[round(x, 4), round(y, 4)] for x, y in thin(r["geometry"]["coordinates"], 0.3)]}
json.dump(out, open(D / "trip_geo.json", "w"), separators=(",", ":"))
for k, v in out["walk"].items():
    print(k, {kk: vv for kk, vv in v.items() if kk != "coords"}, len(v["coords"]))
for k, v in out["drive"].items():
    print(k, v["km"], v["min"], len(v["coords"]))
kj = max(days["d5"], key=lambda p: p[2]); print("Kaweka J approx", kj)
print("size", (D / "trip_geo.json").stat().st_size)
