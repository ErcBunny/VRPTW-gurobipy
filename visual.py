import numpy as np
import matplotlib.pyplot as plt
import os


def pretty_print(
    title: str,
    customer_quantity: int,
    is_feasible: bool,
    objective_value: float,
    vehicle_quantity: float,
    vehicle_capacity: float,
    cost_per_distance: float,
    time_per_distance: float,
    solver_runtime: float,
    chrono_info: list,
    mip_gap: float,
):

    V = range(vehicle_quantity)

    if(not os.path.exists("./result")):
        os.mkdir("result")
    f = open("./result/pretty-" + title + ".txt", "w")
    print(title, file=f)
    print("====================================================================================", file=f)
    print("customer quantity:", customer_quantity, file=f)
    print("vehicle quantity:", vehicle_quantity, file=f)
    print("vehicle capacity:", vehicle_capacity, file=f)
    print("cost per distance:", cost_per_distance, file=f)
    print("time per distance:", time_per_distance, file=f)
    print("====================================================================================", file=f)
    print("feasible:", is_feasible, file=f)
    print("solver runtime:", solver_runtime, file=f)
    if(is_feasible):
        print("objective function value:", objective_value, file=f)
        print("MIP gap:", mip_gap, file=f)
        print("====================================================================================", file=f)
        print("{:<13} {:<13} {:<13} {:<13} {:<13} {:<13}".format("|vehicle no.", "|time", "|node no.", "|cargo", "|X", "|Y"), file=f)
        print("------------------------------------------------------------------------------------", file=f)
        for k in V:
            if(chrono_info[k].shape[0] > 2):
                for i in range(chrono_info[k].shape[0]):
                    print(
                        "{:<13} {:<13} {:<13} {:<13} {:<13} {:<13}".format(
                            "|" + str(k),
                            "|" + str(round(chrono_info[k][i, 0], 3)),
                            "|" + str(int(chrono_info[k][i, 1])),
                            "|" + str(chrono_info[k][i, 2]),
                            "|" + str(chrono_info[k][i, 3]),
                            "|" + str(chrono_info[k][i, 4])
                        ),
                        file=f
                    )
                print("------------------------------------------------------------------------------------", file=f)
    

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

    if(show_plot):
        plt.figure(title)
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
            if(show_plot):
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
            if(show_plot):
                if(t.shape[0] > 2):
                    plt.subplot(1, 3, 2)
                    plt.plot(t, node, label="vehicle " + str(k), marker=M[k // 10])
                    plt.legend(loc="upper right")
                    plt.subplot(1, 3, 3)
                    plt.plot(t, cargo, label="vehicle " + str(k), marker=M[k // 10])
                    plt.legend(loc="upper right")

        if(show_plot):
            plt.subplot(1, 3, 1)
            plt.legend(loc="upper right")

    else:

        x = coordinate[:, 0]
        y = coordinate[:, 1]
        if(show_plot):
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

    if(show_plot):

        plt.subplot(1, 3, 1)
        plt.plot(coordinate[0, 0], coordinate[0, 1], marker="o", color='0.5', markersize=10)
        plt.grid(True)
        plt.xlabel("X")
        plt.ylabel("Y")
        plt.title("Activated Arcs")

        plt.subplot(1, 3, 2)
        plt.grid(True)
        plt.xlabel("t")
        plt.ylabel("Node")
        plt.title("Node - Time")

        plt.subplot(1, 3, 3)
        plt.grid(True)
        plt.xlabel("t")
        plt.ylabel("Cargo")
        plt.title("Cargo - Time")

        plt.show()
