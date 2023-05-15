""" Script to evaluate strategies for traffic engineering on real topologies
    from SNDLib and TopologyZoo using real and synthetic traffic.
    The produced results will be stored in JSON format in the directory 'out'. """

import os

from algorithm import sr_factory
from demand import dp_factory
from utility import utility
from topology import topology_factory
from utility.json_result_handler import JsonResultWriter
from utility.utility import HIGHLIGHT, CEND, FAIL, error_solution, get_setup_dict, get_fpp

OUT_DIR = os.path.abspath("../out/")
LOG_DIR = os.path.join(OUT_DIR, "log/")

# demands settings
SEED = 318924135
DEMANDS_SAMPLES = 10
ALGORITHM_TIME_OUT = 3600 * 4
ACTIVE_PAIRS_FRACTION = 0.2


def work(algorithm_name, links, n, demands, ilp_method, setup, time_out, res_handler):
    """ Thread worker method: starts a single test instance, i.e.,
        creates algorithm object and solves problem, appends the result to a json file """
    success = False
    result_dict = dict()
    result_dict.update(setup)
    try:
        nodes = list(range(n))
        algorithm = sr_factory.get_algorithm(
            algorithm_name, nodes=nodes, links=links, demands=demands, ilp_method=ilp_method, time_out=time_out)
        solution = algorithm.solve()
        result_dict.update(solution)
        success = True
    except Exception as ex:
        err_solution = error_solution()
        result_dict.update(err_solution)
        print(f"{HIGHLIGHT}Error on: {setup}\n msg: {str(ex)}{CEND}")
    res_handler.insert_result(result_dict)
    return success, result_dict["objective"]


def get_demands_generator_mcf_maximal(n, links, active_pairs_fraction, seed):
    """ Creates a set of 10 samples of demands fitted to the capacity of the topology with MCF maximal """
    flows_per_pair = get_fpp(links)
    demands_provider = "mcf"
    mcf_method = "maximal"
    mcf_dp = dp_factory.get_demand_provider(
        n=n, provider=demands_provider, number_samples=DEMANDS_SAMPLES, links=links,
        active_pairs_fraction=active_pairs_fraction,
        mcf_method=mcf_method, flows_per_pair=flows_per_pair, seed=seed)
    for sample_idx, demands in enumerate(mcf_dp.demand_sequences()):
        yield demands, demands_provider, sample_idx


def get_demands_generator_scaled_snd(n, links, topology, seed):
    """ Creates a set of 10 samples of demands from sndlib and scales the demand using MCF concurrent """
    # Get demands from snd_lib demand provider
    snd_lib_dp = dp_factory.get_demand_provider(
        provider="snd_lib", topology_name=topology, number_samples=DEMANDS_SAMPLES)
    unscaled_demand_matrices = list(snd_lib_dp.demand_matrices())

    # Scale demands with mcf maximal concurrent
    flows_per_pair = get_fpp(links)
    mcf_dp = dp_factory.get_demand_provider(
        n=n, provider="mcf", number_samples=DEMANDS_SAMPLES, links=links,
        unscaled_demands_sets=unscaled_demand_matrices,
        mcf_method="MAXIMAL_CONCURRENT", flows_per_pair=flows_per_pair, seed=seed)
    for sample_idx, demands in enumerate(mcf_dp.demand_sequences()):
        yield demands, "snd_lib_mcf_scaled", sample_idx


def get_topology_generator(top_provider, tops_names, max_edges=None):
    """ Retrieves topology file data from src top_provider """
    top_provider = topology_factory.get_topology_factory(top_provider)
    for topology_name in tops_names:
        links, n = top_provider.get_topology(topology_name)
        if max_edges and len(links) > max_edges:
            continue
        yield links, n, topology_name


def all_topologies_synthetic_demands():
    """ Sets up tests using all topology data having complete link capacity data from SNDLib and TopologyZoo.
    For these tests synthetic demands generated with MCF MAXIMAL are used.
    Each test instance is executed on 4 heuristic algorithms """

    # algorithm settings
    algorithms = [
        "demand_first_waypoints",
        "inverse_capacity",
        "seq_com_way_cap",
        "seq_com_cap_way",
        #"sequential_combination",
    ]
    ilp_method = ""

    # topology provider settings
    topology_map = {
        # SNDLib with complete capacity information
        "snd_lib": [
            "abilene",  #: |E|: 30 , |V|: 12
            "polska",  #: |E|: 36 , |V|: 12
            "nobel-us",  #: |E|: 42 , |V|: 14
        ],

        # TopologyZoo complete capacity information
        "topology_zoo": [
            "basnet",  #: |E|: 12 , |V|: 7
        ]
    }

    if not os.path.exists(os.path.join(utility.BASE_PATH_ZOO_TOPOLOGY, f"{topology_map['topology_zoo'][0].title()}.graphml")):
        print(f"{FAIL}The data from TopologyZoo is not available - pls follow the instruction in README.md{CEND}")
        return

    # demand provider settings
    mcf_method = "maximal"

    result_filename = os.path.join(OUT_DIR, "results_all_topologies.json")
    result_handler = JsonResultWriter(result_filename, overwrite=True)

    test_idx = 0
    # for each source of topology (SNDLib and TopologyZoo)
    for topology_provider in topology_map:
        topologies = topology_map[topology_provider]
        topology_generator = get_topology_generator(topology_provider, topologies)
        for links, n, topology in topology_generator:
            # setup topology specific demand generator and iterate over 10 samples of demands
            demands_generator = get_demands_generator_mcf_maximal(n, links.copy(), ACTIVE_PAIRS_FRACTION, SEED)
            for demands, demands_provider, sample_idx in demands_generator:
                # perform each test instance on each algorithm
                for algorithm in algorithms:
                    setup = get_setup_dict(algorithm, demands, demands_provider, links, ilp_method, n, sample_idx,
                                           test_idx,
                                           topology, topology_provider, ACTIVE_PAIRS_FRACTION, mcf_method, SEED)

                    print(f"submit test: {test_idx} ({topology}, {algorithm}, D_idx = {sample_idx})")
                    success, objective = work(algorithm, links.copy(), n, demands.copy(), ilp_method, setup,
                                              ALGORITHM_TIME_OUT, result_handler)
                    print(f"Test-ID: {test_idx}, success: {success} [{algorithm}, "
                          f"{topology}, {sample_idx}]: objective: {round(objective, 4)}")
                    test_idx += 1
    return


