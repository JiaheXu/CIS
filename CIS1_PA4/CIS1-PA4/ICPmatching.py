import numpy as np
import sys, os
import time
import glob
from registration_3d import *
from cartesian import *
from collections import namedtuple
from operator import itemgetter
from pprint import pformat
import matplotlib.pyplot as plt
from read_files import *
import argparse
# from KD_tree import *

def get_d_k(A_frames, A_points, A_tip, B_frames, B_points, B_tip):
    
    d_k = []
    for i in range(len(A_frames)):
        F_AK = registration_3d(A_points , A_frames[i])
        F_BK = registration_3d(B_points , B_frames[i])
        # F_AK is the transformation from A tool frame to optical frame
        # F_AK is the transformation from B tool frame to optical frame
        d_k_i = points_transform( Fi(F_BK) @ F_AK , A_tip)
        d_k.append(d_k_i)
    d_k = np.array(d_k).astype(float)
    d_k = d_k.reshape(-1,3)
    return d_k

def ProjectOnSegment(c,p,q):
# c is the point we want to find corresponding closest point
# p q are the start and the and of a segment

#according to https://ciis.lcsr.jhu.edu/lib/exe/fetch.php?media=courses:455-655:lectures:finding_point-pairs.pdf
# page 7
    c = np.array(c).astype(float)
    p = np.array(p).astype(float)
    q = np.array(q).astype(float)
    #print(np.dot( c-p , q-p ))
    #print(np.dot( q-p ,q-p ))
    Lambda = np.dot( c-p , q-p ) / np.dot( q-p ,q-p )
    Lambda = max(0, min(Lambda, 1))
    c_star = p + Lambda*(q-p)
    return c_star

def FindClosestPoint( a, p, q, r ):
    
    A = np.zeros((3,2),dtype = float )
    
    for i in range(3):
        A[i][0] = q[i] - p[i]
        A[i][1] = r[i] - p[i]
        
    B = a - p
    B = B.reshape(-1,1)
    X = np.linalg.lstsq(A, B, rcond=None)[0]
    
    Lambda = X[0]
    Miu = X[1]

    a = p + Lambda * (q - p) + Miu * (r - p)
    P_closest = np.zeros(3)

    if Lambda >= 0 and Miu>=0 and Lambda+Miu<=1:
        P_closest = a
    elif Lambda < 0:
        P_closest = ProjectOnSegment(a, r, p)
    elif Miu < 0:
        P_closest = ProjectOnSegment(a, p, q)
    elif Lambda + Miu > 1:
        P_closest = ProjectOnSegment(a, q, r)

    return P_closest

def point_to_triangle(s_k_i , j, mesh_points, mesh_vertices):
    p = mesh_points[mesh_vertices[j][0]] 
    q = mesh_points[mesh_vertices[j][1]]
    r = mesh_points[mesh_vertices[j][2]] 
            
    tmp = FindClosestPoint( s_k_i, p, q, r )
    
    return tmp

def get_rectangles(Np , mesh_points , Ntriangles , mesh_vertices):
    
    rectangles = np.zeros( (Ntriangles,7) ,dtype=float)
    
    for i in range(Ntriangles):
        p = mesh_points[mesh_vertices[i][0]] 
        q = mesh_points[mesh_vertices[i][1]]
        r = mesh_points[mesh_vertices[i][2]]
        
        # the last place saves index we will need this when we build trees
        rectangles[i,6] = i
        for j in range(3):
            rectangles[i,j] = min( p[j],q[j],r[j])
        for j in range(3):
            rectangles[i,j+3] = max( p[j],q[j],r[j])
        #print(rectangle[i,0:3] - rectangle[i,3:6])
        
    return rectangles

def bruteforce_matching(s_k , Np , mesh_points , Ntriangles , mesh_vertices ):
    Ns = s_k.shape[0]
    
    closest_p = []
    for i in range(Ns):
        min_dist = np.finfo(np.float32).max
        P_closest = []
        for j in range(Ntriangles):

            tmp = point_to_triangle(s_k[i] , j, mesh_points, mesh_vertices)

            dist = np.linalg.norm(s_k[i] - tmp)
            if min_dist > dist:
                min_dist = dist
                P_closest = tmp
        closest_p.append(P_closest)
                
    return closest_p

