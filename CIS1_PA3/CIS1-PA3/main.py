#!/usr/bin/env python

import numpy as np
import sys, os
import time
import glob

from numpy.lib.function_base import diff
from registration_3d import *
from cartesian import *
from collections import namedtuple
from operator import itemgetter
from pprint import pformat
import matplotlib.pyplot as plt
from read_files import *
import argparse
from KD_tree import *
from ICPmatching import *
import csv

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "data_dir",
        type=str,
        help="path to data directory",
    )
    parser.add_argument(
        "num",
        type=int,
        help="index of letter, runtype is automatically chosen",
    )
    # parser.add_argument(
    #     "letter",
    #     type=int,
    #     help="index of the letter",
    # )

    parser.add_argument(
        "output_dir",
        type=str,
        help="path to output directory(automatically created if does not exist)",
    )

    parser.add_argument(
        "--eval",
        type=bool,
        default=False,
        help="Whether to evaluate or not"
    )

    return parser.parse_args()

def get_difference( A , B):

    dist = np.zeros(( A.shape[0],1))
    for i in range(A.shape[1]):
        dist[i] = np.linalg.norm( A[i,:] - B[i,:])

    return dist

def main():
    args = parse_args()
    num = args.num
    # for num in range(9):
    data_dir = args.data_dir
    letters = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'J']
    runtype = ['Debug' ,'Debug' ,'Debug' ,'Debug' ,'Debug' ,'Debug' ,'Unknown','Unknown','Unknown']
    pa = "/PA3-"
    filename = '/Problem3MeshFile.sur'
    data_type = num
    letter = num
    Np,mesh_points,Ntriangles,mesh_vertices = read_mesh(data_dir , filename)
    N_Ap,A_points,A_tip = read_body(data_dir , '/Problem3-BodyA.txt')
    N_Bp,B_points,B_tip = read_body(data_dir , '/Problem3-BodyB.txt')
    
    sample_dir = pa + letters[num] + '-' + runtype[num] + '-SampleReadingsTest.txt'
    A_frames , B_frames = read_sample(data_dir, sample_dir, N_Ap , N_Bp)
    
    d_k = get_d_k(A_frames, A_points, A_tip, B_frames, B_points, B_tip)
    F_reg = np.eye(4)
    #in PA3 F_reg = identity matrix
    s_k = points_transform(F_reg , d_k) 
    
    start = time.time()
    # c_k_i are the closest points on the surface to s_k_i 
    c_k = bruteforce_matching(s_k , Np , mesh_points , Ntriangles , mesh_vertices )
    brute_time = time.time() - start
    # brute_time_lst.append(brute_time)
    # print(brute_time)

    start = time.time()
    c_k2 = kd_matching(s_k , Np , mesh_points , Ntriangles , mesh_vertices )
    kd_time = time.time() - start
    # print(kd_time)
    # kd_time_lst.append(kd_time)

    c_k = np.array(c_k)
    c_k2 = np.array(c_k2)
    
    difference = get_difference(d_k,c_k)
    N_samples = len(c_k)
    c_k = np.round(c_k, decimals=2)
    difference = np.round(difference, decimals=2)
    d_k = np.round(d_k, decimals=2)
    output_dir = 'PA3-' + letters[num] + '-' + runtype[num] + '-Output.txt'
    output_path = os.path.join(args.output_dir, output_dir)
    # print(output_path)
    headers = [str(N_samples), '\t' + str(output_dir), '\t' + str(0)]
    if not (os.path.exists(os.path.join(os.getcwd(), args.output_dir))):
        os.mkdir(args.output_dir)
    with open(output_path, mode='a') as file:
        writer = csv.writer(file, delimiter="\t")
        writer.writerow(headers)
        # difference = difference.reshape(len(difference), 1)
        # print(difference[0].shape)
        write_data = []
        tmp_line = np.concatenate((d_k[0].reshape(1, 3), difference[0].reshape(1, 1)), 1)
        tmp_line = np.concatenate((c_k[0].reshape(1, 3), tmp_line), 1)
        write_data = tmp_line
        for i in range(1, N_samples):
            tmp_line = np.concatenate((d_k[i].reshape(1, 3), difference[i].reshape(1, 1)), 1)
            tmp_line = np.concatenate((c_k[i].reshape(1, 3), tmp_line), 1)
            write_data = np.concatenate((write_data, tmp_line), 0)
        writer.writerows(write_data)
    c_eval = []
    d_eval = []
    dkck_eval = []



    if num < 6 and args.eval:
        output_dir = '/PA3-' + letters[num] + '-' + runtype[num] + '-Output.txt'
        # difference = get_difference(d_k,c_k)
        c_output, d_output, dkck = read_output(data_dir, output_dir)
        c_diff = np.round(np.abs(c_output - c_k), decimals=2)
        d_diff = np.round(np.abs(d_output - d_k), decimals=2)
        dc_diff = np.round(np.abs(difference - dkck), decimals=2)
        # print(c_diff.shape, d_diff.shape, dc_diff.shape)
        c_size = c_diff.shape[0] * c_diff.shape[1]
        # print(dc_diff)
        # print(dc_diff[dc_diff > 1])
        c_eval = [np.round(np.average(c_diff), decimals=2), np.max(c_diff), np.min(c_diff), ((c_diff[c_diff > 1]).shape[0] / c_size)]
        d_eval = [np.round(np.average(d_diff), decimals=2), np.max(d_diff), np.min(d_diff), ((d_diff[d_diff > 1]).shape[0] / c_size)]
        dkck_eval = [np.round(np.average(dc_diff), decimals=2), np.max(dc_diff), np.min(dc_diff), ((dc_diff[dc_diff > 1]).shape[0] / N_samples)]
        headers = ["field", "average", "max", "min", "error_nums(%)"]
        c_eval = [str(i) for i in c_eval]
        c_eval.insert(0, "c_k  ")

        d_eval = [str(i) for i in d_eval]
        d_eval.insert(0, "d_k  ")

        dkck_eval = [str(i) for i in dkck_eval]
        dkck_eval.insert(0, "dk_ck")
        log_dir = "EVAL"
        if not (os.path.exists(os.path.join(os.getcwd(), log_dir))):
            os.mkdir(log_dir)
        logs_name = 'PA3-' + letters[num] + '-' + runtype[num] + '-Eval.txt'
        logs_path = os.path.join(log_dir, logs_name)
        time_header = ["brute_time", "kd_time"]
        timer = [brute_time, kd_time]
        
        with open(logs_path, mode='a') as file:
            writer = csv.writer(file, delimiter="\t")
            writer.writerow(headers)
            writer.writerow(c_eval)
            writer.writerow(d_eval)
            writer.writerow(dkck_eval)
            writer.writerow(" ")
            writer.writerow(time_header)
            writer.writerow(timer)

if __name__ == '__main__':
    main()