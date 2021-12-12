import numpy as np
import copy
from cartesian import *
######
# calculate the lsq transform between 2 sets 
# start and goal are a nx3 numpy array 
# return a 4*4 transform matrix F that F*start[i] = goal[i] in a lsq way 
######
def error_correction(F, g, d):
    #F_0 = registration_3d(start=g, goal=d)
    g_k = points_transform(F, g)
    F_k = copy.deepcopy(F)
    # print(g_k)
    # print("\n")
    # print(d)
    delta_sum = np.sum(g_k - d)
    # print(delta_sum)
    while delta_sum > 1e-5:
        # print (delta_sum)
        g_k = points_transform(F_k, g)
        A = np.concatenate((skew(-1 * g_k[0]), np.identity(3)), 1)
        B = (d - g_k).reshape((d.shape[0] * d.shape[1]), 1)

        # print(np.abs(np.sum(g_k - d)))
        for i in range (1, len(g_k)):
            tmp_sk = np.concatenate((skew(-1 * g_k[i]), np.identity(3)), 1)
            A = np.concatenate((A, tmp_sk), 0)
        # print(A.shape)
        # print(B.shape)
        X = np.linalg.lstsq(A, B, rcond=None)
        # print(X.shape)
        
        alpha = X[0][0:3, :].reshape(3)
        epsilon = X[0][3:6, :]
        delta_R = np.identity(3) + skew(alpha)
        delta_t = epsilon
        delta_F = concat_frame(delta_R, delta_t)
        F_k = delta_F @ F_k

        # delta = concat_frame(skew(alpha), delta_t)
        g_k = points_transform(F_k, g)
        delta_sum = np.sum(g_k - d)
        # print(np.abs(np.sum(delta) - 1))
        # print("\n")
        # g_k = points_transform(F, g)
    return F_k

def registration_3d( start , goal ):
    g = start
    d = goal
    n = np.shape(start)[0]
    #middle point
    start_mid = np.sum(start, axis=0)/n
    start = start - start_mid
    
    goal_mid = np.sum(goal, axis=0)/n
    goal = goal - goal_mid
    
    # according to formula on rigid3d3dcalculations.pdf p9
    H = start.T @ goal
    u,s,vt = np.linalg.svd(H)
    v = vt.T
    R = v@(u.T)
    if np.abs( np.linalg.det(R) - 1 ) > 1e-5: #det(R) != 1
        #A@t = b
        #use lsq find t, lsq method have relatively greater error, so we take it as a plan B
        A = np.zeros((3*n, 9))
        B = np.zeros((3*n, 1))
        for i in range(n):
            A[i*3,0] = start[i,0]
            A[i*3,1] = start[i,1]
            A[i*3,2] = start[i,2]
            A[i*3+1,3] = start[i,0]
            A[i*3+1,4] = start[i,1]
            A[i*3+1,5] = start[i,2]
            A[i*3+2,6] = start[i,0]
            A[i*3+2,7] = start[i,1]
            A[i*3+2,8] = start[i,2]
            
            B[i*3] = goal[i,0]
            B[i*3+1] = goal[i,1]
            B[i*3+2] = goal[i,2]
        # print(A.shape)
        # print(B.shape)    
        X = np.linalg.lstsq(A, B, rcond=None)[0]
        R = X.reshape(3,3)
        
    p = goal_mid - R@start_mid

    F = concat_frame(R,p)
    F = error_correction(F, g, d)
    return F
