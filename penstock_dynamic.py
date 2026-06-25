import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# PENSTOCK DYNAMIC EQUATION SOLVER
# Formula: h = ((-Tw)(dq/dt)) - ((2*hf*q)/(H0))
# where:
#   h = (H - H0) / H0 (normalized head deviation)
#   q = (Q - Q0) / Q0 (normalized discharge deviation)
#   Tw = time constant = (L*v0)/(g*H0)
#   hf = head loss in penstock
#   H0, Q0 = initial/previous time step head, discharge
#   H, Q = current time step head, discharge
# ============================================================================

print("=" * 80)
print("PENSTOCK DYNAMIC EQUATION SOLVER")
print("Formula: h = ((-Tw)(dq/dt)) - ((2*hf*q)/(H0))")
print("=" * 80)

# ============================================================================
# PARAMETERS - MODIFY THESE VALUES IN THE CODE
# ============================================================================

# Time parameters
t_initial = 0.0           # Initial time (seconds)
t_final = 100.0           # Final time (seconds)
dt = 0.1                  # Time step (seconds)

# Pipe/tunnel parameters
L = 300.0                 # Pipe length (meters)
g = 9.81                  # Gravitational acceleration (m/s²)
diameter = 3.3            # Circular tunnel diameter (meters)
roughness = 0.0015        # Pipe roughness (mm) - typical for steel/concrete

# Discharge parameters
Q_initial = 44.0          # Initial discharge (m³/s)
Q_additional = 22.0       # Additional discharge to add (m³/s)
t_start_ramp = 20.0       # Start of ramp (seconds)
t_end_ramp = 50.0         # End of ramp (seconds)
t_ramp = t_end_ramp - t_start_ramp  # Ramp duration (seconds)

# Initial hydraulic head (reference)
H_initial = 150.0         # Initial head at intake (meters)


# Axis limits (set to None for auto-scaling)
H_axis_min = None         # Minimum head axis limit (m) - None for auto-scaling
H_axis_max = None         # Maximum head axis limit (m) - None for auto-scaling
Q_axis_min = 40           # Minimum discharge axis limit (m³/s)
Q_axis_max = 70           # Maximum discharge axis limit (m³/s) 
A = np.pi * (diameter / 2) ** 2

print(f"\n" + "=" * 80)
print(f"Configuration Summary:")
print(f"  Pipe Length (L): {L} m")
print(f"  Pipe Diameter (D): {diameter} m")
print(f"  Cross-sectional Area (A): {A:.4f} m²")
print(f"  Pipe Roughness: {roughness} mm")
print(f"  Initial Discharge (Q₀): {Q_initial} m³/s")
print(f"  Initial Head (H₀): {H_initial} m")
print(f"\n  Additional Discharge: +{Q_additional} m³/s (ramping from t={t_start_ramp}s to t={t_end_ramp}s)")
print(f"=" * 80 + "\n")

# ============================================================================
# HELPER FUNCTION: CALCULATE FRICTION FACTOR (Swamee-Jain Equation)
# ============================================================================

def calculate_friction_factor(D, roughness, Re):
    """
    Calculate friction factor using Swamee-Jain equation.
    D: pipe diameter (m)
    roughness: absolute roughness (m)
    Re: Reynolds number
    """
    if Re < 1:
        return 0
    # Relative roughness
    rel_roughness = roughness / D
    # Swamee-Jain equation (valid for 5000 < Re < 10^8 and 10^-6 < rel_roughness < 10^-2)
    f = 0.25 / (np.log10(rel_roughness / 3.7 + 5.74 / (Re ** 0.9))) ** 2
    return f

# ============================================================================
# HELPER FUNCTION: CALCULATE HEAD LOSS (Darcy-Weisbach)
# ============================================================================

def calculate_head_loss(f, L, D, v, g):
    """
    Calculate head loss using Darcy-Weisbach equation.
    f: friction factor
    L: pipe length (m)
    D: pipe diameter (m)
    v: velocity (m/s)
    g: gravitational acceleration (m/s²)
    """
    if v == 0:
        return 0
    hf = f * (L / D) * (v ** 2 / (2 * g))
    return hf

# ============================================================================
# TIME ARRAY AND DISCHARGE PROFILE
# ============================================================================

time = np.arange(t_initial, t_final + dt, dt)
n_points = len(time)

