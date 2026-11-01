import numpy as np
import pandas as pd

from sts import analysis as A

idx = pd.bdate_range("2020-01-01", periods=400)


def test_market_model_recovers_alpha_beta():
    rng = np.random.default_rng(0); m = pd.Series(rng.normal(0, 0.01, 300)); r = 0.0002 + 1.5 * m + rng.normal(0, 0.002, 300)
    a, b, sd, n = A.market_model(r, m, None)
    assert abs(b - 1.5) < 0.05 and n == 300


def test_event_car_isolates_the_jump():
    rng = np.random.default_rng(1); m = rng.normal(0, 0.01, 400); r = 1.2 * m + rng.normal(0, 0.003, 400)
    r[300] += 0.10                                  # a 10% jump on day 0 only
    P = pd.DataFrame({"SPY": m, "AAA": r}, index=idx)
    t = A.event_table(P, ["AAA"], "SPY", {"id": "e", "day0": str(idx[300].date())}, [-260, -21], {"0,1": (0, 1), "2,20": (2, 20)})
    assert abs(t.loc[0, "car_0,1"] - 0.10) < 0.02 and abs(t.loc[0, "car_2,20"]) < 0.04


def test_estimation_window_excludes_the_event():
    # a huge jump on day 0 must not change the estimated beta (estimation ends at day -21)
    rng = np.random.default_rng(2); m = rng.normal(0, 0.01, 400); r = m.copy(); r2 = r.copy(); r2[300] += 0.5
    P1 = pd.DataFrame({"SPY": m, "AAA": r}, index=idx); P2 = pd.DataFrame({"SPY": m, "AAA": r2}, index=idx)
    ev = {"id": "e", "day0": str(idx[300].date())}; w = {"0,1": (0, 1)}
    assert A.event_table(P1, ["AAA"], "SPY", ev, [-260, -21], w).loc[0, "beta"] == A.event_table(P2, ["AAA"], "SPY", ev, [-260, -21], w).loc[0, "beta"]


def test_bhar_definition():
    P = pd.DataFrame({"SPY": [0.01] * 5, "AAA": [0.02] * 5}, index=idx[:5])
    b = A.bhar(P, ["AAA"], "SPY", str(idx[0].date()), 5)
    assert abs(b["bhar"] - (1.02 ** 5 - 1.01 ** 5)) < 1e-12
