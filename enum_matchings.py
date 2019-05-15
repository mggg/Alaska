#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 09:54:08 2018

@author: samirkhan

last updated 7/20/18 by @caranix
"""

import numpy as np
from scipy.sparse.csgraph import connected_components
import pysal as ps
from copy import copy
import sys


def prune(A, vs):
    forced = []

    degs = np.sum(A, axis=0)
    ones = degs == 1

    while np.any(ones):
        j = np.where(ones)[0][0]
        pair = np.nonzero(A[j])[0][0]

        forced.append((vs[j], vs[pair]))

        if j > pair:
            vs.pop(j)
            vs.pop(pair)
        else:
            vs.pop(pair)
            vs.pop(j)

        A = np.delete(A, (j, pair), axis=0)
        A = np.delete(A, (j, pair), axis=1)

        degs = np.sum(A, axis=0)
        ones = degs == 1

    return A, forced, vs


def check(A):
    comps = connected_components(A)[1]
    for j in range(np.max(comps) + 1):
        count = np.sum(comps == j)
        if count % 2 != 0:
            return False

    return True


def enumerate_matchings(A, vs, d=0):
    sys.stdout.write("\r" + "Recursion depth: %.0f" % d)
    if A.shape[0] == 0:
        return []

    if not check(A):
        return []

    Ap, forced, vsp = prune(A, vs)

    if Ap.shape[0] == 0:
        return [forced]

    else:
        matchings = []
        degs = np.sum(Ap, axis=0)
        m = np.argmin(degs)
        pairs = np.nonzero(Ap[m])[0]

        for pair in pairs:
            vs2 = copy(vsp)

            current = (vs2[m], vs2[pair])

            if m > pair:
                vs2.remove(vs2[m])
                vs2.remove(vs2[pair])
            else:
                vs2.remove(vs2[pair])
                vs2.remove(vs2[m])

            A2 = np.delete(Ap, (m, pair), axis=0)
            A2 = np.delete(A2, (m, pair), axis=1)

            r = enumerate_matchings(A2, vs2, d=d + 1)

            if len(r) == 0:
                continue

            else:
                matchings += [[current] + x for x in r]

        return [forced + x for x in matchings]


if __name__ == "__main__":
    rW = ps.rook_from_shapefile("cb_2017_30_sldl_500k.shp")
    A = rW.full()[0]
    vs = range(1, A.shape[0] + 1)
    matchings = enumerate_matchings(A, vs)
    print(matchings)
