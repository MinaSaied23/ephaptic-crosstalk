import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

plt.rcParams.update({'font.size': 9.5, 'font.family': 'serif'})

fig, ax = plt.subplots(figsize=(7.16, 3.9))
ax.set_xlim(0, 10.2)
ax.set_ylim(0, 6.4)
ax.axis('off')

# --- Extracellular cleft envelope ---
cleft_y0, cleft_h = 2.55, 2.0
cleft = Rectangle((0.55, cleft_y0), 8.75, cleft_h, facecolor='#eaf1fb', edgecolor='#4472a8', linewidth=1.3, zorder=0)
ax.add_patch(cleft)
# (cleft label omitted here; identified in figure caption instead, to avoid
# crowding the ephaptic-feedback label at the same x-position)

# --- A-beta fiber (myelinated, top row, inside cleft near top) ---
y_ab = cleft_y0 + cleft_h - 0.45
node_xs = [1.0, 3.0, 5.0, 7.0, 8.85]
seg_width = 1.55
for i, nx in enumerate(node_xs):
    if i < len(node_xs) - 1:
        ax.add_patch(Rectangle((nx + 0.09, y_ab - 0.14), seg_width - 0.18, 0.28, facecolor='#c9d6e8', edgecolor='#4472a8', linewidth=0.8, zorder=2))
    ax.add_patch(Rectangle((nx - 0.09, y_ab - 0.19), 0.18, 0.38, facecolor='#d94f4f', edgecolor='#7a1f1f', linewidth=0.8, zorder=3))
ax.text(0.15, y_ab, 'A\u03b2', fontsize=12, fontweight='bold', ha='center', va='center', color='#7a1f1f')

# stimulus arrow (well above the cleft box, clearly separated)
ax.annotate('', xy=(1.0, cleft_y0 + cleft_h + 0.08), xytext=(1.0, cleft_y0 + cleft_h + 0.75),
            arrowprops=dict(arrowstyle='-|>', color='#d94f4f', lw=1.6))
ax.text(1.0, cleft_y0 + cleft_h + 0.95, 'stimulus', fontsize=8.5, ha='center', color='#7a1f1f')

# --- C-fiber (unmyelinated, bottom row, inside cleft near bottom) ---
y_c = cleft_y0 + 0.45
ax.add_patch(Rectangle((0.75, y_c - 0.12), 8.15, 0.24, facecolor='#f4c98b', edgecolor='#8a5a1e', linewidth=0.8, zorder=2))
ax.text(0.15, y_c, 'C', fontsize=12, fontweight='bold', ha='center', va='center', color='#8a5a1e')

# --- ephaptic coupling arrows (vertical, both directions, well inside the box) ---
for cx in [2.3, 4.3, 6.3, 8.15]:
    ax.annotate('', xy=(cx, y_c + 0.20), xytext=(cx, y_ab - 0.24),
                arrowprops=dict(arrowstyle='<->', color='#2c5178', lw=1.1, linestyle=(0, (3, 2))))

# --- Poisson solver box (well below the cleft, generous gap) ---
solver_y0, solver_h = 0.25, 1.15

# arrow connecting solver box to the bottom of the cleft, offset to the right
# side so it does not cross through the C-fiber caption text below
arrow_x = 8.6
ax.annotate('', xy=(arrow_x, cleft_y0 - 0.05), xytext=(arrow_x, solver_y0 + solver_h + 0.05),
            arrowprops=dict(arrowstyle='<->', color='#8a6d1e', lw=1.3))
ax.text(arrow_x + 0.18, (cleft_y0 + solver_y0 + solver_h) / 2, 'feeds\nback into\nboth fibers', fontsize=7, color='#5c4813', ha='left', va='center')

# widen the solver box slightly and keep it centered under the cleft, but left
# of the connector arrow so nothing collides
solver = Rectangle((1.7, solver_y0), 6.2, solver_h, facecolor='#fff7e0', edgecolor='#8a6d1e', linewidth=1.2, zorder=4)
ax.add_patch(solver)
ax.text(4.8, solver_y0 + solver_h - 0.32, r'$\partial^2 u_e/\partial z^2 - \kappa u_e = r_e\, I_{total}(z)$', fontsize=9.5, ha='center', va='center')
ax.text(4.8, solver_y0 + solver_h - 0.66, 'shared extracellular potential $u_e(z,t)$', fontsize=8, ha='center', va='center', color='#5c4813')
ax.text(4.8, solver_y0 + solver_h - 0.94, 'solved every time step (Sec. II-C)', fontsize=7.5, ha='center', va='center', color='#5c4813', style='italic')

# --- captions below each element, placed OUTSIDE any box with clear vertical gaps ---
ax.text(5.05, cleft_y0 + cleft_h + 0.28, 'myelinated A\u03b2 fiber (CRRSS kinetics): active nodes of Ranvier (red), passive internodes (blue)',
        fontsize=7.8, ha='center', color='#333333')
ax.text(5.05, cleft_y0 - 0.30, 'unmyelinated C-fiber: continuously active membrane\n(Phase 1: classical HH; Phase 2: Nav1.8/Nav1.9)',
        fontsize=7.8, ha='center', va='top', color='#333333')
ax.text(9.55, y_ab, 'ephaptic\nfeedback\n(u$_e$)', fontsize=8, color='#2c5178', ha='left', va='center')

plt.tight_layout()
plt.savefig('./fig0_v2_fixed_layout.pdf', dpi=300, bbox_inches='tight')
print("Fig0 v2 saved")
