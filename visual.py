import numpy as np
import matplotlib.pyplot as plt

def save_pretty_result(
    filepath: str,
    is_feasible: bool,
    objective_value: float,
    vehicle_quantity: float,
    vehicle_capacity: float,
    cost_per_distance: float,
    time_per_distance: float,
    solver_runtime: float,
    arrival_time_reordered: list,
    coordinate_reordered: list,
    time_window_reordered: list,
    demand_reordered: list,
    service_duration_reordered: list,
    node_sequence: list
):

    todo = True


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
    solver_runtime: float
):
    """
    if the problem is feasible, plot all the results

    otherwise only plot the problem setting

    no return values, this function blocks later commands until the graph is closed

    """

    node_quantity = coordinate.shape[0]
    customer_quantity = node_quantity - 2
    N = range(node_quantity)
    C = range(1, customer_quantity + 1)
    V = range(vehicle_quantity)

    plt.figure(title)
    M = ["o", "s", "D", "P", "X", "^", "v"]

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
                plt.plot(x, y, label="vehicle " + str(k), marker=M[k // 10])

        plt.title("Objective Value: " + str(round(objective_value, 2)))
        plt.legend()

    else:

        x = coordinate[:, 0]
        y = coordinate[:, 1]
        plt.plot(x, y, "o")
        plt.title("Problem not feasible")
    
    plt.plot(coordinate[0, 0], coordinate[0, 1], marker="o", color='0.5', markersize=10)
    plt.grid(True)
    plt.xlabel("X")
    plt.ylabel("Y")

    save_pretty_result(
        "./result/" + title + "-pretty.txt",
        
    )
    plt.show()