def abilene_all_algorithms():
    """ Sets up tests for topology Abilene (snd_lib) and synthetic demands using MCF MAXIMAL.
    Each test instance is executed on all available algorithms """

    # algorithm settings
    algorithms = [  # ("algorithm_name", "ilp_method")
        ("demand_first_waypoints", ""),
        ("inverse_capacity", ""),
        ("seq_com_way_cap", ""),
        ("seq_com_cap_way", ""),
        #("sequential_combination", ""),
    ]

    # topology provider setup
    topology_provider = "snd_lib"
    topologies = ['abilene']
    topology_generator = get_topology_generator(topology_provider, topologies)

    # demand provider setup
    mcf_method = "maximal"

    # setup result handler
    result_filename = os.path.join(OUT_DIR, "results_all_algorithms.json")
    result_handler = JsonResultWriter(result_filename, overwrite=True)

    # fetch data for test instance and perform test
    test_idx = 0
    for links, n, topology in topology_generator:
        # setup topology specific demand generator and iterate over 10 samples of demands
        demands_generator = get_demands_generator_mcf_maximal(n, links.copy(), ACTIVE_PAIRS_FRACTION, SEED)
        for demands, demands_provider, sample_idx in demands_generator:
            # perform each test instance on each algorithm
            for algorithm, ilp_method in algorithms:
                setup = get_setup_dict(algorithm, demands, demands_provider, links, ilp_method, n, sample_idx, test_idx,
                                       topology, topology_provider, ACTIVE_PAIRS_FRACTION, mcf_method, SEED)

                print(f"submit test: {test_idx} ({topology}, {algorithm} {ilp_method}, D_idx = {sample_idx})")
                success, objective = work(algorithm, links.copy(), n, demands.copy(), ilp_method, setup,
                                          ALGORITHM_TIME_OUT, result_handler)
                print(f"Test-ID: {test_idx}, success: {success} [{algorithm} {ilp_method}, "
                      f"{topology}, {sample_idx}]: objective: {round(objective, 4)}")
                test_idx += 1
    return


def snd_real_demands():
    """ Sets up tests using topology and demand data from snd_lib. The demand data is scaled with MCF MAXIMAL CONCURRENT
    Each test instance is executed  on 4 heuristic algorithms """

    # algorithm settings
    algorithms = [
        "demand_first_waypoints",
        "inverse_capacity",
        "seq_com_way_cap",
        "seq_com_cap_way",
        #"sequential_combination",
    ]
    ilp_method = ""

    # topology provider setup
    topology_provider = "snd_lib"
    topologies = ['abilene']
    #topologies = ['abilene', 'polska']
    #topologies = ['abilene', 'polska', 'nobel-us']
    topology_generator = get_topology_generator(topology_provider, topologies)

    # demand provider setup
    mcf_method = "maximal_concurrent"

    # setup result handler
    result_filename = os.path.join(OUT_DIR, "results_real_demands.json")
    result_handler = JsonResultWriter(result_filename, overwrite=True)

    test_idx = 0
    for links, n, topology in topology_generator:
        # setup topology specific demand generator and iterate over 10 samples of demands
        demands_generator = get_demands_generator_scaled_snd(n, links.copy(), topology, SEED)
        for demands, demands_provider, sample_idx in demands_generator:
            # perform each test instance on each algorithm
            for algorithm in algorithms:
                setup = get_setup_dict(algorithm, demands, demands_provider, links, ilp_method, n, sample_idx, test_idx,
                                       topology, topology_provider, 1, mcf_method, SEED)

                print(f"submit test: {test_idx} ({topology}, {algorithm}, D_idx = {sample_idx})")
                success, objective = work(algorithm, links.copy(), n, demands.copy(), ilp_method, setup,
                                          ALGORITHM_TIME_OUT, result_handler)
                print(f"Test-ID: {test_idx}, success: {success} [{algorithm}, "
                      f"{topology}, {sample_idx}]: objective: {round(objective, 4)}")
                test_idx += 1
    return


def main():
    """ For each figure used in the paper we perform a single test-run comprising each multiple test instances """
    # Evaluation Fig. 3
    print(f"Start {HIGHLIGHT}MCF Synthetic Demands - All Topologies{CEND}:")
    all_topologies_synthetic_demands()

    # Evaluation Fig. 4
    print(f"Start {HIGHLIGHT}MCF Synthetic Demands - All Algorithms - Abilene{CEND}:")
    abilene_all_algorithms()

    # Evaluation Fig. 5
    print(f"Start {HIGHLIGHT}Scaled Real Demands - Abilene, Geant, Germany50{CEND}:")
    snd_real_demands()


if __name__ == '__main__':
    main()