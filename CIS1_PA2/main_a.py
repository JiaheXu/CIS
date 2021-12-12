#!/usr/bin/env python
#Used specifically for a due to the fact that it does not have a opt_pivot file.
from genericpath import exists
import numpy as np
import glob
from distort_calibration import *
from cartesian import *
from registration_3d import *
from optical_tracking import *
from em_tracking import *
from eval import *
from pathlib import Path
import argparse
import csv
from improved_em_tracking import *
from fiducials import *

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir",
        type=str,
        help="path to data directory",
    )
    parser.add_argument(
        "runtype",
        type=int,
        help="0 for debug, 1 for unknown",
    )
    parser.add_argument(
        "letter",
        type=int,
        help="index of the letter",
    )

    parser.add_argument(
        "output_dir",
        type=str,
        help="path to output directory(automatically created if does not exist)",
    )

    parser.add_argument(
        "--eval",
        type=bool,
        default=False,
        help="Whether to evaluate or not"
    )

    return parser.parse_args()


def main():

    args = parse_args()
    runtype = args.runtype
    run = args.letter
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j']
    type = ['debug', 'unknown']
    data_dir = args.data_dir
    # first read in Calbody (Nd, Na, Nc)
    # then readings  (ND, NA, NC, nframes)
    
    # the last output determines whether to show the result in terminal
    em_pivot = em_tracking( data_dir , "pa2-", type[runtype] , letters[run] , output = 0)
    # optical_pivot = optical_tracking( data_dir , "pa2-", type[runtype] , letters[run] , output = 0)
    #Added improved_em_tracking file instead of the original
    em_pivot = improved_em_tracking(data_dir, "pa2-", type[runtype] , letters[run], output=0)[1]
    optical_pivot = np.zeros((1, 3))
    tmp_ce = distort_calibration( data_dir , "pa2-", type[runtype] , letters[run] ,output = 0)
    C_exp = tmp_ce[0]
    Nc = tmp_ce[1]
    Nframes = tmp_ce[2]
    # print(optical_pivot.shape)
    ep = np.transpose(em_pivot)
    op = np.transpose(optical_pivot)
    # print(em_pivot)
    # print(optical_pivot)
    em_rounded = np.round(em_pivot.reshape(3), decimals=2)
    opt_rounded = np.round(optical_pivot.reshape(3), decimals=2)
    C_exp_rounded = np.round(C_exp, decimals=2)
    
    #Reading input from the output1 files instead to reduce possible errors in our own code
    output_name = 'pa2-' + type[runtype] + '-' + letters[run] + '-output1.txt'
    output_dir = args.output_dir
    if not (os.path.exists(os.path.join(os.getcwd(), output_dir))):
        os.mkdir(output_dir)
    output_path = os.path.join(args.output_dir, output_name)
    headers = [str(Nc), '\t' + str(Nframes), '\t' + str(output_name)]

    with open(output_path, mode='a') as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerow(em_rounded)
        writer.writerow(opt_rounded)
        writer.writerows(C_exp_rounded)

    output_path = glob.glob(data_dir + "pa2-" + type[runtype] + '-' + letters[run] + '-output1.txt')
    output_data = []
    read_file = open(output_path[0], mode='r')
    lines = read_file.read().splitlines()
    for num in range(len(lines)):
        output_data.append( lines[num].split(',') )
        for i in range(len(output_data[-1])):
            output_data[-1][i] = output_data[-1][i].strip()
    Nc = int(output_data[0][0])
    Nframes = int(output_data[0][1])
    output_name = output_data[0][2]
    C_expected = np.asarray(output_data[3:]).astype(float)
    # print(output_data.shape)
    
    #Calculating correction
    C_exp, Nc, Nframes,C = distort_calibration( data_dir ,"pa2-", type[runtype] , letters[run], output = 0 )    
    X, qmin, qmax = distortion_correction(C, C_expected, order=5)
    #Calculating F_reg with improved tracking and em_ct
    empivot = improved_em_tracking(data_dir, "pa2-", type[runtype] , letters[run], output=0)
    F_reg = em_ct(data_dir,"pa2-", type[runtype] , letters[run],X, qmin, qmax,empivot)
    #Producing results and saving the initial points for evaluation purposes.
    ct_results = em_nav2ct( data_dir,"pa2-", type[runtype] , letters[run], F_reg , X, qmin, qmax,empivot, output=0)
    ct_points = ct_results[0]
    pivot_set = ct_results[1]
    ct_rounded = np.round(ct_points, decimals=2)

    
    Nframes = len(ct_rounded)
    output_name = 'pa2-' + type[runtype] + '-' + letters[run] + '-output2.txt'
    output_dir = args.output_dir
    output_path = os.path.join(args.output_dir, output_name)
    headers = [str(Nframes), '\t' + str(output_name)]

    
    with open(output_path, mode='a') as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerow(headers)
        # writer.writerow(em_rounded)
        # writer.writerow(opt_rounded)
        writer.writerows(ct_rounded)
    # print(em_pivot, optical_pivot)
    # print(Nc, Nframes)

    if args.eval:
        tmp = eval( data_dir , type[runtype] , letters[run] , C_exp_rounded, em_rounded.reshape(3, 1), opt_rounded.reshape(3, 1), ct_rounded, F_reg, pivot_set)
        str_tmp = [str(float(x)) for x in tmp]
        log_dir = "eval_logs"
        if not (os.path.exists(os.path.join(os.getcwd(), log_dir))):
            os.mkdir(log_dir)
        logs_name = 'pa2-' + type[runtype] + '-' + letters[run] + '-eval_logs.txt'
        
        logs_lst = []

        logs_lst.append(("Average for difference of C_exp = " + str_tmp[0]))
        logs_lst.append(("Variance for difference of C_exp = " + str_tmp[1]))
        logs_lst.append(("Max for difference of C_exp = " + str_tmp[2]))
        logs_lst.append(("Min for difference of C_exp = " + str_tmp[3]))
        logs_lst.append("\n")
        logs_lst.append(("Average for difference of em_pivot = " + str_tmp[4]))
        logs_lst.append(("Variance for difference of em_pivot = " + str_tmp[5]))
        logs_lst.append(("Max for difference of em_pivot = " + str_tmp[6]))
        logs_lst.append(("Min for difference of em_pivot = " + str_tmp[7]))
        logs_lst.append("\n")
        logs_lst.append(("Average for difference of opt_pivot = " + str_tmp[8]))
        logs_lst.append(("Variance for difference of opt_pivot = " + str_tmp[9]))
        logs_lst.append(("Max for difference of opt_pivot = " + str_tmp[10]))
        logs_lst.append(("Min for difference of opt_pivot = " + str_tmp[11]))
        logs_lst.append("\n")
        logs_lst.append(("Average for difference of ct_points = " + str_tmp[12]))
        logs_lst.append(("Variance for difference of ct_points = " + str_tmp[13]))
        logs_lst.append(("Max for difference of ct_points = " + str_tmp[14]))
        logs_lst.append(("Min for difference of ct_points = " + str_tmp[15]))
        logs_lst.append("\n")
        logs_lst.append(("Average for difference of F_reg = " + str_tmp[16]))
        logs_lst.append(("Variance for difference of F_reg = " + str_tmp[17]))
        logs_lst.append(("Max for difference of F_reg = " + str_tmp[18]))
        logs_lst.append(("Min for difference of F_reg = " + str_tmp[19]))
 

        logs_path = os.path.join(log_dir, logs_name)

        with open(logs_path, mode='a') as file:
            for line in logs_lst:
                file.write(line)
                file.write('\n')
        # print("Average for difference of C_exp = " + str_tmp[0])
        # print("Variance for difference of C_exp = " + str_tmp[1])
        # print("Max for difference of C_exp = " + str_tmp[2])
        # print("Min for difference of C_exp = " + str_tmp[3])

        # print("Average for difference of em_pivot = " + str_tmp[4])
        # print("Variance for difference of em_pivot = " + str_tmp[5])
        # print("Max for difference of em_pivot = " + str_tmp[6])
        # print("Min for difference of em_pivot = " + str_tmp[7])

        # print("Average for difference of opt_pivot = " + str_tmp[8])
        # print("Variance for difference of opt_pivot = " + str_tmp[9])
        # print("Max for difference of opt_pivot = " + str_tmp[10])
        # print("Min for difference of opt_pivot = " + str_tmp[11])
    
if __name__ == '__main__':
    main()
