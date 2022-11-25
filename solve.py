from core import solve_VRPTW
from fileutil import load_dataset, save_raw_result
from visual import plot_solution


def solve_and_save(xmlpath: str, cpd: float, tpd: float, big_m: float, tlimit:float, name: str):

    coord, tw, d, service_dur, v_quant, v_cap = load_dataset(xmlpath)
    is_feasible, obj, arc, time, runtime, gap = solve_VRPTW(coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, big_m, tlimit)

    save_raw_result(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap)
    plot_solution(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap, False)


def solve_solomon(setname: str, cpd: float, tpd: float, big_m: float, tlimit: float, start: int, end: int):

    I = range(start, end + 1)
    for i in I:
        print("======================================================")
        print(setname, i)
        print("======================================================")
        if i < 10:
            xmlpath_25 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + "0" + str(i) + "_025.xml"
            xmlpath_50 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + "0" + str(i) + "_050.xml"
            xmlpath_100 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + "0" + str(i) + "_100.xml"
            solve_and_save(xmlpath_25, cpd, tpd, big_m, tlimit, setname.upper() + "0" + str(i) + "_025")
            solve_and_save(xmlpath_50, cpd, tpd, big_m, tlimit, setname.upper() + "0" + str(i) + "_050")
            solve_and_save(xmlpath_100, cpd, tpd, big_m, tlimit, setname.upper() + "0" + str(i) + "_100")
        else:
            xmlpath_25 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + str(i) + "_025.xml"
            xmlpath_50 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + str(i) + "_050.xml"
            xmlpath_100 = "./dataset/solomon-1987-" + setname + "/" + setname.upper() + str(i) + "_100.xml"
            solve_and_save(xmlpath_25, cpd, tpd, big_m, tlimit, setname.upper() + str(i) + "_025")
            solve_and_save(xmlpath_50, cpd, tpd, big_m, tlimit, setname.upper() + str(i) + "_050")
            solve_and_save(xmlpath_100, cpd, tpd, big_m, tlimit, setname.upper() + str(i) + "_100")


def solve_simple_test():

    solve_and_save("./dataset/simple/TW10.xml", 1, 0.5, 1e6, 3600, "TW10-TPD0.5")
    solve_and_save("./dataset/simple/TW10.xml", 1, 1.0, 1e6, 3600, "TW10-TPD1.0")
    solve_and_save("./dataset/simple/TW60.xml", 1, 0.5, 1e6, 3600, "TW60-TPD0.5")
    solve_and_save("./dataset/simple/TW60.xml", 1, 1.0, 1e6, 3600, "TW60-TPD1.0")


if __name__ == "__main__":

    solve_simple_test()
    solve_solomon("c1", 1, 1, 1e6, 3600, 1, 9)
    solve_solomon("c2", 1, 1, 1e6, 3600, 1, 8)
    solve_solomon("r1", 1, 1, 1e6, 3600, 1, 12)
    solve_solomon("r2", 1, 1, 1e6, 3600, 1, 11)
    solve_solomon("rc1", 1, 1, 1e6, 3600, 1, 3)
    solve_solomon("rc2", 1, 1, 1e6, 3600, 1, 8)
