import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coupled_model import run_coupled

plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})

widths = [20e-9, 90e-9, 148.9e-9, 246e-9, 406e-9, 1000e-9]
first_cross = []
for w in widths:
    res = run_coupled(w_cleft=w, T=8e-3, stim_amp=100e-9, stim_dur=0.2e-3, sens_bias=0.0, record_full=True)
    crossed = (res['v2'][:,200:800] > 0)
    if crossed.any():
        t_idx = np.argmax(crossed.any(axis=1))
        first_cross.append(t_idx*5e-6*1e3)
    else:
        first_cross.append(np.nan)
    print(w, first_cross[-1])

fig, ax = plt.subplots(figsize=(3.4, 2.6))
ax.plot(np.array(widths)*1e9, first_cross, 's--', color='#8e44ad', ms=5, lw=1.2)
ax.set_xscale('log')
ax.set_xlabel('Cleft width $w_{cleft}$ (nm)')
ax.set_ylabel('Time to spurious threshold\ncrossing (ms)')
ax.set_title('Strong coupling ($\\kappa=3\\times10^7$): non-physical,\ngeometry-independent delayed onset', fontsize=7)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('./fig4_artifact.pdf', dpi=300, bbox_inches='tight')
print('saved')
