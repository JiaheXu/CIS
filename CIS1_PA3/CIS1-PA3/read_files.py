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

#Read mesh.sur files
def read_mesh( data_dir , filename ):
# get the coordinate of points
# get the vertices of each triangle
    mesh = glob.glob( data_dir + filename )
    mesh_file = open( mesh[0] , "r")
    mesh_lines = mesh_file.read().splitlines()
    mesh_data = []
    
    for num in range(len(mesh_lines)):
        mesh_data.append( mesh_lines[num].split(' ') )
        for i in range(len( mesh_data[-1])):
            mesh_data[-1][i] = mesh_data[-1][i].strip() # to remove space and tabs
    Np = int(mesh_data[0][0])
    mesh_data = mesh_data[1:]
    
    mesh_points = np.asarray(mesh_data[0:Np]).astype(float)
    mesh_data = mesh_data[Np:]
    
    Ntriangles = int(mesh_data[0][0])
    mesh_data = mesh_data[1:]
    mesh_vertices = np.asarray(mesh_data[0:Ntriangles]).astype(int)
    mesh_data = mesh_data[Ntriangles:]
    
    return Np,mesh_points,Ntriangles,mesh_vertices

#Read Body-A and Body-B data
def read_body( data_dir , filename ):

# get the markers' positions and tip of a body
    body = glob.glob( data_dir + filename )
    body_file = open( body[0] , "r")
    body_lines = body_file.read().splitlines()
    body_data = []
    
    for num in range(len(body_lines)):
        body_data.append( body_lines[num].split() )
        for i in range(len( body_data[-1])):
            body_data[-1][i] = body_data[-1][i].strip() # to remove space and tabs
    Np = int(body_data[0][0])
    body_data = body_data[1:]
    
    body_points = np.asarray(body_data[0:Np]).astype(float)
    body_data = body_data[Np:]
    
    tip = body_data[0]
    tip = np.array(tip).astype(float)
    tip = tip.reshape(1,-1)
    return Np,body_points,tip

#Read SampleReadingsTest data
def read_sample( data_dir , filename , N_Ap , N_Bp ):
# get the markers' positions and tip of a body
# N_Ap is the number of marker in A
# N_Bp is the number of marker in B
    sample = glob.glob( data_dir + filename )
    sample_file = open( sample[0] , "r")
    sample_lines = sample_file.read().splitlines()
    sample_data = []
    
    for num in range(len(sample_lines)):
        sample_data.append( sample_lines[num].split(',') )
        for i in range(len( sample_data[-1])):
            sample_data[-1][i] = sample_data[-1][i].strip() # to remove space and tabs
    Np = int(sample_data[0][0])
    N_sample = int(sample_data[0][1])
    N_Dp = Np - N_Ap - N_Bp
    sample_data = sample_data[1:]
    sample_data = np.array(sample_data).astype(float)
    A_frames=[]
    B_frames=[]
    
    for i in range(N_sample):
        A_sample_points = np.asarray( sample_data[ i*Np : i*Np + N_Ap ] ).astype( float )
        A_frames.append( A_sample_points )
        
        B_sample_points = np.asarray( sample_data[ i*Np + N_Ap :  i*Np + N_Ap + N_Bp] ).astype( float )
        B_frames.append( B_sample_points )

    A_frames = np.array(A_frames).astype(float)
    B_frames = np.array(B_frames).astype(float)
        
    return A_frames , B_frames

def read_output( data_dir , filename):
# get the markers' positions and tip of a body
# N_Ap is the number of marker in A
# N_Bp is the number of marker in B
    output = glob.glob( data_dir + filename )
    c_data = []
    d_data = []
    dkck = []
    with open( output[0] , "r") as file:
        first_line = next(file)
        # lines = file.readlines()
        
        first_data = next(file)
        first_data = first_data.split()
        # print(first_data)
        first_data = [float(i) for i in first_data]
        c_data = np.array(first_data[0:3]).reshape(1, 3)
        d_data = np.array(first_data[3:6]).reshape(1, 3)
        dkck.append(first_data[6])

        for line in file:
            tmp_line = line.split()
            tmp_line = [float(i) for i in tmp_line]
            c_data = np.concatenate((c_data, np.array(tmp_line[0:3]).reshape(1, 3)))
            d_data = np.concatenate((d_data, np.array(tmp_line[3:6]).reshape(1, 3)))
            dkck.append(tmp_line[6])
    return c_data, d_data, np.array(dkck).reshape(len(dkck), 1)