# Initialize arrays
discharge = np.zeros(n_points)
velocity = np.zeros(n_points)
head_loss = np.zeros(n_points)
Reynolds = np.zeros(n_points)
friction_factor = np.zeros(n_points)
h_normalized = np.zeros(n_points)  # Normalized head deviation
H_head = np.zeros(n_points)        # Actual head
q_normalized = np.zeros(n_points)  # Normalized discharge deviation
dq_dt = np.zeros(n_points)         # Discharge rate of change
Tw = np.zeros(n_points)            # Time constant

# ============================================================================
# CALCULATE DISCHARGE PROFILE
# ============================================================================

for i, t in enumerate(time):
    # Initial discharge
    discharge[i] = Q_initial
    
    # Additional discharge ramping from t_start_ramp to t_end_ramp
    if t >= t_start_ramp and t < t_end_ramp:
        ramp_progress = (t - t_start_ramp) / t_ramp
        discharge[i] += Q_additional * ramp_progress
    elif t >= t_end_ramp:
        discharge[i] += Q_additional
    
    # Calculate velocity
    velocity[i] = discharge[i] / A
    
    # Calculate Reynolds number (assuming kinematic viscosity of water at 20°C = 1e-6 m²/s)
    nu = 1e-6  # m²/s
    Reynolds[i] = (velocity[i] * diameter) / nu
    
    # Calculate friction factor
    friction_factor[i] = calculate_friction_factor(diameter, roughness / 1000, Reynolds[i])
    
    # Calculate head loss
    head_loss[i] = calculate_head_loss(friction_factor[i], L, diameter, velocity[i], g)

# ============================================================================
# CALCULATE dQ/dt (Rate of change of discharge)
# ============================================================================

for i in range(len(time)):
    if i == 0:
        dq_dt[i] = (discharge[i + 1] - discharge[i]) / dt if len(time) > 1 else 0
    elif i == len(time) - 1:
        dq_dt[i] = (discharge[i] - discharge[i - 1]) / dt
    else:
        dq_dt[i] = (discharge[i + 1] - discharge[i - 1]) / (2 * dt)

# ============================================================================
# CALCULATE PENSTOCK DYNAMICS
# ============================================================================

# Initialize with initial conditions
H_head[0] = H_initial
q_normalized[0] = 0  # Initially, Q = Q_initial, so q = 0
h_normalized[0] = 0  # Initially, H = H_initial, so h = 0

# Solve the dynamic equation step by step
for i in range(n_points):
    if i == 0:
        continue
    
    # Previous step values
    H0 = H_head[i - 1] if H_head[i - 1] > 0 else H_initial
    Q0 = Q_initial if i == 1 else discharge[i - 1]
    
    # Normalized discharge deviation
    q_normalized[i] = (discharge[i] - Q_initial) / Q_initial
    
    # Time constant: Tw = (L * v) / (g * H0)
    # Using current velocity at this time step
    Tw[i] = (L * velocity[i]) / (g * H0)
    
    # Penstock dynamic equation (new formula):
    # H = H0(1-(Tw*dq/dt)) - c - 2*hf*q
    
    # Normalized discharge rate of change
    dq_dt_normalized = dq_dt[i] / Q_initial
    
    # Calculate head using the new formula
    H_head[i] = H0 * (1 - (Tw[i] * dq_dt_normalized)) - (2 * head_loss[i] * q_normalized[i])
    
    # Calculate normalized head for reference
    h_normalized[i] = (H_head[i] - H0) / H0
    
    # Ensure head doesn't go negative
    if H_head[i] < 0:
        H_head[i] = 0.1  # Small positive value to avoid issues

# ============================================================================
# PLOTTING
# ============================================================================

fig, ax1 = plt.subplots(figsize=(14, 8))

# Plot Head (H) on primary y-axis
color_h = '#1f77b4'  # Blue
ax1.set_xlabel('Time (seconds)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Head, H (m)', fontsize=12, fontweight='bold', color=color_h)
line1 = ax1.plot(time, H_head, color=color_h, linewidth=2.0, marker='o', 
                 markersize=2, label='Head (H)', linestyle='-')
ax1.tick_params(axis='y', labelcolor=color_h)
ax1.grid(True, linestyle='--', alpha=0.3)

