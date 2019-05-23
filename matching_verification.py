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


GOV18x= sorted((0.4464612822647793, 0.38781079442086114, 0.44586334861383975,
                0.21595373199476212, 0.2690041809198024, 0.2736756168359942, 
                0.348307220335269, 0.5071350164654226, 0.581616925879221, 
                0.6333762886597938, 0.5078282585726636, 0.4601878317680686, 
                0.4554883318928263, 0.4819267050672009, 0.28439815742038854, 
                0.45294296423867897, 0.5767558164818439, 0.47288220551378446, 
                0.7029333333333333, 0.6748514851485149))
GOV18ns= sorted((0.4676226754599207, 0.42829760031663167, 0.4618983956666181, 
                 0.22362457290429352, 0.2824773413825426, 0.2879301987552867,
                 0.3599484378307593, 0.5278798697754102, 0.6099356805771895, 
                 0.66089826955172, 0.5240823394928785, 0.47175060636977745, 
                 0.47262266878310366, 0.4933236493835675, 0.29545454545662897,
                 0.49077875527620873, 0.6193197895384107, 0.48997864866716534,
                 0.6954798628970641, 0.6770289774619113))
USH18x= sorted((0.4580262736302467, 0.4109521943573668, 0.4420473773265651, 
                0.2635924932975871, 0.30460251046025105, 0.3053428317008014,
                0.376907480525024, 0.5216595485051861, 0.5793047256925584, 
                0.6301691729323309, 0.5184593705965241, 0.4637579872204473, 
                0.4594340509542164, 0.4799281984334204, 0.32327166504381694, 
                0.4478700641898463, 0.6076680672268907, 0.4985154678670625, 
                0.5402944111776448, 0.48850713767239295))
USH18ns= sorted((0.4800036828504361, 0.4491738433709142, 0.461014997780927, 
                 0.2711623081172799, 0.3193550626858298, 0.3179648181763695, 
                 0.3841204106466343, 0.5379747100186753, 0.6065600063588037,
                 0.6535109734718672, 0.5346452384636674, 0.47764200355277736,
                 0.47761058520967536, 0.4967409579393119, 0.33186989293196734,
                 0.4811166025445444, 0.6403531762874495, 0.5091097061551921,
                 0.5376860497049738, 0.497248698656098))
