# Kaimanawa to Kaweka traverse, 12–16 Dec 2026

Trip page (map, schedule, day-by-day times) served from `docs/` on GitHub Pages.

Rebuild the page data after changing the route:

```sh
python -I scripts/prep_data.py data      # tracks + elevations -> data/trip_geo.json
python -I scripts/build_site.py .        # -> docs/trip-data.js, docs/kaimanawa-kaweka-2026.gpx
```

Sources: walking legs routed with BRouter (hiking-mountain profile) on OpenStreetMap, except day 2,
which is the OSM "Oamaru - Boyd Track" way with Open-Meteo elevations (BRouter can't connect it).
Driving routes and times from the OSRM demo server.
