The files are for CIS1 Programming assignment 1.

Required Packages and environment:

The env.yml should construct a conda environment used to run this package include as followings:
genericpath, numpy, glob, pathlib, argparse, os, copy and csv.

Running the program:

main.py gives you the proper outputs listed in the output files. Using ./main.py --help
./main.py [path to data directory] [0 or 1 for debug or unknown] [the index of the letter the file carries(0-10 for a to k)] [path to output directory]
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

3. distort_calibration.py: Used for calculating C_exp in the output files.

4. pivot_calibration.py: Used for calculating pivot calibration. Used in both Question 5 and 6.

5. registration_3d.py: Used for calculating point set to point set transformations.

6. em_tracking and optic_tracking: Just as the name describes, these two files are used for calculating problem 5 and 6.

7. eval.py: Used for evaluating and calculating the error between the output calculated by us and the given correct answers. The output is broken up into the average, variance and max and min of the errors.

8. main.py: This file puts all components together, as given above, running this file gives you the output and error evaluation files. The files will be stored in designated positions.

9. CIS PA1 Report: The complete report of this assignment.
