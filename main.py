from core import load_data, solve_VRPTW
import matplotlib.pyplot as plt

if __name__ == "__main__":

    coord, tw, d, service_dur, v_quant, v_cap = load_data("./dataset/simple/TW10.xml")                  # try TW10 and TW60

    is_feasible, obj, arcs, time = solve_VRPTW(coord, tw, d, service_dur, v_quant, v_cap, 1, 0.5, 1e6)  # try time per distance 1 and 0.5

    if(is_feasible):
        print(arcs)
        print(time)
        print(obj)

    else:
        print("not feasible")
