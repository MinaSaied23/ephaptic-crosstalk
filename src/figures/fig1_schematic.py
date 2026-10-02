"""Fig. 1 - Model geometry and equivalent circuit."""
import numpy as np
from matplotlib.patches import Rectangle, FancyBboxPatch, FancyArrowPatch
from style import plt, save, COL, panel

fig = plt.figure(figsize=(7.0, 4.6))
ax = fig.add_axes([0.02, 0.50, 0.96, 0.48])
ax.set_xlim(-0.6, 10.6); ax.set_ylim(-1.5, 2.6); ax.axis("off")
panel(ax, "a")

# lesion compartment
ax.add_patch(Rectangle((2.5, -0.55), 5.0, 2.25, fc="#f3e6f7", ec=COL["ue"], lw=1.0, ls="--", zorder=0))
ax.text(5.0, 1.82, "focal lesion: shared extracellular compartment (z = 2.5–7.5 mm)\n"
        r"cross-section $A_e$ shared by $n$ A$\beta$ fibers, leak $G_e=\kappa/r_e$ to bulk",
        ha="center", va="bottom", fontsize=7, color=COL["ue"])
ax.text(1.25, 0.40, r"grounded bulk ($u_e=0$)", ha="center", va="center", fontsize=6.5, color=COL["grey"])
ax.text(8.75, 0.40, r"grounded bulk ($u_e=0$)", ha="center", va="center", fontsize=6.5, color=COL["grey"])

# Abeta fiber with nodes
y1 = 0.9
ax.add_patch(FancyBboxPatch((0, y1 - 0.22), 10, 0.44, boxstyle="round,pad=0.0,rounding_size=0.2",
                            fc="#e8f3ea", ec=COL["abeta"], lw=1.0))
for k in range(10):
    ax.add_patch(Rectangle((k - 0.03, y1 - 0.25), 0.06, 0.50, fc=COL["abeta"], ec="none"))
ax.text(10.15, y1, r"A$\beta$ ($\times n$)" "\nCRRSS nodes, 1 mm", va="center", fontsize=7, color=COL["abeta"])
# C fiber
y2 = 0.0
ax.add_patch(FancyBboxPatch((0, y2 - 0.08), 10, 0.16, boxstyle="round,pad=0.0,rounding_size=0.08",
                            fc="#fbe9e7", ec=COL["NavC"], lw=1.0))
ax.text(10.15, y2, "C-fiber (1 µm)\nHH or Nav1.8/1.9", va="center", fontsize=7, color=COL["NavC"])
# stimulus electrode
ax.annotate("", xy=(0.0, y1 + 0.26), xytext=(0.0, y1 + 0.85),
            arrowprops=dict(arrowstyle="-|>", color="k", lw=1.0))
ax.text(0.05, y1 + 0.9, r"$I_{stim}$ = 2$\times$ threshold" "\n0.2 ms at node 0", fontsize=7, va="bottom")
# propagation arrow
ax.add_patch(FancyArrowPatch((0.6, -1.05), (2.3, -1.05), arrowstyle="-|>", mutation_scale=8, color=COL["abeta"]))
ax.text(1.45, -1.35, r"A$\beta$ AP enters lesion", ha="center", fontsize=7, color=COL["abeta"])
for x in (0, 2.5, 5, 7.5, 10):
    ax.text(x, -0.75, f"{x:g}", ha="center", fontsize=6, color=COL["grey"])
ax.text(5.0, -1.02, "z (mm)", ha="center", fontsize=6, color=COL["grey"])

# --- equivalent circuit (one compartment) ---
ax2 = fig.add_axes([0.05, 0.02, 0.55, 0.44])
ax2.set_xlim(0, 10); ax2.set_ylim(0, 6); ax2.axis("off")
panel(ax2, "b")


def resistor(a, x0, y0, x1, y1, label, color="k"):
    xs = np.linspace(0, 1, 13)
    zig = np.array([0, 0, .5, -.5, .5, -.5, .5, -.5, .5, -.5, 0, 0, 0]) * 0.18
    dx, dy = x1 - x0, y1 - y0
    L = np.hypot(dx, dy); ux, uy = dx / L, dy / L
    px, py = -uy, ux
    X = x0 + xs * dx + zig * px
    Y = y0 + xs * dy + zig * py
    a.plot(X, Y, color=color, lw=1)
    a.text((x0 + x1) / 2 + 0.35 * px, (y0 + y1) / 2 + 0.35 * py, label, fontsize=7, ha="center", va="center", color=color)


def membrane(a, x, y0, y1, label, color):
    ym = (y0 + y1) / 2
    a.plot([x, x], [y0, ym - 0.35], color=color, lw=1); a.plot([x, x], [ym + 0.35, y1], color=color, lw=1)
    a.add_patch(Rectangle((x - 0.35, ym - 0.35), 0.7, 0.7, fc="white", ec=color, lw=1))
    a.text(x, ym, label, fontsize=6, ha="center", va="center", color=color)


# rails: u1 (top), ue (middle), u2 (bottom)
resistor(ax2, 1.0, 5.2, 4.0, 5.2, r"$r_{i,1}/n$", COL["abeta"]); resistor(ax2, 4.0, 5.2, 7.0, 5.2, r"$r_{i,1}/n$", COL["abeta"])
resistor(ax2, 1.0, 3.0, 4.0, 3.0, r"$r_e$", COL["ue"]); resistor(ax2, 4.0, 3.0, 7.0, 3.0, r"$r_e$", COL["ue"])
resistor(ax2, 1.0, 0.8, 4.0, 0.8, r"$r_{i,2}$", COL["NavC"]); resistor(ax2, 4.0, 0.8, 7.0, 0.8, r"$r_{i,2}$", COL["NavC"])
membrane(ax2, 4.0, 3.0, 5.2, r"$n\,i_{m,1}$", COL["abeta"])
membrane(ax2, 4.0, 0.8, 3.0, r"$i_{m,2}$", COL["NavC"])
resistor(ax2, 4.0, 3.0, 5.6, 1.9, "", COL["ue"])
ax2.text(6.15, 1.75, r"$G_e$", fontsize=7, color=COL["ue"])
ax2.plot([5.6, 5.9], [1.9, 1.9], color="k", lw=1); ax2.plot([5.65, 5.85], [1.78, 1.78], color="k", lw=1)
ax2.text(0.6, 5.2, r"$u_{1}$", fontsize=8, va="center"); ax2.text(0.6, 3.0, r"$u_e$", fontsize=8, va="center")
ax2.text(0.6, 0.8, r"$u_{2}$", fontsize=8, va="center")

ax3 = fig.add_axes([0.62, 0.02, 0.37, 0.44]); ax3.axis("off")
ax3.text(0.0, 0.95, "Per unit length, with $v_k = u_k - u_e$:", fontsize=7, va="top", transform=ax3.transAxes)
eqs = [r"$\pi d_k\,(C_{m,k}\dot v_k + I_{ion,k}) = g_k\,\partial_z^2(v_k+u_e)$",
       r"$\frac{1}{r_e}\partial_z^2 u_e - G_e u_e + n\,i_{m,1} + i_{m,2} = 0$",
       r"$g_k = 1/r_{i,k} = \pi d_k^2/(4\rho_i)$,   $\kappa = r_e G_e$",
       r"$[v_1, v_2, u_e]$ advanced together (backward Euler)"]
for i, e in enumerate(eqs):
    ax3.text(0.0, 0.78 - i * 0.2, e, fontsize=7.5, va="top", transform=ax3.transAxes)
save(fig, "fig1_model.png")
