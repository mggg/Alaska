#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 28 08:20:06 2019

@author: ddeford


        if A.sum()/2 > maxe:
            maxea = dict(c_part.assignment)
            maxeA = A[:]
            maxen = t
            maxe = A.sum()/2

        if (A.sum()/2) < mine:
            minea = dict(c_part.assignment)
            mineA = A[:]
            minen = t
            mine = A.sum()/2

        if round(ans) > maxm:
            maxma = dict(c_part.assignment)
            maxmA = A[:]
            maxmn = t
            maxm = round(ans)

            
        if round(ans) < minm  and round(ans) !=0:
            minma = dict(c_part.assignment)
            minmA = A[:]
            minmn = t
            minm = round(ans)

        if round(ans) == 0:
            zerom = dict(c_part.assignment)
            zeroA = A[:]
            zerot = t
            zeroe = A.sum()/2


        
        if t%1000 == 0:
            print(types[z],"chain ",t," steps")
        t+=1
        
    print("Finished ", types[z], " Ensemble")

    with open("./Outputs/Ensemble_"+types[z]+"_extremes.json",'w') as wf:
        json.dump({0:maxea,1:maxeA.tolist(),2:maxen,3:maxe,4:minea,5:mineA.tolist(),6:minen,7:mine,
8:maxma,9:maxmA.tolist(),10:maxmn,11:maxm,12:minma,13:minmA.tolist(),14:minmn,15:minm,16:zerom,
17:zeroA.tolist(),18:zerot,19:zeroe}, wf)
    
    
"""

import json
import networkx as nx
import seaborn as sns
import numpy as np
from FKT import FKT
from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.constraints.validity import within_percent_of_ideal_population
from enum_matchings import enumerate_matchings
import geopandas as gpd

df = gpd.read_file("./data/AK_precincts_ns/AK_precincts_ns/AK_precincts_ns.shp")
df["nAMIN"] = df["TOTPOP"]-df["AMIN"]
elections = [
    Election("GOV18x", {"Democratic": "GOV18D_x", "Republican": "GOV18R_x"}),
    Election("USH18x", {"Democratic": "USH18D_x", "Republican": "USH18R_x"}),
    Election("GOV18ns", {"Democratic": "GOV18D_NS", "Republican": "GOV18R_NS"}),
    Election("USH18ns", {"Democratic": "USH18D_NS", "Republican": "USH18R_NS"}),
    Election("Native_percent", {"Native":"AMIN", "nonNative":"nAMIN"})
]

my_updaters = {"population": updaters.Tally("POPULATION", alias="population")}

election_updaters = {election.name: election for election in elections}
my_updaters.update(election_updaters)


with open('./Outputs/Ensemble_Permissive_extremes.json') as json_file:  
    data = json.load(json_file)
    
    
G_loose = Graph.from_file("./data/AK_precincts_ns/AK_precincts_ns/AK_precincts_ns.shp")
G_loose.join(df,columns= ["nAMIN"])

idict={}

for index, row in df.iterrows():

	idict[int(row["ID"])] = index
	
#Attach Islands	
to_add2 = [(426,444), (437,438), (437,436), (437,423), (437,428), (437,432), (437,374), (437,441), 
(437,443), (437,439), (437,427), (437,430), (437,445), (437,435), (437,434), (437,442), (411,420),
(411,414), (411,358),(411,407), (399,400),(399,349),(381,384),(240,210), (400,411), (399,348),
(399,381),(399,384),(399,386),(399,397)]

for i in range(len(to_add2)):
	G_loose.add_edge(idict[to_add2[i][0]],idict[to_add2[i][1]])
	G_loose[idict[to_add2[i][0]]][idict[to_add2[i][1]]]["shared_perim"]=1

nd ={int(x):data['0'][x] for x in data['0'].keys()}

initial_max = GeographicPartition(G_loose, assignment=nd, updaters=my_updaters)

nd ={int(x):data['4'][x] for x in data['4'].keys()}


initial_min = GeographicPartition(G_loose, assignment=nd, updaters=my_updaters)



vs = list(range(1, 41))


matchings_max = enumerate_matchings(np.array(data['1']), vs)

vs = list(range(1, 41))

matchings_min = enumerate_matchings(np.array(data['5']), vs)

vs = list(range(1, 41))
MminM =  enumerate_matchings(np.array(data['13']), vs)


types = ["MinM","MaxE","MinE"]
ms = [MminM, matchings_max, matchings_min]
gs = [ G_loose,G_loose, G_loose]
dfcols=["minM","max","min"]

nd ={int(x):data['12'][x] for x in data['12'].keys()}

df["minM"]=df.index.map(nd)



nd ={int(x):data['0'][x] for x in data['0'].keys()}

df["max"]=df.index.map(nd)
nd ={int(x):data['4'][x] for x in data['4'].keys()}

df["min"]=df.index.map(nd)
for z in range(3):
    
    matchings = ms[z]
    G = gs[z]
    
    
    print("Computing Stats on", types[z])

    percents1 = []
    wins1 = []
    percents2 = []
    wins2 = []
    percents3 = []
    wins3 = []
    percents4 = []
    wins4 = []
    percents5= []
    wins5 =[]
    
    
    for i in range(len(matchings)):
        temp= {x: 0 for x in range(40)}
        for j in range(20):
            for k in [0,1]:
                temp[matchings[i][j][k]]=j#[matchings[str(i)][j][k]-1]=j
        df["MERGEDIST"] = df[dfcols[z]].map(temp)
        G.join(df,columns= ["MERGEDIST"])
        c_part = GeographicPartition(G, assignment="MERGEDIST", updaters= my_updaters)
        wins1.append(c_part["GOV18x"].wins("Democratic"))
        percents1.append(sorted(c_part["GOV18x"].percents("Democratic")))
        wins2.append(c_part["GOV18ns"].wins("Democratic"))
        percents2.append(sorted(c_part["GOV18ns"].percents("Democratic")))
        wins3.append(c_part["USH18x"].wins("Democratic"))
        percents3.append(sorted(c_part["USH18x"].percents("Democratic")))
        wins4.append(c_part["USH18ns"].wins("Democratic"))
        percents4.append(sorted(c_part["USH18ns"].percents("Democratic")))
        wins5.append(c_part["Native_percent"].wins("Native"))
        percents5.append(sorted(c_part["Native_percent"].percents("Native")))
        
        
        
        
    with open("./Outputs/Extreme_Matchings_"+types[z]+"_stats.json",'w') as wf:
        json.dump({0:wins1,1:percents1,2:wins2,3:percents2,4:wins3,5:percents3,
                   6:wins4,7:percents4,8:wins5,9:percents5}, wf)
    
    print("wrote ",types[z]," stats to file")
    
    
    print("Plotting ", types[z], " figures")
    






    
