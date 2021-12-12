The files are for CIS1 Programming assignment 4.

Required Packages and environment:

The env.yml should construct a conda environment used to run this package include as followings:
genericpath, numpy, glob, pathlib, argparse, os, copy and csv.

Running the program:

main.py gives you the proper outputs listed in the output files. Using ./main.py --help
./main.py [path to data directory] [the index of the letter the file carries(0-8)] [path to output directory]
Optional argument: --eval [True or False]

Explanations of each file:

1. All ipynb files are not actually used files in main. They are just scratch programs we created when developing used for testing.

2. cartesian.py: Created first and includes multiple functions:
    a. isRot: This function determines whether the given R matrix is a rotation matrix or not.
    b. Ri: This function calculates the inverse of a Rotation matrix.
    c. get_R and get_t: Returns the rotation and translation of a frame.
    d. concat_frame: Given a rotation and a translation, return a frame.
    e. Fi: Returns the inverse of a frame.
    f. points_transform: Given a point and a transformation, return the resulting points.
    g. combinations: Given two numbers: N and k, return the results of N choose k.

3. registration_3d.py: Used for calculating point set to point set transformations.

4. main.py: This file puts all components together, as given above, running this file gives you the output and error evaluation files. The files will be stored in designated positions.

5. CIS1 PA3 Report: The complete report of this assignment.

6. read_files.py: Contains function which reads from all types of data files.
    a. read_mesh: Reads the mesh file.
    b. read_body: Reads the Body A and Body B data.
    c. read_sample: Reads SampleTestReadings for each set of data.
    d. read_output: Used at the end to compare our results with. These
    data will be used as the ground truth to determine our error rate.

7. run.sh and clean.sh: run.sh runs all existing letter files from a to h, clean.sh clears all output and eval files.

8. ICPmatching.py:
    a. point_to_triangle and get_rectangles are both functions used for getting the bounding box.
    b. brute_force_matching: Using a linear method for finding the closest points and completing the matching.
    c. FindClosestPoint: Finds the closest point for brute_force_matching
    d. get_d_k: Calculates d_k according to the given formula on the
    assignment instructions
    e. ProjectOnSegment: Using interpolation to find c* in the given
    formula.

9. KD_tree.py:
    a. Class KD_tree:
        ● pushup, point_to_cube, find and build are all basic functions
        of the KD_tree
        ● FindClosestPoint is as the name suggests, used for
        calculating the closest point on a kd tree structure.
    b. kd_matching: First get rectangles then use the results to build the
    kd tree. Then apply the find_closest_point function to get the results.
    c. ICP: Calculates the Freg and ck like before. However, at the end of each iteration, the difference between the previous and current Freg is compared. If the difference is small enough(less than 1e-4), it is considered solved. In addition, the default option now is using the KD_tree method. We will further discuss the results and how huge the time difference is later.
    Note that this is placed in KD_tree.py in order to avoid causing mutual importing with ICPmatching.py.
