# -*- coding: utf-8 -*-
"""
Created on Wed May 15 11:54:57 2019

@author: daryl
"""

import networkx as nx
import matplotlib.pyplot as plt
import random
import math
import numpy as np
import time

#######################################################################
# BASED On An Original Sage Version by:
# AUTHOR: Dr. Christian Schridde
# E-MAIL: christianschridde [at] googlemail [dot] com
#
# DESCRIPTION: Implementation of the FKT-algorithm
#
# INPUT:  Adjacency matrix A of a undirected loop-free planar graph G
# OUTPUT: Skew matrix M, such that PerfMatch(G) = Sqrt(Determinat(M))
########################################################################
    
def FKT(A):
 # make some local copies
    n = len(A)
    B_graph = A[:];
    B_digraph = A[:];
 
    G = nx.Graph(A)

 

 # THIRD: COMPUTE A PLANAR EMBEDDING
    tf, embd = nx.check_planarity(G);
 # each face is listed in clockwise order, except the first one which is the outer face
    faces = find_faces(embd);
     
 # FOURTH: GET THE SPANNING TREE
    T1 = nx.minimum_spanning_tree(G)
    T1 = nx.Graph(T1) 

 # FIFTH: ASSIGN AN ARBITRARY DIRECTION TO THE EDGES
    #DG = DiGraph(B_digraph);
    #DG = DG.to_undirected();
    #B_digraph = DG.adjacency_matrix();
    for i in range(0,n):
        for j in range(0,n):
            if (B_digraph[i,j] == 1):
                if (B_digraph[j,i] == 1):
                    r = random.choice([0,1])
                    if (r==0):
                        B_digraph[j,i] = 0
                    else:
                        B_digraph[i,j] = 0
    G = nx.DiGraph(B_digraph)

 # SIXTH: FIND FACE THAT HAS ONLY ONE EDGE NOT IN T1
    edgesT1 = T1.edges();
    adj_T1 = (nx.adjacency_matrix(T1)).todense();
    
    
 # give the edges in T1 the orientation from B_digraph
    for edge in edgesT1:
        if (B_digraph[edge[0],edge[1]] == 0):
            adj_T1[edge[0],edge[1]] = 0
        else:
            adj_T1[edge[1],edge[0]] = 0
             
    T1 = nx.DiGraph(adj_T1)
    edgesT1 = list(T1.edges())   
     
 # remove the first face, which is the outer face
 # QUESTION: Is it always correct to remove this face?
 
    faces.sort(key=len)
    faces.reverse()
    faces.pop(0);
     
    while (len(faces) > 0):
        index = -1;
        for face in faces:
            countMissingEdges = 0; 
            missingEdge = 0;
            index += 1;
            for edge in face:
                try:
                    idx1 = edgesT1.index(edge);
                except ValueError:
                    try:
                        idx2 = edgesT1.index(reverseEdge(edge));
                    except ValueError:
                        countMissingEdges += 1;
                        missingEdge = edge;
                    else:
                        doNothing();
                else:
                    doNothing();

            if (countMissingEdges == 1):
    # in this face, only one edge is missing.        
    # Place the missing edge such that the total number
    # of clockwise edges of this face is odd
    # add this edge to the spanning tree
                if ((numberOfClockwiseEdges(face,edgesT1))%2 == 1):
     # insert counterclockwise in adj_T1;
                    if (isClockwise(missingEdge,face) == False):
                        adj_T1[missingEdge[0],missingEdge[1]] = 1;
                    else:
                        adj_T1[missingEdge[1],missingEdge[0]] = 1;
                else:
     # insert clockwise in adj_T1
                    if (isClockwise(missingEdge,face) == True):
                        adj_T1[missingEdge[0],missingEdge[1]] = 1;
                    else:
                        adj_T1[missingEdge[1],missingEdge[0]] = 1;
                             
    # rebuild the graph
                T1 = nx.DiGraph(adj_T1);
                edgesT1 = list(T1.edges());
                             
    # remove the face that was found
                faceFound = faces.pop(index);
                break;
 
    return math.sqrt(np.linalg.det(toSkewSymmetricMatrix(adj_T1)));

############################
# Returns true if the given edge is
# clockwise oriented regarding the given face
def isClockwise(e,face):
  try:
   face.index(e);
  except ValueError:
   return False;
  else:
   return True;


