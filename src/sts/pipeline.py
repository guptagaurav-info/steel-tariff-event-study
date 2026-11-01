"""Run the event study end to end: returns -> market models -> CARs per event -> long-horizon BHARs -> metrics.json + figures."""
import json
from pathlib import Path

import pandas as pd
import yaml

from . import analysis as A
from . import data, figures as F

ANNOUNCE = ["2018_announce", "2025_restored", "2025_doubled"]


def main(cfg_path="configs/default.yaml"):
    cfg = yaml.safe_load(open(cfg_path)); out = Path("reports"); (out / "figures").mkdir(parents=True, exist_ok=True)
    P = data.panel(cfg); US = list(cfg["us_steel"]); FO = list(cfg["foreign_steel"]); W = {k: tuple(v) for k, v in cfg["windows"].items()}
    tabs, G, G2 = [], {}, {}
    for ev in cfg["events"]:
        t = A.event_table(P, US + FO, cfg["market"], ev, cfg["estimation"], W); tabs.append(t)
        G[ev["id"]] = {"US": A.group_car(t, US, W), "FO": A.group_car(t, FO, W), "label": ev["label"], "day0": ev["day0"]}
        t2 = A.event_table(P, US, cfg["market"], ev, cfg["estimation"], W, extra=cfg["metals_proxy"])
        G2[ev["id"]] = A.group_car(t2, US, W)
    T = pd.concat(tabs)
    B = {}
    for k, d0 in [("2018", "2018-03-01"), ("2025", "2025-02-10")]:
        B[k] = {}
        for g, names in [("US", US), ("FO", FO)]:
            B[k][g] = {h: A.bhar(P, names, cfg["market"], d0, h)["bhar"] for h in cfg["long_horizons"]}
    last = {}
    for k, d0 in [("2018_to_2019_11", "2018-03-01"), ("2025_to_end", "2025-02-10")]:
        i0 = A.locate(P.index, d0); h = 430 if k.startswith("2018") else len(P) - i0
        last[k] = {g: A.bhar(P, names, cfg["market"], d0, h) for g, names in [("US", US), ("FO", FO)]}
    res = {"sample_end": str(P.index[-1].date()), "events": G, "events_two_factor_US": G2, "bhar": B, "longest": last,
           "per_stock": T.round(5).to_dict("records")}
    json.dump(res, open(out / "metrics.json", "w"), indent=2, default=float)
    T.to_csv(out / "event_car_by_stock.csv", index=False)
    F.announcement_bars({e: G[e] for e in ANNOUNCE}, ["1 Mar 2018\n25% announced", "10 Feb 2025\n25% restored", "2 Jun 2025\ndoubled to 50%"], out / "figures/announcements.png")
    F.paths([("1 Mar 2018", A.path(P, US, "SPY", "2018-03-01", 10, 250), "#1f3a5f", "-"),
             ("10 Feb 2025", A.path(P, US, "SPY", "2025-02-10", 10, 250), "#c9a227", "-"),
             ("2 Jun 2025", A.path(P, US, "SPY", "2025-06-02", 10, 250), "#2a7f7f", "--")], out / "figures/paths.png")
    F.bhar_bars(B, out / "figures/bhar.png"); F.stock_bars(T[T.event.isin(ANNOUNCE)], out / "figures/stocks.png")
    print(json.dumps({e: {g: {k: round(v, 4) for k, v in G[e][g].items()} for g in ("US", "FO")} for e in G}, indent=0)); print(json.dumps(B, indent=0, default=float)); print(json.dumps(last, default=str))
    return res


if __name__ == "__main__":
    main()
