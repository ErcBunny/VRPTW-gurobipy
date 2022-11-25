import math
import os
import xml.etree.ElementTree as ET

import numpy as np
from tabulate import tabulate

import SOTA2005


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
    
    f.close()


def load_pretty_result(txtpath: str):
    try:
        f = open(txtpath)
    except:
        print("Cannot find file")
        exit()

    feasible = False
    solver_runtime = 0
    obj = 0
    mip_gap = 0
    activated_vehicle = 0

    v_separation = "------------------------------------------------------------------------------------"
    while True:
        line = f.readline().strip("\n")
        if not line:
            break
        if(line[0:10] == "feasible: "):
            feasible = bool(line[10:] == "True")
        if(line[0:16] == "solver runtime: "):
            solver_runtime = float(line[16:])
        if(line[0:26] == "objective function value: "):
            obj = float(line[26:])
        if(line[0:9] == "MIP gap: "):
            mip_gap = float(line[9:])
        if(line == v_separation):
            activated_vehicle += 1
    
    activated_vehicle -= 1

    if(not feasible):
        mip_gap = math.nan
        obj = math.nan
        activated_vehicle = math.nan

    if(mip_gap < 1e-4 and solver_runtime < 3559):
        mip_gap = 0
    
    f.close()

    return activated_vehicle, obj, solver_runtime, mip_gap


