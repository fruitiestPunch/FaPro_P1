import time
import networkit as nk

from algorithm.generic_sr import GenericSR
from algorithm.segment_routing.equal_split_shortest_path import EqualSplitShortestPath

"""
Version 1.1
Author: Kai Ilmenau
Date: 15.05.2023

Uses the capacity and the eigenvector centrality metric to set weights along the links.
"""
class EigenvectorCapacity(GenericSR):
    def __init__(self, nodes: list, links: list, demands: list, weights: dict = None, waypoints: dict = None, **kwargs):
        super().__init__(nodes, links, demands, weights, waypoints)

        self.__nodes = nodes  # [i, ...]
        self.__links = links  # [(i,j,c), ...]
        self.__demands = demands  # {idx: (s,t,d), ...}
        self.__weights = None
        self.__waypoints = waypoints
        
        # networKit graph
        self.__n = len(nodes)
        self.__g = None

    def solve(self) -> dict:
        """ set weights to capacity divided by weighted eigenvector centrality and use shortest path algorithm """

        # add random waypoint for each demand
        t = time.process_time()
        pt_start = time.process_time()  # count process time (e.g. sleep excluded)

        #set link weights to capacity
        self.__weights = {(i, j): c for i, j, c in self.__links}    

        self.__init_graph()

        self.__calculated_eigenvectorcentrality()
                
        post_processing = EqualSplitShortestPath(nodes=self.__nodes, links=self.__links, demands=self.__demands,
                                                 split=True, weights=self.__weights, waypoints=self.__waypoints)
        solution = post_processing.solve()

        pt_duration = time.process_time() - pt_start
        exe_time = time.process_time() - t

        # update execution time
        solution["execution_time"] = exe_time
        solution["process_time"] = pt_duration
        return solution

    def __calculated_eigenvectorcentrality(self):
        """" sets weights to the current weight value divide by the average of the eigenvector-centralities"""
        eigVec = nk.centrality.EigenvectorCentrality(self.__g, 1e-9)
        eigVec.run()
        centralities = eigVec.ranking()

        for i, j, _ in self.__links:
            centrality_i = 0
            centrality_j = 0
            
            for a in centralities:
                if a[0] == i:
                    centrality_i = a[1]
                elif a[0] == j:
                    centrality_j = a[1]

            self.__weights[i, j] = self.__weights[i, j] / ((centrality_i+centrality_j)/2)

   
    def __init_graph(self):
        """ Create networKit graph, add weighted edges """
        self.__g = nk.Graph(weighted=True, directed=False, n=self.__n)
        for u, v, _ in self.__links:
            self.__g.addEdge(u, v, self.__weights[u,v])

    def get_name(self):
        """ returns name of algorithm """
        return f"eigenvector_capacity"
       