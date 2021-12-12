#!/usr/bin/env python

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
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    type = ['debug', 'unknown']
    data_dir = args.data_dir
    # first read in Calbody (Nd, Na, Nc)
    # then readings  (ND, NA, NC, nframes)
    
    # the last output determines whether to show the result in terminal
    em_pivot = em_tracking( data_dir , type[runtype] , letters[run] , output = 0)
    optical_pivot = optical_tracking( data_dir , type[runtype] , letters[run] , output = 0)

    tmp_ce = distort_calibration( data_dir , type[runtype] , letters[run] ,output = 0)
    C_exp = tmp_ce[0]
    Nc = tmp_ce[1]
    Nframes = tmp_ce[2]
    # print(optical_pivot.shape)
    ep = np.transpose(em_pivot)
    op = np.transpose(optical_pivot)
    em_rounded = np.round(em_pivot.reshape(3), decimals=2)
    opt_rounded = np.round(optical_pivot.reshape(3), decimals=2)
    C_exp_rounded = np.round(C_exp, decimals=2)
    if args.eval:
        tmp = eval( data_dir , type[runtype] , letters[run] , C_exp_rounded, em_rounded.reshape(3, 1), opt_rounded.reshape(3, 1))
        str_tmp = [str(float(x)) for x in tmp]
        log_dir = "eval_logs"
        if not (os.path.exists(os.path.join(os.getcwd(), log_dir))):
            os.mkdir(log_dir)
        logs_name = 'pa1-' + type[runtype] + '-' + letters[run] + '-eval_logs.txt'
        
        logs_lst = []

        logs_lst.append(("Average for difference of C_exp = " + str_tmp[0]))
        logs_lst.append(("Variance for difference of C_exp = " + str_tmp[1]))
        logs_lst.append(("Max for difference of C_exp = " + str_tmp[2]))
        logs_lst.append(("Min for difference of C_exp = " + str_tmp[3]))

        logs_lst.append(("Average for difference of em_pivot = " + str_tmp[4]))
        logs_lst.append(("Variance for difference of em_pivot = " + str_tmp[5]))
        logs_lst.append(("Max for difference of em_pivot = " + str_tmp[6]))
        logs_lst.append(("Min for difference of em_pivot = " + str_tmp[7]))
        
        logs_lst.append(("Average for difference of opt_pivot = " + str_tmp[8]))
        logs_lst.append(("Variance for difference of opt_pivot = " + str_tmp[9]))
        logs_lst.append(("Max for difference of opt_pivot = " + str_tmp[10]))
        logs_lst.append(("Min for difference of opt_pivot = " + str_tmp[11]))

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

    output_name = 'pa1-' + type[runtype] + '-' + letters[run] + '-output.txt'
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
        
    # print(em_pivot, optical_pivot)
    # print(Nc, Nframes)

    
    
if __name__ == '__main__':
    main()