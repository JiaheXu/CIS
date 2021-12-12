import numpy as np
from registration_3d import *
# data are n*3, n points
# Np in the number of points in a frame
# Nframes is the number of frames 
def pivot_calibration( data , Np ,Nframes):
    P = data[ : Np , : ]
    P0 = np.sum(P, axis=0)/Np

#p is marker positions in initial tool frame
    p = P - P0 
    #print("pivot_calibration: ")
    #print("P0 :\n",P0)
    #print("P :\n",p)

    Rotation = np.zeros((3,3))
    Translation = np.zeros((3,1))
    Transform = []
    for i in range(Nframes):
        P = data[ i*Np : (i+1)*Np , : ]
        F = registration_3d( p , P )
        Transform.append(F)

        rotation = F[0:3,0:3]
            #print( rotation.shape )
        Rotation = np.vstack( ( Rotation , rotation ) )
            #Translation .append()
            # need to save all those data and applied hw3 Q1C
        translation = F[ 0:3 , 3 ]
        Translation = np.vstack( ( Translation , translation.reshape(3,1) ) )

    Transform = np.asarray( Transform ).astype(float)
    Rotation = Rotation[3:]    
    Translation = Translation[3:]
    ans = solve_lsq( Rotation , Translation )
############### ans contains P_tip and P_dimple, p is marker positions in initial tool frame
    return ans , p

def get_ptip( data , Np ,Nframes):
    P = data[ : Np , : ]
    P0 = np.sum(P, axis=0)/Np
    p = P - P0

    Rotation = np.zeros((3,3))
    Translation = np.zeros((3,1))
    Transform = []
    for i in range(Nframes):
        P = data[ i*Np : (i+1)*Np , : ]
        F = registration_3d( p , P )
        Transform.append(F)

        rotation = F[0:3,0:3]
            #print( rotation.shape )
        Rotation = np.vstack( ( Rotation , rotation ) )
            #Translation .append()
            # need to save all those data and applied hw3 Q1C
        translation = F[ 0:3 , 3 ]
        Translation = np.vstack( ( Translation , translation.reshape(3,1) ) )

    Transform = np.asarray( Transform ).astype(float)
    Rotation = Rotation[3:]    
    Translation = Translation[3:]
    ans = solve_lsq( Rotation , Translation )
    ans = np.transpose(Rotation[0]) @(ans[3:] - translation[0])
    return ans


######
# calculate P_dimple using different pairs of rotations and translations
# P_dimple is fixed
# with each pair of ratation and translation, we have [R P]* P_pivot = P_dimple
# P_pivot is the position of pivot rt g0(a frame on tool) 
# Ri * P_pivot + Pi = P_dimple
# P_pivot and P_dimple are unkown vectors
# we hope to use lsq method get these two vectors
# so we change the equation as: Ri* P_pivot - P_dimple = -Pi
# in AX = B form:  
# Ai = [Ri | -I] * [P_pivot, P_dimple] = -Pi
# we need X = inv( A.T @ A ) @ A.T @ B
######
def solve_lsq( Rotation , Translation ):
    
    n = (Rotation.shape)[0] // 3
    right_half = -1 * np.eye(3)
    for i in range(n-1):
        right_half = np.vstack( ( right_half , -1 * np.eye(3) ) )
    
    A = np.concatenate((Rotation,right_half),1)
    B = -1*Translation
    
    #X =  np.linalg.inv(np.transpose(A) @ A) @ np.transpose(A) @ B
    
    X = np.linalg.lstsq(A, B, rcond=None)[0]
    return X
