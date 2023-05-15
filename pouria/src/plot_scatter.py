""" Plot script for Fig. 3, 4 and 5 in paper: 'Traffic Engineering with Joint Link Weight and Segment Optimization' """

import os
import sys
import json

import matplotlib.pyplot as plt
import numpy as np

from utility import utility
from utility.json_result_handler import JsonResultReader
from utility.utility import HIGHLIGHT, CEND

DEFAULT_DIR_DATA = utility.create_dirs(f"../results_paper")
DIR_PLOT = utility.create_dirs(f"../out/plots")

# ###########################################################################
# custom variables
num_of_topologies = 1
enable_seqential_combination = False
# ###########################################################################

# plot settings
SMALL_SIZE = 14
LARGE_SIZE = 15
TITLE_SIZE = 17
plt.style.use('ggplot')
plt.rc('font', weight='bold', family='serif')
plt.rc('xtick', labelsize=SMALL_SIZE)
plt.rc('ytick', labelsize=SMALL_SIZE)
plt.rc('figure', titlesize=TITLE_SIZE)

# maps each algorithm to a color
if(enable_seqential_combination):
    algo_c_map = {
        'GreedyWaypoints': "hotpink",
        'InverseCapacity': "skyblue",
        'SeqComWayCap': "darkgreen",
        'SeqComCapWay': "orange",
        'JointHeur': "seagreen",
    }
else:
    algo_c_map = {
        'GreedyWaypoints': "hotpink",
        'InverseCapacity': "skyblue",
        'SeqComWayCap': "darkgreen",
        'SeqComCapWay': "orange",
        #'JointHeur': "seagreen",
    }

# maps display name to internal name of topologies
if(num_of_topologies <= 1):
    top_n_map = {
        "abilene": "Abilene",
        "basnet": "BasNet",
    }
elif(num_of_topologies == 2):
    top_n_map = {
        "abilene": "Abilene",
        "geant": "Geant",
        "basnet": "BasNet",
    }
else:
    top_n_map = {
        "abilene": "Abilene",
        "geant": "Geant",
        "germany50": "Germany50",
        "basnet": "BasNet",
    }

# dict {name: string, objective: double, execution_time: double, process_time: double}
def plot_and_save_pdf(plot_data, dirname):
 
    fig_e, ax_e = plt.subplots()
    fig_p, ax_p = plt.subplots()

    for algo in plot_data:
        ax_e.scatter(algo['objective'], algo['execution_time'], color=algo_c_map[algo['name']], label=algo['name'])
        ax_p.scatter(algo['objective'], algo['process_time'], color=algo_c_map[algo['name']], label=algo['name'] )


    ax_e.set_xlabel(r'objective', fontsize=15)
    ax_e.set_ylabel(r'execution_time', fontsize=15)
    ax_e.set_title('Objective an execution time')
    ax_e.grid(True)
    ax_e.legend()
    fig_e.tight_layout()

    ax_p.set_xlabel(r'objective', fontsize=15)
    ax_p.set_ylabel(r'process_time', fontsize=15)
    ax_p.set_title('Objective and process time')
    ax_p.grid(True)
    ax_p.legend()
    fig_p.tight_layout()
 
    fig_e.savefig(f"{DIR_PLOT}/{dirname}/execution_time.pdf", bbox_inches='tight')
    fig_p.savefig(f"{DIR_PLOT}/{dirname}/process_time.pdf", bbox_inches='tight')


def load_data(filepath):
    with open(filepath, "r") as read_file:
       return json.load(read_file)

def reduce_list(data):
    # algo_name as key
    sum_e = dict();
    sum_p = dict();
    sum_o = dict();
    count = dict();

    for el in data:
        key = el['name']
        # if it is already there update the value
        if(el['name'] in sum_e):
            sum_e[key] = sum_e[key] + el['execution_time']
            sum_p[key] = sum_p[key] + el['process_time']
            sum_o[key] = sum_o[key] + el['objective']
            count[key] = count[key] + 1
        else:
            sum_e[key] = el['execution_time']
            sum_p[key] = el['process_time']
            sum_o[key] = el['objective']
            count[key] = 1

    data_list = []
    for key in sum_e:
        data_list.append({'name': key, 'objective': sum_o[key] / count[key], 'execution_time': sum_e[key] / count[key], 'process_time': sum_p[key] / count[key]})
   
    return data_list

def beautify_algo_name(plot_data):

    for algo in plot_data:
        algo['name'] = algo['name'].replace("_", " ").title().replace(" ", "")
        algo['name'] = algo['name'].replace("DemandFirstWaypoints", "GreedyWaypoints")
        algo['name'] = algo['name'].replace("SequentialCombination", "JointHeur")

    return plot_data


if __name__ == "__main__":
    # parse args
    if len(sys.argv) == 1:
        dir_data = DEFAULT_DIR_DATA
    elif len(sys.argv) == 2:
        dir_data = os.path.abspath(sys.argv[1])
        if not os.path.exists(dir_data):
            raise NotADirectoryError(f"Directory {dir_data} doesn't exist")
    else:
        raise SyntaxError("Max. one argument allowed: <data-dir> containing json result data. ")

    json_filenames = ['results_real_demands.json', 'results_all_algorithms.json', 'results_all_topologies.json']

    for filename in json_filenames:
        print(f"Loading json {filename} .")
        json_data = list(map(
            lambda  json_dict: {
                'name': json_dict['algorithm'], 
                'objective': json_dict['objective'], 
                'execution_time': json_dict['execution_time'], 
                'process_time': json_dict['process_time']},
            load_data(f"{dir_data}/{filename}")))
    
        plot_data = reduce_list(json_data)
        plot_data = beautify_algo_name(plot_data);
        pdf_dir = filename.replace(".json", "").replace("results_", "")
        plot_and_save_pdf(plot_data, pdf_dir) 
        print(f"Plots saved in  {DIR_PLOT}/{pdf_dir}")
