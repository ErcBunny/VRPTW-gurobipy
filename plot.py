from core import load_raw_result
from visual import plot_solution
import multiprocessing as mp
import os


def load_and_plot(txtpath: str):
    
    name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap = load_raw_result(txtpath)  
    plot_solution(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap, True)


if __name__ == "__main__":

    process = []
    for i in os.listdir("./result"):
        if(i[0:3] == "raw"):
            print(i)
            p = mp.Process(target=load_and_plot, args=("./result/" + str(i),))
            p.start()
            process.append(p)

    for p in process:
        p.join()