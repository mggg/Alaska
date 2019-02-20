#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Jul  6 09:54:08 2018

@author: samirkhan

last updated 7/20/18 by @caranix
"""

#pruning function

import numpy as np
from scipy.sparse.csgraph import connected_components
import pysal as ps 
from copy import copy
import sys

#G = nx.Graph()

#toy example 1
#G.add_nodes_from(range(1,13))
#
#G.add_edges_from([(1,2), (2,3), (3,7), (3,8), (3,4), (4,8), (7,8), (8,9), (9,10), (10,11), (11,12),
#                  (11, 5), (5,6)])
#
#A = nx.adjacency_matrix(G).toarray()

#toy example 2

#G.add_nodes_from(range(1,11))
#G.add_edges_from([(1,3), (1,2), (1,7), (2,3), (2,4), (2,7), (3,4), (4,7), (7,6), 
#                  (7,5), (6,5), (5,8), (5,10), (8,9), (8,10), (9,10)])
#A = nx.adjacency_matrix(G).toarray()

#G.add_nodes_from(range(1,11))
#G.add_edges_from([(1,2), (1,10), (2,3), (2,9), (3,4), (3,8), (4,7), (4,5), (5,6), (6,7), (7,8), (8,9), (9,10)])
#A = nx.adjacency_matrix(G).toarray()

#A = np.loadtxt("ak_adj.csv", delimiter =",")
#vs = range(1, A.shape[0]+1)
#A = np.delete(A, (8, 23, 29, 20), axis = 0)
#A = np.delete(A, (8, 23, 29, 20), axis = 1)
#
#vs.remove(29)
#vs.remove(23)
#vs.remove(20)
#vs.remove(8)

#rW = ps.rook_from_shapefile("cb_2017_02_sldl_500k.shp")
#A = rW.full()[0] # View full contiguity matrix


def prune(A, vs):
    forced = []         
    
    degs = np.sum(A, axis = 0)
#    if 1 not in degs:
#        print "Nothing to prune!"
#    else:
#        print "Something to prune!"
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
            
        A = np.delete(A, (j, pair), axis = 0)
        A = np.delete(A, (j, pair), axis = 1)
        
        degs = np.sum(A, axis = 0)
        ones = degs == 1
                            
            
    return A, forced, vs

def check(A):
    comps = connected_components(A)[1]
    for j in range(np.max(comps)+1):
        count = np.sum(comps == j)
        if count%2 != 0:
#            print "A component had odd size"
            return False 
    
    return True 
        
    
def enumerate_matchings(A, vs, d = 0):   
    sys.stdout.write('\r' + "Recursion depth: %.0f" % d)
    if A.shape[0] == 0:  
        return [] 
    
    if not check(A):
        return [] 
    
        
    Ap, forced, vsp = prune(A, vs)
    
    if Ap.shape[0] == 0:
        return [forced]
    
    else:
        matchings = []        
        degs = np.sum(Ap, axis = 0)
        m = np.argmin(degs)
#        print "Min degree vertex: %.0f" % vsp[m]
        pairs = np.nonzero(Ap[m])[0]

#        print "Vertices"
#        print vsp
#        
#        print "Adjacency matrix"

        for pair in pairs:
#            print "Choosing vertex %.0f from" % vsp[pair]
#            print map(lambda x : vsp[x], pairs)
            vs2 = copy(vsp)
            
            current = (vs2[m], vs2[pair])
                
            if m > pair:
                vs2.remove(vs2[m])
                vs2.remove(vs2[pair])
            else:
                vs2.remove(vs2[pair])
                vs2.remove(vs2[m])
                
            A2 = np.delete(Ap, (m, pair), axis = 0)
            A2 = np.delete(A2, (m, pair), axis = 1)
            
            r = enumerate_matchings(A2, vs2, d = d+1)
            
            if len(r) == 0:
                continue 
            
            else:
                matchings += map(lambda x : [current] + x, r)
            
        return map(lambda x : forced + x, matchings)
                


rW = ps.rook_from_shapefile("cb_2017_30_sldl_500k.shp")
A = rW.full()[0] # View full contiguity matrix
vs = range(1, A.shape[0]+1)
#ms = enumerate_matchings(A, vs)

#with open("alaska_matchings.pkl", "wb") as f:
#    pickle.dump(ms, f)
            

#def make_matching(l):
#    return [l[i:i+2] for i in range(0, len(l)-1, 2)]
#        
#  
#def is_equal_p(p1, p2):
#    return p1 == p2 or p1 == tuple(reversed(p2))
#    
#def is_equal_m(m1, m2):
#    for p in m1:
#        tmp = map(lambda x : is_equal_p(x, p), m2)
#        if not np.all(tmp):
#            return False 
#    return True 
#   
#unmatched = []      
#with open("AKallpairings.csv") as f:
#    reader = csv.reader(f)
#    for row in tqdm(reader): 
#        matching = make_matching(row)
#        tmp = map(lambda x : is_equal_m(matching, x), ms) 
#        if not np.any(tmp):
#            unmatched.append(matching)
    
    
#labels = {0:"12", 1:"29", 2:"17", 3:"38", 4:"5", 5:"8", 6:"23", 7:"31", 8:"33", 9:"04", 10:"39",
#          11:"10", 12:"09", 13:"24", 14:"32", 15:"03", 16:"16", 17:"21", 18:"37", 19:"40", 20:"35",
#          21:"06", 22:"07", 23:"34", 24:"14", 25:"27", 26:"20", 27:"26", 28:"19", 29:"36", 30:"25",
#          31:"28", 32:"01", 33:"02", 34:"11", 35:"18", 36:"15", 37:"30", 38:"13", 39:"22"}                
#
#with open("neighbors.txt", "w") as f:            
#    for j in range(40):
#        f.write("The neighbors of %s are: " % labels[j])
#        neighbors = map(lambda x : labels[x], list(np.where(A[j] != 0)[0]))
#        for n in neighbors:
#            f.write(" %s " % n)
#        f.write("\n\n")
