#!/usr/bin/env python3
"""Generate all figures for the README."""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import numpy as np
from collections import defaultdict
import math
import os

# ═══════════════════════════════════════════════════════
# Style
# ═══════════════════════════════════════════════════════

BG = '#0b0e17'
BG2 = '#101625'
GOLD = '#d4a843'
GOLD_DIM = '#8a7230'
TEAL = '#3fbfa0'
CORAL = '#e06050'
BLUE = '#5a8fcc'
PURPLE = '#9070c0'
GREY = '#4a5068'
TEXT = '#c8c4b8'
TEXT_DIM = '#6a6e7e'
GRID = '#1a1f30'

plt.rcParams.update({
    'figure.facecolor': BG,
    'axes.facecolor': BG2,
    'axes.edgecolor': GREY,
    'axes.labelcolor': TEXT,
    'text.color': TEXT,
    'xtick.color': TEXT_DIM,
    'ytick.color': TEXT_DIM,
    'grid.color': GRID,
    'grid.alpha': 0.6,
    'font.family': 'serif',
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.labelsize': 12,
    'legend.facecolor': BG2,
    'legend.edgecolor': GREY,
    'legend.fontsize': 10,
    'savefig.dpi': 200,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.2,
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
                if spf[j] == j:
                    spf[j] = i
    return spf

def factorize(n, spf):
    factors = {}
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        factors[p] = e
    return factors

def ell(n, spf):
    if n <= 1: return 0.0
    f = factorize(n, spf)
    return sum(a / p for p, a in f.items())

def digit_sum(n, p):
    s = 0
    while n > 0:
        s += n % p
        n //= p
    return s

def sieve_primes(limit):
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

# Precompute
N_MAX = 100000
spf = smallest_prime_factor(N_MAX)
primes_big = sieve_primes(10**6)
C = sum(1.0 / (p * (p - 1)) for p in primes_big)

# Compute ell(n) and S(N) for all n up to N_MAX
ell_vals = np.zeros(N_MAX + 1)
for n in range(2, N_MAX + 1):
    f = factorize(n, spf)
    ell_vals[n] = sum(a / p for p, a in f.items())

S_vals = np.cumsum(ell_vals)

print("Precomputation done.")

# ═══════════════════════════════════════════════════════
# FIGURE 1: Hero — S(N) vs CN with error ribbon
# ═══════════════════════════════════════════════════════

def fig_hero():
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 7), height_ratios=[2.2, 1],
                                     gridspec_kw={'hspace': 0.08})
    
    N_range = np.arange(1, N_MAX + 1)
    
    # Top: S(N) and CN
    ax1.plot(N_range, S_vals[1:], color=GOLD, linewidth=1.2, label=r'$S(N) = \sum_{n \leq N} D(n)/n$', zorder=3)
    ax1.plot(N_range, C * N_range, color=TEAL, linewidth=1.2, linestyle='--', alpha=0.8,
             label=r'$\mathcal{C}\,N$  where $\mathcal{C} \approx 0.7732$', zorder=2)
    ax1.fill_between(N_range, S_vals[1:], C * N_range, color=CORAL, alpha=0.08, zorder=1)
    ax1.set_ylabel(r'$S(N)$')
    ax1.set_xlim(0, N_MAX)
    ax1.legend(loc='upper left', framealpha=0.9)
    ax1.set_xticklabels([])
    ax1.grid(True, alpha=0.3)
    ax1.set_title(r'The Summatory Logarithmic Arithmetic Derivative', fontsize=16, color=GOLD, pad=12)
    
    # Bottom: Error E(N) = S(N) - CN
    E_vals = S_vals[1:] - C * N_range
    ax2.fill_between(N_range, E_vals, 0, where=(E_vals < 0), color=CORAL, alpha=0.25, zorder=1)
    ax2.plot(N_range, E_vals, color=CORAL, linewidth=0.6, alpha=0.8, zorder=2)
    ax2.axhline(0, color=GREY, linewidth=0.8, linestyle='-')
    ax2.set_xlabel(r'$N$')
    ax2.set_ylabel(r'$E(N) = S(N) - \mathcal{C}N$')
    ax2.set_xlim(0, N_MAX)
    ax2.grid(True, alpha=0.3)
    
    # Annotate
    ax2.text(N_MAX * 0.75, min(E_vals) * 0.4, r'Always negative $\longrightarrow$ Theorem 2',
             color=CORAL, fontsize=11, ha='center', style='italic')
    
    fig.savefig('/home/claude/figs/01_hero.png')
    plt.close()
    print("Figure 1 done.")

