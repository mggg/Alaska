import matplotlib.pyplot as plt
import pandas as pd
import geopandas as gpd
import numpy as np
import seaborn as sns
import json
import networkx as nx
import time 

from gerrychain import Graph, Partition, Election
from gerrychain.updaters import Tally, cut_edges
from gerrychain import MarkovChain
from gerrychain.constraints import single_flip_contiguous
from gerrychain.proposals import propose_random_flip
from gerrychain.accept import always_accept
from gerrychain import (GeographicPartition, Partition, Graph, MarkovChain,
                        proposals, updaters, constraints, accept, Election)
from gerrychain.constraints.validity import within_percent_of_ideal_population

from gerrychain.proposals import recom
from functools import partial


from FKT import FKT

from enum_matchings import enumerate_matchings

whole_start = time.time()

#Initialization
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


GOV18x= sorted((0.4464612822647793, 0.38781079442086114, 0.44586334861383975, 0.21595373199476212, 0.2690041809198024, 0.2736756168359942, 0.348307220335269, 0.5071350164654226, 0.581616925879221, 0.6333762886597938, 0.5078282585726636, 0.4601878317680686, 0.4554883318928263, 0.4819267050672009, 0.28439815742038854, 0.45294296423867897, 0.5767558164818439, 0.47288220551378446, 0.7029333333333333, 0.6748514851485149))
GOV18ns= sorted((0.4676226754599207, 0.42829760031663167, 0.4618983956666181, 0.22362457290429352, 0.2824773413825426, 0.2879301987552867, 0.3599484378307593, 0.5278798697754102, 0.6099356805771895, 0.66089826955172, 0.5240823394928785, 0.47175060636977745, 0.47262266878310366, 0.4933236493835675, 0.29545454545662897, 0.49077875527620873, 0.6193197895384107, 0.48997864866716534, 0.6954798628970641, 0.6770289774619113))
USH18x= sorted((0.4580262736302467, 0.4109521943573668, 0.4420473773265651, 0.2635924932975871, 0.30460251046025105, 0.3053428317008014, 0.376907480525024, 0.5216595485051861, 0.5793047256925584, 0.6301691729323309, 0.5184593705965241, 0.4637579872204473, 0.4594340509542164, 0.4799281984334204, 0.32327166504381694, 0.4478700641898463, 0.6076680672268907, 0.4985154678670625, 0.5402944111776448, 0.48850713767239295))
USH18ns= sorted((0.4800036828504361, 0.4491738433709142, 0.461014997780927, 0.2711623081172799, 0.3193550626858298, 0.3179648181763695, 0.3841204106466343, 0.5379747100186753, 0.6065600063588037, 0.6535109734718672, 0.5346452384636674, 0.47764200355277736, 0.47761058520967536, 0.4967409579393119, 0.33186989293196734, 0.4811166025445444, 0.6403531762874495, 0.5091097061551921, 0.5376860497049738, 0.497248698656098))
Native= sorted((0.0962102413715317, 0.04433289150850278, 0.14142632701155874, 0.05763656319477669, 0.05454647697238936, 0.052279085539887526, 0.03625760649087221, 0.0856587180788094, 0.10959632719332624, 0.13024569330697544, 0.07415882701923891, 0.07839824279800625, 0.07406575511693854, 0.05113379963898917, 0.07531833439675979, 0.10261318242343542, 0.1146361499022746, 0.20748480349589624, 0.6321083614333886, 0.7516285714285714))

print("Loaded Data")

#Construct Dual Graphs

#Older Alaska (by hand)
Old_AK = np.matrix([
[0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,1,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,1,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,1,1,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,1,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,1,1],
[0,0,0,0,0,0,0,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,1,1,1,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0],
[0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,1,1,1,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,1,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,1,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,1,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,0,0,0,0,0,0,0,1,1,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,1,0,0,0,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,1,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0],
[0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,1,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0],
[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,1],
[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0]]
)

