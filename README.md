# OpenFOAM tailrace tunnel(Pressure Transient Analysis)

CFD simulation of a merged tailrace tunnel serving three draft tube units of a hydropower plant, with a lumped-mass analytical model to interpret pressure transients observed during staged unit commissioning.

---

## Background

In hydropower plants with multiple turbine units discharging into a common tailrace tunnel, staged unit start-up introduces transient pressure responses that are not fully captured by steady-state hydraulic analysis. This repository documents a pressurized tailrace tunnel simulation where a sudden pressure head spike was observed the moment a third draft tube unit's discharge was introduced into the already-operating merged tunnel system.

The third unit discharge was ramped gradually from 0 m³/s to 22 m³/s. Despite the gradual ramp, a sharp pressure spike occurred at the **instant the third unit flow was initiated**, followed by a relatively stable plateau during the ramp, and then a **sudden pressure drop** when the discharge reached its final value of 22 m³/s and the ramp ended.

---

## Physical Interpretation of the pressure spike

The observed pressure transient pattern is explained using the **lumped-mass (rigid water column) approach** for fluid inertia in conduit flow.

Under the lumped-mass assumptions:
- Tunnel walls are rigid and water is incompressible — flow changes propagate instantaneously through the system
- The entire water mass in the tunnel accelerates as a single rigid slug
- Head losses during transients are approximated using steady-state friction equations

The inertial head required to accelerate the water column is:

$$\Delta H = \frac{L}{gA} \frac{dQ}{dt}$$

where:
- $L$ = tunnel length from probe location to downstream end (m)
- $g$ = gravitational acceleration (m/s²)
- $A$ = tunnel cross-sectional area (m²)
- $\frac{dQ}{dt}$ = rate of change of discharge (m³/s²)

**Spike at onset:** When the third unit discharge is introduced, $dQ/dt$ is maximum at the start of the ramp. The entire upstream water column must be accelerated, the inertial head demand manifests as a pressure spike.

**Plateau during ramp:** Once the slug is moving at the demanded velocity, $dQ/dt$ is approximately constant (linear ramp), so $\Delta H$ remains steady.

**Drop at end of ramp:** When the discharge reaches 22 m³/s and ramping stops, $dQ/dt$ returns to zero, the inertial driving head is no longer required and pressure drops back toward the pre-addition baseline.

This is physically consistent with the incompressible Navier-Stokes momentum equation solved by OpenFOAM (PIMPLE), where the $\partial \mathbf{u}/\partial t$ term represents the same inertial mechanism. The lumped-mass model is a 0D simplification of the same physics, valid when spatial variation along the tunnel is secondary to temporal acceleration effects.

> **Note:** Alternative contributors (mesh artifacts, VOF free-surface compression, PIMPLE under-relaxation transients at large flow changes) have not been fully ruled out and warrant further investigation.

---

## Simplified setup of openfoFOAM simulation in this python analysis

| Parameter | Value |
|---|---|
| Solver | OpenFOAM (interFoam / VOF approach) |
| Tunnel geometry | Circular, uniform diameter |
| Tunnel diameter | 3.3 m |
| Cross-sectional area | 8.553 m² |
| Units discharging | 3 draft tube exit tunnels merging into single tailrace |
| Initial discharge (Units 1+2) | 44 m³/s |
| Third unit discharge (ramped) | 0 → 22 m³/s over 30 s |
| Simulation time step | 0.005 s |
| Total simulation duration | 100 s |
| Ramp start time | t = 20 s |

---

## Repository Structure

```
openFOAM_tailrace_tunnel/
│
├── lumped_mass_analysis/
│   ├── pressure_spike_lumped_mass.py     # Analytical ΔH computation for multiple probe distances
│   └── delH_vs_time_results.csv          # Output: ΔH vs time for L = 50–500 m (auto-generated)
│
└── README.md
```

> OpenFOAM case files (0/, constant/, system/, postProcessing/) to be added.

---

## Lumped-Mass Python Analysis

`pressure_spike_lumped_mass.py` implements the analytical lumped-mass model to compute the inertial head $\Delta H$ at probe locations placed at different distances from the downstream end of the tunnel.

### What it does
- Constructs the discharge time series Q(t): steady at 44 m³/s, then linearly ramped +22 m³/s from t = 20 s to t = 50 s
- Computes $dQ/dt$ using central finite differences (forward/backward at boundaries)
- Applies $\Delta H = \frac{L}{gA} \frac{dQ}{dt}$ for six probe distances: L = 500, 400, 300, 200, 100, 50 m
- Plots $\Delta H$ vs time for all probe distances on a single figure
- Exports results to CSV

### Probe distances and expected ΔH

The model is a simplified 1D representation of the actual 3D CFD tunnel. Probe distances represent how far upstream from the downstream boundary a monitoring point is located.

| Probe distance L (m) | Peak ΔH (m) |
|---|---|
| 500 | highest |
| 400 | — |
| 300 | — |
| 200 | — |
| 100 | — |
| 50 | lowest |

*(Run the script to populate exact values — they scale linearly with L)*

### Usage

```bash
# Install dependencies
pip install numpy matplotlib pandas openpyxl

# Run analysis
python pressure_spike_lumped_mass.py
```

Output CSV saved as `delH_vs_time_results.csv` in the working directory.

---

## Dependencies

- Python 3.x
- numpy
- matplotlib
- pandas
- openpyxl

---

## Authored 
as intern, Hydro Lab Pvt. Ltd., Lalitpur, Nepal
2026

---
Lumped-mass interpretation under review against OpenFOAM source-level pressure-velocity coupling behavior.