fig_hero()

# ═══════════════════════════════════════════════════════
# FIGURE 2: ell(n) scatter with running mean
# ═══════════════════════════════════════════════════════

def fig_scatter():
    fig, ax = plt.subplots(figsize=(12, 5))
    
    N_show = 5000
    ns = np.arange(2, N_show + 1)
    vals = ell_vals[2:N_show + 1]
    
    # Color by magnitude
    colors = plt.cm.magma(np.clip(vals / 3.0, 0, 1))
    ax.scatter(ns, vals, c=colors, s=1.2, alpha=0.6, zorder=2, rasterized=True)
    
    # Running mean
    window = 200
    running = np.convolve(ell_vals[1:N_show+1], np.ones(window)/window, mode='valid')
    ax.plot(np.arange(window, N_show + 1), running, color=GOLD, linewidth=1.8, label=f'Running mean (window={window})', zorder=3)
    ax.axhline(C, color=TEAL, linewidth=1.2, linestyle='--', alpha=0.8, label=r'$\mathcal{C} \approx 0.7732$', zorder=3)
    
    ax.set_xlabel(r'$n$')
    ax.set_ylabel(r'$\ell(n) = D(n)/n$')
    ax.set_xlim(0, N_show)
    ax.set_ylim(-0.1, 5.5)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_title(r'The Logarithmic Arithmetic Derivative $\ell(n) = D(n)/n$', fontsize=14, color=GOLD, pad=10)
    
    fig.savefig('/home/claude/figs/02_scatter.png')
    plt.close()
    print("Figure 2 done.")

fig_scatter()

# ═══════════════════════════════════════════════════════
# FIGURE 3: Digit-sum decomposition of the error
# ═══════════════════════════════════════════════════════

def fig_digit_error():
    fig, ax = plt.subplots(figsize=(12, 5))
    
    N_range = np.arange(2, 10001)
    primes_small = sieve_primes(10000)
    
    # Compute digit-sum contributions from first few primes
    contrib = {}
    for p in [2, 3, 5, 7, 11]:
        contrib[p] = np.array([digit_sum(int(N), p) / (p * (p - 1)) for N in N_range])
    
    # Stacked area (negative)
    colors_stack = [CORAL, GOLD, TEAL, BLUE, PURPLE]
    labels = [f'$p = {p}$' for p in [2, 3, 5, 7, 11]]
    bottom = np.zeros(len(N_range))
    
    for i, p in enumerate([2, 3, 5, 7, 11]):
        ax.fill_between(N_range, -bottom - contrib[p], -bottom, color=colors_stack[i], alpha=0.5, label=labels[i])
        bottom += contrib[p]
    
    # Actual error
    E_actual = np.array([S_vals[int(N)] - C * N for N in N_range])
    ax.plot(N_range, E_actual, color='white', linewidth=1.2, alpha=0.9, label=r'$E(N)$ actual', zorder=5)
    
    ax.axhline(0, color=GREY, linewidth=0.8)
    ax.set_xlabel(r'$N$')
    ax.set_ylabel(r'Error contribution')
    ax.legend(loc='lower left', framealpha=0.9, ncol=3)
    ax.grid(True, alpha=0.3)
    ax.set_title(r'Decomposition of $E(N)$ by Prime Digit Sums: $E(N) \approx -\sum_p \frac{s_p(N)}{p(p-1)}$',
                 fontsize=13, color=GOLD, pad=10)
    ax.set_xlim(2, 10000)
    
    fig.savefig('/home/claude/figs/03_digit_error.png')
    plt.close()
    print("Figure 3 done.")

fig_digit_error()

# ═══════════════════════════════════════════════════════
# FIGURE 4: Distribution / histogram of ell(n)
# ═══════════════════════════════════════════════════════

