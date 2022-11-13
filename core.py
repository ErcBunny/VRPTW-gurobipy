def solve_VRPTW(coordinate, time_window, demand, service_duration, vehicle_quantity, vehicle_capacity, cost_per_distance, time_per_distance, big_m):
    """
    node quantity = customer quantity + 2 = n + 2

    the starting depot is node 0 and the ending depot is node n + 1

    time window for node 0 should be [0, 0] and for node n + 1 should be [0, max operating time]

    return: is_feasible, objective value, arcs matrix, arrival time matrixd

    """

    from gurobipy import Model, GRB, quicksum
    import numpy as np

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

    model.optimize()

    is_feasible = True
    obj = 0
    result_arcs = np.zeros([vehicle_quantity, node_quantity, node_quantity], dtype=int)
    result_arrival_time = np.zeros([node_quantity, vehicle_quantity])

    for k in V:
        for i in N:
            for j in N:
                try:
                    result_arcs[k, i, j] = round(x[i, j, k].X)
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
    except:
        is_feasible = False

    return is_feasible, obj, result_arcs, result_arrival_time


def load_data(xmlpath):
    """
    get processed (node 0 and node n + 1 added) matrices from xml datasets

    assume node 0 is the depot in the xml file

    return: coordinate, time_window, demand, service_duration, vehicle_quantity, vehicle_capacity

    """

    import numpy as np
    import xml.etree.ElementTree as ET
    
    try:
        tree = ET.parse(xmlpath)
    except:
        print("Cannot find file")
        return
    
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
    demand = np.array([0])
    service_duration = np.array([0])
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
