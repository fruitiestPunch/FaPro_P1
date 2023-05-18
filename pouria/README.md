# Fachprojet "Routing Algorithms"

## Dependencies and assumptions
It will be assumed that the person interested in the project already has a working and running version of the base project,
 including the gurobi license and a correctly running anaconda instance. 
If not, please look up the instructions given in the **[README_base.md](README_base.md)**

## Install
To start working on this project, it is necessary to clone/download this repository.
The download location is not important.
Please keep in mind to download the necessary .graphml/.gml files into the **/data/topologies/topology_zoo/** directory.

## Running the project
To run the project, one has to (similarly to the base project) open up a terminal and enter the following commands:

```bash
conda activate wan_sr
```
```bash
cd pathToProjectFolder/src/
```
```bash
python3 main.py
```
To view the results as box plot diagrams, the following command is useful.

*Note: The algorithm to create box plot diagrams from all topologies was removed due to issues.*
*It seems that an error is occurring when only a subset (possibly < 12) of all topologies are selected for the main.py.*
```bash
python3 plot_results.py "../out/"
```
The following command is optional, but will highlight the differences in computation time between the used algorithms.
```bash
python3 plot_scatters.py "../out/"
```

### Additional options/flags
The choice of algorithms and topologies was based on computational time.
Therefore, only 4-5 algorithms are used in the process and the choice of topologies was reduced to the top 3 smallest ones.
To reduce the overall computation time even more, flags are introduced.
The code can be run with multiple options.
These are given by flags that are always at the top of each python file.
*Note: It is advised that the same configuration of flags that were used in one Python file are used in the others.*
*For eample: If **bool sequential_combination = True** is set in main.py, it also has to be set the same way in the other Python files.*

This number decides how many topologies you are running. This is relevant for the test in **SDN Real  Demands**.
```bash
mian.py
int num_of_topologies <= 1 // just abilene will be used
int num_of_topologies  = 2 // abilene and geant will be used
int num_of_topologies >= 3 // abilene, geant and germany50 will be used
```

By default, the boolean is set to **False**.
If set to **True**, the algorithm *sequential_combination* will be run which will in turn run the *heur_OSPF_weights*.
This will drastically increase the computation time.
```bash
main.py
bool sequential_combination = False
```