#Remove Mistaken Adjacency #Plus add the one that was probably a type miss?
Old_AK[16,25] = 0
Old_AK[25,16] = 0
Old_AK[22,24] = 1
Old_AK[24,22] = 1


#Tightest Alaska
print("Building Tight Graph")

G_tight = Graph.from_file("./data/AK_precincts_ns/AK_precincts_ns/AK_precincts_ns.shp")
G_tight.join(df,columns= ["nAMIN"])

idict={}

for index, row in df.iterrows():

	idict[int(row["ID"])] = index

#Connect Islands
to_add = [(426,444), (437,438),(437,442),(411,420),
(411,414), (411,358),(411,407),(399,400),(399,349),(381,384),(240,210)]
	

for i in range(len(to_add)):
	G_tight.add_edge(idict[to_add[i][0]],idict[to_add[i][1]])
	G_tight[idict[to_add[i][0]]][idict[to_add[i][1]]]["shared_perim"]=1

#Separate Anchorage
to_remove = [(210,195),(210,203),(210,202),(210,193),(210,235),(210,234),(169,78),(169,77),(169,70),
(169,68),(169,32),(169,23),(169,179),(234,78),(235,78),(235,89),(235,106),(235,102),(102,190),
(190,105),(190,145),(145,233),(233,133),(234,169),(234,151),(77,74),(77,70)]

for i in range(len(to_remove)):
    G_tight.remove_edge(idict[to_remove[i][0]],idict[to_remove[i][1]])
    

#Build restricted_partition    
initial_tight = GeographicPartition(G_tight, assignment="HDIST", updaters=my_updaters)


A_tight = np.zeros([40,40])

for edge in initial_tight["cut_edges"]:
    A_tight[initial_tight.assignment[edge[0]]-1,initial_tight.assignment[edge[1]]-1] = 1
    A_tight[initial_tight.assignment[edge[1]]-1,initial_tight.assignment[edge[0]]-1] = 1
    

smallest = nx.Graph(A_tight)
np.savetxt("./Outputs/tight_dual.csv",nx.adjacency_matrix(smallest).todense() , fmt="%1i")


print("Built Tight Graph")
print(smallest.number_of_edges(),"Edges")



    
#Restricted Alaska
print("Building Restrictive Graph")

G_restricted = Graph.from_file("./data/AK_precincts_ns/AK_precincts_ns/AK_precincts_ns.shp")
G_restricted.join(df,columns= ["nAMIN"])

idict={}

for index, row in df.iterrows():

	idict[int(row["ID"])] = index

#Connect Islands
to_add = [(426,444), (437,438),(437,442),(411,420),
(411,414), (411,358),(411,407),(399,400),(399,349),(381,384),(240,210)]
	

for i in range(len(to_add)):
	G_restricted.add_edge(idict[to_add[i][0]],idict[to_add[i][1]])
	G_restricted[idict[to_add[i][0]]][idict[to_add[i][1]]]["shared_perim"]=1

#Separate Anchorage
to_remove = [(210,195),(210,203),(210,202),(210,193),(210,235),(210,234),(169,78),(169,77),(169,70),
(169,68),(169,32),(169,23),(169,179),(234,78),(235,78),(235,89),(235,106),(235,102),(102,190),
(190,105),(190,145),(145,233),(233,133)]

for i in range(len(to_remove)):
    G_restricted.remove_edge(idict[to_remove[i][0]],idict[to_remove[i][1]])
    

#Build restricted_partition    
initial_restricted = GeographicPartition(G_restricted, assignment="HDIST", updaters=my_updaters)


A_restricted = np.zeros([40,40])

for edge in initial_restricted["cut_edges"]:
    A_restricted[initial_restricted.assignment[edge[0]]-1,initial_restricted.assignment[edge[1]]-1] = 1
    A_restricted[initial_restricted.assignment[edge[1]]-1,initial_restricted.assignment[edge[0]]-1] = 1
    

