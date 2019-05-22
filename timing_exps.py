#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:14:55 2019

@author: ddeford
"""

import time
from FKT import FKT
from uniform_matching import uniform_matching
import networkx as nx
import numpy as np
import math
import matplotlib.pyplot as plt


start_time = time.time()

G=nx.grid_graph([10,10])

print(len(G.edges()))

Adj = (nx.adjacency_matrix(G)).todense()

ans = np.matrix(FKT(Adj))
print(ans)


print(time.time()-start_time)

start_time = time.time()

G=nx.grid_graph([10,10])
G.add_edge((0,0),(1,1))

G.add_edge((8,8),(9,9))

G.add_edge((0,9),(1,8))

G.add_edge((9,0),(8,1))



print(len(G.edges()))

Adj = (nx.adjacency_matrix(G)).todense()

ans = np.matrix(FKT(Adj))
print(ans)


print(time.time()-start_time)


start_time = time.time()

G=nx.grid_graph([5,8])
print(len(G.edges()))

Adj = (nx.adjacency_matrix(G)).todense()

ans = np.matrix(FKT(Adj))
print(math.sqrt(np.linalg.det(ans)))


print(time.time()-start_time)

start_time = time.time()

G=nx.grid_graph([2,20])
print(len(G.edges()))


Adj = (nx.adjacency_matrix(G)).todense()

ans = np.matrix(FKT(Adj))
print(math.sqrt(np.linalg.det(ans)))


print(time.time()-start_time)

#fnlsdnldn


#################################
#State Examples
states = [
        "Alaska",
        "Iowa",
        "Montana",
        #"Ohio",
        #"Wisconsin",
        "Illinois",
        "Minnesota",
        "Nevada",
        "Oregon",
        "Wyoming",
    ]


#math.sqrt(np.linalg.det(FKT(Adj)))
for state in states:
    start_time = time.time()


    Adj = np.loadtxt(f"./data/graphs/{state}.csv")
    print(state)
    #print(FKT(Adj))
    #m=Matrix(FKT(Adj))
    #ex = m#.applyfunc(lambda x:N(x, 100))
    #print(ex.det())
    #math.sqrt(np.linalg.det(FKT(Adj)))
    ans = round(FKT(Adj))
    #np.savetxt(f"./graphs/skew_{state}.csv",ans , fmt="%1i")
    print(ans)
    #ans= math.sqrt(np.linalg.det(ans))
    print(state)
   
    plt.figure()
   
    g= nx.Graph(np.matrix(Adj))
    nx.draw_kamada_kawai(g,node_size=800,node_color=['w' for x in g.nodes()],width=4)
    pos =nx.kamada_kawai_layout(g)
    nx.draw_networkx_labels(g,pos,font_color='blue',font_size=20)
    
    
    
    #plt.savefig(f"./plots/planar_{state}.png")
    #plt.close()
   
   
   


    print(time.time()-start_time)
    
    
    start_time = time.time()

    m = uniform_matching(g)
    print(time.time()-start_time, " seconds for a uniform matching")
    
    

aknncs

"""
Alaska
108764.99999999993
'108765'
Alaska
0.03989243507385254

Iowa
1494354140510.9883
'1494354140511'
Iowa
0.3131136894226074

Montana
11629786967358.035
'11629786967358'
Montana
0.3670632839202881

Illinois
9380573911.123652
'9380573911'
Illinois
0.584395170211792

Minnesota
6.156723718225525e+18
'6,156,723,718,225,577,984'
Minnesota
0.8148200511932373

Nevada
313698.0000000005
313698
Nevada
0.0658257007598877

Oregon
229968612.9999996
229968613
Oregon
0.13962531089782715

Wyoming
920863.9999999942
920864
Wyoming
0.10472416877746582
"""


#kjjdnvklasnvdkajdsv
###################ACTUAL RUNS
start_time = time.time()

G=nx.grid_graph([10,10])

Adj = (nx.adjacency_matrix(G)).todense()

print(FKT(Adj))


print(time.time()-start_time)

