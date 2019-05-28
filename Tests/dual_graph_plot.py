

import geopandas as gpd
import pysal as ps
import numpy as np
import matplotlib.pyplot as plt
#plt.switch_backend('agg')
import networkx as nx
import maup
#from partitions import Graph


def remove_o(name):
    if name[0] == '0':
        name = name[1:]
        
    return name


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

for state in states:


    df = gpd.read_file(f"./shapefiles/{state}/{state}.shp")

    centroids = df.centroid
    c_x = centroids.x
    c_y = centroids.y
    
    #edges = maup.adjacencies(df).index
    #graph = Graph.from_edges(edges)

    rW = ps.rook_from_shapefile(f"./shapefiles/{state}/{state}.shp")

    #rW = ps.weights.Rook.from_file("./US_cont.gal")
    #basemap = df_counties.plot(color = "white", edgecolor = "white")
    #county_centroids.plot(ax = basemap, markersize = 1)

    #for i, jj in rW.neighbors.items():
        # origin = centroids[k]
    #    for j in jj:
    #        segment = county_centroids
    #        basemap.plot([c_x[i], c_x[j]], [c_y[i], c_y[j]], linestyle = '-', linewidth = .75, color='black')
            
            
    #plt.axis('off')
    #plt.savefig("./AR_test3.png")
    
    g=nx.Graph(rW.neighbors)
    #g2=sorted(nx.connected_components(g), key = len, reverse=True)
    #graph.remove_nodes_from(list(nx.isolates(graph)))

    ctds={x:(c_x[int(x)],c_y[int(x)]) for x in rW.neighbors.keys()}
    #ctds={x:(c_x[int(x)],c_y[int(x)]) for x in graph.nodes()}
    
    plt.figure()
    nx.draw(g,pos=ctds,node_size=.1,node_color='k',width=.4)
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar.png")
    plt.close()
    
    plt.figure()
    
    ctds={x:(c_x[int(x)],c_y[int(x)]) for x in rW.neighbors.keys()}
    #ctds={x:(c_x[int(x)],c_y[int(x)]) for x in graph.nodes()}
    plt.figure()
    nx.draw(g,pos=ctds,node_size=0,node_color='k',width=.4,with_labels=True,font_color='b',
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar2.png")
    plt.close()
    
    plt.figure()
    nx.draw_kamada_kawai(g,node_size=0,edge_color='lightblue',alpha =.5, width=.6,with_labels=True,font_color='k',
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar3.png")
    plt.close()

    plt.figure()
    nx.draw_kamada_kawai(g,node_size=600,edge_color='slateblue',alpha =.5, width=1,with_labels=True,font_color='k',node_color=['w' for x in g.nodes()],
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar4.png")
    plt.close()
    
    plt.figure()
    nx.draw_planar(g,node_size=600,edge_color='slateblue',alpha =.5, width=1,with_labels=True,font_color='k',node_color=['w' for x in g.nodes()],
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar5.png")
    plt.close()
    
    plt.figure()
    nx.draw_spectral(g,node_size=600,edge_color='slateblue',alpha =.5, width=1,with_labels=True,font_color='k',node_color=['w' for x in g.nodes()],
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar6.png")
    plt.close()
    
    plt.figure()
    nx.draw_spring(g,node_size=600,edge_color='slateblue',alpha =.5, width=1,with_labels=True,font_color='k',node_color=['w' for x in g.nodes()],
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar7.png")
    plt.close()
    
    plt.figure()
    nx.draw_shell(g,node_size=600,edge_color='slateblue',alpha =.5, width=1,with_labels=True,font_color='k',node_color=['w' for x in g.nodes()],
    labels={x:remove_o(df["SLDLST"][x]) for x in g.nodes()})
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar8.png")
    plt.close()
    
        
    plt.figure()
    df.plot(color='black', edgecolor='white')
    nx.draw(g,pos=ctds,node_size=.1,node_color='lime',edge_color='lime',width=.4)
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar_overlay2.png")
    plt.close()

    plt.figure()
    df.plot(color='black', edgecolor='lime')
    nx.draw(g,pos=ctds,node_size=.1,node_color='w',edge_color='w',width=.4)
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar_overlay3.png")
    plt.close()
    
    plt.figure()
    df.plot(color='white', edgecolor='black')
    nx.draw(g,pos=ctds,node_size=.1,node_color='hotpink',edge_color='hotpink',width=.4)
    #plt.show()
    #fig=plt.gcf()
    #fig.set_size_inches(12,4)
    plt.savefig(f"./Outputs/plots/{state}_planar_overlay4.png")
    plt.close()
#print("It took:", end - start, "seconds")

#out = ps.open("./US_cont.gal", 'w')
#out.write(rW)
#out.close()
