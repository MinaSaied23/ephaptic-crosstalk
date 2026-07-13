import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyArrowPatch, Rectangle, Circle, Ellipse
import numpy as np

plt.rcParams.update({'font.size': 9, 'font.family': 'serif'})

fig, ax = plt.subplots(figsize=(7.16, 3.4))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.6)
ax.axis('off')

# --- Extracellular cleft envelope ---
cleft = Rectangle((0.5, 1.6), 9.0, 2.4, facecolor='#eaf1fb', edgecolor='#4472a8', linewidth=1.2, zorder=0)
ax.add_patch(cleft)
ax.text(9.55, 3.75, 'shared\nextracellular\ncleft', fontsize=7.5, color='#2c5178', ha='left', va='center')

# --- A-beta fiber (myelinated, top) ---
y_ab = 3.55
ax.plot([0.8, 9.2], [y_ab, y_ab], color='#8a8a8a', linewidth=0, zorder=1)  # baseline (invisible)
node_xs = [1.1, 3.1, 5.1, 7.1, 9.1]
seg_width = 1.35
for i, nx in enumerate(node_xs):
    # myelin internode segments (skip after last node)
    if i < len(node_xs)-1:
        ax.add_patch(Rectangle((nx+0.08, y_ab-0.16), seg_width-0.16, 0.32, facecolor='#c9d6e8', edgecolor='#4472a8', linewidth=0.8, zorder=2))
    # node of Ranvier (bare, active)
    ax.add_patch(Rectangle((nx-0.08, y_ab-0.22), 0.16, 0.44, facecolor='#d94f4f', edgecolor='#7a1f1f', linewidth=0.8, zorder=3))
ax.text(0.55, y_ab, 'A\u03b2', fontsize=11, fontweight='bold', ha='center', va='center', color='#7a1f1f')
ax.text(5.05, y_ab+0.65, 'myelinated A\u03b2 fiber (CRRSS kinetics): active nodes of Ranvier (red), passive internodes (blue)', fontsize=7, ha='center', color='#333333')

# stimulus arrow
ax.annotate('', xy=(1.1, y_ab+0.55), xytext=(1.1, y_ab+1.05),
            arrowprops=dict(arrowstyle='-|>', color='#d94f4f', lw=1.4))
ax.text(1.1, y_ab+1.15, 'stimulus', fontsize=7, ha='center', color='#7a1f1f')

# --- C-fiber (unmyelinated, bottom) ---
y_c = 2.05
ax.add_patch(Rectangle((0.8, y_c-0.13), 8.4, 0.26, facecolor='#f4c98b', edgecolor='#8a5a1e', linewidth=0.8, zorder=2))
ax.text(0.55, y_c, 'C', fontsize=11, fontweight='bold', ha='center', va='center', color='#8a5a1e')
ax.text(5.05, y_c-0.55, 'unmyelinated C-fiber: continuously active membrane (Phase 1: classical HH; Phase 2: Nav1.8/Nav1.9)', fontsize=7, ha='center', color='#333333')

# --- ephaptic coupling arrows (vertical, both directions) ---
for cx in [2.5, 4.5, 6.5, 8.5]:
    ax.annotate('', xy=(cx, y_c+0.16), xytext=(cx, y_ab-0.28),
                arrowprops=dict(arrowstyle='<->', color='#2c5178', lw=1.0, linestyle=(0,(3,2))))
ax.text(9.55, 2.8, 'ephaptic\nfeedback\n(u$_e$)', fontsize=7.5, color='#2c5178', ha='left', va='center')

# --- Poisson solver box ---
solver = Rectangle((3.3, 0.15), 3.4, 1.05, facecolor='#fff7e0', edgecolor='#8a6d1e', linewidth=1.1, zorder=4)
ax.add_patch(solver)
ax.text(5.0, 0.9, r'$\partial^2 u_e/\partial z^2 - \kappa u_e = r_e\, I_{total}(z)$', fontsize=8.5, ha='center', va='center')
ax.text(5.0, 0.55, 'shared extracellular potential', fontsize=7, ha='center', va='center', color='#5c4813')
ax.text(5.0, 0.30, '(solved every time step; Sec. II-C)', fontsize=6.5, ha='center', va='center', color='#5c4813', style='italic')

ax.annotate('', xy=(5.0, 1.2), xytext=(5.0, 1.75),
            arrowprops=dict(arrowstyle='<->', color='#8a6d1e', lw=1.0))

plt.tight_layout()
plt.savefig('./fig0_v1_node_detail.pdf', dpi=300, bbox_inches='tight')
print("Fig0 schematic saved")
