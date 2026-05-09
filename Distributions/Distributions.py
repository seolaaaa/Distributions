
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.widgets import Slider, RadioButtons
from scipy import stats

# ── Color palette ──────────────────────────────────────────────────────────
PALETTE = {
    "Normal":      "#378ADD",
    "Beta":        "#1D9E75",
    "Gamma":       "#BA7517",
    "Exponential": "#D4537E",
    "Poisson":     "#7F77DD",
    "Binomial":    "#D85A30",
}
BG       = "#0f0f12"
SURFACE  = "#1a1a20"
BORDER   = "#2e2e38"
TEXT     = "#e8e8f0"
MUTED    = "#888898"

plt.rcParams.update({
    "figure.facecolor":  BG,
    "axes.facecolor":    SURFACE,
    "axes.edgecolor":    BORDER,
    "axes.labelcolor":   TEXT,
    "xtick.color":       MUTED,
    "ytick.color":       MUTED,
    "text.color":        TEXT,
    "grid.color":        BORDER,
    "grid.linewidth":    0.6,
    "font.family":       "monospace",
    "font.size":         10,
})

# ── Distribution definitions ────────────────────────────────────────────────
DISTRIBUTIONS = {
    "Normal": {
        "params": {"μ (mean)": (0.0, -5.0, 5.0, 0.1),
                   "σ (std)":  (1.0,  0.1, 5.0, 0.1)},
        "xrange": (-8, 8),
        "continuous": True,
        "desc": "Bell curve — defined by mean & std dev.\nAppears via the Central Limit Theorem.",
        "rv_fn": lambda p: stats.norm(loc=p[0], scale=p[1]),
    },
    "Beta": {
        "params": {"α (alpha)": (2.0, 0.1, 10.0, 0.1),
                   "β (beta)":  (5.0, 0.1, 10.0, 0.1)},
        "xrange": (0, 1),
        "continuous": True,
        "desc": "Lives on [0,1]. Models probabilities.\nTry α=β=1 (uniform) or α=β=0.5 (U-shape).",
        "rv_fn": lambda p: stats.beta(a=p[0], b=p[1]),
    },
    "Gamma": {
        "params": {"k (shape)": (2.0, 0.5, 10.0, 0.5),
                   "θ (scale)": (1.0, 0.1,  4.0, 0.1)},
        "xrange": (0, 20),
        "continuous": True,
        "desc": "Models waiting times & positive processes.\nk=1 → Exponential. χ² is a special case.",
        "rv_fn": lambda p: stats.gamma(a=p[0], scale=p[1]),
    },
    "Exponential": {
        "params": {"λ (rate)": (1.0, 0.1, 5.0, 0.1)},
        "xrange": (0, 10),
        "continuous": True,
        "desc": "Time between random events.\nMemoryless: future ⊥ past.",
        "rv_fn": lambda p: stats.expon(scale=1/p[0]),
    },
    "Poisson": {
        "params": {"λ (rate)": (4.0, 0.5, 20.0, 0.5)},
        "xrange": (0, 35),
        "continuous": False,
        "desc": "Counts events in a fixed interval.\nMean = Variance = λ.",
        "rv_fn": lambda p: stats.poisson(mu=p[0]),
    },
    "Binomial": {
        "params": {"n (trials)": (20.0,  1.0, 50.0, 1.0),
                   "p (prob)":   ( 0.5, 0.01,  0.99, 0.01)},
        "xrange": (0, 50),
        "continuous": False,
        "desc": "Successes in n independent trials.\nApproaches Poisson as n→∞.",
        "rv_fn": lambda p: stats.binom(n=int(p[0]), p=p[1]),
    },
}

DIST_NAMES = list(DISTRIBUTIONS.keys())

# ── Figure layout ────────────────────────────────────────────────────────────
fig = plt.figure(figsize=(14, 8))
fig.suptitle("Family of Distributions", fontsize=16, fontweight="bold",
             color=TEXT, y=0.98)

gs = gridspec.GridSpec(
    3, 3,
    figure=fig,
    left=0.05, right=0.98,
    top=0.92, bottom=0.06,
    hspace=0.55, wspace=0.35,
)

ax_main   = fig.add_subplot(gs[:2, :2])   # large plot
ax_radio  = fig.add_subplot(gs[:2,  2])   # distribution selector
ax_sl1    = fig.add_subplot(gs[2,   0])   # slider 1
ax_sl2    = fig.add_subplot(gs[2,   1])   # slider 2
ax_stats  = fig.add_subplot(gs[2,   2])   # stats

for ax in [ax_radio, ax_sl1, ax_sl2, ax_stats]:
    ax.set_facecolor(BG)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_xticks([])
    ax.set_yticks([])

ax_main.grid(True, alpha=0.4)

# ── State ───────────────────────────────────────────────────────────────────
state = {"dist": "Normal", "sliders": {}}

# ── Radio buttons ────────────────────────────────────────────────────────────
radio = RadioButtons(
    ax_radio, DIST_NAMES,
    active=0,
    activecolor=PALETTE["Normal"],
)
ax_radio.set_title("Distribution", color=MUTED, fontsize=9, pad=4)
for lbl in radio.labels:
    lbl.set_color(TEXT)
    lbl.set_fontsize(10)
radio.ax.set_facecolor(BG)

# ── Slider holders ───────────────────────────────────────────────────────────
slider_axes = [ax_sl1, ax_sl2]
sliders     = [None, None]

