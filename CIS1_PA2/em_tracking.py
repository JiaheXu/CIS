import glob
import numpy as np
from cartesian import *
from registration_3d import *
from pivot_calibration import *

def em_tracking( data_dir ,pa, data_type , letter  , output = 1 ):

#################### read in data
    empivot = glob.glob(data_dir + pa + data_type + '-' + letter + '-empivot.txt')
    # print(empivot)
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

    ans, p = pivot_calibration( empivot_data ,Ng, Nframes)
    # Use the first “frame” of pivot calibration data to define a local “probe” coordinate system
    
    if(output == 1):
        print(data_dir + pa + letter + '-' + data_type)
        print("em_pivot: " , ans[3][0]," ", ans[4][0]," ",ans[5][0] )
    return ans[3:]