small = nx.Graph(A_restricted)
np.savetxt("./Outputs/small_dual.csv",nx.adjacency_matrix(small).todense() , fmt="%1i")


print("Built Restrictive Graph")
print(small.number_of_edges(),"Edges")

#Permissive Alaska

print("Building Permissive Graph")

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


initial_large = GeographicPartition(G_loose, assignment="HDIST", updaters=my_updaters)


A_loose = np.zeros([40,40])

for edge in initial_large["cut_edges"]:
    A_loose[initial_large.assignment[edge[0]]-1,initial_large.assignment[edge[1]]-1] = 1
    A_loose[initial_large.assignment[edge[1]]-1,initial_large.assignment[edge[0]]-1] = 1
    

large = nx.Graph(A_loose)
np.savetxt("./Outputs/large_dual.csv", nx.adjacency_matrix(large).todense() , fmt="%1i")

print("Built Permissive Graph")
print(large.number_of_edges(),"Edges")


#Check matrix compatibility
print("Checking Dual Graph Compatibility")

if (A_restricted[A_tight==1]==1).sum() == A_tight.sum():
    print("Tight nests in Restrictve!")
    
    
    
if (A_loose[A_restricted==1]==1).sum() == A_restricted.sum():
    print("Restrictve nests in Permissive!") 
    
    


#for i in range(40):
#    for j in range(40):
#        if Old_AK[i,j]==1:
#            if A_restricted[i,j]==0:
#                print(i,j)
            
            







#Compute matching numbers
print("Using FKT to enumerate matchings")
start = time.time() 
print("Tight Matchings: ", round(FKT(A_tight)), "in", time.time()-start,"seconds")

start = time.time() 
print("Restricted Matchings: ", round(FKT(A_restricted)), "in", time.time()-start,"seconds")

start = time.time() 
print("Permissive Matchings: ", round(FKT(A_loose)), "in", time.time()-start,"seconds")


#List all pairings
print("Generating All Matchings")

vs = list(range(1, 41))
start = time.time() 

matchings_tight = enumerate_matchings(A_tight, vs)
print("\n Tight Matchings: ", len(matchings_tight), "in", time.time()-start,"seconds")

#print(matchings)

with open("./Outputs/tight_matchings.json",'w') as wf:
    json.dump({x:matchings_tight[x] for x in range(len(matchings_tight))}, wf)


vs = list(range(1, 41))
start = time.time() 

matchings_small = enumerate_matchings(A_restricted, vs)
print("\n Restricted Matchings: ", len(matchings_small), "in", time.time()-start,"seconds")

#print(matchings)

with open("./Outputs/small_matchings.json",'w') as wf:
    json.dump({x:matchings_small[x] for x in range(len(matchings_small))}, wf)



vs = list(range(1, 41))
start = time.time() 

matchings_large = enumerate_matchings(A_loose, vs)
print("\n Permissive Matchings: ", len(matchings_large), "in", time.time()-start,"seconds")

#print(matchings)

with open("./Outputs/large_matchings.json",'w') as wf:
    json.dump({x:matchings_large[x] for x in range(len(matchings_large))}, wf)


#Verify proper labeling
print("Checking Dual Graph Edges Match Matchings")

check = 0 

tight_dual_edges = set([(initial_tight.assignment[edge[0]],initial_tight.assignment[edge[1]]) for edge in initial_tight["cut_edges"]])
for x in matchings_tight[0]:
    if (x[0],x[1]) in tight_dual_edges or (x[1],x[0]) in tight_dual_edges:
        check += 1

if check == 20:
    print("All tight matchings are allowed!")
    
check = 0 

restricted_dual_edges = set([(initial_restricted.assignment[edge[0]],initial_restricted.assignment[edge[1]]) for edge in initial_restricted["cut_edges"]])
for x in matchings_small[0]:
    if (x[0],x[1]) in restricted_dual_edges or (x[1],x[0]) in restricted_dual_edges:
        check += 1