def fig_distribution():
    fig, ax = plt.subplots(figsize=(10, 5))
    
    vals = ell_vals[2:N_MAX+1]
    
    bins = np.linspace(0, 6, 150)
    counts, edges = np.histogram(vals, bins=bins, density=True)
    centers = (edges[:-1] + edges[1:]) / 2
    
    ax.bar(centers, counts, width=edges[1]-edges[0], color=GOLD, alpha=0.6, edgecolor='none', zorder=2)
    ax.axvline(C, color=TEAL, linewidth=2, linestyle='--', label=r'Mean $\mathcal{C} \approx 0.7732$', zorder=3)
    
    # Variance annotation
    var_theory = sum(1.0 / (p * (p - 1)**2) for p in primes_big)
    ax.axvline(C - np.sqrt(var_theory), color=CORAL, linewidth=1, linestyle=':', alpha=0.6, zorder=3)
    ax.axvline(C + np.sqrt(var_theory), color=CORAL, linewidth=1, linestyle=':', alpha=0.6,
               label=r'$\pm\sigma$,  $\sigma^2 = \sum_p \frac{1}{p(p-1)^2}$', zorder=3)
    
    ax.set_xlabel(r'$\ell(n)$')
    ax.set_ylabel('Density')
    ax.set_xlim(0, 5)
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_title(r'Distribution of $\ell(n) = D(n)/n$ for $n \leq 10^5$', fontsize=14, color=GOLD, pad=10)
    
    fig.savefig('/home/claude/figs/04_distribution.png')
    plt.close()
    print("Figure 4 done.")

fig_distribution()

# ═══════════════════════════════════════════════════════
# FIGURE 5: Dirichlet series verification
# ═══════════════════════════════════════════════════════

def fig_dirichlet():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))
    
    primes_med = sieve_primes(10000)
    
    s_range = np.linspace(1.05, 6, 80)
    direct_vals = []
    formula_vals = []
    
    N_sum = 30000
    spf_local = smallest_prime_factor(N_sum)
    
    # Precompute ell values
    ell_cache = np.zeros(N_sum + 1)
    for n in range(2, N_sum + 1):
        f = factorize(n, spf_local)
        ell_cache[n] = sum(a / p for p, a in f.items())
    
    for s in s_range:
        # Direct: sum ell(n)/n^s
        d = sum(ell_cache[n] / (n ** s) for n in range(2, N_sum + 1))
        direct_vals.append(d)
        
        # Formula: zeta(s) * G(s)
        zeta_s = sum(1.0 / (n ** s) for n in range(1, N_sum + 1))
        G_s = 0.0
        for j in range(1, 60):
            w = j * s + 1
            P_w = sum(1.0 / (p ** w) for p in primes_med if p ** w < 1e15)
            G_s += P_w
            if P_w < 1e-15: break
        formula_vals.append(zeta_s * G_s)
    
    direct_vals = np.array(direct_vals)
    formula_vals = np.array(formula_vals)
    
    # Left: F(s)
    ax1.plot(s_range, direct_vals, color=GOLD, linewidth=2, label='Direct sum')
    ax1.plot(s_range, formula_vals, color=TEAL, linewidth=2, linestyle='--', label=r'$\zeta(s)\cdot G(s)$')
    ax1.axvline(1, color=CORAL, linewidth=1, linestyle=':', alpha=0.5, label='Pole at $s=1$')
    ax1.set_xlabel(r'$s$')
    ax1.set_ylabel(r'$F(s)$')
    ax1.legend(loc='upper right', framealpha=0.9)
    ax1.grid(True, alpha=0.3)
    ax1.set_title(r'Dirichlet Series $F(s) = \sum \frac{\ell(n)}{n^s}$', fontsize=12, color=GOLD)
    ax1.set_ylim(0, 8)
    
    # Right: Relative error
    rel_err = np.abs(direct_vals - formula_vals) / np.maximum(np.abs(direct_vals), 1e-15)
    ax2.semilogy(s_range, rel_err + 1e-16, color=CORAL, linewidth=1.5)
    ax2.set_xlabel(r'$s$')
    ax2.set_ylabel('Relative error')
    ax2.grid(True, alpha=0.3)
    ax2.set_title('Verification: Direct vs Formula', fontsize=12, color=GOLD)
    ax2.set_ylim(1e-12, 1e-1)
    
    fig.tight_layout()
    fig.savefig('/home/claude/figs/05_dirichlet.png')
    plt.close()
    print("Figure 5 done.")