# Set head axis limits if specified
if H_axis_min is not None or H_axis_max is not None:
    ax1.set_ylim(H_axis_min, H_axis_max)

# Create secondary y-axis for discharge
ax2 = ax1.twinx()
color_q = '#ff7f0e'  # Orange
ax2.set_ylabel('Discharge, Q (m³/s)', fontsize=12, fontweight='bold', color=color_q)
line2 = ax2.plot(time, discharge, color=color_q, linewidth=2.0, marker='s', 
                 markersize=2, label='Discharge (Q)', linestyle='-')
ax2.tick_params(axis='y', labelcolor=color_q)

# Set discharge axis limits if specified
if Q_axis_min is not None or Q_axis_max is not None:
    ax2.set_ylim(Q_axis_min, Q_axis_max)

# Combine legends from both axes
lines = line1 + line2
labels = [l.get_label() for l in lines]
ax1.legend(lines, labels, loc='upper left', bbox_to_anchor=(0.8, 0.8), 
          fontsize=11, framealpha=0.95, edgecolor='black')

# Title and layout
plt.title('Penstock Dynamic Response: Head vs Time and Discharge Profile', 
         fontsize=14, fontweight='bold', pad=20)
fig.tight_layout()

# Display the plot
plt.show()

# ============================================================================
# PRINT RESULTS
# ============================================================================

print("\n" + "=" * 80)
print("PENSTOCK DYNAMICS RESULTS")
print("=" * 80)
print(f"\nFormula: H = H0(1-(Tw*dq/dt)) - c - 2*hf*q")
print(f"Time Range: {t_initial} to {t_final} seconds (step: {dt}s)")
print(f"\nActual Head (H) Summary:")
print(f"  Initial Head (H₀): {H_initial:.4f} m")
print(f"  Maximum Head: {np.max(H_head):.4f} m (at t={time[np.argmax(H_head)]:.2f}s)")
print(f"  Minimum Head: {np.min(H_head):.4f} m (at t={time[np.argmin(H_head)]:.2f}s)")
print(f"  Final Head: {H_head[-1]:.4f} m")

print(f"\nNormalized Head (h) Summary:")
print(f"  Maximum h: {np.max(h_normalized):.6f} (at t={time[np.argmax(h_normalized)]:.2f}s)")
print(f"  Minimum h: {np.min(h_normalized):.6f} (at t={time[np.argmin(h_normalized)]:.2f}s)")

print(f"\nDischarge Summary:")
print(f"  Initial Discharge: {discharge[0]:.4f} m³/s")
print(f"  Maximum Discharge: {np.max(discharge):.4f} m³/s")
print(f"  Final Discharge: {discharge[-1]:.4f} m³/s")

print(f"\nHead Loss Summary:")
print(f"  Initial Head Loss: {head_loss[0]:.4f} m")
print(f"  Maximum Head Loss: {np.max(head_loss):.4f} m (at t={time[np.argmax(head_loss)]:.2f}s)")
print(f"  Final Head Loss: {head_loss[-1]:.4f} m")

print(f"\nVelocity Summary:")
print(f"  Initial Velocity: {velocity[0]:.4f} m/s")
print(f"  Maximum Velocity: {np.max(velocity):.4f} m/s")
print(f"  Final Velocity: {velocity[-1]:.4f} m/s")

print(f"\nTime Constant (Tw) Summary:")
print(f"  Average Tw: {np.mean(Tw[1:]):.4f} s")
print(f"  Min Tw: {np.min(Tw[1:]):.4f} s")
print(f"  Max Tw: {np.max(Tw[1:]):.4f} s")

print("=" * 80)

# ============================================================================
# SAVE RESULTS TO CSV
# ============================================================================

import pandas as pd
df = pd.DataFrame({
    'Time (s)': time,
    'Discharge Q (m³/s)': discharge,
    'dQ/dt (m³/s²)': dq_dt,
    'q_normalized': q_normalized,
    'Velocity (m/s)': velocity,
    'Head Loss hf (m)': head_loss,
    'Head H (m)': H_head,
    'h_normalized': h_normalized,
    'Friction Factor': friction_factor,
    'Reynolds Number': Reynolds,
    'Time Constant Tw (s)': Tw
})

# filename = 'penstock_dynamic_results.csv'
# df.to_csv(filename, index=False)
# print(f"\nResults saved to '{filename}'")
