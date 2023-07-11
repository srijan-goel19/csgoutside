import os
import glob

import pandas as pd

label_list = glob.glob(os.path.join(
    r'C:\Small_dset\test\labels', '*.txt'))

for file in label_list:
    with open(file, 'r') as f:
        rows = f.readlines()

        for row in rows:
            row_data = [float(x) for x in row.split()]

            if (row_data[3] > 1.0 or row_data[4] > 1.0):
                print("fuckkk")