fig_dirichlet()

# ═══════════════════════════════════════════════════════
# FIGURE 6: One-sided bound — zoomed
# ═══════════════════════════════════════════════════════

def fig_onesided_zoom():
    fig, ax = plt.subplots(figsize=(12, 4.5))
    
    N_range = np.arange(2, 1001)
    E_vals = np.array([S_vals[int(N)] - C * N for N in N_range])
    
    ax.fill_between(N_range, E_vals, 0, color=CORAL, alpha=0.2)
    ax.plot(N_range, E_vals, color=CORAL, linewidth=1.2, zorder=3)
    ax.axhline(0, color=TEAL, linewidth=1.5, linestyle='-', zorder=4)
    
    # Mark special points
    for k in range(2, 10):
        N = 2**k - 1
        if N <= 1000:
            E = S_vals[N] - C * N
            ax.plot(N, E, 'o', color=GOLD, markersize=6, zorder=5)
            ax.annotate(f'$2^{{{k}}}-1$', (N, E), textcoords='offset points',
                       xytext=(6, 8), fontsize=8, color=GOLD)
    
    ax.set_xlabel(r'$N$')
    ax.set_ylabel(r'$E(N) = S(N) - \mathcal{C}N$')
    ax.grid(True, alpha=0.3)
    ax.set_title(r'One-Sided Bound: $E(N) < 0$ for all $N \geq 2$  (gold = binary repunits $2^k - 1$)',
                 fontsize=12, color=GOLD, pad=10)
    ax.set_xlim(2, 1000)
    
    # Add annotation
    ax.text(500, min(E_vals) * 0.3,
            r'$E(N) = -\sum_p \frac{s_p(N)}{p(p-1)} + O(1/\!\log N)$',
            fontsize=13, color=TEXT, ha='center',
            bbox=dict(boxstyle='round,pad=0.4', facecolor=BG2, edgecolor=GREY, alpha=0.9))
    
    fig.savefig('/home/claude/figs/06_onesided.png')
    plt.close()
    print("Figure 6 done.")

fig_onesided_zoom()

# ═══════════════════════════════════════════════════════
# FIGURE 7: Convolution identity visualization
# ═══════════════════════════════════════════════════════

def fig_convolution():
    fig, ax = plt.subplots(figsize=(12, 5))
    
    ns = list(range(2, 61))
    
    # For each n, decompose ell(n) = sum_{d|n} Lambda*(d)
    # Color by the prime p that Lambda* hits
    prime_colors = {2: CORAL, 3: GOLD, 5: TEAL, 7: BLUE, 11: PURPLE,
                    13: '#d070a0', 17: '#70d0a0', 19: '#a0a0d0', 23: '#d0d070',
                    29: '#70a0d0', 31: '#d0a070', 37: '#a070d0', 41: '#70d070',
                    43: '#d07070', 47: '#7070d0', 53: '#d0d0a0', 59: '#a0d0d0'}
    
    for n in ns:
        f = factorize(n, spf)
        bottom = 0
        for p in sorted(f.keys()):
            a = f[p]
            contrib = a / p
            color = prime_colors.get(p, GREY)
            ax.bar(n, contrib, bottom=bottom, width=0.7, color=color, edgecolor='none', alpha=0.8)
            bottom += contrib
    
    # Legend for first few primes
    from matplotlib.patches import Patch
    legend_elements = [Patch(facecolor=prime_colors[p], label=f'$\\Lambda_\\star(p^k) = 1/{p}$  [$p={p}$]')
                       for p in [2, 3, 5, 7, 11, 13]]
    ax.legend(handles=legend_elements, loc='upper left', framealpha=0.9, ncol=2)
    
    ax.axhline(C, color='white', linewidth=1, linestyle='--', alpha=0.4)
    ax.set_xlabel(r'$n$')
    ax.set_ylabel(r'$\ell(n) = \sum_{d \mid n} \Lambda_\star(d)$')
    ax.set_xlim(1, 61)
    ax.grid(True, alpha=0.2, axis='y')
    ax.set_title(r'Convolution Decomposition: $D(n)/n = \sum_{d \mid n} \Lambda_\star(d)$',
                 fontsize=13, color=GOLD, pad=10)
    
    fig.savefig('/home/claude/figs/07_convolution.png')
    plt.close()
    print("Figure 7 done.")

