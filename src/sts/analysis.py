"""Event study: market-model abnormal returns, cumulative windows, Brown-Warner t-statistics, buy-and-hold abnormal returns."""
import numpy as np
import pandas as pd
import statsmodels.api as sm


def locate(index, day0):
    """Position of the first trading day on or after day0."""
    return int(index.searchsorted(pd.Timestamp(day0)))


def market_model(r, m, est):
    d = pd.concat([r, m], axis=1).dropna(); d.columns = ["r", "m"]
    if len(d) < 120: return None
    f = sm.OLS(d["r"], sm.add_constant(d["m"])).fit()
    return float(f.params["const"]), float(f.params["m"]), float(np.std(f.resid, ddof=2)), len(d)


def event_table(P, names, market, ev, est, windows, extra=None):
    """Abnormal returns for each stock around one event. extra: optional second factor (e.g. metals) for robustness."""
    i0 = locate(P.index, ev["day0"]); rows = []
    for s in names:
        e = P.iloc[i0 + est[0]: i0 + est[1] + 1]
        if extra is None:
            mm = market_model(e[s], e[market], est)
            if mm is None: continue
            a, b, sd, n = mm; exp = lambda w: a + b * w[market]
        else:
            d = e[[s, market, extra]].dropna()
            if len(d) < 120: continue
            f = sm.OLS(d[s], sm.add_constant(d[[market, extra]])).fit(); sd = float(np.std(f.resid, ddof=3)); n = len(d)
            exp = lambda w, f=f: f.params["const"] + f.params[market] * w[market] + f.params[extra] * w[extra]
            a, b = float(f.params["const"]), float(f.params[market])
        row = {"event": ev["id"], "stock": s, "beta": b, "sd": sd, "n_est": n}
        for k, (lo, hi) in windows.items():
            w = P.iloc[i0 + lo: i0 + hi + 1]
            ar = w[s] - exp(w); L = hi - lo + 1
            row[f"car_{k}"] = float(ar.sum()); row[f"t_{k}"] = float(ar.sum() / (sd * np.sqrt(L)))
        rows.append(row)
    return pd.DataFrame(rows)


def group_car(tab, group, windows):
    g = tab[tab.stock.isin(group)]; out = {"n": len(g)}
    for k in windows:
        c = g[f"car_{k}"]; out[f"car_{k}"] = float(c.mean())
        # portfolio t: mean CAR over the root-sum of each stock's CAR variance / n (ignores cross-correlation, so it overstates t; reported with that caveat)
        L = windows[k][1] - windows[k][0] + 1
        out[f"t_{k}"] = float(c.mean() / (np.sqrt((g["sd"] ** 2 * L).sum()) / len(g)))
        out[f"share_pos_{k}"] = float((c > 0).mean())
    return out


def basket(P, names):
    return P[names].mean(axis=1)


def bhar(P, names, market, day0, h):
    """Buy-and-hold return of the equal-weight basket minus SPY over h trading days from day 0 (inclusive)."""
    i0 = locate(P.index, day0); w = P.iloc[i0: i0 + h]
    if len(w) < h: return None
    b = (1 + w[names]).prod().mean() - 1; m = (1 + w[market]).prod() - 1
    return {"basket": float(b), "market": float(m), "bhar": float(b - m), "end": str(w.index[-1].date())}


def path(P, names, market, day0, before, after):
    i0 = locate(P.index, day0); w = P.iloc[max(0, i0 - before): i0 + after]
    rel = (1 + w[names]).cumprod().mean(axis=1) / (1 + w[market]).cumprod()
    base = rel.iloc[before - 1] if before > 0 else 1.0
    return pd.Series(rel.values / base - 1, index=np.arange(-before + 1, len(w) - before + 1))
