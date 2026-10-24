import numpy as np
import matplotlib.pyplot as plt

def arc_points(x0, y0, phi, length, kappa, n=30):
    # one segment: starts at (x0, y0) pointing at angle phi, bends with curvature kappa
    s = np.linspace(0, length, n)
    if abs(kappa) < 1e-9:                       # no bend: straight line
        x = x0 + s * np.cos(phi)
        y = y0 + s * np.sin(phi)
    else:
        psi = phi + kappa * s                   # heading along the arc
        x = x0 + (np.sin(psi) - np.sin(phi)) / kappa
        y = y0 - (np.cos(psi) - np.cos(phi)) / kappa
    return x, y, phi + kappa * length           # also return the end heading

def continuum_robot(lengths, curvatures):
    # chain the segments: each starts where the previous one ended
    xs, ys = [0.0], [0.0]
    x0, y0, phi = 0.0, 0.0, np.pi / 2           # base at origin, pointing up
    for L, k in zip(lengths, curvatures):
        x, y, phi = arc_points(x0, y0, phi, L, k)
        xs.extend(x[1:]); ys.extend(y[1:])
        x0, y0 = x[-1], y[-1]
    return np.array(xs), np.array(ys)

lengths = [2.0, 2.0, 2.0]

# ---------- Part 1: three example shapes ----------
configs = {
    "Straight": [0.0, 0.0, 0.0],
    "Gentle C-bend": [0.2, 0.2, 0.2],
    "S-bend": [0.4, -0.4, 0.4],
}

plt.figure(figsize=(6, 6))
for name, kappas in configs.items():
    x, y = continuum_robot(lengths, kappas)
    line, = plt.plot(x, y, linewidth=3, label=name)
    plt.plot(x[-1], y[-1], "o", color=line.get_color())   # tip dot, same colour as its line
    print(name, round(x[-1], 2), round(y[-1], 2))
plt.axis("equal")
plt.legend()
plt.title("Constant-curvature model of a three-segment continuum robot")
plt.xlabel("x (arbitrary units)")
plt.ylabel("y (arbitrary units)")
plt.savefig("continuum_bending.png", dpi=200)
plt.show()

# Part 2: how curvature errors move the tip
np.random.seed(42)   # so the numbers repeat between runs

nominal = [0.4, -0.4, 0.4]                      # the S-bend
x_nom, y_nom = continuum_robot(lengths, nominal)
tip_nom = np.array([x_nom[-1], y_nom[-1]])

def tip_scatter(sigma, n_trials=200):
    tips = []
    for _ in range(n_trials):
        noisy = np.array(nominal) + np.random.normal(0, sigma, size=len(nominal))
        x, y = continuum_robot(lengths, noisy)
        tips.append([x[-1], y[-1]])
    return np.array(tips)

plt.figure(figsize=(6, 6))
plt.plot(x_nom, y_nom, linewidth=3, color="black", label="Nominal S-bend")
for sigma, color in [(0.01, "tab:green"), (0.03, "tab:red")]:
    tips = tip_scatter(sigma)
    err = np.linalg.norm(tips - tip_nom, axis=1)   # distance of each tip from the nominal tip
    print(f"curvature error std {sigma}: mean tip error {err.mean():.3f}, "
          f"95th percentile {np.percentile(err, 95):.3f}")
    plt.scatter(tips[:, 0], tips[:, 1], s=10, alpha=0.5, color=color,
                label=f"Tip positions (curvature error std {sigma})")
plt.axis("equal")
plt.legend()
plt.title("Tip uncertainty from small curvature errors (synthetic)")
plt.xlabel("x (arbitrary units)")
plt.ylabel("y (arbitrary units)")
plt.savefig("tip_uncertainty.png", dpi=200)
plt.show()