fig_convolution()

# ═══════════════════════════════════════════════════════
# FIGURE 8: Banner / equation card
# ═══════════════════════════════════════════════════════

def fig_banner():
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis('off')
    fig.patch.set_facecolor(BG)
    
    # Title
    ax.text(0.5, 0.82, 'The Summatory Arithmetic Derivative', fontsize=26, ha='center', va='center',
            color=GOLD, fontweight='bold', family='serif')
    ax.text(0.5, 0.65, "Legendre's Formula and a One-Sided Asymptotic Bound", fontsize=15, ha='center',
            va='center', color=TEXT_DIM, style='italic', family='serif')
    
    # Equations
    ax.text(0.18, 0.35,
            r'$\sum_{n=1}^{N} \frac{D(n)}{n} = \sum_{p} \frac{v_p(N!)}{p}$',
            fontsize=20, ha='center', va='center', color=TEXT,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG2, edgecolor=GREY, alpha=0.8))
    
    ax.text(0.50, 0.35,
            r'$S(N) \;<\; \mathcal{C}\,N$',
            fontsize=20, ha='center', va='center', color=CORAL,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG2, edgecolor=GREY, alpha=0.8))
    
    ax.text(0.82, 0.35,
            r'$F(s) = \zeta(s)\!\sum_{j\geq 1} P(js\!+\!1)$',
            fontsize=20, ha='center', va='center', color=TEAL,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=BG2, edgecolor=GREY, alpha=0.8))
    
    # Subtitle
    ax.text(0.5, 0.08, 'Five novel theorems connecting the arithmetic derivative to Legendre, Dirichlet, and digit sums',
            fontsize=11, ha='center', va='center', color=TEXT_DIM, family='serif')
    
    # Decorative line
    ax.plot([0.1, 0.9], [0.55, 0.55], color=GOLD, linewidth=0.8, alpha=0.4)
    ax.plot([0.1, 0.9], [0.20, 0.20], color=GOLD, linewidth=0.8, alpha=0.4)
    
    fig.savefig('/home/claude/figs/00_banner.png')
    plt.close()
    print("Banner done.")

fig_banner()

# ═══════════════════════════════════════════════════════
# FIGURE 9: Variance convergence
# ═══════════════════════════════════════════════════════

def fig_variance():
    fig, ax = plt.subplots(figsize=(10, 4.5))
    
    var_theory = sum(1.0 / (p * (p - 1)**2) for p in primes_big)
    
    # Compute empirical variance at increasing N
    checkpoints = list(range(100, N_MAX + 1, 200))
    emp_vars = []
    
    running_sum = 0.0
    running_sum2 = 0.0
    n = 1
    cp_idx = 0
    
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
               label=r'$\sum_p \frac{1}{p(p-1)^2} \approx ' + f'{var_theory:.4f}$', zorder=4)
    
    ax.set_xlabel(r'$N$')
    ax.set_ylabel(r'$\frac{1}{N}\sum_{n \leq N}(\ell(n) - \mathcal{C})^2$')
    ax.legend(loc='upper right', framealpha=0.9)
    ax.grid(True, alpha=0.3)
    ax.set_title(r'Convergence of the Empirical Variance to $\sum_p \frac{1}{p(p-1)^2}$',
                 fontsize=13, color=GOLD, pad=10)
    ax.set_xlim(0, N_MAX)
    
    fig.savefig('/home/claude/figs/08_variance.png')
    plt.close()
    print("Figure 8 (variance) done.")

fig_variance()

print("\nAll figures generated!")
