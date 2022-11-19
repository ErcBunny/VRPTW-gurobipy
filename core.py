from gurobipy import Model, GRB, quicksum
import numpy as np
import xml.etree.ElementTree as ET
import os


def solve_VRPTW(
    coordinate: np.ndarray,
    time_window: np.ndarray,
    demand: np.ndarray,
    service_duration: np.ndarray,
    vehicle_quantity: int,
    vehicle_capacity: float,
    cost_per_distance: float,
    time_per_distance: float,
    big_m: float,
    timelimit: float
):
    """
    node quantity = customer quantity + 2 = n + 2

    the starting depot is node 0 and the ending depot is node n + 1

    time window for node 0 should be [0, 0] and for node n + 1 should be [0, max operating time]

    return: is_feasible, objective value, arc matrix, arrival time matrixd

    """

    node_quantity = coordinate.shape[0]
    customer_quantity = node_quantity - 2

    N = range(node_quantity)
    C = range(1, customer_quantity + 1)
    V = range(vehicle_quantity)

    distance = np.zeros([node_quantity, node_quantity])
    for i in N:
        for j in N:
            if i == j:
                distance[i, j] = big_m
            else:
                distance[i, j] = np.hypot(coordinate[i, 0] - coordinate[j, 0], coordinate[i, 1] - coordinate[j, 1])
    
    travel_time = np.zeros([node_quantity, node_quantity])
    for i in N:
        for j in N:
            travel_time[i, j] = time_per_distance * np.hypot(coordinate[i, 0] - coordinate[j, 0], coordinate[i, 1] - coordinate[j, 1])

    model = Model("VRPTW")
    x = model.addVars(node_quantity, node_quantity, vehicle_quantity, vtype=GRB.BINARY)
    s = model.addVars(node_quantity, vehicle_quantity, vtype=GRB.CONTINUOUS)

    model.modelSense = GRB.MINIMIZE
    model.setObjective(quicksum(x[i, j, k] * distance[i, j] * cost_per_distance for i in N for j in N for k in V))

    model.addConstrs(quicksum(x[i, j, k] for j in N for k in V) == 1 for i in C)
    model.addConstrs(quicksum(x[0, j, k] for j in N) == 1 for k in V)
    model.addConstrs(quicksum(x[i, customer_quantity + 1, k] for i in N) == 1 for k in V)
    model.addConstrs(quicksum(x[i, h, k] for i in N) - quicksum(x[h, j, k] for j in N) == 0 for h in C for k in V)
    model.addConstrs(quicksum(demand[i] * quicksum(x[i, j, k] for j in N) for i in C) <= vehicle_capacity for k in V)
    model.addConstrs(s[i, k] >= time_window[i, 0] for i in N for k in V)
    model.addConstrs(s[i, k] <= time_window[i, 1] for i in N for k in V)
    model.addConstrs(s[i, k] + travel_time[i, j] + service_duration[i] - big_m * (1 - x[i, j, k]) <= s[j, k] for i in N for j in N for k in V)

    model.Params.Timelimit = timelimit
    model.optimize()

    is_feasible = True
    obj = 0
    runtime = model.Runtime
    mip_gap = GRB.INFINITY
    result_arc = np.zeros([vehicle_quantity, node_quantity, node_quantity], dtype=int)
    result_arrival_time = np.zeros([node_quantity, vehicle_quantity])

    for k in V:
        for i in N:
            for j in N:
                try:
                    result_arc[k, i, j] = round(x[i, j, k].X)
                except:
                    is_feasible = False
                    break

    for k in V:
        for i in N:
            try:
                result_arrival_time[i, k] = s[i, k].X
            except:
                is_feasible = False
                break

    try:
        obj = model.getObjective().getValue()
        mip_gap = model.MIPGap
    except:
        is_feasible = False


    return is_feasible, obj, result_arc, result_arrival_time, runtime, mip_gap


