# Fachprojet "Routing Algorithms"

# Structure
Each subfolder contains the algorithmic idea of each project member.

# Workflow
To work on a project, just clone the git repository.
Once cloned, you can go into each individual subfolder and work on it.
But first you have to go into each subfolder's **/data/topologies/topology_zoo/ directory**.
There you follow the README there to download and install the necessary *.graphml* files.
To run the project, you have to (similarly to the base project) open up a terminal and enter the following commands:

```bash
conda activate wan_sr
```
```bash
cd FaPro1_P1/<projectFolder>/src/
```
```bash
python3 main.py
```
```bash
python3 plot_results.py "../out/"
```