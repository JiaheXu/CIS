import glob
import numpy as np
from cartesian import *
from registration_3d import *

def distort_calibration( data_dir , data_type , letter  , output = 1 ):

    calbody = glob.glob(data_dir + 'pa1-' + data_type + '-' + letter + '-calbody.txt')
    calbody_file = open(calbody[0], "r")
    calbody_lines = calbody_file.read().splitlines()
    calbody_data = []
    
    for num in range(len(calbody_lines)):
        calbody_data.append( calbody_lines[num].split(',') )
        for i in range(len(calbody_data[-1])):
            calbody_data[-1][i] = calbody_data[-1][i].strip() # to remove space and tabs
    
    Nd = int(calbody_data[0][0])
    Na = int(calbody_data[0][1])
    Nc = int(calbody_data[0][2])
    
    calbody_data = np.asarray(calbody_data[1:]).astype(float)
    c_expected = np.zeros(1)

    d = calbody_data[0: Nd, :]
    a = calbody_data[Nd: Nd + Na, :]
    c = calbody_data[Nd + Na:, :]

    calreadings = glob.glob(data_dir + 'pa1-' + data_type + '-' + letter + '-calreadings.txt')
    calreadings_file = open(calreadings[0], "r")
    calreadings_lines = calreadings_file.read().splitlines()
    calreadings_data = []
    
    for num in range(len(calreadings_lines)):
        calreadings_data.append( calreadings_lines[num].split(',') )
        for i in range(len( calreadings_data[-1] )):
            calreadings_data[-1][i] = calreadings_data[-1][i].strip()

    ND = int(calreadings_data[0][0])
    NA = int(calreadings_data[0][1])
    NC = int(calreadings_data[0][2])
    Nframes = int(calreadings_data[0][3])
    
    calreadings_data = np.asarray(calreadings_data[1:]).astype(float)
    C_exp = np.zeros((1,3))
    
    for i in range(Nframes):
    #for i in range(1):
        start_index = i*(ND + NA + NC)
        D = calreadings_data[start_index : start_index + ND, :]
        A = calreadings_data[start_index + ND: start_index + ND + NA, :]
        C = calreadings_data[start_index + ND + NA : start_index + ND + NA + NC , :]
    
        
        FD = registration_3d(d, D)
        FA = registration_3d(a, A)
        
        FD_inv = Fi(FD)
        C_exp_new = points_transform(FD_inv@FA,c)
        C_exp = np.vstack((C_exp,C_exp_new))
    C_exp = C_exp[1:]
    if(output == 1):
        print(data_dir + 'pa1-' + letter + '-' + data_type )
        print("C_expected:")
        print(C_exp)
    return C_exp, Nc, Nframes