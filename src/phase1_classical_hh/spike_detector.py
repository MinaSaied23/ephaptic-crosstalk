"""
Unified spike-detection and fixed-node discretization module for Phase 1.
Ensures physical node of Ranvier dimensions (l_node = 1.0 um) are preserved
across arbitrary computational spatial grids (dz), and provides standardized
spatiotemporal event classification across all Phase 1 experiments.
"""

import numpy as np

def build_fixed_node_geometry(L=10e-3, dz=10e-6, internode_spacing=1e-3, l_node=1.0e-6):
    """
    Build spatial grid and nodal mask ensuring physical node length
    l_node remains exactly 1.0 um regardless of computational cell size dz.
    Returns:
        N: number of spatial compartments
        z: spatial coordinate array (m)
        node_mask: boolean array indicating compartments containing an active node
        f_node: fraction of the compartment occupied by the active node
    """
    N = int(round(L / dz))
    z = np.arange(N) * dz
    
    # Identify compartment containing each physical node (z = 0, 1, 2, ..., 9 mm)
    node_mask = np.zeros(N, dtype=bool)
    n_nodes = int(round(L / internode_spacing))
    for k in range(n_nodes):
        node_z = k * internode_spacing
        node_idx = int(round(node_z / dz))
        if node_idx < N:
            node_mask[node_idx] = True

    f_node = l_node / dz
    if f_node > 1.0 + 1e-9:
        raise ValueError(f"dz ({dz*1e6} um) cannot be smaller than physical l_node ({l_node*1e6} um) in single-cell homogenization")
    
    f_node = min(1.0, f_node)
    return N, z, node_mask, f_node

def classify_waveform(v_rec, z_arr, dt, fiber_type="abeta"):
    """
    Unified spike and event detector.
    Evaluates spatiotemporal matrix v_rec (nsteps, N) on grid z_arr (N,).
    
    Distinguishes:
        - NO_RESPONSE
        - PASSIVE_DEPOLARIZATION
        - LOCAL_STIMULUS_TRANSIENT
        - LOCAL_ABORTED_SPIKE
        - PROPAGATED_ACTION_POTENTIAL
        - UNPHYSIOLOGICAL_VELOCITY_ARTIFACT
        - NON_PROPAGATING_ELECTROTONIC_ARTIFACT
    """
    v_mV = v_rec * 1e3
    nsteps, N = v_rec.shape
    
    # Define physical downstream evaluation window: 3.0 mm to 8.0 mm
    idx_downstream = np.where((z_arr >= 3.0e-3 - 1e-9) & (z_arr <= 8.0e-3 + 1e-9))[0]
    if len(idx_downstream) == 0:
        idx_downstream = np.array([N // 2])
        
    v_downstream = v_mV[:, idx_downstream]
    v_base = np.mean(v_downstream[0, :])
    v_max = np.max(v_downstream)
    delta_v = v_max - v_base
    
    # Calculate max dV/dt in downstream window
    dvdt_downstream = np.diff(v_downstream, axis=0) / (dt * 1e3) # V/s
    max_dvdt = np.max(dvdt_downstream)
    
    # Fiber-specific thresholds
    if fiber_type.lower() == "abeta":
        thresh_amp = 40.0      # mV (excursion from -80 to >= -40 mV)
        thresh_dvdt = 500.0    # V/s
        min_cv = 15.0          # m/s
        max_cv = 80.0          # m/s
        thresh_detect = -40.0  # mV
    else: # C-fiber
        thresh_amp = 45.0      # mV (excursion from -65 to >= -20 mV)
        thresh_dvdt = 30.0     # V/s
        min_cv = 0.2           # m/s
        max_cv = 3.0           # m/s
        thresh_detect = -20.0  # mV

    # 1. No response
    if delta_v < 0.5:
        return {
            "classification": "NO_RESPONSE",
            "spiked": False,
            "v_base": v_base,
            "v_max": v_max,
            "delta_v": delta_v,
            "max_dvdt": max_dvdt,
            "cv": None,
            "t_cross_first": None
        }
        
    # 2. Check if threshold reached downstream
    if delta_v < thresh_amp or max_dvdt < thresh_dvdt:
        prox_idx = np.where(z_arr < 2.0e-3)[0]
        v_prox_max = np.max(v_mV[:, prox_idx])
        if v_prox_max - v_base >= thresh_amp:
            classification = "LOCAL_STIMULUS_TRANSIENT"
        else:
            classification = "PASSIVE_DEPOLARIZATION"
            
        return {
            "classification": classification,
            "spiked": False,
            "v_base": v_base,
            "v_max": v_max,
            "delta_v": delta_v,
            "max_dvdt": max_dvdt,
            "cv": None,
            "t_cross_first": None
        }

    # 3. If amplitude and dV/dt criteria met, verify propagation and CV
    z4_target = 4.0e-3
    z8_target = 8.0e-3
    i4 = idx_downstream[np.argmin(np.abs(z_arr[idx_downstream] - z4_target))]
    i8 = idx_downstream[np.argmin(np.abs(z_arr[idx_downstream] - z8_target))]
    
    tr4 = v_mV[:, i4]
    tr8 = v_mV[:, i8]
    
    cross4 = np.where(tr4 >= thresh_detect)[0]
    cross8 = np.where(tr8 >= thresh_detect)[0]
    
    if len(cross4) == 0 or len(cross8) == 0:
        return {
            "classification": "LOCAL_ABORTED_SPIKE",
            "spiked": False,
            "v_base": v_base,
            "v_max": v_max,
            "delta_v": delta_v,
            "max_dvdt": max_dvdt,
            "cv": None,
            "t_cross_first": cross4[0]*dt*1e3 if len(cross4)>0 else None
        }
        
    t4 = cross4[0] * dt
    t8 = cross8[0] * dt
    
    if t8 <= t4:
        return {
            "classification": "NON_PROPAGATING_ELECTROTONIC_ARTIFACT",
            "spiked": False,
            "v_base": v_base,
            "v_max": v_max,
            "delta_v": delta_v,
            "max_dvdt": max_dvdt,
            "cv": None,
            "t_cross_first": t4 * 1e3
        }
        
    dist = z_arr[i8] - z_arr[i4]
    cv = dist / (t8 - t4)
    
    if min_cv <= cv <= max_cv:
        classification = "PROPAGATED_ACTION_POTENTIAL"
        spiked = True
    else:
        classification = "UNPHYSIOLOGICAL_VELOCITY_ARTIFACT"
        spiked = False
        
    return {
        "classification": classification,
        "spiked": spiked,
        "v_base": v_base,
        "v_max": v_max,
        "delta_v": delta_v,
        "max_dvdt": max_dvdt,
        "cv": cv,
        "t_cross_first": t4 * 1e3
    }