Native= sorted((0.0962102413715317, 0.04433289150850278, 0.14142632701155874, 
                0.05763656319477669, 0.05454647697238936, 0.052279085539887526,
                0.03625760649087221, 0.0856587180788094, 0.10959632719332624, 
                0.13024569330697544, 0.07415882701923891, 0.07839824279800625,
                0.07406575511693854, 0.05113379963898917, 0.07531833439675979, 
                0.10261318242343542, 0.1146361499022746, 0.20748480349589624, 
                0.6321083614333886, 0.7516285714285714))

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
        
        
        
        
    with open("./Outputs/Matchings_"+types[z]+"_stats.json",'w') as wf:
        json.dump({0:wins1,1:percents1,2:wins2,3:percents2,4:wins3,5:percents3,
                   6:wins4,7:percents4,8:wins5,9:percents5}, wf)
    
    print("wrote ",types[z]," stats to file")
    
    
    print("Plotting ", types[z], " figures")
    
    
    partisan_w = [wins1,wins2,wins3,wins4]
    partisan_p = [percents1,percents2,percents3,percents4]
    p_types=["GOV18N", "GOV18A", "USH18N", "USH18A"]
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
        plt.xlabel("Sorted Districts")
        plt.ylabel("Dem %")
        plt.xticks([1,10,20],['1','10','20'])
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
    plt.xlabel("Sorted Districts")
    plt.ylabel("Native %")
    plt.xticks([1,10,20],['1','10','20'])

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
    sns.distplot(wins5,kde=False,color='slateblue',bins=[x for x in range(5)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=2,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(wins5),color='g',label="Matchigs Mean",linewidth=5)
    plt.legend()
    print("Native wins: ", np.mean(wins5))
    plt.savefig("./Outputs/plots/Match_Hist_"+ types[z] + "Native.png")
    plt.close()
    
    
    with open("./Outputs/values/Matchings_" + types[z] + ".txt", "w") as f:
        f.write("Matching Values for Graph: "+types[z]+" \n\n")
    
        for y in range(4):
            
            
            f.write("Enacted Wins : "+ p_types[y] + ": "+ str(sum([val>.5 for val in p_vecs[y]])))
            f.write("\n")
            f.write("Matching Average Wins : "+ p_types[y] + ": "+ str(np.mean(partisan_w[y])))
            f.write("\n")
            f.write("\n")
    
    
    print("Finished ",types[z]," Seats plots")
    
    
    
    cis=[] 
    ces=[]
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
                
                
        cis.append(c_init)
                
        
        sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(6,20)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=c_init,color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
        print(p_types[y],"competitive: ",np.mean(comp))
        plt.legend()
        plt.savefig("./Outputs/plots/Match_Comp_"+ types[z] + p_types[y] + ".png")
        plt.close()
        
        
        ces.append(np.mean(comp))
        
        

    with open("./Outputs/values/Matchings_Comp" + types[z] + ".txt", "w") as f:
        f.write("Matching Values for Graph: "+types[z]+" \n\n")

        for y in range(4):
        
        
            f.write("Enacted Comp : "+ p_types[y] + ": "+ str(cis[y]))
            f.write("\n")
            f.write("Matching Average Comp : "+ p_types[y] + ": "+ str(ces[y]))
            f.write("\n")
            f.write("\n") 
            
            
            
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

GOV18ns= sorted((0.5187406297776442, 0.3916434540240218, 0.23378661089760477,
          0.561916167590201, 0.5277943813115976, 0.3967808623758262, 
          0.24347460005648527, 0.2040194040100815, 0.29961685822777134, 
          0.2658227848088675, 0.30213024956718243, 0.2738569188011496, 
          0.3331949346122295, 0.3753434474711785, 0.5018867924316115,
          0.5426127015341067, 0.5913152254553772, 0.6266881029630763,
          0.6404409922858867, 0.6744921745562409, 0.5829798514395329, 
          0.46457747422269396, 0.49254507629009764, 0.45721212122003807, 
          0.5081005584437817, 0.44071841251982957, 0.5078786300489014, 
          0.4823874755528126, 0.3030897498782328, 0.28720868644817754, 
          0.45392418577347565, 0.548494983265805, 0.6961661695141408, 
          0.5386310904517134, 0.5566274613453184, 0.4174338319909295, 
          0.6555631089965965, 0.7312614259593524, 0.7193151212004562, 
          0.61932265686532))
GOV18x=sorted((0.4974431818181818, 0.37424547283702214, 0.20789779326364694, 
        0.5263911254249418, 0.50988230068843, 0.38398798025327324, 
        0.23922875505831945, 0.19625226677412855, 0.28292410714285715, 
        0.2544677544677545, 0.28685985055585933, 0.2606104388658118, 
        0.32402732402732404, 0.3625, 0.47884788478847884, 0.5222623345367028,
        0.5623608017817372, 0.6011283497884344, 0.6125967628430683,
        0.6509209744503862, 0.5640572886011379, 0.45389537071885583, 
        0.4786472475931869, 0.447171453437772, 0.48655110579796773,
        0.42658509454949944, 0.49777777777777776, 0.46891624867001064, 
        0.28942840757025423, 0.27886435331230286, 0.40277539832105536, 
        0.525532969757065, 0.6567947910102919, 0.4908722109533469, 
        0.5396059509449136, 0.4065186962607478, 0.6617647058823529,
        0.7358445297504799, 0.7188718183902775, 0.6151213441194773))
USH18x=sorted((0.5058695058695059, 0.3900736719658782, 0.2543404735062007,
        0.5312662393902651, 0.5138918802498385, 0.37274049449407853, 
        0.2843413033286451, 0.2460960664162878, 0.3040479215828644, 
        0.3051849027830728, 0.32579668862382055, 0.2848743987172635,
        0.35922610453364134, 0.38727149627623564, 0.5108885017421603, 
        0.5274647887323943, 0.5599028602266595, 0.5989611809732094, 
        0.6076079506511309, 0.6491633006347375, 0.5707167497125335,
        0.46821448313985625, 0.4998794309139137, 0.43823479298006474, 
        0.49396417445482865, 0.4271950554444646, 0.49546608632571637, 
        0.467220409374073, 0.33054471091280907, 0.3152729503169086, 
        0.4366804979253112, 0.46370683579985905, 0.6810362274843149,
        0.5284996724175585, 0.5495891458054654, 0.44719662058371734,
        0.4837432852700028, 0.584951998213887, 0.5047358450852452,
        0.4665718349928876))
USH18ns=sorted((0.526629425384675, 0.41081640244677586, 0.2774311777926235, 
         0.5665135137823519, 0.5324396994583951, 0.39077610338199437,
         0.29063095741083556, 0.2520081528281857, 0.3242478870458404,
         0.3145534181033724, 0.3380180359170024, 0.2979472351935256,
         0.36280653131210194, 0.3964223985086792, 0.5198083711638748, 
         0.5483611707902181, 0.5889840870354133, 0.6223695336477948, 
         0.632669752041204, 0.6672778804198621, 0.5931440818852669,
         0.4755756282959946, 0.5105624482537662, 0.4545425262952549,
         0.5164939040837906, 0.4425673222996577, 0.5097079657012924,
         0.4870557891023724, 0.33723477574740685, 0.3260691986801825, 
         0.47925932440512, 0.4839707790207739, 0.7077419247658372, 
         0.5693768081345366, 0.5608357157934066, 0.45216772423949964,
         0.48482656936912155, 0.5846342120988194, 0.5154696428000252,
         0.47246020775337016))
Native=sorted((0.14453345368385423, 0.04791972037433758, 0.04153228088043909,
        0.04711570898459463, 0.09071032124236138, 0.19222777559386758,
        0.0498220640569395, 0.06539540100953449, 0.05580923389142567,
        0.0532899534414091, 0.0553172273650937, 0.04923320694923886, 
        0.03773051250141419, 0.034796273431361546, 0.07209144409234948,
        0.09912389082331799, 0.10816429735348654, 0.1110181311018131, 
        0.1408546235586706, 0.11965233096286262, 0.07601179004648, 
        0.07231765699802872, 0.09871413330338592, 0.05795955259292735, 
        0.08296139254630663, 0.0650539761487594, 0.07099219368706867,
        0.03138710766115423, 0.08620880949739265, 0.06442483768936241,
        0.04401535807690168, 0.16086740056425292, 0.13535582648142896,
        0.09395517319447588, 0.20246844319775595, 0.21248741188318226, 
        0.4281292984869326, 0.8349481363273681, 0.8371329976806019,
        0.6643768400392541))


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
    total_steps=100000
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
        ans = FKT(A)
        if ans is not None:
            num_matchings.append(round(ans))
        else:
            num_matchings.append(0)
            
        
        if t%1000 == 0:
            print(types[z],"chain ",t," steps")
        t+=1
        
    print("Finished ", types[z], " Ensemble")
    
    
    partisan_w = [wins1,wins2,wins3,wins4]
    partisan_p = [percents1,percents2,percents3,percents4]
    p_types=["GOV18N", "GOV18A", "USH18N", "USH18A"]
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
        
        plt.plot(range(1,41),p_vecs[y],'o',color='red',label='Current Plan')
        plt.plot([.5,41],[.5,.5],color='green',label="50%")
        plt.xlabel("Sorted Districts")
        plt.ylabel("Dem %")
        plt.xticks([1,20,40],['1','20','40'])
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
    
    plt.plot(range(1,41),Native,'o',color='red',label='Current Plan')
    plt.plot([.5,41],[.5,.5],color='green',label="50%")
    plt.xlabel("Sorted Districts")
    plt.ylabel("Native %")
    plt.xticks([1,20,40],['1','20','40'])
    plt.legend()
    
    fig = plt.gcf()
    fig.set_size_inches((20,10), forward=False)
    fig.savefig("./Outputs/plots/Ensemble_Box_"+ types[z] +"Native.png")
    plt.close()
    
    print("Finished ",types[z]," Box plots")
    
    for y in range(4):
        plt.figure()
        sns.distplot(partisan_w[y],kde=False,color='slateblue',bins=[x for x in range(10,25)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=sum([val>.5 for val in p_vecs[y]]),color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(partisan_w[y]),color='g',label="Matchings Mean",linewidth=5)
        plt.legend()
        print(p_types[y],"wins: ", np.mean(partisan_w[y]))
        plt.savefig("./Outputs/plots/Ensemble_Hist_"+ types[z] + p_types[y] + ".png")
        plt.close()
        
        
    plt.figure()
    sns.distplot(wins5,kde=False,color='slateblue',bins=[x for x in range(5)],
                                                    hist_kws={"rwidth":1,"align":"left"})
    plt.axvline(x=2,color='r',label="Current Plan",linewidth=5)
    plt.axvline(x=np.mean(wins5),color='g',label="Matchigs Mean",linewidth=5)
    plt.legend()
    print("Native wins: ", np.mean(wins5))
    plt.savefig("./Outputs/plots/Ensemble_Hist_"+ types[z] + "Native.png")
    plt.close()
    
    
    print("Finished ",types[z]," Seats plots")
    
    
    
    with open("./Outputs/values/Ensemble_" + types[z] + ".txt", "w") as f:
        f.write("Ensemble Values for Graph: "+types[z]+" \n\n")

        for y in range(4):
        
        
            f.write("Enacted Wins : "+ p_types[y] + ": "+ str(sum([val>.5 for val in p_vecs[y]])))
            f.write("\n")
            f.write("Ensemble Average Wins : "+ p_types[y] + ": "+ str(np.mean(partisan_w[y])))
            f.write("\n")
            f.write("\n")

    
    
    
    cis=[]
    ces=[]
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
                
        cis.append(c_init)
                
        
        sns.distplot(comp,kde=False,color='slateblue',bins=[x for x in range(15,35)],
                                                        hist_kws={"rwidth":1,"align":"left"})
        plt.axvline(x=c_init,color='r',label="Current Plan",linewidth=5)
        plt.axvline(x=np.mean(comp),color='g',label="Matchings Mean",linewidth=5)
        print(p_types[y],"competitive: ",np.mean(comp))
        plt.legend()
        plt.savefig("./Outputs/plots/Ensemble_Comp_"+ types[z] + p_types[y] + ".png")
        plt.close()
        
        ces.append(np.mean(comp))


    with open("./Outputs/values/Ensemble_Comp" + types[z] + ".txt", "w") as f:
        f.write("Ensemble Values for Graph: "+types[z]+" \n\n")

        for y in range(4):
        
        
            f.write("Enacted Comp : "+ p_types[y] + ": "+ str(cis[y]))
            f.write("\n")
            f.write("Ensemble Average Comp : "+ p_types[y] + ": "+ str(ces[y]))
            f.write("\n")
            f.write("\n")    
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
    
    plt.figure()
    plt.plot(num_edges,num_matchings,'o',markersize=1)
    plt.savefig("./Outputs/plots/Ensemble_Comp_"+ types[z] + "edges.png")
    plt.close()
    
    
    
    with open("./Outputs/Ensemble_"+types[z]+"_stats.json",'w') as wf:
        json.dump({0:wins1,1:percents1,2:wins2,3:percents2,4:wins3,5:percents3,
                   6:wins4,7:percents4,8:wins5,9:percents5,10:num_edges,11:num_matchings}, wf)

    
    
print("All chains run in: ", time.time()-ensemble_time, " seconds.")
print("Full replication complete in: ", time.time()-whole_start, " seconds.")
