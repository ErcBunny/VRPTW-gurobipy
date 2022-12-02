import os

import matplotlib.pyplot as plt
import numpy as np

from fileutil import pretty_print


def plot_solution(
    title: str,
    is_feasible: bool,
    objective_value: float,
    arc: np.ndarray,
    arrival_time: np.ndarray,
    coordinate: np.ndarray,
    time_window: np.ndarray,
    demand: np.ndarray,
    service_duration: np.ndarray,
    vehicle_quantity: int,
    vehicle_capacity: float,
    cost_per_distance: float,
    time_per_distance: float,
    solver_runtime: float,
    mip_gap: float,
    show_plot: bool
):
    """
    if the problem is feasible, plot all the results

    otherwise only plot the problem setting

    no return values, this function blocks later commands until the graph is closed

    """

    node_quantity = coordinate.shape[0]
    customer_quantity = node_quantity - 2
    N = range(node_quantity)
    V = range(vehicle_quantity)

    
    px = 1/plt.rcParams['figure.dpi']
    plt.figure(title, figsize=(2700/1.75*px, 900/1.75*px))
    plt.rcParams["font.family"] = "Times New Roman"
    M = ["o", "s", "D", "P", "X", "^", "v"]

    chrono_info = []

    if(is_feasible):

        coordinate_reordered = []
        time_window_reordered = []
        demand_reordered = []
        service_duration_reordered = []
        arrival_time_reordered = []
        node_sequence = []

        for k in V:

            i = 0
            coordinate_reordered.append(coordinate[i, :])
            time_window_reordered.append(time_window[i, :])
            demand_reordered.append(np.array(demand[i]))
            service_duration_reordered.append(np.array(service_duration[i]))
            arrival_time_reordered.append(np.array(arrival_time[i, k]))
            node_sequence.append(np.array(i))

            while(i != N[-1]):

                for j in N:
                    if(arc[k, i, j] == 1):
                        i = j
                        break
                
                coordinate_reordered[k] = np.vstack((coordinate_reordered[k], coordinate[i, :]))
                time_window_reordered[k] = np.vstack((time_window_reordered[k], time_window[i, :]))
                demand_reordered[k] = np.append(demand_reordered[k], demand[i])
                service_duration_reordered[k] = np.append(service_duration_reordered[k], service_duration[i])
                arrival_time_reordered[k] = np.append(arrival_time_reordered[k], arrival_time[i, k])
                node_sequence[k] = np.append(node_sequence[k], i)

            if(coordinate_reordered[k].shape[0] == 2):
                arrival_time_reordered[k] = np.zeros_like(arrival_time_reordered[k])

            x = coordinate_reordered[k][:, 0]
            y = coordinate_reordered[k][:, 1]
            if(x.shape[0] > 2):
                plt.subplot(1, 3, 1)
                plt.plot(x, y, label="vehicle " + str(k), marker=M[k // 10])

        for k in V:
            
            init_cargo = np.sum(demand_reordered[k])
            chrono_info.append(np.zeros([2 * (node_sequence[k].shape[0] - 2) + 2, 5]))
            chrono_info[k][0, :] = np.array([0, 0, init_cargo, coordinate_reordered[k][0, 0], coordinate_reordered[k][0, 1]])

            for i in range(node_sequence[k].shape[0] - 2):
                chrono_info[k][1 + 2 * i, :] = np.array(
                    [arrival_time_reordered[k][i + 1], node_sequence[k][i + 1], chrono_info[k][2 * i, 2], coordinate_reordered[k][i + 1, 0], coordinate_reordered[k][i + 1, 1]]
                )
                chrono_info[k][2 + 2 * i, :] = chrono_info[k][1 + 2 * i, :] + np.array([service_duration_reordered[k][i + 1], 0, -demand_reordered[k][i + 1], 0, 0])

            chrono_info[k][-1, :] = np.array([arrival_time_reordered[k][-1], 0, 0, coordinate_reordered[k][0, 0], coordinate_reordered[k][0, 1]])

            t = chrono_info[k][:, 0]
            node = chrono_info[k][:, 1]
            cargo = chrono_info[k][:, 2]
            if(t.shape[0] > 2):
                plt.subplot(1, 3, 2)
                plt.plot(t, node, label="vehicle " + str(k), marker=M[k // 10])
                plt.legend(loc="upper right")
                plt.subplot(1, 3, 3)
                plt.plot(t, cargo, label="vehicle " + str(k), marker=M[k // 10])
                plt.legend(loc="upper right")

        plt.subplot(1, 3, 1)
        plt.legend(loc="upper right")

    else:

        x = coordinate[:, 0]
        y = coordinate[:, 1]
        plt.subplot(1, 3, 1)
        plt.plot(x, y, "o")

    pretty_print(
        title,
        customer_quantity,
        is_feasible,
        objective_value,
        vehicle_quantity,
        vehicle_capacity,
        cost_per_distance,
        time_per_distance,
        solver_runtime,
        chrono_info,
        mip_gap
    )


    plt.subplot(1, 3, 1)
    plt.plot(coordinate[0, 0], coordinate[0, 1], marker="o", color='0.5', markersize=10)
    plt.grid(True)
    plt.xlabel("X", fontsize=16)
    plt.ylabel("Y", fontsize=16)
    plt.title("Activated Arcs", fontsize=16)

    plt.subplot(1, 3, 2)
    plt.grid(True)
    plt.xlabel("t", fontsize=16)
    plt.ylabel("Node", fontsize=16)
    plt.title("Node - Time", fontsize=16)

    plt.subplot(1, 3, 3)
    plt.grid(True)
    plt.xlabel("t", fontsize=16)
    plt.ylabel("Cargo", fontsize=16)
    plt.title("Cargo - Time", fontsize=16)

    plt.tight_layout()

    if(not os.path.exists("./result/fig")):
        os.mkdir("./result/fig")
    
    plt.savefig("./result/fig/" + title + ".pdf")

    if(show_plot):
        plt.show()


def plot_survey(results, category_names, file_type, height):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    plt.rcParams["font.family"] = "Times New Roman"

    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)
    category_colors = plt.colormaps['RdYlGn'](np.linspace(0.15, 0.85, data.shape[1]))

    fig, ax = plt.subplots(figsize=(9, height))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())

    for i, (colname, color) in enumerate(zip(category_names, category_colors)):
        widths = data[:, i]
        starts = data_cum[:, i] - widths
        rects = ax.barh(labels, widths, left=starts, height=.75,
                        label=colname, color=color)

        r, g, b, _ = color
        text_color = 'white' if r * g * b < 0.5 else 'darkgrey'
        # ax.bar_label(rects, label_type='center', color=text_color)
    ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
              loc='lower left', fontsize='small')
    
    plt.tight_layout()
    plt.savefig("./result/fig/distribution" + file_type + ".pdf")

    return fig, ax