if check == 20:
    print("All restricted matchings are allowed!")

check = 0 

loose_dual_edges = set([(initial_large.assignment[edge[0]],initial_large.assignment[edge[1]]) for edge in initial_large["cut_edges"]])
for x in matchings_large[0]:
    if (x[0],x[1]) in loose_dual_edges or (x[1],x[0]) in loose_dual_edges:
        check += 1

if check == 20:
    print("All permissive matchings are allowed!")
    
#Compute stats on matchings
    
types = ["Tight","Restricted","Permissive"]
ms = [matchings_tight, matchings_small, matchings_large]
gs = [G_tight, G_restricted, G_loose]
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
        df["MERGEDIST"] = df["HDIST"].map(temp)
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
        
        
        
        
    with open("./Outputs/"+types[z]+"_stats.json",'w') as wf:
        json.dump({0:wins1,1:percents1,2:wins2,3:percents2,4:wins3,5:percents3,
                   6:wins4,7:percents4,8:wins5,9:percents5}, wf)
    
    print("wrote ",types[z]," stats to file")
    
    
    print("Plotting ", types[z], " figures")
    
    
    partisan_w = [wins1,wins2,wins3,wins4]
    partisan_p = [percents1,percents2,percents3,percents4]
    p_types=["GOV18x", "GOV18ns", "USH18x", "USH18ns"]
    p_vecs=[GOV18x, GOV18ns, USH18x, USH18ns]

    c='black'
    
    for y in range(4):
        
    
        plt.figure()
        plt.boxplot(np.array(partisan_p[y]),whis=[0,100],showfliers=True, patch_artist=True,
                        boxprops=dict(facecolor="None", color=c),
                        capprops=dict(color=c),
                        whiskerprops=dict(color=c),
                        flierprops=dict(color=c, markeredgecolor=c),
                        medianprops=dict(color=c),
                        )
        
        plt.plot(range(1,21),p_vecs[y],'o',color='red',label='Current Plan')
        plt.plot([.5,21],[.5,.5],color='green',label="50%")
        plt.xlabel("Indexed Districts")
        plt.ylabel("Dem %")
        plt.legend()
        
        fig = plt.gcf()
        fig.set_size_inches((20,10), forward=False)
        fig.savefig("./Outputs/plots/Match_Box_"+ types[z] + p_types[y] + ".png")
        plt.close()
    
    
    
    plt.figure()
    plt.boxplot(np.array(percents5),whis=[0,100],showfliers=True, patch_artist=True,
                    boxprops=dict(facecolor="None", color=c),
                    capprops=dict(color=c),
                    whiskerprops=dict(color=c),
                    flierprops=dict(color=c, markeredgecolor=c),
                    medianprops=dict(color=c),
                    )
    
    plt.plot(range(1,21),Native,'o',color='red',label='Current Plan')
    plt.plot([.5,21],[.5,.5],color='green',label="50%")
    plt.xlabel("Indexed Districts")
    plt.ylabel("Native %")
    plt.legend()
    
    fig = plt.gcf()
    fig.set_size_inches((20,10), forward=False)
    fig.savefig("./Outputs/plots/Match_Box_"+ types[z] +"Native.png")
    plt.close()
    
    print("Finished ",types[z]," Box plots")
    
    for y in range(4):
        plt.figure()
        sns.distplot(partisan_w[y],kde=False,color='slateblue',bins=[x for x in range(4,13)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=sum([val>.5 for val in p_vecs[y]]),color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(partisan_w[y]),color='g',label="Matchings Mean",linewidth=5)
        plt.legend()
        print(p_types[y],"wins: ", np.mean(partisan_w[y]))
        plt.savefig("./Outputs/plots/Match_Hist_"+ types[z] + p_types[y] + ".png")
        plt.close()
        
        
    plt.figure()
    sns.distplot(wins5,kde=False,color='slateblue',bins=[x for x in range(8)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=2,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(wins5),color='g',label="Matchigs Mean",linewidth=5)
    plt.legend()
    print("Native wins: ", np.mean(wins5))
    plt.savefig("./Outputs/plots/Match_Hist_"+ types[z] + "Native.png")
    plt.close()
    
    
    print("Finished ",types[z]," Seats plots")
    
    
    
 
    for y in range(4):
        votes = partisan_p[y]
        comp = []
        
        for i in range(len(votes)):
            temp = 0
            for j in votes[i]:
                if .4 < j < .6:
                    temp+=1
            comp.append(temp)
        
        c_init = 0
        
        for x in p_vecs[y]:
            if .4 < x <.6:
                c_init += 1
                
        
        sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(6,16)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=c_init,color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
        print(p_types[y],"competitive: ",np.mean(comp))
        plt.legend()
        plt.savefig("./Outputs/plots/Match_Comp_"+ types[z] + p_types[y] + ".png")
        plt.close()

    
    votes = percents5
    comp = []
    
    for i in range(len(votes)):
        temp = 0
        for j in votes[i]:
            if .4 < j < .6:
                temp+=1
        comp.append(temp)
    
    sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(6)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=0,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
    print("Native competitive: ", np.mean(comp))
    plt.legend()
    plt.savefig("./Outputs/plots/Match_Comp_"+ types[z] + "Native.png")
    plt.close()
    
    print("Finished ",types[z]," Competitive plots")

    
print("All matchings reproduced in :", time.time()- whole_start, " seconds")    


print("Starting Ensemble Analysis")

ensemble_time = time.time()


ps = [initial_tight, initial_restricted, initial_large]

for z in range(3):
    
    
    initial_partition = ps[z]
    
    
    
    ideal_population = sum(initial_partition["population"].values()) / len(initial_partition)
    #print(ideal_population)
    
    proposal = partial(recom,
                       pop_col="POPULATION",
                       pop_target=ideal_population,
                       epsilon=0.05,
                       node_repeats=2
                      )
    
    
    compactness_bound = constraints.UpperBound(
        lambda p: len(p["cut_edges"]),
        2*len(initial_partition["cut_edges"])
    )
    
    chain = MarkovChain(
    proposal=proposal, 
    constraints=[
        constraints.within_percent_of_ideal_population(initial_partition, .05),
        compactness_bound, #single_flip_contiguous#no_more_discontiguous
    ],
    accept=accept.always_accept,
    initial_state=initial_partition,
    total_steps=10000
        )

    print("Started ", types[z], "chain")

    
    percents1 = []
    wins1 = []
    percents2 = []
    wins2 = []
    percents3 = []
    wins3 = []
    percents4 = []
    wins4 = []
    
    num_edges = []
    num_matchings = []
    
    wins5 = []
    percents5 = []
    
    t=0
    for c_part in chain:
        
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
        
        new_dg = nx.Graph()
        new_dg.add_edges_from(list({(c_part.assignment[x[0]],c_part.assignment[x[1]]) for x in c_part["cut_edges"]}) )
        A = nx.adjacency_matrix(new_dg).todense()
        
        num_edges.append(A.sum()/2)
        num_matchings.append(FKT(A))
        
        if t%1000 == 0:
            print(types[z],"chain ",t," steps")
        t+=1
        
    print("Finished ", types[z], " Ensemble")
    
    
    partisan_w = [wins1,wins2,wins3,wins4]
    partisan_p = [percents1,percents2,percents3,percents4]
    p_types=["GOV18x", "GOV18ns", "USH18x", "USH18ns"]
    p_vecs=[GOV18x, GOV18ns, USH18x, USH18ns]
    
    for y in range(4):
        
    
        plt.figure()
        plt.boxplot(np.array(partisan_p[y]),whis=[1,99],showfliers=False, patch_artist=True,
                        boxprops=dict(facecolor="None", color=c),
                        capprops=dict(color=c),
                        whiskerprops=dict(color=c),
                        flierprops=dict(color=c, markeredgecolor=c),
                        medianprops=dict(color=c),
                        )
        
        plt.plot(range(1,21),p_vecs[y],'o',color='red',label='Current Plan')
        plt.plot([.5,21],[.5,.5],color='green',label="50%")
        plt.xlabel("Indexed Districts")
        plt.ylabel("Dem %")
        plt.legend()
        
        fig = plt.gcf()
        fig.set_size_inches((20,10), forward=False)
        fig.savefig("./Outputs/plots/Ensemble_Box_"+ types[z] + p_types[y] + ".png")
        plt.close()
    
    
    
    plt.figure()
    plt.boxplot(np.array(percents5),whis=[1,99],showfliers=False, patch_artist=True,
                    boxprops=dict(facecolor="None", color=c),
                    capprops=dict(color=c),
                    whiskerprops=dict(color=c),
                    flierprops=dict(color=c, markeredgecolor=c),
                    medianprops=dict(color=c),
                    )
    
    plt.plot(range(1,21),Native,'o',color='red',label='Current Plan')
    plt.plot([.5,21],[.5,.5],color='green',label="50%")
    plt.xlabel("Indexed Districts")
    plt.ylabel("Native %")
    plt.legend()
    
    fig = plt.gcf()
    fig.set_size_inches((20,10), forward=False)
    fig.savefig("./Outputs/plots/Ensemble_Box_"+ types[z] +"Native.png")
    plt.close()
    
    print("Finished ",types[z]," Box plots")
    
    for y in range(4):
        plt.figure()
        sns.distplot(partisan_w[y],kde=False,color='slateblue',bins=[x for x in range(4,13)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=sum([val>.5 for val in p_vecs[y]]),color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(partisan_w[y]),color='g',label="Matchings Mean",linewidth=5)
        plt.legend()
        print(p_types[y],"wins: ", np.mean(partisan_w[y]))
        plt.savefig("./Outputs/plots/Ensemble_Hist_"+ types[z] + p_types[y] + ".png")
        plt.close()
        
        
    plt.figure()
    sns.distplot(wins5,kde=False,color='slateblue',bins=[x for x in range(8)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=2,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(wins5),color='g',label="Matchigs Mean",linewidth=5)
    plt.legend()
    print("Native wins: ", np.mean(wins5))
    plt.savefig("./Outputs/plots/Ensemble_Hist_"+ types[z] + "Native.png")
    plt.close()
    
    
    print("Finished ",types[z]," Seats plots")
    
    
    
 
    for y in range(4):
        votes = partisan_p[y]
        comp = []
        
        for i in range(len(votes)):
            temp = 0
            for j in votes[i]:
                if .4 < j < .6:
                    temp+=1
            comp.append(temp)
        
        c_init = 0
        
        for x in p_vecs[y]:
            if .4 < x <.6:
                c_init += 1
                
        
        sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(6,16)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=c_init,color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
        print(p_types[y],"competitive: ",np.mean(comp))
        plt.legend()
        plt.savefig("./Outputs/plots/Ensemble_Comp_"+ types[z] + p_types[y] + ".png")
        plt.close()

    
    votes = percents5
    comp = []
    
    for i in range(len(votes)):
        temp = 0
        for j in votes[i]:
            if .4 < j < .6:
                temp+=1
        comp.append(temp)
    
    sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(6)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=0,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
    print("Native competitive: ", np.mean(comp))
    plt.legend()
    plt.savefig("./Outputs/plots/Ensemble_Comp_"+ types[z] + "Native.png")
    plt.close()
    
    print("Finished ",types[z]," Competitive plots")

        

            
        
    
    

