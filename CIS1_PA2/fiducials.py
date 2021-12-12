import numpy as np
import glob
from distort_calibration import *
from cartesian import*
from improved_em_tracking import improved_em_tracking
from registration_3d import*
from optical_tracking import*
from em_tracking import *
from eval import *
from pathlib import Path
import argparse
from distort_calibration import *
from distortion_correction import *

# modified partially from pivot_calibration
# Used for calculating F_reg
# data_dir, pa, data_type, letter: Components of data file names
# X, qmin and qmax: c_k and qmin, qmax from calculating distortion correction
# empivot: data containing [ptip, pdimple, p]
# ptip: transformation between tool and tip
# pdimple: em position of probe tip(not used in this function)
# p: the set of points in the system while calculating pivot
def em_ct( data_dir ,pa, data_type , letter  ,X, qmin, qmax,empivot, output = 1 ):

##################### read in input data
    emfiducials_path = glob.glob(data_dir + pa + data_type + '-' + letter + '-em-fiducialss.txt')
    emfiducials_data = []
    read_file = open(emfiducials_path[0], mode='r')
    lines = read_file.read().splitlines()
    for num in range(len(lines)):
        emfiducials_data.append( lines[num].split(',') )
        for i in range(len(emfiducials_data[-1])):
            emfiducials_data[-1][i] = emfiducials_data[-1][i].strip()
    Ng = int(emfiducials_data[0][0])
    Nb = int(emfiducials_data[0][1])
    emfiducials_name = emfiducials_data[0][2]
    emfiducials_data = np.asarray(emfiducials_data[1:]).astype(float)
##################### end of read in input data

    p_tip = empivot[0] #position of tip in initial tool frame
    p = empivot[2] #markers positions in initial tool frame
    emfiducials_corrected = data_correction(emfiducials_data, X, Nb, Ng, qmin, qmax)
    P = emfiducials_corrected[ : Ng , : ]
  
    pivot_set = []

##################### compute undisorted fiducial positions in EM frame
    for i in range(Nb):
        P = emfiducials_corrected[ i*Ng : (i+1)*Ng , : ]

        # F*p =P
        F = registration_3d( p , P )
        
        pivot_em = points_transform(F, p_tip.reshape(1, 3))
        pivot_set.append(pivot_em)

##################### read fiducial positions in CT frame
    ctfiducials_path = glob.glob(data_dir + pa + data_type + '-' + letter + '-ct-fiducials.txt')
    ctfiducials_data = []
    read_file = open(ctfiducials_path[0], mode='r')
    lines = read_file.read().splitlines()
    for num in range(len(lines)):
        ctfiducials_data.append( lines[num].split(',') )
        for i in range(len(ctfiducials_data[-1])):
            ctfiducials_data[-1][i] = ctfiducials_data[-1][i].strip()
    Nb_ct = int(ctfiducials_data[0][0])

    ctfiducials_name = ctfiducials_data[0][1]
    ctfiducials_data = np.asarray(ctfiducials_data[1:]).astype(float)
    assert Nb == Nb_ct
    pivot_set = np.squeeze(np.array(pivot_set))
    #print(pivot_set.shape)
    #print(ctfiducials_data.shape)

##################### F_reg * fiducial positions in EM frame
    F_reg = registration_3d(pivot_set, ctfiducials_data)

    return F_reg

# modified partially from pivot_calibration
# Used for calculating F_reg
# data_dir, pa, data_type, letter: Components of data file names
# X, qmin and qmax: c_k and qmin, qmax from calculating distortion correction
# empivot: data containing [ptip, pdimple, p]
# ptip: transformation between tool and tip
# pdimple: em position of probe tip(not used in this function)
# p: the set of points in the system while calculating pivot
# F_reg: The registration matrix which converts em to ct
def em_nav2ct( data_dir ,pa, data_type , letter  ,F_reg, X, qmin, qmax,empivot, output = 1 ):
    
    em_nav_path = glob.glob(data_dir + pa + data_type + '-' + letter + '-EM-nav.txt')
    em_nav_data = []

####################### read in data positions of markers in EM frame
    read_file = open(em_nav_path[0], mode='r')
    lines = read_file.read().splitlines()
    for num in range(len(lines)):
        em_nav_data.append( lines[num].split(',') )
        for i in range(len(em_nav_data[-1])):
            em_nav_data[-1][i] = em_nav_data[-1][i].strip()
    Ng = int(em_nav_data[0][0])
    Nframes_emn = int(em_nav_data[0][1])
    Nframes = Nframes_emn

    em_nav_name = em_nav_data[0][2]
    em_nav_data = np.asarray(em_nav_data[1:]).astype(float)
####################### end of read in data

    em_nav_corrected = data_correction(em_nav_data, X, Nframes, Ng, qmin, qmax)
    P = em_nav_corrected[ : Ng , : ]
    
    p_tip = empivot[0] #position of tip in initial tool frame
    p = empivot[2] #markers positions in initial tool frame

##################### compute undisorted tool tip positions in EM frame
    pivot_set = []
    for i in range(Nframes_emn):
        P = em_nav_corrected[ i*Ng : (i+1)*Ng , : ]
        F = registration_3d( p , P )
        pivot_em = points_transform(F, p_tip.reshape(1, 3))
        pivot_set.append(pivot_em)
    
    pivot_set = np.array(pivot_set)
    pivot_set =pivot_set.reshape(-1,3)
    
##################### compute undisorted tool tip positions in CT frame
    pivot_ct = points_transform( (F_reg),pivot_set)
    if(output == 1):
        print("output2:\n",pivot_ct)
    
    return pivot_ct, pivot_set
