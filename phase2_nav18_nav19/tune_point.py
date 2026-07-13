import numpy as np
from nav_kinetics import nav_c_fiber_rates

E_Na = 50e-3
E_K = -77e-3
E_leak = -55e-3   # nociceptor resting potential is more depolarized than -65mV typically (~-55 to -60mV)
Cm = 1.0e-2       # F/m^2

# classical K+ (delayed rectifier), reused from HH
def hh_k_rates(v):
    vmV = v * 1e3
    def safe_div(num, denom):
        denom = np.where(np.abs(denom) < 1e-9, 1e-9, denom)
        return num / denom
    alpha_n = safe_div(0.01 * (vmV + 55.0), (1.0 - np.exp(-(vmV + 55.0) / 10.0))) * 1e3
    beta_n = 0.125 * np.exp(-(vmV + 65.0) / 80.0) * 1e3
    return alpha_n, beta_n

def run_point(g8, g9, g_k, g_leak, T=30e-3, dt=5e-6, stim_amp=0.0, stim_start=5e-3, stim_dur=1e-3, v0=None):
    v = v0 if v0 is not None else E_leak
    m8, h8, m9, n = 0.02, 0.9, 0.05, 0.3
    nsteps = int(T / dt)
    v_rec = np.zeros(nsteps)
    for step in range(nsteps):
        m8_inf, tau_m8, h8_inf, tau_h8, m9_inf, tau_m9 = nav_c_fiber_rates(np.array([v]))
        m8 += dt * (m8_inf[0] - m8) / tau_m8
        h8 += dt * (h8_inf[0] - h8) / tau_h8
        m9 += dt * (m9_inf[0] - m9) / tau_m9
        an, bn = hh_k_rates(np.array([v]))
        n += dt * (an[0] * (1 - n) - bn[0] * n)

        I_na8 = g8 * m8**3 * h8 * (v - E_Na)
        I_na9 = g9 * m9 * (v - E_Na)
        I_k = g_k * n**4 * (v - E_K)
        I_leak = g_leak * (v - E_leak)
        I_stim = stim_amp if (stim_start <= step*dt < stim_start+stim_dur) else 0.0
        I_ion = I_na8 + I_na9 + I_k + I_leak
        v += dt * (I_stim - I_ion) / Cm
        v_rec[step] = v
    return v_rec

if __name__ == "__main__":
    # Step 1: check resting stability with no stimulus, various g8/g9
    print("--- resting stability scan (no stimulus) ---")
    for g8 in [400, 600, 800]:
        for g9 in [1, 2, 4]:
            v_rec = run_point(g8=g8, g9=g9, g_k=360, g_leak=3.0, T=50e-3, stim_amp=0.0)
            print(f"g8={g8} g9={g9} -> final v={v_rec[-1]*1e3:.2f}mV max={v_rec.max()*1e3:.2f}mV spiked={v_rec.max()>0}")