def append_row_names(table: np.ndarray, setname: str):
    i = 0
    while(i < table.shape[0]):
        if i//3 < 10:
            table[i, 0] = setname.upper() + "0" + str(i//3 + 1) + "_025"
            table[i + 1, 0] = setname.upper() + "0" + str(i//3 + 1) + "_050"
            table[i + 2, 0] = setname.upper() + "0" + str(i//3 + 1) + "_100"
        else:
            table[i, 0] = setname.upper() + str(i//3 + 1) + "_025"
            table[i + 1, 0] = setname.upper() + str(i//3 + 1) + "_050"
            table[i + 2, 0] = setname.upper() + str(i//3 + 1) + "_100"
        i += 3


def save_result_comparison():
    dist_c1, v_num_c1, dist_c2, v_num_c2, dist_r1, v_num_r1, dist_r2, v_num_r2, dist_rc1, v_num_rc1, dist_rc2, v_num_rc2 = SOTA2005.get_results()
    
    v_c1 = []   # total number of used vehicle
    d_c1 = []   # total distance (obj)
    t_c1 = []   # solver runtime
    g_c1 = []   # mip gap

    v_c2 = []
    d_c2 = []
    t_c2 = []
    g_c2 = []

    v_r1 = []
    d_r1 = []
    t_r1 = []
    g_r1 = []

    v_r2 = []
    d_r2 = []
    t_r2 = []
    g_r2 = []

    v_rc1 = []
    d_rc1 = []
    t_rc1 = []
    g_rc1 = []

    v_rc2 = []
    d_rc2 = []
    t_rc2 = []
    g_rc2 = []

    files = sorted(os.listdir("./result"))
    for i in files:
        if(i[0:6] == "pretty"):
            v, d, t, g = load_pretty_result("./result/" + str(i))
            if(i[0:9] == "pretty-C1"):
                v_c1.append(v)
                d_c1.append(d)
                t_c1.append(t)
                g_c1.append(g)
            if(i[0:9] == "pretty-C2"):
                v_c2.append(v)
                d_c2.append(d)
                t_c2.append(t)
                g_c2.append(g)
            if(i[0:9] == "pretty-R1"):
                v_r1.append(v)
                d_r1.append(d)
                t_r1.append(t)
                g_r1.append(g)
            if(i[0:9] == "pretty-R2"):
                v_r2.append(v)
                d_r2.append(d)
                t_r2.append(t)
                g_r2.append(g)
            if(i[0:10] == "pretty-RC1"):
                v_rc1.append(v)
                d_rc1.append(d)
                t_rc1.append(t)
                g_rc1.append(g)
            if(i[0:10] == "pretty-RC2"):
                v_rc2.append(v)
                d_rc2.append(d)
                t_rc2.append(t)
                g_rc2.append(g)

    v_c1 = np.array(v_c1)[..., None]
    d_c1 = np.array(d_c1)[..., None]
    t_c1 = np.array(t_c1)[..., None]
    g_c1 = np.array(g_c1)[..., None]
    name_c1 = np.empty_like(v_c1, dtype=str)

    v_c2 = np.array(v_c2)[..., None]
    d_c2 = np.array(d_c2)[..., None]
    t_c2 = np.array(t_c2)[..., None]
    g_c2 = np.array(g_c2)[..., None]
    name_c2 = np.empty_like(v_c2, dtype=str)


    v_r1 = np.array(v_r1)[..., None]
    d_r1 = np.array(d_r1)[..., None]
    t_r1 = np.array(t_r1)[..., None]
    g_r1 = np.array(g_r1)[..., None]
    name_r1 = np.empty_like(v_r1, dtype=str)


    v_r2 = np.array(v_r2)[..., None]
    d_r2 = np.array(d_r2)[..., None]
    t_r2 = np.array(t_r2)[..., None]
    g_r2 = np.array(g_r2)[..., None]
    name_r2 = np.empty_like(v_r2, dtype=str)


    v_rc1 = np.array(v_rc1)[..., None]
    d_rc1 = np.array(d_rc1)[..., None]
    t_rc1 = np.array(t_rc1)[..., None]
    g_rc1 = np.array(g_rc1)[..., None]

    name_rc1 = np.empty_like(v_rc1, dtype=str)


    v_rc2 = np.array(v_rc2)[..., None]
    d_rc2 = np.array(d_rc2)[..., None]
    t_rc2 = np.array(t_rc2)[..., None]
    g_rc2 = np.array(g_rc2)[..., None]
    name_rc2 = np.empty_like(v_rc2, dtype=str)

    table_c1 = np.hstack((name_c1, v_c1, v_num_c1, d_c1, dist_c1, g_c1, t_c1))
    append_row_names(table_c1, "c1")

    table_c2 = np.hstack((name_c2, v_c2, v_num_c2, d_c2, dist_c2, g_c2, t_c2))
    append_row_names(table_c2, "c2")

    table_r1 = np.hstack((name_r1, v_r1, v_num_r1, d_r1, dist_r1, g_r1, t_r1))
    append_row_names(table_r1, "r1")

    table_r2 = np.hstack((name_r2, v_r2, v_num_r2, d_r2, dist_r2, g_r2, t_r2))
    append_row_names(table_r2, "r2")

    table_rc1 = np.hstack((name_rc1, v_rc1, v_num_rc1, d_rc1, dist_rc1, g_rc1, t_rc1))
    append_row_names(table_rc1, "rc1")

    table_rc2 = np.hstack((name_rc2, v_rc2, v_num_rc2, d_rc2, dist_rc2, g_rc2, t_rc2))
    append_row_names(table_rc2, "rc2")

    table_header = ["Problem", "Vehicle", "Vehicle (SOTA)", "Distance", "Distance (SOTA)", "MIP Gap", "Solver Runtime"]
    if(not os.path.exists("./result")):
        os.mkdir("result")
    f = open("./result/comparision.txt", "w")

    print("=========================================================================================================", file=f)
    print(tabulate(table_c1, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_c1, table_header, tablefmt="latex"), file=f)

    print("=========================================================================================================", file=f)
    print(tabulate(table_c2, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_c2, table_header, tablefmt="latex"), file=f)

    print("=========================================================================================================", file=f)
    print(tabulate(table_r1, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_r1, table_header, tablefmt="latex"), file=f)

    print("=========================================================================================================", file=f)
    print(tabulate(table_r2, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_r2, table_header, tablefmt="latex"), file=f)

    print("=========================================================================================================", file=f)
    print(tabulate(table_rc1, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_rc1, table_header, tablefmt="latex"), file=f)

    print("=========================================================================================================", file=f)
    print(tabulate(table_rc2, table_header), file=f)
    print('\n', file=f)
    print(tabulate(table_rc2, table_header, tablefmt="latex"), file=f)

    f.close()