def load_dataset(xmlpath: str):
    """
    get processed (node 0 and node n + 1 added) matrices from xml datasets

    assume node 0 is the depot in the xml file

    return: coordinate, time_window, demand, service_duration, vehicle_quantity, vehicle_capacity

    """
    
    try:
        tree = ET.parse(xmlpath)
    except:
        print("Cannot find file")
        exit()
    
    root = tree.getroot()

    coordinate = np.zeros([1, 2])
    first_iter = True
    for node in root.iter("node"):
        if first_iter:
            first_iter = False
            coordinate = np.array([float(node.find("cx").text), float(node.find("cy").text)])
        else:
            coordinate = np.vstack((coordinate, np.array([float(node.find("cx").text), float(node.find("cy").text)])))
    coordinate = np.vstack((coordinate, coordinate[0, :]))

    time_window = np.zeros([1, 2])
    demand = np.array(0)
    service_duration = np.array(0)
    for request in root.iter("request"):
        time_window = np.vstack((
            time_window,
            np.array([float(request.find("tw").find("start").text), float(request.find("tw").find("end").text)])
        ))
        demand = np.append(demand, float(request.find("quantity").text))
        service_duration = np.append(service_duration, float(request.find("service_time").text))
    time_window = np.vstack((time_window, np.array([0, float(root.find("fleet").find("vehicle_profile").find("max_travel_time").text)])))
    demand = np.append(demand, 0)
    service_duration = np.append(service_duration, 0)
    
    vehicle_quantity = int(root.find("fleet").find("vehicle_profile").get("number"))

    vehicle_capacity = float(root.find("fleet").find("vehicle_profile").find("capacity").text)

    return coordinate, time_window, demand, service_duration, vehicle_quantity, vehicle_capacity


def save_raw_result(
    name: str,
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
    mip_gap: float
):

    node_quantity = coordinate.shape[0]
    customer_quantity = node_quantity - 2
    N = range(node_quantity)
    C = range(1, customer_quantity + 1)
    V = range(vehicle_quantity)

    if(not os.path.exists("./result")):
        os.mkdir("result")
    f = open("./result/raw-" + name + ".txt", "w")
    print(name, file=f)
    print(is_feasible, file=f)
    print(objective_value, file=f)
    print(mip_gap, file=f)
    print(node_quantity, file=f)
    print(vehicle_quantity, file=f)
    print(vehicle_capacity, file=f)
    print(cost_per_distance, file=f)
    print(time_per_distance, file=f)
    print(solver_runtime, file=f)

    for k in V:
        for i in N:
            for j in N:
                print(arc[k, i, j], file=f)

    for k in V:
        for i in N:
            print(arrival_time[i, k], file=f)

    for i in N:
        print(coordinate[i, 0], file=f)
        print(coordinate[i, 1], file=f)

    for i in N:
        print(time_window[i, 0], file=f)
        print(time_window[i, 1], file=f)

    for i in N:
        print(demand[i], file=f)

    for i in N:
        print(service_duration[i], file=f)

    f.close()
        

def load_raw_result(txtpath: str):

    try:
        f = open(txtpath)
    except:
        print("Cannot find file")
        exit()

    name = str(f.readline().strip("\n"))
    is_feasible = bool(f.readline().strip("\n") == "True")
    objective_value = float(f.readline())
    mip_gap = float(f.readline())
    node_quantity = int(f.readline())
    vehicle_quantity = int(f.readline())
    vehicle_capacity = float(f.readline())
    cost_per_distance = float(f.readline())
    time_per_distance = float(f.readline())
    solver_runtime = float(f.readline())

    customer_quantity = node_quantity - 2
    N = range(node_quantity)
    C = range(1, customer_quantity + 1)
    V = range(vehicle_quantity)

    arc = np.zeros([vehicle_quantity, node_quantity, node_quantity], dtype=int)
    for k in V:
        for i in N:
            for j in N:
                arc[k, i, j] = int(f.readline())

    arrival_time = np.zeros([node_quantity, vehicle_quantity])
    for k in V:
        for i in N:
            arrival_time[i, k] = float(f.readline())

    coordinate = np.zeros([node_quantity, 2])
    for i in N:
        coordinate[i, 0] = float(f.readline())
        coordinate[i, 1] = float(f.readline())
        
    time_window = np.zeros([node_quantity, 2])
    for i in N:
        time_window[i, 0] = float(f.readline())
        time_window[i, 1] = float(f.readline())

    demand = np.zeros(node_quantity)
    for i in N:
        demand[i] = f.readline()

    service_duration = np.zeros(node_quantity)
    for i in N:
        service_duration[i] = f.readline()

    f.close()

    return name, is_feasible, objective_value, arc, arrival_time, coordinate, time_window, demand, service_duration, vehicle_quantity, vehicle_capacity, cost_per_distance, time_per_distance, solver_runtime, mip_gap