def make_slider(ax_parent, label, val, vmin, vmax, vstep, color):
    ax_parent.clear()
    ax_parent.set_facecolor(BG)
    for sp in ax_parent.spines.values():
        sp.set_visible(False)
    ax_parent.set_xticks([])
    ax_parent.set_yticks([])
    # inset axes for the actual slider
    sl_ax = ax_parent.inset_axes([0.05, 0.25, 0.90, 0.4])
    sl_ax.set_facecolor(BG)
    sl = Slider(sl_ax, label, vmin, vmax,
                valinit=val, valstep=vstep,
                color=color, track_color=BORDER)
    sl.label.set_color(MUTED)
    sl.label.set_fontsize(9)
    sl.valtext.set_color(TEXT)
    sl.valtext.set_fontsize(9)
    return sl

def rebuild_sliders(dist_name):
    d = DISTRIBUTIONS[dist_name]
    color = PALETTE[dist_name]
    param_items = list(d["params"].items())

    for i, sl_ax in enumerate(slider_axes):
        if i < len(param_items):
            lbl, (val, vmin, vmax, vstep) = param_items[i]
            sliders[i] = make_slider(sl_ax, lbl, val, vmin, vmax, vstep, color)
            sliders[i].on_changed(lambda v: update_plot())
        else:
            sl_ax.clear()
            sl_ax.set_facecolor(BG)
            for sp in sl_ax.spines.values():
                sp.set_visible(False)
            sliders[i] = None

    update_plot()

def get_param_values(dist_name):
    d = DISTRIBUTIONS[dist_name]
    param_items = list(d["params"].items())
    vals = []
    for i, (lbl, (default, *_)) in enumerate(param_items):
        if sliders[i] is not None:
            vals.append(sliders[i].val)
        else:
            vals.append(default)
    return vals

# ── Stats panel ──────────────────────────────────────────────────────────────
def draw_stats(dist_name, rv, params):
    ax_stats.clear()
    ax_stats.set_facecolor(BG)
    for sp in ax_stats.spines.values():
        sp.set_visible(False)
    ax_stats.set_xticks([])
    ax_stats.set_yticks([])

    try:
        mean   = rv.mean()
        var    = rv.var()
        std    = rv.std()
        median = rv.median()
    except Exception:
        mean = var = std = median = float("nan")

    color = PALETTE[dist_name]
    desc  = DISTRIBUTIONS[dist_name]["desc"]

    y = 0.95
    ax_stats.text(0.05, y, "Statistics", color=color, fontsize=9,
                  fontweight="bold", transform=ax_stats.transAxes, va="top")
    y -= 0.12
    for label, val in [("Mean", mean), ("Variance", var),
                        ("Std dev", std), ("Median", median)]:
        ax_stats.text(0.05, y, f"{label}:", color=MUTED, fontsize=8,
                      transform=ax_stats.transAxes, va="top")
        ax_stats.text(0.95, y, f"{val:.3g}", color=TEXT, fontsize=8,
                      transform=ax_stats.transAxes, va="top", ha="right")
        y -= 0.11

    y -= 0.04
    ax_stats.axhline(y=y, xmin=0.05, xmax=0.95,
                     color=BORDER, linewidth=0.8)
    y -= 0.06
    for line in desc.split("\n"):
        ax_stats.text(0.05, y, line, color=MUTED, fontsize=7.5,
                      transform=ax_stats.transAxes, va="top", wrap=True)
        y -= 0.11

# ── Main plot ─────────────────────────────────────────────────────────────────
plot_line   = [None]
plot_bar    = [None]
fill_obj    = [None]

def update_plot():
    dist_name = state["dist"]
    d         = DISTRIBUTIONS[dist_name]
    params    = get_param_values(dist_name)
    color     = PALETTE[dist_name]

    try:
        rv = d["rv_fn"](params)
    except Exception:
        return

    x0, x1 = d["xrange"]

    ax_main.clear()
    ax_main.set_facecolor(SURFACE)
    ax_main.grid(True, alpha=0.3)
    ax_main.set_xlabel("x" if d["continuous"] else "k", color=MUTED, fontsize=9)
    ax_main.set_ylabel("Density" if d["continuous"] else "Probability", color=MUTED, fontsize=9)
    ax_main.tick_params(colors=MUTED, labelsize=8)
    for sp in ax_main.spines.values():
        sp.set_color(BORDER)

    label_str = dist_name + " (" + ", ".join(
        f"{k.split()[0]}={v:.2g}"
        for k, v in zip(d["params"].keys(), params)
    ) + ")"
    ax_main.set_title(label_str, color=TEXT, fontsize=11, pad=8)

    if d["continuous"]:
        xs = np.linspace(x0, x1, 600)
        ys = rv.pdf(xs)
        ax_main.plot(xs, ys, color=color, linewidth=2.2, zorder=3)
        ax_main.fill_between(xs, ys, alpha=0.18, color=color, zorder=2)
        ax_main.set_xlim(x0, x1)
    else:
        ks = np.arange(int(x0), int(x1) + 1)
        ps = rv.pmf(ks)
        ax_main.bar(ks, ps, color=color, alpha=0.75, width=0.7,
                    edgecolor=color, linewidth=0.5, zorder=3)
        ax_main.set_xlim(x0 - 1, min(x1, ks[ps > 1e-4].max() + 2) if ps.any() else x1)

    ax_main.set_ylim(bottom=0)
    draw_stats(dist_name, rv, params)
    fig.canvas.draw_idle()

def on_dist_change(label):
    state["dist"] = label
    rebuild_sliders(label)

radio.on_clicked(on_dist_change)

# ── Bootstrap ────────────────────────────────────────────────────────────────
rebuild_sliders("Normal")
update_plot()

plt.show()
