import numpy as np
import matplotlib.pyplot as plt

# Time parameterss
t_initial = 0.0           # Initial time (seconds)
t_final = 100.0           # Final time (seconds)
dt = 0.005                  # Time step (seconds)

# Discharge parameters
Q_initial =44           # Initial discharge (m³/s)
Q_additional = 22        # Additional discharge to add (m³/s)
t_delay = 20.0            # Time after which additional discharge starts (seconds)
t_ramp = 30.0             # Time for discharge to increase linearly (fixed at 30 seconds)

# Pipe/tunnel parameters
L_values = [500, 400, 300, 200, 100, 50]  # Multiple pipe lengths (meters)
g = 9.81                  
diameter = 3.3            # Circular tunnel (meters)

# Axis limits in Y (set to None for auto-scaling)
Q_axis_min = 30        # (m³/s)
Q_axis_max = 80        # (m³/s)

# cross-sectional area
A = np.pi * (diameter / 2) ** 2

print(f"\n" + "=" * 70)
print(f"Configuration Summary:")
print(f"  Pipe Lengths (L): {L_values} m")
print(f"  Tunnel Diameter: {diameter} m")
print(f"  Cross-sectional Area (A): {A:.4f} m²")
print(f"  Initial Discharge (Q₀): {Q_initial} m³/s")
print(f"  Additional Discharge: {Q_additional} m³/s (ramped over {t_ramp}s starting at t={t_delay}s)")
print(f"=" * 70 + "\n")

# ============================================================================
# TIME ARRAY AND DISCHARGE PROFILE
# ============================================================================

# Create time array
time = np.arange(t_initial, t_final + dt, dt)

# Initialize discharge and its derivative arrays
discharge = np.zeros_like(time)
dQ_dt = np.zeros_like(time)

# Calculate discharge and dQ/dt at each time step
for i, t in enumerate(time):
    discharge[i] = Q_initial
    
    # ramping discharge after delay
    if t >= t_delay and t < (t_delay + t_ramp):
        ramp_progress = (t - t_delay) / t_ramp
        discharge[i] += Q_additional * ramp_progress
    elif t >= (t_delay + t_ramp):
        # Constant additional discharge after ramp completes
        discharge[i] += Q_additional

# dQ/dt
for i in range(len(time)):
    if i == 0:
        # Forward difference for first point
        dQ_dt[i] = (discharge[i + 1] - discharge[i]) / dt if len(time) > 1 else 0
    elif i == len(time) - 1:
        # Backward difference for last point
        dQ_dt[i] = (discharge[i] - discharge[i - 1]) / dt
    else:
        # Central difference for interior points
        dQ_dt[i] = (discharge[i + 1] - discharge[i - 1]) / (2 * dt)

# ============================================================================
# CALCULATE HEAD REQUIRED (ΔH) FOR EACH L VALUE
# ============================================================================

# Define colors for each L value
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# Store results for each L
results_dict = {}
del_H_values = {}

# Calculate ΔH for each L value
for idx, L in enumerate(L_values):
    # ΔH = (L / (g * A)) * (dQ/dt)
    del_H = (L / (g * A)) * dQ_dt
    del_H_values[L] = del_H
    results_dict[L] = {
        'max': np.max(del_H),
        'min': np.min(del_H),
        'max_time': time[np.argmax(del_H)],
        'min_time': time[np.argmin(del_H)]
    }

# ============================================================================
# PLOTTING - ALL L VALUES ON SAME GRAPH
# ============================================================================

fig, ax1 = plt.subplots(figsize=(14, 8))

# Plot ΔH for each L value on the same graph
lines_dh = []
for idx, L in enumerate(L_values):
    line = ax1.plot(time, del_H_values[L], color=colors[idx], linewidth=2.5, 
                    marker='o', markersize=2.5, label=f'L = {L} m', alpha=0.8)
    lines_dh.extend(line)

ax1.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_ylabel(r'Head Required, $\Delta H$ (m)', fontsize=12, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.3)
ax1.legend(loc='best', fontsize=11, framealpha=0.95)

# Title and layout
plt.title(r'Head Required vs Time for Different Pipe Lengths', fontsize=14, fontweight='bold', pad=20)
fig.tight_layout()

# Display the plot
plt.show()

# ============================================================================
# PRINT RESULTS
# ============================================================================

print("\n" + "=" * 70)
print("RESULTS SUMMARY FOR EACH PIPE LENGTH")
print("=" * 70)
print(f"\nTime Range: {t_initial} to {t_final} seconds (step: {dt}s)")
print(f"\nDetailed Results:\n")

for L in L_values:
    print(f"L = {L} m:")
    print(f"  Maximum ΔH: {results_dict[L]['max']:.4f} m (at t={results_dict[L]['max_time']:.2f}s)")
    print(f"  Minimum ΔH: {results_dict[L]['min']:.4f} m (at t={results_dict[L]['min_time']:.2f}s)")
    print()

print("=" * 70)

# Optional: Save data to CSV (all L values)
import pandas as pd

# Create a dataframe with time, discharge, and ΔH for each L value
data = {'Time (s)': time, 'Discharge (m³/s)': discharge}
for L in L_values:
    data[f'ΔH_L{L} (m)'] = del_H_values[L]

df = pd.DataFrame(data)
filename = 'delH_vs_time_results.csv'
df.to_csv(filename, index=False)
print(f"Results saved to '{filename}'")
