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

