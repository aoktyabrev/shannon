"""The upper bound side, to the precision the sources quote it at.

Lovasz's theta function on odd cycles, theta(C_n) = n cos(pi/n) / (1 + cos(pi/n))
[SOURCES.md PS19-2, MO17-2], evaluated with the `decimal` module at 50 digits --
cos by its Taylor series, pi by Chudnovsky -- so that the claims
"theta(C_7) < 3.3177" [PS19-3, MO17-2] and the table value 3.3176672 [BPZ26-3]
can be checked rather than repeated.  No external library is involved.
"""
import json
import os
from decimal import Decimal, getcontext

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
getcontext().prec = 60


def pi():
    """Chudnovsky; more than enough terms for 60 digits."""
    getcontext().prec += 10
    C = 426880 * Decimal(10005).sqrt()
    M, L, X, K, S = 1, 13591409, 1, 6, Decimal(13591409)
    for i in range(1, 25):
        M = M * (K ** 3 - 16 * K) // (i ** 3)
        L += 545140134
        X *= -262537412640768000
        S += Decimal(M * L) / X
        K += 12
    getcontext().prec -= 10
    return +(C / S)


def cos(x):
    getcontext().prec += 10
    i, fact, num, sign, s = 0, 1, Decimal(1), 1, Decimal(0)
    while True:
        term = sign * num / fact
        if abs(term) < Decimal(10) ** (-getcontext().prec):
            break
        s += term
        i += 2
        fact *= i * (i - 1)
        num *= x * x
        sign = -sign
    getcontext().prec -= 10
    return +s


def theta(n):
    c = cos(pi() / n)
    return +(n * c / (1 + c))


def main():
    rep = {"formula": "theta(C_n) = n cos(pi/n) / (1 + cos(pi/n))  [SOURCES.md PS19-2, MO17-2]",
           "precision_digits": 50, "values": {}}
    for n in (5, 7, 9, 11, 13, 15):
        rep["values"][str(n)] = str(theta(n))[:40]
    t7 = theta(7)
    rep["checks"] = {
        "theta_C7_lt_3.3177 [PS19-3, MO17-2]": bool(t7 < Decimal("3.3177")),
        "theta_C7_rounds_to_3.3176672 [BPZ26-3]": str(t7)[:9] == "3.3176672",
        "theta_C5_is_sqrt5": str(t7)[:1] == "3" and str(theta(5))[:15] == str(Decimal(5).sqrt())[:15],
        "theta_C9_lt_4.3601 [MO17-2]": bool(theta(9) < Decimal("4.3601")),
        "theta_C11_lt_5.3864 [MO17-2]": bool(theta(11) < Decimal("5.3864")),
        "theta_C13_lt_6.4042 [MO17-2]": bool(theta(13) < Decimal("6.4042")),
        "theta_C15_lt_7.4172 [MO17-2]": bool(theta(15) < Decimal("7.4172")),
    }
    rep["all_pass"] = all(rep["checks"].values())
    with open(os.path.join(ROOT, "results", "json", "theta.json"), "w") as f:
        json.dump(rep, f, indent=2)
    print(json.dumps(rep, indent=2))


if __name__ == "__main__":
    main()
