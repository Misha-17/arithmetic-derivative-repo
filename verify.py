#!/usr/bin/env python3
"""
Computational verification of results in:
"The Summatory Arithmetic Derivative, Legendre's Formula, and a One-Sided Asymptotic Bound"
"""

import math
from collections import defaultdict

# ═══════════════════════════════════════════════════════
# Core number theory functions
# ═══════════════════════════════════════════════════════

def smallest_prime_factor(limit):
    """Sieve of Eratosthenes returning smallest prime factor for each n."""
    spf = list(range(limit + 1))
    for i in range(2, int(limit**0.5) + 1):
        if spf[i] == i:  # i is prime
            for j in range(i*i, limit + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf

def factorize(n, spf):
    """Return list of (prime, exponent) pairs."""
    factors = {}
    while n > 1:
        p = spf[n]
        e = 0
        while n % p == 0:
            n //= p
            e += 1
        factors[p] = e
    return factors

def arith_deriv_over_n(factors):
    """Compute D(n)/n = sum a_i/p_i from factorization."""
    return sum(a / p for p, a in factors.items())

def digit_sum(n, p):
    """Sum of digits of n in base p."""
    s = 0
    while n > 0:
        s += n % p
        n //= p
    return s

def v_p_factorial(N, p):
    """p-adic valuation of N! via Legendre's formula."""
    v = 0
    pk = p
    while pk <= N:
        v += N // pk
        pk *= p
    return v

def sieve_primes(limit):
    """Return list of primes up to limit."""
    is_prime = [True] * (limit + 1)
    is_prime[0] = is_prime[1] = False
    for i in range(2, int(limit**0.5) + 1):
        if is_prime[i]:
            for j in range(i*i, limit + 1, i):
                is_prime[j] = False
    return [i for i in range(2, limit + 1) if is_prime[i]]

# ═══════════════════════════════════════════════════════
# Verify Theorem 1: Legendre Identity
# ═══════════════════════════════════════════════════════

def verify_legendre_identity(N_max=10000):
    print("=" * 60)
    print("THEOREM 1: Legendre Identity Verification")
    print("  sum_{n<=N} D(n)/n  =  sum_p v_p(N!) / p")
    print("=" * 60)
    
    spf = smallest_prime_factor(N_max)
    primes = sieve_primes(N_max)
    
    # Compute cumulative sum of D(n)/n
    S = [0.0]  # S[0] = 0
    for n in range(1, N_max + 1):
        if n == 1:
            S.append(S[-1])
        else:
            f = factorize(n, spf)
            S.append(S[-1] + arith_deriv_over_n(f))
    
    # Verify at selected values
    test_values = [10, 50, 100, 500, 1000, 5000, 10000]
    max_err = 0
    for N in test_values:
        lhs = S[N]
        rhs = sum(v_p_factorial(N, p) / p for p in primes if p <= N)
        err = abs(lhs - rhs)
        max_err = max(max_err, err)
        print(f"  N={N:>6d}:  LHS={lhs:14.6f}  RHS={rhs:14.6f}  |diff|={err:.2e}")
    
    print(f"\n  Max absolute error: {max_err:.2e}")
    print(f"  IDENTITY {'VERIFIED' if max_err < 1e-8 else 'FAILED'}")
    return S

# ═══════════════════════════════════════════════════════
# Verify Theorem 2: One-Sided Bound
# ═══════════════════════════════════════════════════════

def verify_one_sided_bound(S, N_max=10000):
    print("\n" + "=" * 60)
    print("THEOREM 2: One-Sided Bound  S(N) < C*N  for all N >= 2")
    print("=" * 60)
    
    # Compute C = sum_p 1/(p(p-1))
    primes = sieve_primes(10**6)  # many primes for accurate constant
    C = sum(1.0 / (p * (p - 1)) for p in primes)
    C_tail = sum(1.0 / (p * (p - 1)) for p in primes if p > 10**5)
    print(f"\n  C = sum_p 1/(p(p-1)) = {C:.10f}")
    print(f"  (tail sum for p > 10^5: {C_tail:.2e})")
    
    # Check all N up to N_max
    violations = 0
    for N in range(2, min(N_max + 1, len(S))):
        if S[N] >= C * N:
            violations += 1
            print(f"  VIOLATION at N={N}: S(N)={S[N]:.6f}, CN={C*N:.6f}")
    
    print(f"\n  Checked N = 2 to {min(N_max, len(S)-1)}: {violations} violations")
    print(f"  ONE-SIDED BOUND {'VERIFIED' if violations == 0 else 'FAILED'}")
    
    # Print table from paper
    print("\n  Table of values (for paper):")
    print(f"  {'N':>8s}  {'S(N)':>14s}  {'C*N':>14s}  {'E(N)':>14s}  {'E(N)/ln(N)':>14s}")
    for N in [10, 100, 1000, 10000]:
        if N < len(S):
            E = S[N] - C * N
            ratio = E / math.log(N) if N > 1 else 0
            print(f"  {N:>8d}  {S[N]:>14.4f}  {C*N:>14.4f}  {E:>14.4f}  {ratio:>14.4f}")
    
    return C

# ═══════════════════════════════════════════════════════
# Verify exact error formula via digit sums
# ═══════════════════════════════════════════════════════

def verify_digit_sum_error(S, C, N_max=10000):
    print("\n" + "=" * 60)
    print("THEOREM 2 (cont): Exact Error  E(N) = -sum_p s_p(N)/(p(p-1)) + O(1/logN)")
    print("=" * 60)
    
    primes = sieve_primes(N_max)
    
    test_values = [10, 50, 100, 500, 1000, 5000, 10000]
    for N in test_values:
        if N >= len(S):
            break
        E_actual = S[N] - C * N
        # Digit sum formula (main term of error)
        E_digit = -sum(digit_sum(N, p) / (p * (p - 1)) for p in primes if p <= N)
        # Tail correction: N * sum_{p > N} 1/(p(p-1))
        all_primes = sieve_primes(max(N * 10, 10000))
        tail = -N * sum(1.0 / (p * (p - 1)) for p in all_primes if p > N)
        E_formula = E_digit + tail
        diff = abs(E_actual - E_formula)
        print(f"  N={N:>6d}:  E_actual={E_actual:>12.4f}  E_formula={E_formula:>12.4f}  |diff|={diff:.2e}")

# ═══════════════════════════════════════════════════════
# Verify Theorem 3: Dirichlet Series
# ═══════════════════════════════════════════════════════

def verify_dirichlet_series():
    print("\n" + "=" * 60)
    print("THEOREM 3: Dirichlet Series  F(s) = zeta(s) * sum_{j>=1} P(js+1)")
    print("=" * 60)
    
    primes = sieve_primes(10000)
    
    for s in [2.0, 3.0, 4.0, 5.0]:
        # Direct computation: sum_{n=1}^{N} ell(n) / n^s
        N_direct = 50000
        spf = smallest_prime_factor(N_direct)
        direct_sum = 0.0
        for n in range(2, N_direct + 1):
            f = factorize(n, spf)
            ell_n = arith_deriv_over_n(f)
            direct_sum += ell_n / (n ** s)
        
        # Formula: zeta(s) * sum_{j>=1} P(js+1)
        # Approximate zeta(s) via sum
        zeta_s = sum(1.0 / (n ** s) for n in range(1, N_direct + 1))
        # P(w) = sum_p p^{-w}
        G_s = 0.0
        for j in range(1, 100):
            w = j * s + 1
            P_w = sum(1.0 / (p ** w) for p in primes)
            G_s += P_w
            if P_w < 1e-15:
                break
        
        formula_val = zeta_s * G_s
        diff = abs(direct_sum - formula_val)
        print(f"  s={s:.0f}:  Direct={direct_sum:.10f}  Formula={formula_val:.10f}  |diff|={diff:.2e}")

# ═══════════════════════════════════════════════════════
# Verify Theorem 4: Second Moment and Variance
# ═══════════════════════════════════════════════════════

def verify_second_moment(N_max=100000):
    print("\n" + "=" * 60)
    print("THEOREM 4: Second Moment and Variance")
    print("=" * 60)
    
    primes = sieve_primes(10**6)
    
    # Compute theoretical variance = sum_p 1/(p(p-1)^2)
    var_theory = sum(1.0 / (p * (p - 1)**2) for p in primes)
    print(f"\n  Theoretical variance = sum_p 1/(p(p-1)^2) = {var_theory:.8f}")
    
    C = sum(1.0 / (p * (p - 1)) for p in primes)
    C2_theory = var_theory + C**2
    print(f"  C_2 = C^2 + var = {C2_theory:.8f}")
    
    # Empirical computation
    spf = smallest_prime_factor(N_max)
    sum1 = 0.0
    sum2 = 0.0
    for n in range(1, N_max + 1):
        if n == 1:
            ell = 0.0
        else:
            f = factorize(n, spf)
            ell = arith_deriv_over_n(f)
        sum1 += ell
        sum2 += ell ** 2
    
    emp_mean = sum1 / N_max
    emp_second = sum2 / N_max
    emp_var = emp_second - emp_mean**2
    
    print(f"\n  Empirical (N={N_max}):")
    print(f"    Mean:     {emp_mean:.8f}  (theory: {C:.8f})")
    print(f"    2nd mom:  {emp_second:.8f}  (theory: {C2_theory:.8f})")
    print(f"    Variance: {emp_var:.8f}  (theory: {var_theory:.8f})")
    print(f"    Rel err:  {abs(emp_var - var_theory)/var_theory:.6f}")

# ═══════════════════════════════════════════════════════
# Verify Theorem 5: Convolution Identity
# ═══════════════════════════════════════════════════════

def verify_convolution(N_max=1000):
    print("\n" + "=" * 60)
    print("THEOREM 5: Convolution  ell(n) = sum_{d|n} Lambda_star(d)")
    print("=" * 60)
    
    spf = smallest_prime_factor(N_max)
    
    # Precompute Lambda_star
    def lambda_star(n, spf_table):
        if n <= 1:
            return 0.0
        f = factorize(n, spf_table)
        if len(f) != 1:
            return 0.0  # not a prime power
        p, _ = list(f.items())[0]
        return 1.0 / p
    
    max_err = 0.0
    for n in range(2, N_max + 1):
        # Direct computation of ell(n)
        f = factorize(n, spf)
        ell_direct = arith_deriv_over_n(f)
        
        # Convolution: sum_{d|n} Lambda_star(d)
        ell_conv = 0.0
        for d in range(1, n + 1):
            if n % d == 0:
                ell_conv += lambda_star(d, spf)
        
        err = abs(ell_direct - ell_conv)
        max_err = max(max_err, err)
    
    print(f"  Checked n = 2 to {N_max}: max |error| = {max_err:.2e}")
    print(f"  CONVOLUTION IDENTITY {'VERIFIED' if max_err < 1e-10 else 'FAILED'}")

# ═══════════════════════════════════════════════════════
# Extended computation for the paper table
# ═══════════════════════════════════════════════════════

def compute_paper_table():
    print("\n" + "=" * 60)
    print("PAPER TABLE: Extended values for the manuscript")
    print("=" * 60)
    
    primes_big = sieve_primes(10**6)
    C = sum(1.0 / (p * (p - 1)) for p in primes_big)
    
    targets = [10, 100, 1000, 10000, 100000]
    max_N = max(targets)
    
    spf = smallest_prime_factor(max_N)
    S = 0.0
    results = {}
    
    for n in range(1, max_N + 1):
        if n == 1:
            pass
        else:
            f = factorize(n, spf)
            S += arith_deriv_over_n(f)
        if n in targets:
            results[n] = S
    
    print(f"\n  {'N':>8s}  {'S(N)':>14s}  {'C*N':>14s}  {'E(N)':>14s}  {'E(N)/ln(N)':>14s}")
    print("  " + "-" * 70)
    for N in targets:
        E = results[N] - C * N
        ratio = E / math.log(N)
        print(f"  {N:>8d}  {results[N]:>14.2f}  {C*N:>14.2f}  {E:>14.2f}  {ratio:>14.2f}")

# ═══════════════════════════════════════════════════════
# Extremal analysis
# ═══════════════════════════════════════════════════════

def verify_extremal():
    print("\n" + "=" * 60)
    print("PROPOSITION: Extremal behavior of E(N)")
    print("=" * 60)
    
    primes = sieve_primes(1000)
    C = sum(1.0 / (p * (p - 1)) for p in sieve_primes(10**6))
    spf = smallest_prime_factor(10000)
    
    # Check E(N) for N = 2^k - 1
    print("\n  Binary repunits N = 2^k - 1:")
    print(f"  {'k':>4s}  {'N':>8s}  {'|E(N)|':>12s}  {'k/2':>8s}  {'ratio':>8s}")
    for k in range(2, 14):
        N = 2**k - 1
        if N > 10000:
            break
        # Compute S(N) directly
        S = 0.0
        for n in range(2, N + 1):
            f = factorize(n, spf)
            S += arith_deriv_over_n(f)
        E = abs(S - C * N)
        print(f"  {k:>4d}  {N:>8d}  {E:>12.4f}  {k/2:>8.4f}  {E/(k/2):>8.4f}")
    
    # Check E(N) for prime powers N = p^k (should be small)
    print("\n  Prime powers N = p^k (expect smaller |E|):")
    for p in [2, 3, 5, 7]:
        for k in range(2, 8):
            N = p**k
            if N > 10000:
                break
            S = 0.0
            for n in range(2, N + 1):
                f = factorize(n, spf)
                S += arith_deriv_over_n(f)
            E = abs(S - C * N)
            print(f"  {p}^{k} = {N:>6d}:  |E(N)| = {E:>10.4f},  |E|/log(N) = {E/math.log(N):>8.4f}")

# ═══════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    print("COMPUTATIONAL VERIFICATION")
    print("The Summatory Arithmetic Derivative via Legendre's Formula")
    print("=" * 60)
    
    S = verify_legendre_identity(N_max=10000)
    C = verify_one_sided_bound(S, N_max=10000)
    verify_digit_sum_error(S, C, N_max=10000)
    verify_dirichlet_series()
    verify_second_moment(N_max=100000)
    verify_convolution(N_max=1000)
    compute_paper_table()
    verify_extremal()
    
    print("\n" + "=" * 60)
    print("ALL VERIFICATIONS COMPLETE")
    print("=" * 60)
