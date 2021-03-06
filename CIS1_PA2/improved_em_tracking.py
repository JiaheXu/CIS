# -*- coding: utf-8 -*-
"""improved.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1nfJ8r-OUQ08-SnoZPV0TohDyMMKHZ-Hj
"""
#A modification based on em_tracking. The given data is undistorted first.
import numpy as np
import glob
from distort_calibration import *
from cartesian import*
from registration_3d import*
from optical_tracking import*
from em_tracking import *
from eval import *
from pathlib import Path
import argparse
from distort_calibration import *
from distortion_correction import *

def improved_em_tracking( data_dir ,pa, data_type , letter  , output = 1 , have_output1 = 1):
#Params: Most of them are components for data file name creation.
# example: improved_em_tracking("DATA/", "pa2-", "unknown", "j")    
    C_expected = []
#################### read in data
    if( have_output1 ):
        output_path = glob.glob(data_dir + pa + data_type + '-' + letter + '-output1.txt')
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
#################### end of read in data

    C_exp, Nc, Nframes,C = distort_calibration( data_dir ,pa, data_type , letter  , output = 0 )

    if( have_output1 == 0):
        C_expected = C_exp

#################### get distortion parameters
    X, qmin, qmax = distortion_correction(C, C_expected, order=5)


#################### read in data
    empivot = glob.glob(data_dir + pa + data_type + '-' + letter + '-empivot.txt')

    empivot_file = open(empivot[0], "r")
    empivot_lines = empivot_file.read().splitlines()
    empivot_data = []
    for num in range(len(empivot_lines)):
        empivot_data.append( empivot_lines[num].split(',') )
        for i in range(len(empivot_data[-1])):
            empivot_data[-1][i] = empivot_data[-1][i].strip()

    Ng = int(empivot_data[0][0])
    Nframes = int(empivot_data[0][1])
    empivot_data = np.asarray(empivot_data[1:]).astype(float)
#################### end of read in data

#################### compute corrected position
    empivot_corrected = []
    for i in range(Nframes):
        if i == 0:
            B_mat = Berntensor_matrix(empivot_data[i*Ng:(i+1) * Ng, :], qmin, qmax, 5)
            empivot_corrected = B_mat @ X
        else:
            B_mat = Berntensor_matrix(empivot_data[i*Ng:(i+1) * Ng, :], qmin, qmax, 5)
            tmp_cor = B_mat @ X
            empivot_corrected = np.concatenate((empivot_corrected, tmp_cor), 0)

############### ans contains P_tip and P_dimple, p is marker positions in initial tool frame
    ans,p = pivot_calibration( empivot_corrected ,Ng, Nframes)

    if(output == 1):
        print(data_dir + 'pa2-' + letter + '-' + data_type)
        print("improved_em_pivot P_tip: " , ans[0][0]," ", ans[1][0]," ",ans[2][0] )
        print("improved_em_pivot P_dimple: " , ans[3][0]," ", ans[4][0]," ",ans[5][0] )
    
    return (ans[:3], ans[3:], p )
    # ans = get_ptip(empivot_corrected, Ng, Nframes)
    # return ans[3:]