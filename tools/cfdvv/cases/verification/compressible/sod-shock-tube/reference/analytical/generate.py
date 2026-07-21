import numpy as np

gam = 1.4
rho_L, p_L = 1.0, 1.0
rho_R, p_R = 0.125, 0.1
t = 0.2
a_L = np.sqrt(gam * p_L / rho_L)
a_R = np.sqrt(gam * p_R / rho_R)

def u_fan(p):
    return (2*a_L/(gam-1))*(1 - (p/p_L)**((gam-1)/(2*gam)))

def u_shock(p):
    return (p - p_R) * np.sqrt(2.0/(rho_R*((gam+1)*p + (gam-1)*p_R)))

def f(p):
    return u_fan(p) - u_shock(p)

lo, hi = 0.001, 1.0
for _ in range(100):
    m = (lo+hi)/2
    if f(lo)*f(m) <= 0:
        hi = m
    else:
        lo = m
p_star = (lo+hi)/2
u_star = u_fan(p_star)
rho_star_L = rho_L * (p_star/p_L)**(1/gam)
beta = (gam+1)/(gam-1)
rho_star_R = rho_R * (p_star/p_R * beta + 1) / (p_star/p_R + beta)
a_star_L = a_L * (p_star/p_L)**((gam-1)/(2*gam))

x_head = 0.5 - a_L * t
x_tail = 0.5 - a_star_L * t
x_contact = 0.5 + u_star * t
M_s = np.sqrt((p_star/p_R * (gam+1)/(2*gam)) + (gam-1)/(2*gam))
S = M_s * a_R
x_shock = 0.5 + S * t

print(f"p*={p_star:.6f} u*={u_star:.6f}")
print(f"rho*_L={rho_star_L:.6f} rho*_R={rho_star_R:.6f}")
print(f"fan=[{x_head:.4f},{x_tail:.4f}] contact={x_contact:.4f} shock={x_shock:.4f}")

n = 200
xs = np.linspace(0, 1, n)
data = []
for x in xs:
    if x < x_head:
        rho, u, p = rho_L, 0.0, p_L
    elif x < x_tail:
        xi = (x-0.5)/t
        u = 2/(gam+1)*(a_L + xi)
        a = a_L - (gam-1)/2*u
        p = p_L * (a/a_L)**(2*gam/(gam-1))
        rho = rho_L * (a/a_L)**(2/(gam-1))
    elif x < x_contact:
        rho, u, p = rho_star_L, u_star, p_star
    elif x < x_shock:
        rho, u, p = rho_star_R, u_star, p_star
    else:
        rho, u, p = rho_R, 0.0, p_R
    e = p/((gam-1)*rho)
    data.append((x, rho, u, p, e))

with open("solution_t0.2.csv", "w") as f:
    f.write("x,rho,u,p,e\n")
    for x, rho, u, p, e in data:
        f.write(f"{x:.10f},{rho:.10f},{u:.10f},{p:.10f},{e:.10f}\n")
