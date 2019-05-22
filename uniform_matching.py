#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 22 16:20:12 2019

@author: ddeford
"""

from FKT import *
import networkx as nx #Requires at least networkx 2.3+
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import time


def select_edge_clean(H,slow=True):

    G2=H.copy()
    
    ccs = list((G2.subgraph(c) for c in nx.connected_components(G2)))
    
    edges=[]
    adds2 = [[None,0]]
    rsum=0    
    for cc in ccs:
        
        
        G=cc.copy()
        
        
        if len(list(G.nodes())) == 1:
           break
        
        match_all = FKT((nx.adjacency_matrix(G)).todense())
        
        if match_all == 0:
            break
    
        elist = list(G.edges())

        
        temp=0

        for edge in elist:

            G.remove_nodes_from([edge[0],edge[1]])

            C=[G.subgraph(c) for c in nx.connected_components(G)]
            
           
            
            compprod = 1
            for comp in C:
                
                if len(list(comp.nodes())) %2 == 1:
                    compprod = 0

                else:
                    compprod = compprod * round(FKT((nx.adjacency_matrix(comp)).todense()))
                    
            if not C:
                rsum+= match_all
                adds2.append([edge,rsum])
                
            elif compprod > 0:
                rsum += compprod
                adds2.append([edge,rsum])          
                
                
            G=cc.copy()

    r = random.randint(1,rsum)


    
    for x in range(len(adds2)-1):
        if int(adds2[x+1][1])>=r and int(adds2[x][1]) < r:

            return adds2[x+1][0]
                          

        
def select_edge(H,slow=True):
    
    #print("new call")
    
    G2=H.copy()
    
    ccs = list((G2.subgraph(c) for c in nx.connected_components(G2)))
    
    #print(len(ccs))

    edges=[]
    adds2 = [[None,0]]
    rsum=0    
    for cc in ccs:
        
        
        G=cc.copy()
        
        
        if len(list(G.nodes())) == 1:
           break
        
        match_all = FKT((nx.adjacency_matrix(G)).todense())
        
        if match_all == 0:
            break
        
        #print("did all")
        

        

        
        elist = list(G.edges())
        #print(len(elist))
        
        temp=0

        for edge in elist:
            #G.remove_edge(edge[0],edge[1])
            G.remove_nodes_from([edge[0],edge[1]])
            #print("edge",edge)
            C=[G.subgraph(c) for c in nx.connected_components(G)]
            
           
            
            compprod = 1
            for comp in C:
                
                if len(list(comp.nodes())) %2 == 1:
                    compprod = 0
                    #break
                else:
                    check = FKT((nx.adjacency_matrix(comp)).todense())
                    if check is not None: #new from IA test
                        compprod = compprod * round(check)#FKT((nx.adjacency_matrix(comp)).todense()).
                    else: 
                        compprod = 0
                    
                   
            #if compprod == match_all:
            #    #edges.append(edge)
            #    rsum += compprod
            #    
            #    adds2.append([edge,rsum])
            #    
            #else:
            #
            #
            #   rsum += compprod
                
            #    adds2.append([edge,rsum])
            
            if not C:
                rsum+= match_all
                adds2.append([edge,rsum])
                
            elif compprod > 0:
                rsum += compprod
                adds2.append([edge,rsum])
            
            #print(edge,compprod)
    
                #for i in range(compprod):
                #    adds.append(edge)
                
            
            
            #print(adds)
            #probs.append(probs[-1]+compprod/match_all)
            #probs.append(probs[-1]+compprod)
            #G.add_edge(edge[0],edge[1])
            G=cc.copy()
    #print(adds2)            
    r = random.randint(1,rsum)

    #print("r",r)
    
    for x in range(len(adds2)-1):
        if int(adds2[x+1][1])>=r and int(adds2[x][1]) < r:
            #print(adds2[x+1])
            return adds2[x+1][0]
            #edges.append(adds2[x+1][0])
            #print(edge)
            #temp+=1
            #print(temp)
        #avlsdkn   
        #if adds:
            #toremove = random.choice(adds)
            #print(toremove)
        
        #edges.append(toremove)
        #edges.append(random.choice(adds))
    #print(edges)
        
    #return edges

"""        
    probs.pop(0)
    print(probs)
    
    #r = random.random()
    r = random.randint(0,rsum)
    print(r)
    
    for x in range(len(elist)):
        if probs[x]>r:
            
            return elist[x]
        
    
    return random.choice(elist)
"""       


def select_edge_leaves(H,slow=True):
    
    #print("new call")
    
    G2=H.copy()
    
    ccs = list((G2.subgraph(c) for c in nx.connected_components(G2)))
    
    #print(len(ccs))

    edges=[]
    adds2 = [[None,0]]
    rsum=0    
    for cc in ccs:
        
        
        G=cc.copy()
        
        
        if len(list(G.nodes())) == 1:
           break
        
        #match_all = FKT((nx.adjacency_matrix(G)).todense())
        
        #if match_all == 0:
        #    break
        
        #print("did all")
        

        

        
        elist = list(G.edges())
        #print(len(elist))
        
        temp=0

        for edge in elist:
            #G.remove_edge(edge[0],edge[1])
            G.remove_nodes_from([edge[0],edge[1]])
            #print("edge",edge)
            C=[G.subgraph(c) for c in nx.connected_components(G)]
            
           
            
            compprod = 1
            for comp in C:
                
                if len(list(comp.nodes())) %2 == 1:
                    compprod = 0
                    break
                else:
                    compprod = compprod * FKT((nx.adjacency_matrix(comp)).todense())
                    
                   
            #if compprod == match_all:
            #    #edges.append(edge)
            #    rsum += compprod
            #    
            #    adds2.append([edge,rsum])
            #    
            #else:
            #
            #
            #   rsum += compprod
                
            #    adds2.append([edge,rsum])
            
            if not C:
                #rsum+= match_all
                #adds2.append([edge,rsum])
                return(edge)
                
            #elif compprod == match_all:
            #    return(edge)
                
            elif compprod > 0:
                rsum += compprod
                adds2.append([edge,rsum])
            
            #print(edge,compprod)
    
                #for i in range(compprod):
                #    adds.append(edge)
                
            
            
            #print(adds)
            #probs.append(probs[-1]+compprod/match_all)
            #probs.append(probs[-1]+compprod)
            #G.add_edge(edge[0],edge[1])
            G=cc.copy()
    #print(adds2)            
    r = random.randint(1,math.ceil(rsum))
    #r=random.random()*rsum + 1

    #print("r",r)
    
    for x in range(len(adds2)-1):
        if adds2[x+1][1]>=r and adds2[x][1] < r:
            #print(adds2[x+1])
            return adds2[x+1][0]
     



def uniform_matching(H):
    
    g=H.copy()
    
    nlist = list(g.nodes())
    
    mlist=[]
    
    if len(nlist)%2 ==1:
        return []
    
    while len(nlist)>0:
                
        edge = select_edge(g)
        
        #for edge in edges:
        
        mlist.append(edge)
    
        #if edge[0] in nlist:
        nlist.remove(edge[0])
        g.remove_node(edge[0])
        #if edge[1] in nlist:
        
        nlist.remove(edge[1])


        g.remove_node(edge[1])
                
        
        
        
        #plt.figure()
        #nx.draw(H,pos={x:x for x in H.nodes()},node_color=['r' for x in H.nodes()])
        #nx.draw(g,pos={x:x for x in g.nodes()})
        #plt.show()
        
    
    return mlist
    
    
    
#FKT(nx.adjacency_matrix(nx.grid_graph([2,2])).todense())