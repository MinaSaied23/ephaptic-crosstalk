import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

plt.rcParams.update({'font.size': 13, 'font.family': 'serif'})

fig, ax = plt.subplots(figsize=(7.0, 3.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 5)
ax.axis('off')

# --- Shared extracellular cleft (outer box) ---
cleft = Rectangle((1.3, 1.0), 8.0, 3.0, facecolor='#eaf1fb', edgecolor='#4472a8', linewidth=1.5, zorder=0)
ax.add_patch(cleft)

# --- Abeta fiber bar (top) ---
y_ab = 3.35
ab_bar = Rectangle((1.7, y_ab - 0.22), 7.2, 0.44, facecolor='#d94f4f', edgecolor='#7a1f1f', linewidth=1.2, zorder=2)
ax.add_patch(ab_bar)

# --- C fiber bar (bottom) ---
y_c = 1.65
c_bar = Rectangle((1.7, y_c - 0.22), 7.2, 0.44, facecolor='#f4c98b', edgecolor='#8a5a1e', linewidth=1.2, zorder=2)
ax.add_patch(c_bar)

# --- coupling arrows (just two, widely spaced) ---
for cx in [4.0, 6.6]:
    ax.annotate('', xy=(cx, y_c + 0.24), xytext=(cx, y_ab - 0.24),
                arrowprops=dict(arrowstyle='<->', color='#2c5178', lw=1.6))

# --- labels: only 4 short text elements total, all far apart ---
t1 = ax.text(0.15, y_ab, 'A\u03b2', fontsize=17, fontweight='bold', ha='left', va='center', color='#7a1f1f')
t2 = ax.text(0.15, y_c, 'C', fontsize=17, fontweight='bold', ha='left', va='center', color='#8a5a1e')
t3 = ax.text(5.3, 4.55, 'shared extracellular cleft', fontsize=12.5, ha='center', va='center', color='#2c5178')
t4 = ax.text(5.3, 0.45, 'ephaptic coupling via shared field  $u_e(z,t)$', fontsize=12, ha='center', va='center', color='#2c5178')

plt.tight_layout()
fig.canvas.draw()
renderer = fig.canvas.get_renderer()

boxes = {}
for name, t in [('t1',t1),('t2',t2),('t3',t3),('t4',t4)]:
    bbox = t.get_window_extent(renderer=renderer).transformed(ax.transData.inverted())
    boxes[name] = (bbox.x0, bbox.y0, bbox.x1, bbox.y1)
    print(f"{name}: x=({bbox.x0:.2f},{bbox.x1:.2f}) y=({bbox.y0:.2f},{bbox.y1:.2f})")

boxes['cleft'] = (1.3, 1.0, 9.3, 4.0)
boxes['ab_bar'] = (1.7, y_ab-0.22, 8.9, y_ab+0.22)
boxes['c_bar'] = (1.7, y_c-0.22, 8.9, y_c+0.22)
for name in ['cleft','ab_bar','c_bar']:
    b = boxes[name]
    print(f"{name}: x=({b[0]:.2f},{b[2]:.2f}) y=({b[1]:.2f},{b[3]:.2f})")

def overlaps(b1, b2):
    return not (b1[2] < b2[0] or b2[2] < b1[0] or b1[3] < b2[1] or b2[3] < b1[1])

print("\n--- OVERLAP CHECK (ignoring intended containment: t1/t2 vs bars, bars vs cleft) ---")
ignore_pairs = {frozenset(['t1','ab_bar']), frozenset(['t2','c_bar']),
                 frozenset(['ab_bar','cleft']), frozenset(['c_bar','cleft'])}
names = list(boxes.keys())
found = False
for i in range(len(names)):
    for j in range(i+1, len(names)):
        n1, n2 = names[i], names[j]
        if frozenset([n1,n2]) in ignore_pairs:
            continue
        if overlaps(boxes[n1], boxes[n2]):
            print(f"OVERLAP: {n1} <-> {n2}")
            found = True
if not found:
    print("No unintended overlaps.")

plt.savefig('./fig0_simple_raw.png', dpi=300, bbox_inches='tight')
