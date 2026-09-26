import numpy as np
import matplotlib.pyplot as plt
import os
import sys
base_dir = os.path.dirname(__file__)
sys.path.append(os.path.join(base_dir, 'phase1_classical_hh'))
from ephaptic_model import crrss_rates

def plot_gating():
    v = np.linspace(-100e-3, 50e-3, 500)
    alpha_m, beta_m, alpha_h, beta_h = crrss_rates(v)
    
    m_inf = alpha_m / (alpha_m + beta_m)
    h_inf = alpha_h / (alpha_h + beta_h)
    
    tau_m = 1.0 / (alpha_m + beta_m) * 1e3 # in ms
    tau_h = 1.0 / (alpha_h + beta_h) * 1e3 # in ms
    
    v_mV = v * 1000
    
    plt.figure(figsize=(10, 4))
    
    plt.subplot(1, 2, 1)
    plt.plot(v_mV, m_inf, label=r'$m_\infty$', lw=2)
    plt.plot(v_mV, h_inf, label=r'$h_\infty$', lw=2)
    plt.xlabel('Membrane Potential (mV)')
    plt.ylabel('Steady State')
    plt.title('CRRSS Gating Steady States')
    plt.legend()
    plt.grid(True)
    
    plt.subplot(1, 2, 2)
    plt.plot(v_mV, tau_m, label=r'$\tau_m$', lw=2)
    plt.plot(v_mV, tau_h, label=r'$\tau_h$', lw=2)
    plt.xlabel('Membrane Potential (mV)')
    plt.ylabel('Time Constant (ms)')
    plt.title('CRRSS Time Constants')
    plt.legend()
    plt.grid(True)
    
    plt.tight_layout()
    out_dir = os.path.join(base_dir, '..', 'results', 'figures')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'crrss_gating_plots.png')
    plt.savefig(out_path, dpi=300)
    print(f"Saved {out_path}")

if __name__ == "__main__":
    plot_gating()
