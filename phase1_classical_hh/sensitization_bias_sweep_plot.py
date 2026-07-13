import pickle
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})

with open('./fig3_data.pkl','rb') as f:
    biases, quasi_steady, spontaneous = pickle.load(f)

biases = np.array(biases)
quasi_steady = np.array(quasi_steady)
spontaneous = np.array(spontaneous)

fig, ax = plt.subplots(figsize=(3.4, 2.6))
stable_mask = ~spontaneous
ax.plot(biases[stable_mask], quasi_steady[stable_mask], 'o', color='#2471a3', ms=5,
        label='No threshold crossing (80 ms)')
ax.plot(biases[spontaneous], quasi_steady[spontaneous], 'x', color='#c0392b', ms=7, mew=1.6,
        label='Spontaneous threshold crossing')
ax.set_xlabel('Sensitizing bias current density (A/m$^2$)')
ax.set_ylabel('Quasi-steady $V_m$ at 1 ms (mV)')
ax.set_title('C-fiber under tonic depolarizing bias alone', fontsize=7.5)
ax.legend(fontsize=6, loc='lower right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.savefig('./fig3_sensitization.pdf', dpi=300, bbox_inches='tight')
print('saved')
