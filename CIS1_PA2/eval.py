import glob
import numpy as np
import cartesian
from registration_3d import *
from pivot_calibration import pivot_calibration
import copy
import os
from improved_em_tracking import *
from distortion_correction import *
from fiducials import *

#Evaluation for all data
#data_dir, data_type, letter: Values used for composing the data file names.
# Cexp: The C_exp data calculated from distortion_calibration
# empivot: data calculated from em_tracking
#optpivot: calculated from op-tracking
#ct: calculated from em_nav2ct
def eval( data_dir , data_type , letter, Cexp, empivot, optpivot, ct, F_reg, pivot_set):
    # file_path = glob.glob(data_dir + 'pa1-' + data_type + '-' + letter + '-output')
    ################################################################################
    #For output1, this part is mostly the same as in PA1
        
    file_path = 'pa2-' + data_type + '-' + letter + '-output1'
    path_lst = []
    for file in os.listdir(data_dir):
        if file.startswith(file_path):
            path_lst.append(file)
    output_data = []
    for file in path_lst:
        read_file = open(os.path.join(data_dir, file), mode='r')
        lines = read_file.read().splitlines()
        for num in range(len(lines)):
            output_data.append( lines[num].split(',') )
            for i in range(len(output_data[-1])):
                output_data[-1][i] = output_data[-1][i].strip()
    Nc = int(output_data[0][0])
    Nframes = int(output_data[0][1])
    output_name = output_data[0][2]
    output_data = np.asarray(output_data[1:]).astype(float)

    em_pivot = (output_data[0, :].reshape(3, 1))
    # print(em_pivot)
    opt_pivot = output_data[1, :].reshape(3, 1)
    output_data = output_data[2:]
    row = output_data.shape[0]
    col = output_data.shape[1]
    assert output_data.shape == Cexp.shape, "Dimensions of the input Cexp and file data shape must be the same!"
    # print(em_pivot.shape)
    diff_arr_ce = np.abs(output_data - Cexp).reshape(row * col)
    # print(np.abs(em_pivot - empivot).shape)
    diff_arr_em = np.abs(em_pivot - empivot).reshape(3)
    diff_arr_opt = np.abs(opt_pivot - optpivot).reshape(3)
    
    ################################################################################
    #For output2, this part was added. It extracts the data from output2 to evaluate F_reg and ct_points
    output_path = glob.glob(data_dir + "pa2-" + data_type + '-' + letter + '-output2.txt')
    output_data = []
    read_file = open(output_path[0], mode='r')
    lines = read_file.read().splitlines()
    for num in range(len(lines)):
        output_data.append( lines[num].split(',') )
        for i in range(len(output_data[-1])):
            output_data[-1][i] = output_data[-1][i].strip()
    
    Nframes = int(output_data[0][0])
    output_name = output_data[0][1]
    #Ground truth answers
    ct_points = np.asarray(output_data[1:]).astype(float)
    rows, cols = ct_points.shape
    # print(output_data.shape)

    #Calculating the answer for F_reg which should be closer to ground truth, 
    #acting as a source for evaluation.
    F_reg_gt = registration_3d(pivot_set, ct_points)
    #Differences in both CT_points and F_reg
    diff_arr_ct = np.abs(ct_points - ct).reshape(rows * cols)
    diff_freg = np.abs(F_reg - F_reg_gt)

    return (np.average(diff_arr_ce), np.var(diff_arr_ce), np.max(diff_arr_ce), np.min(diff_arr_ce), 
    np.average(diff_arr_em), np.var(diff_arr_em), np.max(diff_arr_em), np.min(diff_arr_em), 
    np.average(diff_arr_opt), np.var(diff_arr_opt), np.max(diff_arr_opt), np.min(diff_arr_opt),
    np.average(diff_arr_ct), np.var(diff_arr_ct), np.max(diff_arr_ct), np.min(diff_arr_ct),
    np.average(diff_freg), np.var(diff_freg), np.max(diff_freg), np.min(diff_freg))