import glob
import numpy as np
from cartesian import *
from registration_3d import *
from pivot_calibration import *
import copy


def optical_tracking( data_dir , data_type , letter  , output = 1 ):

    optpivot = glob.glob(data_dir + 'pa1-' + data_type + '-' + letter + '-optpivot.txt')
    #print(optpivot)
    optpivot_file = open(optpivot[0], "r")
    optpivot_lines = optpivot_file.read().splitlines()
    optpivot_data = []
    for num in range(len(optpivot_lines)):
        optpivot_data.append( optpivot_lines[num].split(',') )
        for i in range(len(optpivot_data[-1])):
            optpivot_data[-1][i] = optpivot_data[-1][i].strip()


    Nd = int(optpivot_data[0][0])
    Nh = int(optpivot_data[0][1])
    Nframes = int(optpivot_data[0][2])
    optpivot_data = np.asarray(optpivot_data[1:]).astype(float)

        # Use the first “frame” of pivot calibration data to define a local “probe” coordinate system
    D = optpivot_data[ : Nd , : ]
    D0 = np.sum(D, axis=0)/Nd
    d = D - D0

    frame_size = Nd + Nh
    Nd_frame = np.zeros((1, 3))
    Nh_frame = np.zeros((1, 3))

    for i in range(Nframes):
        start = i * frame_size
        end = start + frame_size
        Nd_frame = np.concatenate((Nd_frame, copy.deepcopy(optpivot_data[start: start + Nd, :])), 0)
        Nh_frame = np.concatenate((Nh_frame, copy.deepcopy(optpivot_data[start + Nd: end, :])), 0)

    Nd_frame = np.asarray(Nd_frame[1:]).astype(float)
    Nh_frame = np.asarray(Nh_frame[1:]).astype(float)
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

    d_i = calbody_data[0: Nd, :]
    a_i = calbody_data[Nd: Nd + Na, :]
    c_i = calbody_data[Nd + Na:, :]
    D_i = Nd_frame[0: Nd, :]
    # print(optpivot_data[0:Nd, :])
    F_d = np.zeros((1, 4, 4))
    # print(D_i)
    # print(d_i)
    for i in range(Nframes):
        D_i = Nd_frame[i * Nd : (i + 1) * Nd, :]
        F_d_i = registration_3d(D_i, d_i)
        F_d = np.concatenate((F_d, np.expand_dims(F_d_i, 0)), 0)
    # print(F_d_i)

    F_d = np.asarray(F_d[1:]).astype(float)

    data = np.zeros((1,3))
    for i in range(Nframes):
        data = np.vstack( ( data , points_transform(F_d[i] , Nh_frame[i*Nh : (i+1)*Nh ,:] ) ) )
    data = data[1:]
    
    ans = pivot_calibration( data ,Nh, Nframes)
    
    if(output == 1):
        print(data_dir + 'pa1-' + letter + '-' + data_type)
        print("optical_pivot: " , ans[3][0]," ", ans[4][0]," ",ans[5][0] )
    return ans[3:]