""" Plot script for Fig. 3, 4 and 5 in paper: 'Traffic Engineering with Joint Link Weight and Segment Optimization' """

import os
import sys

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from utility import utility
from utility.json_result_handler import JsonResultReader
from utility.utility import HIGHLIGHT, CEND

DEFAULT_DIR_DATA = utility.create_dirs(f"../results_paper")
DIR_PLOT = utility.create_dirs(f"../out/plots")

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
algo_c_map = {
    'demand_first_waypoints': "grey",
    'uniform_weights': "skyblue",
    'heur_ospf_weights': "hotpink",
    'sequential_combination': "darkgreen",
    'sequential_combination_2': "seagreen",

}

# maps display name to internal name of topologies
top_n_map = {
    # sndlib
    "abilene": "Abilene",
    "geant": "Géant",
    "germany50": "Germany50",
    # topology zoo
    "basnet": "BasNet",
}


def add_vertical_algorithm_labels(ax):
    """ Computes the position of the vertical algorithm labels and adds them to the plot """
    ymin, ymax = ax.get_ylim()
    lines = ax.get_lines()
    boxes = [c for c in ax.get_children() if type(c).__name__ == 'PathPatch']
    lines_per_box = int(len(lines) / len(boxes))

    val_list = list(algo_c_map.keys())
    off_set = (ymax - ymin) * 0.025
    for i, median in enumerate(lines[3:len(lines):lines_per_box]):
        x, y = (data.mean() for data in median.get_data())

        value = val_list[i % len(val_list)]
        label = value
        # if y position of label is above a certain level, label will be abbreviated
        if y > ymax - (ymax - ymin) * 0.25:
            label = f"{value[0:3]}."
        ax.text(x, y + off_set, label, ha='center', va='bottom', fontsize=SMALL_SIZE, rotation=90,
                color=algo_c_map[value],
                fontweight='bold')


def create_box_plot(df_plot, x, y, hue, file_name, x_label="", y_label="", fig_size=None,
                    title=None, y_lim_top=None):
    """ Setup and perform matplotlib boxplot"""
    fig, ax = plt.subplots(figsize=fig_size)

    flier_props = dict(markersize=1, linestyle='none')
    box_plot = sns.boxplot(x=x, y=y, hue=hue, data=df_plot, ax=ax, linewidth=0.5, flierprops=flier_props,
                           palette=algo_c_map)
    plt.ylabel(y_label, weight='bold', fontsize=LARGE_SIZE)
    plt.xlabel(f'{x_label}', weight='bold', fontsize=LARGE_SIZE)
    if title:
        plt.title(title, weight='bold', fontsize=TITLE_SIZE, color="dimgrey")
    plt.tight_layout()
    ax.set_facecolor('white')
    ax.grid(linestyle=':', color='grey', linewidth=0.5)
    ax.get_legend().remove()
    x_grid_lines = ax.get_xgridlines()
    if y_lim_top:
        plt.ylim(0.8, y_lim_top)
    for y_line in x_grid_lines:
        y_line.set_color('white')
    add_vertical_algorithm_labels(box_plot.axes)
    plt.xticks(rotation=0)
    plt.savefig(file_name.replace(" ", ""), bbox_inches="tight", format='pdf')
    plt.close()
    print(file_name)
    return


def get_incomplete_sample_nrs(df):
    """ Returns sample nrs + topologies if at least 1 algorithm result is missing """
    topology_incomplete_sample_nr_map = dict()
    try:
        n_samples = df.loc[df['sample_idx'].idxmax()]['sample_idx'] + 1
    except ValueError:
        print("TEST-------------->")
    for ilp_method in np.unique(df['algorithm_complete']):
        dfx = df[df['algorithm_complete'] == ilp_method]
        dfg_tops = dfx.groupby(by='topology_name')
        for key, group in dfg_tops:
            if n_samples > group.shape[0]:
                if key not in topology_incomplete_sample_nr_map:
                    topology_incomplete_sample_nr_map[key] = set()
                for s_nr in range(n_samples):
                    if s_nr not in list(group['sample_idx']):
                        topology_incomplete_sample_nr_map[key].add(s_nr)

    return topology_incomplete_sample_nr_map


def filter_trees(df):
    """ All results from tree topologies are removed """
    df = df[df["topology_name"] != "amres"]
    df = df[df["topology_name"] != "atmnet"]
    df = df[df["topology_name"] != "basnet"]
    df = df[df["topology_name"] != "brain"]
    df = df[df["topology_name"] != "carnet"]
    df = df[df["topology_name"] != "cesnet1999"]
    df = df[df["topology_name"] != "eenet"]
    df = df[df["topology_name"] != "kentmanjan2011"]
    df = df[df["topology_name"] != "sanet"]
    df = df[df["topology_name"] != "savvis"]
    return df


