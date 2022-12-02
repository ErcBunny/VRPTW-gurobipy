import multiprocessing as mp
import os

from fileutil import load_raw_result, save_result_comparison
from visual import plot_solution, plot_survey


def load_and_plot(txtpath: str, show=True):
    
    name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap = load_raw_result(txtpath)  
    plot_solution(name, is_feasible, obj, arc, time, coord, tw, d, service_dur, v_quant, v_cap, cpd, tpd, runtime, gap, show)


if __name__ == "__main__":

    # plot and save figure, but do not show
    print("generating figures, check ./result/fig/. These figures should be combined with 'pretty' txt files")
    process = []
    for i in os.listdir("./result"):
        if(i[0:3] == "raw"):
            p = mp.Process(target=load_and_plot, args=("./result/" + str(i), False))
            p.start()
            process.append(p)

    for p in process:
        p.join()

    # plot selected ones
    print("showing results of small scenarios")
    process = []

    p = mp.Process(target=load_and_plot, args=("./result/raw-TW10-TPD0.5.txt",))
    process.append(p)

    p = mp.Process(target=load_and_plot, args=("./result/raw-TW10-TPD1.0.txt",))
    process.append(p)

    p = mp.Process(target=load_and_plot, args=("./result/raw-TW60-TPD0.5.txt",))
    process.append(p)

    p = mp.Process(target=load_and_plot, args=("./result/raw-TW60-TPD1.0.txt",))
    process.append(p)

    for p in process:
        p.start()

    # update result comparison with SOTA2005
    survey_data, survey_data_size, categories = save_result_comparison()
    print("saved comparison with SOTA2005 to ./result/comparison.txt")

    # save
    plot_survey(survey_data, categories, "", 2)
    plot_survey(survey_data_size, categories, "_size", 1.25)

    for p in process:
        p.join()
