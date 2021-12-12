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


def main():

    # args = parse_args()
    
    runtype = 0
    run = 0
    letters = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    type = ['debug', 'unknown']
    data_dir = "DATA/"
    # first read in Calbody (Nd, Na, Nc)
    # then readings  (ND, NA, NC, nframes)
    tmp_all = np.array([0, 0, 0])
    for i in range(7):
        run = i
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
    
        tmp = eval( data_dir , type[runtype] , letters[run] , C_exp_rounded, em_rounded.reshape(3, 1), opt_rounded.reshape(3, 1))
        np_avg = np.array([tmp[0], tmp[4], tmp[8]])

        tmp_all = tmp_all + np_avg
    runtype = 1
    for i in range(4):
        run = i + 7
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
    
        tmp = eval( data_dir , type[runtype] , letters[run] , C_exp_rounded, em_rounded.reshape(3, 1), opt_rounded.reshape(3, 1))
        np_avg = [tmp[0], tmp[4], tmp[8]]
        tmp_all = tmp_all + np.array(np_avg)
    eval_results = tmp_all / 11
    print(eval_results)


        
    # print(em_pivot, optical_pivot)
    # print(Nc, Nframes)

    
    
if __name__ == '__main__':
    main()