def prepare_data_and_plot(df, title, plot_type):
    """ Prepares data (filter topologies, beautify naming, sorting) and starts plotting """
    # create plot sub directory
    out_path = utility.create_dirs(os.path.join(DIR_PLOT, plot_type))

    # filter out tree topologies
    df = filter_trees(df)

    # filter results from valiants trick (Note: algorithm is not mentioned in paper)
    df = df[df["algorithm"] != "valiants_trick"]

    # for the 'all algorithm plot' (including ilps) show only abilene
    if plot_type.startswith("all_algorithms"):
        df = df[(df["topology_name"] == "abilene")]

    if not plot_type.startswith("all_algorithms"):
        df = df[df["algorithm"] != "uniform_weights"]

        ignored_algorithms = ['ILP Weights', 'UnitWeights', 'ILP Waypoints', 'ILP Joint']
        for algo in ignored_algorithms:
            if algo in algo_c_map:
                algo_c_map.pop(algo)

    # beautify algorithm names
    df["algorithm"] = df["algorithm"].str.replace("_", " ").str.title().str.replace(" ", "")
    df["ilp_method"] = df["ilp_method"].str.replace("_", " ").str.title().str.replace(" ", "")
    df["algorithm_complete"] = df[['algorithm', 'ilp_method']].agg(' '.join, axis=1).astype(str).str.replace('  ',
                                                                                                             ' ').str.strip()
    df["algorithm_complete"] = df["algorithm_complete"].str.replace("heur_ospf_weights", "OSPF")
    df["algorithm_complete"] = df["algorithm_complete"].str.replace("uniform_weights", "Unit_Weights")
    #  df["algorithm_complete"] = df["algorithm_complete"].str.replace("SegmentIlp", "ILP")
    df["algorithm_complete"] = df["algorithm_complete"].str.replace("demand_first_waypoints", "GreedyWaypoints")
    df["algorithm_complete"] = df["algorithm_complete"].str.replace("sequential_combination", "JointHeur")
    df["algorithm_complete"] = df["algorithm_complete"].str.replace("sequential_combination_2", "JointHeur_2")

    # beautify topology names
    df["topology_name"] = df["topology_name"].apply(lambda x: top_n_map[x])

    # sort df by topology + algorithm name
    df['algorithm_complete'] = pd.Categorical(df['algorithm_complete'], list(algo_c_map.keys()))
    df = df.sort_values(by=["topology_name", "algorithm_complete"], ignore_index=True)

    # filter incomplete samples:
    incomplete = get_incomplete_sample_nrs(df)
    if incomplete:
        print(f"Remove incomplete samples from topologies (Topology, SampleNr): {incomplete}")
        for top in get_incomplete_sample_nrs(df):
            df.drop(df[(df["topology_name"] == top) & (df["sample_idx"].isin(incomplete[top]))].index, inplace=True)
        print()

    # print mean values to console
    print("Mean objective over all topologies:")
    for algo in df['algorithm_complete'].unique():
        df_x = df[df["algorithm_complete"] == algo]
        mean = np.mean(df_x["objective"].values.mean())
        print(f'{algo:>20}: {mean}')
    print()

    # plot files
    print("Plot files:")
    # PLOT FIGURE 4 + 5
    y_lim_top = None
    plot_file = os.path.join(out_path, f"{plot_type}.pdf")
    if plot_type == "all_algorithms":
        plot_file = os.path.join(out_path, f"all_algorithms_abilene.pdf")
    create_box_plot(df, "topology_name", "objective", "algorithm_complete", plot_file, x_label="",
                    y_label="Max. Normalized Link Utilization", fig_size=(8, 6), title=title,
                    y_lim_top=y_lim_top)
    return


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

    # map data to plot titles and plot type
    raw_dfs_title = list()

    # fetch results from file and create dataframe
    # figure (all_algorithms)
    data_all_algorithm = os.path.join(dir_data, "results_all_algorithms.json")
    if os.path.exists(data_all_algorithm):
        df_all_algorithms = pd.DataFrame(JsonResultReader(data_all_algorithm).fetch_results())
        raw_dfs_title.append((df_all_algorithms, "MCF Synthetic Demands", "all_algorithms"))
    else:
        print(f"{utility.FAIL}results_all_algorithms.json not existing in {dir_data}{utility.CEND}")

    # figure (real_demands)
    data_real_demands = os.path.join(dir_data, "results_real_demands.json")
    if os.path.exists(data_real_demands):
        df_real_demands = pd.DataFrame(JsonResultReader(data_real_demands).fetch_results())
        raw_dfs_title.append((df_real_demands, "Scaled Real Demands", "real_demands"))
    else:
        print(f"{utility.FAIL}results_real_demands.json not existing in {dir_data}{utility.CEND}")

    # start plot process for each dataframe
    for df_i, title_i, plot_type_i in raw_dfs_title:
        print(f"{HIGHLIGHT}{title_i} - {plot_type_i}{CEND}")
        prepare_data_and_plot(df_i, title_i, plot_type_i)
        print()