############################
# This is a placeHolder function
def doNothing():
 return 0;


############################ 
# Reverses a given edge
def reverseEdge(edge):
 return (edge[1],edge[0]);


############################
# Inputs are the face and the orientedEdges from the spanning-tree T1
# Note, that all edges in face are clockwise (since it is the result
# from the obtained embedding).
# It returns how many of the edges from T1 that are part of the
# given face are actually clockwise.
def numberOfClockwiseEdges(face, edgesT1):
 clockwise = 0;
 for edge in face:
   try:
     edgesT1.index(edge);
   except ValueError:
     doNothing();
   else:
     clockwise += 1;
 return clockwise;


############################
# Transforms a given matrix A to a 
# skewSymmetric Matrix
def toSkewSymmetricMatrix(A):
    n=len(A)
    for i in range(0,n):
        for j in range(0,n):
            if (A[i,j] == 1):
                A[j,i] = -1;
    return A



def find_faces(embd):
    ed_list = list(embd.edges())
    faces=[]
    
    for ed in embd.edges():
        if ed in ed_list:
            faces.append(embd.traverse_face(ed[0],ed[1]))
            
            for i in range(len(faces[-1])):
                ed_list.remove((faces[-1][i],faces[-1][(i+1)%len(faces[-1])]))
                
    face_edges=[]
    for face in faces:
        face_edges.append([])
        for i in range(len(face)):
            face_edges[-1].append((face[i],face[(i+1)%len(face)]))
            
                
    return face_edges
    

###################ACTUAL RUNS
start_time = time.time()

G=nx.grid_graph([10,10])

Adj = (nx.adjacency_matrix(G)).todense()

print(FKT(Adj))


print(time.time()-start_time)

start_time = time.time()

g2 = nx.Graph(np.matrix(
[[0,1,0,0,0,0,0,0,0,0],[
        1,0,1,0,0,0,0,0,0,0],
    [0,1,0,0,1,1,0,0,0,0],
    [0,0,0,0,1,0,1,0,0,0],
    [0,0,1,1,0,0,0,1,0,0],
    [0,0,1,0,0,0,0,0,1,1],
    [0,0,0,1,0,0,0,1,0,0],
    [0,0,0,0,1,0,1,0,0,0],
    [0,0,0,0,0,1,0,0,0,1],
    [0,0,0,0,0,1,0,0,1,0]]))
    

Adj2 = (nx.adjacency_matrix(g2)).todense()

print(FKT(Adj2))


print(time.time()-start_time)

start_time = time.time()

AK = nx.Graph(np.matrix([[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1],
[0,0,0,0,0,0,0,0,0,0,1,1,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,1,0,1,0,0,0,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0],
[0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,1,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0],
[1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0],
[0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,1,0,1,1,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,1,1,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,1,0,0,0,1,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,1,1,0,0,1,1,0,0,0,1,0,0,0],
[0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0,1],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[1,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0],
[1,0,0,0,0,0,1,1,0,0,0,0,1,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0],
[0,0,0,0,0,0,0,1,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0],
[0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,1,0,0,0,1,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0],
[0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1,0,0,0],
[0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,1,1,0,0,0,0,0,1,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,0,0,0,0,1,0,0],
[0,0,1,0,0,1,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
[0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0],
[0,0,0,0,1,0,0,0,1,0,0,0,1,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,1,1,1,0,0,1,1,0],
[0,0,0,1,0,0,0,0,0,1,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,1,0,0,0,0,0,0],
[0,0,0,0,0,1,0,0,1,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,1,1,0,0,1,0,0,0,0],
[0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,0,0,0,0,1,0],
[1,0,0,0,0,1,0,1,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,0,1],
[0,0,0,1,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,1,0,0,0,1,0,0,0,0,0,0,0,0,0],
[0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0,0,0,0],
[0,0,0,0,0,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0,1,0,0,0,0,0,0,0,1,0,0,1,0,0,0,0,0],
[1,0,1,0,0,0,0,0,0,0,0,0,0,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,0,0,0,0]]))
    
AdjAK = (nx.adjacency_matrix(AK)).todense()

print(FKT(AdjAK))


print(time.time()-start_time)
