import geopandas
import numpy
import wasabi

from scipy.sparse.csgraph import connected_components

import maup
from partitions import Graph

printer = wasabi.Printer()


def main():
    states = [
        "Alaska",
        "Iowa",
        "Montana",
        "Ohio",
        "Wisconsin",
        "Illinois",
        "Minnesota",
        "Nevada",
        "Oregon",
        "Wyoming",
    ]
    for state in states:
        df = geopandas.read_file(f"./shapefiles/{state}/{state}.shp")
        edges = maup.adjacencies(df).index
        graph = Graph.from_edges(edges)

        assert (
            connected_components(
                graph.neighbors.matrix, directed=False, return_labels=False
            )
            == 1
        )

        matrix = graph.neighbors.matrix.toarray()
        numpy.savetxt(f"./graphs/{state}.csv", matrix, fmt="%1i")
        printer.good(f"Generated adjacency matrix for {state}'s state house districts.")


if __name__ == "__main__":
    main()
