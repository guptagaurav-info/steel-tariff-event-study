import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

NAVY, GOLD, GREY, RED, TEAL = "#1f3a5f", "#c9a227", "#8a8f98", "#b23a3a", "#2a7f7f"
plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold",
                     "axes.titlesize": 12.5, "figure.dpi": 150, "savefig.bbox": "tight"})


def announcement_bars(G, labels, path):
    ev = list(G); x = np.arange(len(ev))
    us = [G[e]["US"]["car_0,1"] * 100 for e in ev]; fo = [G[e]["FO"]["car_0,1"] * 100 for e in ev]
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    ax.bar(x - 0.2, us, 0.4, color=NAVY, label="US steelmakers (5)"); ax.bar(x + 0.2, fo, 0.4, color=GREY, label="Foreign steelmakers (5, US-listed)")
    for i, v in enumerate(us): ax.text(i - 0.2, v + (0.3 if v >= 0 else -0.9), f"{v:+.1f}%", ha="center", fontsize=9.5)
    ax.axhline(0, color="black", lw=0.8); ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=9.5)
    ax.set_ylabel("Abnormal return, days 0 to +1 (%)"); ax.set_title("Two-day abnormal return on each tariff event, vs the market model")
    ax.legend(frameon=False, fontsize=9, loc="upper left"); fig.savefig(path); plt.close(fig)


def paths(Pths, path):
    fig, ax = plt.subplots(figsize=(10.5, 4.6))
    for lab, s, c, ls in Pths: ax.plot(s.index, s.values * 100, color=c, lw=1.7, ls=ls, label=lab)
    ax.axhline(0, color="black", lw=0.8); ax.axvline(0, color=GREY, lw=0.8, ls=":")
    ax.set_xlabel("Trading days from the announcement"); ax.set_ylabel("Return vs S&P 500 (%)")
    ax.set_title("US steelmakers vs the S&P 500 after each tariff announcement")
    ax.legend(frameon=False, fontsize=9, loc="upper left"); fig.savefig(path); plt.close(fig)


def bhar_bars(B, path):
    hs = list(B["2018"]["US"]); x = np.arange(len(hs))
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.4), sharey=True)
    for ax, (k, title) in zip(axs, [("2018", "After 1 Mar 2018"), ("2025", "After 10 Feb 2025")]):
        us = [B[k]["US"][h] * 100 for h in hs]; fo = [B[k]["FO"][h] * 100 for h in hs]
        ax.bar(x - 0.2, us, 0.4, color=NAVY, label="US steelmakers"); ax.bar(x + 0.2, fo, 0.4, color=GREY, label="Foreign steelmakers")
        ax.axhline(0, color="black", lw=0.8); ax.set_xticks(x); ax.set_xticklabels([f"{h} days" for h in hs]); ax.set_title(title)
    axs[0].set_ylabel("Buy-and-hold return minus S&P 500 (%)"); axs[0].legend(frameon=False, fontsize=9)
    fig.suptitle("Did the gain last? Equal-weight baskets vs the S&P 500", fontweight="bold"); fig.savefig(path); plt.close(fig)


def stock_bars(T, path):
    fig, ax = plt.subplots(figsize=(10.5, 4.4))
    t = T.groupby("stock")["car_0,1"].mean().sort_values() * 100
    ax.barh(t.index, t.values, color=[NAVY if s in ("NUE", "STLD", "CMC", "CLF", "RS") else GREY for s in t.index])
    ax.axvline(0, color="black", lw=0.8); ax.set_xlabel("Average two-day abnormal return across the three announcements (%)")
    ax.set_title("Which stocks moved: US (navy) vs foreign (grey)"); fig.savefig(path); plt.close(fig)
