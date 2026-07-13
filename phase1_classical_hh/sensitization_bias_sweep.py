import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from coupled_model import run_coupled

plt.rcParams.update({'font.size': 8, 'font.family': 'serif'})

biases = [0,0.2,0.4,0.5,0.7,1.0,1.3,1.6,2.0,3.0,5.0,7.0]
quasi_steady = []
spontaneous = []
for b in biases:
    res_short = run_coupled(w_cleft=1e-6, T=1e-3, stim_amp=0.0, sens_bias=b)
    quasi_steady.append(res_short['v2_mid'][-1]*1e3)
    res_long = run_coupled(w_cleft=1e-6, T=0.08, stim_amp=0.0, sens_bias=b, record_full=True)
    spontaneous.append(bool((res_long['v2'][:,200:800] > 0).any()))
    print(b, quasi_steady[-1], spontaneous[-1])

import pickle
with open('./fig3_data.pkl','wb') as f:
    pickle.dump((biases, quasi_steady, spontaneous), f)
