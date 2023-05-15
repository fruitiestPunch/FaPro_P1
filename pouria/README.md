# Fachprojet "Routing Algorithms"

## Dependencies and assumptions
It will be assumed that the person interested in the project already has a working and running version of the base project, including the gurobi license and a correctly running anaconda instance. 
If not, please look up the instructions given in the **[README_base.md](README_base.md)**

## Install
To start wroking on this project, it is necessary to clone/download this repository.
The download location is not important.

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
```bash
python3 plot_results.py "../out/"
```
```bash
python3 plot_scatters.py "../out/"
```

### Additional options/flags
The code can be run with multiple options.
These are given by flags that are always at the top of each python file.

```bash
int num_of_topologies
```
This number decides how many topologies you are running. This is relevant for the test in **SDN Real  Demands**.
```bash
boolean sequential_combination
```
There are 4 algorithms that are always checked and running with **[main.py](main.py)**. When the bool is set to true, the 5th algorithm **sequential_combination** will run.
*Note: This algorithm will increase the overall runtime of the main function.
```bash
boolean test_1
boolean test_2
boolean test_3
```
It is possible to decide what tests will run with the above booleans.