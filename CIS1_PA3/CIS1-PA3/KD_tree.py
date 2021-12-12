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
from ICPmatching import *

class KD_tree():
    def __init__(self, Np , mesh_points , Ntriangles , mesh_vertices , rectangles):
        
        self.Np = Np
        self.mesh_points = mesh_points
        self.mesh_vertices = mesh_vertices
        self.Ntriangles =  Ntriangles
        self.rectangles = rectangles
        self.num = np.zeros(Ntriangles+10).astype(int)
        #self.D = mesh_points.shape[1]
        self.D = 3
        
        # ls saves the index of left son
        self.ls = np.zeros( Ntriangles+10 )
        # rs saves the index of right son
        self.rs = np.zeros( Ntriangles+10 )
        
        # self.Rectangle : [; , 0:3] represent min(x , y , z)
        # self.Rectangle : [; , 3:6] represent max(x , y , z) 
        self.Rectangle = np.zeros( (Ntriangles+10,6) )
        
        # rectangles[:,6] save the index of triangle each rectangle represent
        self.tree = self.build(rectangles.tolist(), 1 , Ntriangles , depth =0 )
        self.nearest_point = []
        self.nearest_dist = 0
        
    def pushup(self, root):
        # updating current node from son nodes
        # root is the current index number
        ls = self.ls[root]
        rs = self.rs[root]
        if(ls!=0):
            for i in range(3):
                self.Rectangle[root,i] = min(self.Rectangle[root,i],self.Rectangle[int(ls),i])
                self.Rectangle[root,i+3] = max(self.Rectangle[root,i+3],self.Rectangle[int(ls),i+3]) 
        if(rs!=0):
            for i in range(3):
                self.Rectangle[root,i] = min(self.Rectangle[root,i],self.Rectangle[int(rs),i])
                self.Rectangle[root,i+3] = max(self.Rectangle[root,i+3],self.Rectangle[int(rs),i+3]) 
    
    def point_to_cube(self, start_point, root):
        # compute the shortest distant from a point to a cube
        dis = np.zeros(self.D)
        
        for i in range(self.D):
            if(start_point[i] < self.Rectangle[root,i]):
                dis[i] = self.Rectangle[root,i] - start_point[i]
            if(start_point[i] > self.Rectangle[root,i+3]):
                dis[i] = start_point[i] - self.Rectangle[root,i+3]
        dist = np.linalg.norm(dis)
        return dist
    
    def find(self, start_point , left,right,depth):
        # find the closest point from start_point in a tree
        # depth tell us which dimension we should look to
        # left and right means which nodes we are looking at from 1 <=left <=right <= n
        if(left>right):
            return 
        
        middle = ((left + right) // 2) 
        
        dist = self.point_to_cube(start_point , middle)
        
        # if the current optimal solution is better than the possible solution in the cube
        # just return
        if(dist > self.nearest_dist):
            return
        
        # check the distance from start_point to the current node's mesh triangle
        tmp = point_to_triangle(start_point , self.num[middle], self.mesh_points, self.mesh_vertices)
        dist = np.linalg.norm(start_point - tmp)
        
        if( dist < self.nearest_dist):
            self.nearest_dist = dist
            self.nearest_point = tmp
        
        # look into son nodes
        self.find( start_point , left , middle-1 ,depth)
        self.find( start_point , middle+1 , right,depth)
        
    def FindClosestPoint(self, start_point ):
        
        self.nearest_dist =  np.finfo(np.float32).max
    
        self.find( start_point , 1 , self.Ntriangles , depth=0 ) 
        
        return self.nearest_point
        
    def build( self, points, left,right,depth ):
        # build a KD-tree
        # left and right means which nodes we are looking at from 1 <=left <=right <= n
        if(left>right):
            return 0
        
        axis = depth % self.D
        
        # sort with axis, since the number of nodes is not too big
        # we directly use O(nlogn) sort in list, rather than a O(n) sort
        points.sort(key=itemgetter(axis))
        middle = ((left + right) // 2) 
        #print("points: ",len(points))
        #print("middle: ",middle)
        self.Rectangle[middle] = np.array(points[ middle - left ][0:6]).astype(float)
        
        # self.num saves the index number of mesh triangle
        self.num[middle] =  points[middle - left ][6]
        
        self.ls[ middle ] = self.build(points[:middle- left] ,left , middle-1 , depth+1 )
        self.rs[ middle ] = self.build(points[middle-left+1:]   ,middle+1, right , depth+1 )

        # after finished building son nodes, we need update father node's info 
        self.pushup(middle)
        
        return middle

def kd_matching(s_k , Np , mesh_points , Ntriangles , mesh_vertices ):
    
    rectangles = get_rectangles(Np , mesh_points , Ntriangles , mesh_vertices)

    kdtree = KD_tree(Np , mesh_points , Ntriangles , mesh_vertices , rectangles)
    
    Ns = s_k.shape[0]
    
    closest_p = []
    for i in range(Ns):
        min_dist = np.finfo(np.float32).max
        tmp = kdtree.FindClosestPoint( s_k[i] )
        closest_p.append(tmp)
    return closest_p