#!/usr/bin/env python3
"""Generate all figures with LIGHT backgrounds for GitHub."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import os, math

# ═══════════════════════════════════════════════════════
# LIGHT theme for GitHub white background
# ═══════════════════════════════════════════════════════

BG = '#ffffff'
BG2 = '#fafbfc'
GOLD = '#b8860b'
TEAL = '#0d7377'
CORAL = '#c0392b'
BLUE = '#2c6fbb'
PURPLE = '#7b3fa0'
GREY = '#8b95a5'
TEXT = '#1a1a2e'
TEXT_DIM = '#555e70'
GRID = '#e4e8ee'
ACCENT = '#d4a843'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG2,
    'axes.edgecolor': '#c0c8d4',
    'axes.labelcolor': TEXT,
    'text.color': TEXT,
    'xtick.color': TEXT_DIM,
    'ytick.color': TEXT_DIM,
    'grid.color': GRID,
    'grid.alpha': 0.8,
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'legend.facecolor': '#ffffff',
    'legend.edgecolor': '#c0c8d4',
    'legend.fontsize': 10,
    'savefig.dpi': 180,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.25,
    'savefig.facecolor': BG,
})

os.makedirs('/home/claude/figs', exist_ok=True)

# ═══════════════════════════════════════════════════════
# Core functions
# ═══════════════════════════════════════════════════════

def smallest_prime_factor(limit):
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:
            for j in range(i*i, limit + 1, i):
                if spf[j] == j: spf[j] = i
    return spf

def factorize(n, spf):
    factors = {}
    while n > 1:
        p = spf[n]; e = 0
        while n % p == 0: n //= p; e += 1
        factors[p] = e
    return factors

def digit_sum(n, p):
    s = 0
    while n > 0: s += n % p; n //= p
    return s

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i): is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

# Precompute
N_MAX = 100000
print("Precomputing...")
spf = smallest_prime_factor(N_MAX)
primes_big = sieve_primes(10**6)
C = sum(1.0 / (p * (p - 1)) for p in primes_big)

ell_vals = np.zeros(N_MAX + 1)
for n in range(2, N_MAX + 1):
    f = factorize(n, spf)
    ell_vals[n] = sum(a / p for p, a in f.items())

S_vals = np.cumsum(ell_vals)
print("Done.")

# ═══════════════════════════════════════════════════════
# BANNER
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(14, 3.5))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off')

# Subtle background gradient via a colored band
from matplotlib.patches import FancyBboxPatch
rect = FancyBboxPatch((0.02, 0.02), 0.96, 0.96, boxstyle="round,pad=0.02",
                       facecolor='#f0f2f8', edgecolor='#c0c8d4', linewidth=1.5)
ax.add_patch(rect)

ax.text(0.5, 0.78, 'The Summatory Arithmetic Derivative', fontsize=28, ha='center', va='center',
        color='#1a1a2e', fontweight='bold', family='serif')
ax.text(0.5, 0.58, "Legendre's Formula, a One-Sided Asymptotic Bound, and a Dirichlet Series Identity",
        fontsize=13, ha='center', va='center', color='#555e70', style='italic', family='serif')

ax.plot([0.15, 0.85], [0.45, 0.45], color=GOLD, linewidth=1.2, alpha=0.6)

ax.text(0.20, 0.28,
        r'$\sum_{n=1}^{N} \frac{D(n)}{n} = \sum_{p} \frac{v_p(N!)}{p}$',
        fontsize=17, ha='center', va='center', color=TEXT,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#d0d4dc', alpha=0.9))
ax.text(0.50, 0.28,
        r'$S(N) < \mathcal{C}\, N$',
        fontsize=18, ha='center', va='center', color=CORAL,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#d0d4dc', alpha=0.9))
ax.text(0.80, 0.28,
        r'$F(s) = \zeta(s)\sum_{j \geq 1} P(js+1)$',
        fontsize=17, ha='center', va='center', color=TEAL,
        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', edgecolor='#d0d4dc', alpha=0.9))

ax.text(0.5, 0.08, 'Five novel theorems  ·  Computational verification  ·  Full proofs',
        fontsize=10, ha='center', va='center', color='#888e9e', family='serif')

fig.savefig('/home/claude/figs/00_banner.png')
plt.close()
print("Banner done.")

# ═══════════════════════════════════════════════════════
# FIGURE 1: Hero — S(N) vs CN
# ═══════════════════════════════════════════════════════

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), height_ratios=[2.2, 1],
                                 gridspec_kw={'hspace': 0.08})

N_range = np.arange(1, N_MAX + 1)

ax1.plot(N_range, S_vals[1:], color=GOLD, linewidth=1.2, label=r'$S(N) = \sum_{n \leq N} D(n)/n$', zorder=3)
ax1.plot(N_range, C * N_range, color=TEAL, linewidth=1.2, linestyle='--', alpha=0.8,
         label=r'$\mathcal{C}\,N$  where $\mathcal{C} \approx 0.7732$', zorder=2)
ax1.fill_between(N_range, S_vals[1:], C * N_range, color=CORAL, alpha=0.06, zorder=1)
ax1.set_ylabel(r'$S(N)$')
ax1.set_xlim(0, N_MAX)
ax1.legend(loc='upper left', framealpha=0.95)
ax1.grid(True, alpha=0.5)
ax1.set_title(r'The Summatory Logarithmic Arithmetic Derivative', fontsize=16, color=TEXT, pad=12)
ax1.set_xticklabels([])

E_vals = S_vals[1:] - C * N_range
ax2.fill_between(N_range, E_vals, 0, where=(E_vals < 0), color=CORAL, alpha=0.15, zorder=1)
ax2.plot(N_range, E_vals, color=CORAL, linewidth=0.6, alpha=0.8, zorder=2)
ax2.axhline(0, color=GREY, linewidth=0.8, linestyle='-')
ax2.set_xlabel(r'$N$')
ax2.set_ylabel(r'$E(N) = S(N) - \mathcal{C}N$')
ax2.set_xlim(0, N_MAX)
ax2.grid(True, alpha=0.5)
ax2.text(N_MAX * 0.75, min(E_vals) * 0.4, r'Always negative (Theorem 2)',
         color=CORAL, fontsize=11, ha='center', style='italic')

fig.savefig('/home/claude/figs/01_hero.png')
plt.close()
print("Fig 1 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 2: Scatter
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 5))
N_show = 5000
ns = np.arange(2, N_show + 1)
vals = ell_vals[2:N_show + 1]

colors = plt.cm.inferno(np.clip(vals / 3.5, 0, 1))
ax.scatter(ns, vals, c=colors, s=1.5, alpha=0.5, zorder=2, rasterized=True)

window = 200
running = np.convolve(ell_vals[1:N_show+1], np.ones(window)/window, mode='valid')
ax.plot(np.arange(window, N_show + 1), running, color=GOLD, linewidth=2, label=f'Running mean (window={window})', zorder=3)
ax.axhline(C, color=TEAL, linewidth=1.5, linestyle='--', alpha=0.8, label=r'$\mathcal{C} \approx 0.7732$', zorder=3)

ax.set_xlabel(r'$n$'); ax.set_ylabel(r'$\ell(n) = D(n)/n$')
ax.set_xlim(0, N_show); ax.set_ylim(-0.1, 5.5)
ax.legend(loc='upper right', framealpha=0.95)
ax.grid(True, alpha=0.5)
ax.set_title(r'The Logarithmic Arithmetic Derivative $\ell(n) = D(n)/n$', fontsize=14, color=TEXT, pad=10)

fig.savefig('/home/claude/figs/02_scatter.png')
plt.close()
print("Fig 2 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 3: Digit-sum decomposition
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 5))
N_range3 = np.arange(2, 10001)
primes_small = sieve_primes(10000)

contrib = {}
for p in [2, 3, 5, 7, 11]:
    contrib[p] = np.array([digit_sum(int(N), p) / (p * (p - 1)) for N in N_range3])

colors_stack = [CORAL, GOLD, TEAL, BLUE, PURPLE]
labels = [f'$p = {p}$' for p in [2, 3, 5, 7, 11]]
bottom = np.zeros(len(N_range3))

for i, p in enumerate([2, 3, 5, 7, 11]):
    ax.fill_between(N_range3, -bottom - contrib[p], -bottom, color=colors_stack[i], alpha=0.4, label=labels[i])
    bottom += contrib[p]

E_actual = np.array([S_vals[int(N)] - C * N for N in N_range3])
ax.plot(N_range3, E_actual, color='#1a1a2e', linewidth=1.2, alpha=0.9, label=r'$E(N)$ actual', zorder=5)

ax.axhline(0, color=GREY, linewidth=0.8)
ax.set_xlabel(r'$N$'); ax.set_ylabel(r'Error contribution')
ax.legend(loc='lower left', framealpha=0.95, ncol=3)
ax.grid(True, alpha=0.5)
ax.set_title(r'Decomposition of $E(N)$ by Prime Digit Sums', fontsize=13, color=TEXT, pad=10)
ax.set_xlim(2, 10000)

fig.savefig('/home/claude/figs/03_digit_error.png')
plt.close()
print("Fig 3 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 4: Distribution
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 5))
vals = ell_vals[2:N_MAX+1]
bins = np.linspace(0, 6, 150)
counts, edges = np.histogram(vals, bins=bins, density=True)
centers = (edges[:-1] + edges[1:]) / 2

ax.bar(centers, counts, width=edges[1]-edges[0], color=GOLD, alpha=0.55, edgecolor='none', zorder=2)
ax.axvline(C, color=TEAL, linewidth=2, linestyle='--', label=r'Mean $\mathcal{C} \approx 0.7732$', zorder=3)

var_theory = sum(1.0 / (p * (p - 1)**2) for p in primes_big)
ax.axvline(C - np.sqrt(var_theory), color=CORAL, linewidth=1.2, linestyle=':', alpha=0.7, zorder=3)
ax.axvline(C + np.sqrt(var_theory), color=CORAL, linewidth=1.2, linestyle=':', alpha=0.7,
           label=r'$\pm\sigma$', zorder=3)

ax.set_xlabel(r'$\ell(n)$'); ax.set_ylabel('Density')
ax.set_xlim(0, 5)
ax.legend(loc='upper right', framealpha=0.95)
ax.grid(True, alpha=0.5)
ax.set_title(r'Distribution of $\ell(n) = D(n)/n$ for $n \leq 10^5$', fontsize=14, color=TEXT, pad=10)

fig.savefig('/home/claude/figs/04_distribution.png')
plt.close()
print("Fig 4 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 5: Dirichlet series
# ═══════════════════════════════════════════════════════

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

primes_med = sieve_primes(10000)
s_range = np.linspace(1.05, 6, 80)
direct_vals = []; formula_vals = []

N_sum = 30000
spf_local = smallest_prime_factor(N_sum)
ell_cache = np.zeros(N_sum + 1)
for n in range(2, N_sum + 1):
    f = factorize(n, spf_local)
    ell_cache[n] = sum(a / p for p, a in f.items())

for s in s_range:
    d = sum(ell_cache[n] / (n ** s) for n in range(2, N_sum + 1))
    direct_vals.append(d)
    zeta_s = sum(1.0 / (n ** s) for n in range(1, N_sum + 1))
    G_s = 0.0
    for j in range(1, 60):
        w = j * s + 1
        P_w = sum(1.0 / (p ** w) for p in primes_med if p ** w < 1e15)
        G_s += P_w
        if P_w < 1e-15: break
    formula_vals.append(zeta_s * G_s)

direct_vals = np.array(direct_vals); formula_vals = np.array(formula_vals)

ax1.plot(s_range, direct_vals, color=GOLD, linewidth=2, label='Direct sum')
ax1.plot(s_range, formula_vals, color=TEAL, linewidth=2, linestyle='--', label=r'$\zeta(s)\cdot G(s)$')
ax1.axvline(1, color=CORAL, linewidth=1, linestyle=':', alpha=0.5, label='Pole at $s=1$')
ax1.set_xlabel(r'$s$'); ax1.set_ylabel(r'$F(s)$')
ax1.legend(loc='upper right', framealpha=0.95)
ax1.grid(True, alpha=0.5)
ax1.set_title(r'Dirichlet Series $F(s)$', fontsize=12, color=TEXT)
ax1.set_ylim(0, 8)

rel_err = np.abs(direct_vals - formula_vals) / np.maximum(np.abs(direct_vals), 1e-15)
ax2.semilogy(s_range, rel_err + 1e-16, color=CORAL, linewidth=1.5)
ax2.set_xlabel(r'$s$'); ax2.set_ylabel('Relative error')
ax2.grid(True, alpha=0.5)
ax2.set_title('Verification: Direct vs Formula', fontsize=12, color=TEXT)
ax2.set_ylim(1e-12, 1e-1)

fig.tight_layout()
fig.savefig('/home/claude/figs/05_dirichlet.png')
plt.close()
print("Fig 5 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 6: One-sided bound zoom
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 4.5))

N_range6 = np.arange(2, 1001)
E_vals6 = np.array([S_vals[int(N)] - C * N for N in N_range6])

ax.fill_between(N_range6, E_vals6, 0, color=CORAL, alpha=0.15)
ax.plot(N_range6, E_vals6, color=CORAL, linewidth=1.2, zorder=3)
ax.axhline(0, color=TEAL, linewidth=1.5, linestyle='-', zorder=4)

for k in range(2, 10):
    N = 2**k - 1
    if N <= 1000:
        E = S_vals[N] - C * N
        ax.plot(N, E, 'o', color=GOLD, markersize=7, zorder=5, markeredgecolor='#8a6a10', markeredgewidth=0.8)
        ax.annotate(f'$2^{{{k}}}-1$', (N, E), textcoords='offset points',
                   xytext=(6, 8), fontsize=9, color=GOLD)

ax.set_xlabel(r'$N$'); ax.set_ylabel(r'$E(N) = S(N) - \mathcal{C}N$')
ax.grid(True, alpha=0.5)
ax.set_title(r'One-Sided Bound: $E(N) < 0$ for all $N \geq 2$  (gold dots = binary repunits)',
             fontsize=12, color=TEXT, pad=10)
ax.set_xlim(2, 1000)

ax.text(500, min(E_vals6) * 0.3,
        r'$E(N) = -\sum_p \frac{s_p(N)}{p(p-1)} + O(1/\log N)$',
        fontsize=13, color=TEXT, ha='center',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='white', edgecolor='#c0c8d4', alpha=0.95))

fig.savefig('/home/claude/figs/06_onesided.png')
plt.close()
print("Fig 6 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 7: Convolution
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(12, 5))

ns = list(range(2, 61))
prime_colors = {2: CORAL, 3: GOLD, 5: TEAL, 7: BLUE, 11: PURPLE,
                13: '#c06090', 17: '#409070', 19: '#7080b0', 23: '#a0a040',
                29: '#5080b0', 31: '#b08050', 37: '#8050b0', 41: '#50b050',
                43: '#b05050', 47: '#5050b0', 53: '#b0b080', 59: '#80b0b0'}

for n in ns:
    f = factorize(n, spf)
    bottom = 0
    for p in sorted(f.keys()):
        a = f[p]; contrib_val = a / p
        color = prime_colors.get(p, GREY)
        ax.bar(n, contrib_val, bottom=bottom, width=0.7, color=color, edgecolor='none', alpha=0.75)
        bottom += contrib_val

from matplotlib.patches import Patch
legend_elements = [Patch(facecolor=prime_colors[p], alpha=0.75, label=f'$\\Lambda_\\star(p^k) = 1/{p}$')
                   for p in [2, 3, 5, 7, 11, 13]]
ax.legend(handles=legend_elements, loc='upper left', framealpha=0.95, ncol=2)

ax.axhline(C, color=GREY, linewidth=1, linestyle='--', alpha=0.5)
ax.set_xlabel(r'$n$'); ax.set_ylabel(r'$\ell(n) = \sum_{d \mid n} \Lambda_\star(d)$')
ax.set_xlim(1, 61)
ax.grid(True, alpha=0.4, axis='y')
ax.set_title(r'Convolution Decomposition: $D(n)/n = \sum_{d \mid n} \Lambda_\star(d)$',
             fontsize=13, color=TEXT, pad=10)

fig.savefig('/home/claude/figs/07_convolution.png')
plt.close()
print("Fig 7 done.")

# ═══════════════════════════════════════════════════════
# FIGURE 8: Variance convergence
# ═══════════════════════════════════════════════════════

fig, ax = plt.subplots(figsize=(10, 4.5))

var_theory = sum(1.0 / (p * (p - 1)**2) for p in primes_big)

checkpoints = list(range(100, N_MAX + 1, 200))
emp_vars = []
running_sum = 0.0; running_sum2 = 0.0; cp_idx = 0

for n in range(1, N_MAX + 1):
    running_sum += ell_vals[n]
    running_sum2 += ell_vals[n] ** 2
    if cp_idx < len(checkpoints) and n == checkpoints[cp_idx]:
        mean = running_sum / n
        var = running_sum2 / n - mean**2
        emp_vars.append(var)
        cp_idx += 1

ax.plot(checkpoints[:len(emp_vars)], emp_vars, color=GOLD, linewidth=1.5, label='Empirical variance', zorder=3)
ax.axhline(var_theory, color=TEAL, linewidth=2, linestyle='--',
           label=f'Theoretical = {var_theory:.4f}', zorder=4)

ax.set_xlabel(r'$N$')
ax.set_ylabel('Empirical variance')
ax.legend(loc='upper right', framealpha=0.95)
ax.grid(True, alpha=0.5)
ax.set_title('Convergence of Empirical Variance', fontsize=13, color=TEXT, pad=10)
ax.set_xlim(0, N_MAX)

fig.savefig('/home/claude/figs/08_variance.png')
plt.close()
print("Fig 8 done.")

print("\nAll figures generated with light theme!")
