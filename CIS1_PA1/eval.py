import glob
import numpy as np
import cartesian
from registration_3d import *
from pivot_calibration import pivot_calibration
import copy
import os

def eval( data_dir , data_type , letter, Cexp, empivot, optpivot):
    # file_path = glob.glob(data_dir + 'pa1-' + data_type + '-' + letter + '-output')
    file_path = 'pa1-' + data_type + '-' + letter + '-output'
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

    em_pivot = output_data[0, :].reshape(3, 1)
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
    
    return (np.average(diff_arr_ce), np.var(diff_arr_ce), np.max(diff_arr_ce), np.min(diff_arr_ce), 
    np.average(diff_arr_em), np.var(diff_arr_em), np.max(diff_arr_em), np.min(diff_arr_em), 
    np.average(diff_arr_opt), np.var(diff_arr_opt), np.max(diff_arr_opt), np.min(diff_arr_opt))