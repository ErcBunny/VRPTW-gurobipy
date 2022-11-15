from core import load_dataset, solve_VRPTW, save_raw_result, load_raw_result
from visual import plot_solution
import multiprocessing as mp

def solve_dataset(xmlpath: str, cpd: float, tpd: float, big_m: float, name: str):

    coord, tw, d, service_dur, v_quant, v_cap = load_dataset(xmlpath)
    is_feasible, obj, arc, time, runtime = solve_VRPTW(coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, big_m)

    save_raw_result(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime)
    plot_solution(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime)


def solve_and_save(xmlpath: str, cpd: float, tpd: float, big_m: float, name: str):

    coord, tw, d, service_dur, v_quant, v_cap = load_dataset(xmlpath)
    is_feasible, obj, arc, time, runtime = solve_VRPTW(coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, big_m)

    save_raw_result(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime)


def load_and_plot(txtpath: str):
    
    name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime = load_raw_result(txtpath)    
    plot_solution(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime)


if __name__ == "__main__":

    p0 = mp.Process(target=solve_dataset, args=("./dataset/simple/TW10.xml", 1, 0.5, 1e6, "TW10-0.5"))
    p1 = mp.Process(target=solve_dataset, args=("./dataset/simple/TW10.xml", 1, 1.0, 1e6, "TW10-1.0"))
    p2 = mp.Process(target=solve_dataset, args=("./dataset/simple/TW60.xml", 1, 0.5, 1e6, "TW60-0.5"))
    p3 = mp.Process(target=solve_dataset, args=("./dataset/simple/TW60.xml", 1, 1.0, 1e6, "TW60-1.0"))
    p4 = mp.Process(target=solve_dataset, args=("./dataset/solomon-1987-r1/R101_025.xml", 1, 1.0, 1e6, "R101_025-1.0"))
    p5 = mp.Process(target=solve_dataset, args=("./dataset/solomon-1987-r2/R201_100.xml", 1, 1.0, 1e6, "R201_100-1.0"))

    # p0.start()
    # p1.start()
    # p2.start()
    # p3.start()
    # p4.start()
    # p5.start()

    # p0.join()
    # p1.join()
    # p2.join()
    # p3.join()
    # p4.join()
    # p5.join()

    # solve_and_save("./dataset/simple/TW10.xml", 1, 0.5, 1e6, "TW10-0.5")
    # solve_and_save("./dataset/simple/TW10.xml", 1, 1.0, 1e6, "TW10-1.0")
    # solve_and_save("./dataset/simple/TW60.xml", 1, 0.5, 1e6, "TW10-0.5")
    # solve_and_save("./dataset/simple/TW60.xml", 1, 1.0, 1e6, "TW60-1.0")

    # load_and_plot("./result/TW10-0.5.txt")
    # load_and_plot("./result/TW10-1.0.txt")
    # load_and_plot("./result/TW60-0.5.txt")
    # load_and_plot("./result/TW60-1.0.txt")
    # load_and_plot("./result/R101_025-1.0.txt")
