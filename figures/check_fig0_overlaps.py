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

cleft_y0, cleft_h = 2.55, 2.0
cleft = Rectangle((0.55, cleft_y0), 8.75, cleft_h, facecolor='#eaf1fb', edgecolor='#4472a8', linewidth=1.3, zorder=0)
ax.add_patch(cleft)
# cleft label removed

y_ab = cleft_y0 + cleft_h - 0.45
node_xs = [1.0, 3.0, 5.0, 7.0, 8.85]
seg_width = 1.55
node_patches = []
for i, nx in enumerate(node_xs):
    if i < len(node_xs) - 1:
        p = Rectangle((nx + 0.09, y_ab - 0.14), seg_width - 0.18, 0.28, facecolor='#c9d6e8', edgecolor='#4472a8', linewidth=0.8, zorder=2)
        ax.add_patch(p); node_patches.append(('internode', p))
    p2 = Rectangle((nx - 0.09, y_ab - 0.19), 0.18, 0.38, facecolor='#d94f4f', edgecolor='#7a1f1f', linewidth=0.8, zorder=3)
    ax.add_patch(p2); node_patches.append(('node', p2))
t_ab_label = ax.text(0.15, y_ab, 'A\u03b2', fontsize=12, fontweight='bold', ha='center', va='center', color='#7a1f1f')

t_stim_arrow_target = (1.0, cleft_y0 + cleft_h + 0.08)
ax.annotate('', xy=(1.0, cleft_y0 + cleft_h + 0.08), xytext=(1.0, cleft_y0 + cleft_h + 0.75),
            arrowprops=dict(arrowstyle='-|>', color='#d94f4f', lw=1.6))
t_stim_label = ax.text(1.0, cleft_y0 + cleft_h + 0.95, 'stimulus', fontsize=8.5, ha='center', color='#7a1f1f')

y_c = cleft_y0 + 0.45
cfiber_patch = Rectangle((0.75, y_c - 0.12), 8.15, 0.24, facecolor='#f4c98b', edgecolor='#8a5a1e', linewidth=0.8, zorder=2)
ax.add_patch(cfiber_patch)
t_c_label = ax.text(0.15, y_c, 'C', fontsize=12, fontweight='bold', ha='center', va='center', color='#8a5a1e')

for cx in [2.3, 4.3, 6.3, 8.15]:
    ax.annotate('', xy=(cx, y_c + 0.20), xytext=(cx, y_ab - 0.24),
                arrowprops=dict(arrowstyle='<->', color='#2c5178', lw=1.1, linestyle=(0, (3, 2))))

solver_y0, solver_h = 0.25, 1.15
arrow_x = 8.6
ax.annotate('', xy=(arrow_x, cleft_y0 - 0.05), xytext=(arrow_x, solver_y0 + solver_h + 0.05),
            arrowprops=dict(arrowstyle='<->', color='#8a6d1e', lw=1.3))
t_feedback_label = ax.text(arrow_x + 0.18, (cleft_y0 + solver_y0 + solver_h) / 2, 'feeds\nback into\nboth fibers', fontsize=7, color='#5c4813', ha='left', va='center')

solver = Rectangle((1.7, solver_y0), 6.2, solver_h, facecolor='#fff7e0', edgecolor='#8a6d1e', linewidth=1.2, zorder=4)
ax.add_patch(solver)
t_eq = ax.text(4.8, solver_y0 + solver_h - 0.32, r'$\partial^2 u_e/\partial z^2 - \kappa u_e = r_e\, I_{total}(z)$', fontsize=9.5, ha='center', va='center')
t_eq2 = ax.text(4.8, solver_y0 + solver_h - 0.66, 'shared extracellular potential $u_e(z,t)$', fontsize=8, ha='center', va='center', color='#5c4813')
t_eq3 = ax.text(4.8, solver_y0 + solver_h - 0.94, 'solved every time step (Sec. II-C)', fontsize=7.5, ha='center', va='center', color='#5c4813', style='italic')

t_ab_caption = ax.text(5.05, cleft_y0 + cleft_h + 0.28, 'myelinated A\u03b2 fiber (CRRSS kinetics): active nodes of Ranvier (red), passive internodes (blue)',
        fontsize=7.8, ha='center', color='#333333')
t_c_caption = ax.text(5.05, cleft_y0 - 0.30, 'unmyelinated C-fiber: continuously active membrane\n(Phase 1: classical HH; Phase 2: Nav1.8/Nav1.9)',
        fontsize=7.8, ha='center', va='top', color='#333333')
t_side_label = ax.text(9.55, y_ab, 'ephaptic\nfeedback\n(u$_e$)', fontsize=8, color='#2c5178', ha='left', va='center')

plt.tight_layout()
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

# collect all text bounding boxes in data coordinates
named_texts = {
    'ab_label': t_ab_label, 'stim_label': t_stim_label,
    'c_label': t_c_label, 'feedback_label': t_feedback_label, 'eq': t_eq, 'eq2': t_eq2, 'eq3': t_eq3,
    'ab_caption': t_ab_caption, 'c_caption': t_c_caption, 'side_label': t_side_label,
}
boxes = {}
for name, t in named_texts.items():
    bbox = t.get_window_extent(renderer=renderer)
    bbox_data = bbox.transformed(ax.transData.inverted())
    boxes[name] = (bbox_data.x0, bbox_data.y0, bbox_data.x1, bbox_data.y1)
    print(f"{name}: x=({bbox_data.x0:.2f},{bbox_data.x1:.2f}) y=({bbox_data.y0:.2f},{bbox_data.y1:.2f})")

# also patch boxes
# node/internode patches, individually
for idx, (kind, p) in enumerate(node_patches):
    bb = p.get_bbox()
    boxes[f'{kind}_{idx}'] = (bb.x0, bb.y0, bb.x1, bb.y1)

patch_boxes = {
    'cleft_box': (0.55, cleft_y0, 0.55+8.75, cleft_y0+cleft_h),
    'solver_box': (1.7, solver_y0, 1.7+6.2, solver_y0+solver_h),
    'cfiber_patch': (0.75, y_c-0.12, 0.75+8.15, y_c+0.12),
}
for name, b in patch_boxes.items():
    boxes[name] = b
    print(f"{name}: x=({b[0]:.2f},{b[2]:.2f}) y=({b[1]:.2f},{b[3]:.2f})")

def overlaps(b1, b2):
    return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])

print("\n--- OVERLAP CHECK ---")
names = list(boxes.keys())
found_any = False
for i in range(len(names)):
    for j in range(i+1, len(names)):
        n1, n2 = names[i], names[j]
        if overlaps(boxes[n1], boxes[n2]):
            print(f"OVERLAP: {n1} <-> {n2}")
            found_any = True
if not found_any:
    print("No overlaps detected among checked elements.")

plt.savefig('./fig0_check.pdf', dpi=300, bbox_inches='tight')
