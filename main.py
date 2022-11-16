from core import load_dataset, solve_VRPTW, save_raw_result, load_raw_result
from visual import plot_solution
import multiprocessing as mp

def solve_and_plot(xmlpath: str, cpd: float, tpd: float, big_m: float, name: str):

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

    # simple tests
    p0 = mp.Process(target=solve_and_plot, args=("./dataset/simple/TW10.xml", 1, 0.5, 1e6, "TW10-TPD0.5"))
    p1 = mp.Process(target=solve_and_plot, args=("./dataset/simple/TW10.xml", 1, 1.0, 1e6, "TW10-TPD1.0"))
    p2 = mp.Process(target=solve_and_plot, args=("./dataset/simple/TW60.xml", 1, 0.5, 1e6, "TW60-TPD0.5"))
    p3 = mp.Process(target=solve_and_plot, args=("./dataset/simple/TW60.xml", 1, 1.0, 1e6, "TW60-TPD1.0"))

    p0.start()
    p1.start()
    p2.start()
    p3.start()

    p0.join()
    p1.join()
    p2.join()
    p3.join()

    