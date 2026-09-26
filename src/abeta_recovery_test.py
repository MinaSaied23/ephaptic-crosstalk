import numpy as np
import matplotlib.pyplot as plt
import os
import sys
base_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(base_dir, 'phase1_classical_hh'))
from coupled_model import run_coupled
from ephaptic_model import dt

def abeta_recovery():
    # Capture full waveform with dual pulse 3ms apart (333.33 Hz)
    res = run_coupled(w_cleft=1e-6, T=10e-3, stim_amp=100e-9, stim_dur=0.2e-3,
                      sens_bias=0.0, stim_freq=333.33, n_pulses=2, record_full=True)
    
    t = np.arange(len(res['v1'])) * dt
    v1_mid = res['v1'][:, 500] * 1000 # mid node, in mV
    
    p1 = v1_mid[:int(2.5e-3/dt)].max()
    p2 = v1_mid[int(2.5e-3/dt):].max()
    v_inter = v1_mid[int(2.8e-3/dt)]
    v_final = v1_mid[-1]
    
    plt.figure(figsize=(7, 4.5))
    plt.plot(t * 1000, v1_mid, color='#1f77b4', lw=2.0, label='Aβ Membrane Potential (Node 500)')
    plt.axhline(-80.0, color='gray', linestyle='--', alpha=0.7, label='Resting Potential (-80 mV)')
    
    # Annotate peaks and recovery
    t1_pk = t[np.argmax(v1_mid[:int(2.5e-3/dt)])] * 1000
    t2_pk = t[int(2.5e-3/dt) + np.argmax(v1_mid[int(2.5e-3/dt):])] * 1000
    plt.scatter([t1_pk, t2_pk], [p1, p2], color='red', zorder=5)
    
    plt.annotate(f'Pulse 1 Peak: {p1:.1f} mV', 
                 xy=(t1_pk, p1), xytext=(0.3, 28),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='black'),
                 fontsize=10)
    plt.annotate(f'Pulse 2 Peak: {p2:.1f} mV', 
                 xy=(t2_pk, p2), xytext=(3.5, 8),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='black'),
                 fontsize=10)
    plt.annotate(f'Inter-pulse recovery: {v_inter:.2f} mV', 
                 xy=(2.8, v_inter), xytext=(1.2, -55),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='black'),
                 fontsize=10)
    plt.annotate(f'Final potential: {v_final:.2f} mV\n(100% Repolarization)', 
                 xy=(9.8, v_final), xytext=(6.2, -55),
                 arrowprops=dict(arrowstyle='->', lw=1.2, color='black'),
                 fontsize=10)

    plt.xlabel('Time (ms)', fontsize=11)
    plt.ylabel('Membrane Potential (mV)', fontsize=11)
    plt.title('Aβ Double-Pulse Recovery Test (CRRSS Kinetics, 3 ms Interval)', fontsize=12, fontweight='bold')
    plt.ylim(-90, 50)
    plt.grid(True, linestyle=':', alpha=0.6)
    plt.legend(loc='upper right', framealpha=0.9, fontsize=10)
    plt.tight_layout()
    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'abeta_recovery_test.png')
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")
    print(f"  Pulse 1 Peak: {p1:.2f} mV")
    print(f"  Potential at 2.8 ms (inter-pulse): {v_inter:.2f} mV")
    print(f"  Pulse 2 Peak: {p2:.2f} mV")
    print(f"  Final Potential at 10 ms: {v_final:.2f} mV")

if __name__ == "__main__":
    abeta_recovery()
