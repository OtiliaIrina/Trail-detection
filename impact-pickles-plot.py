import numpy as np
import pandas as pd
from astropy.io import fits
import matplotlib.pyplot as plt
import pickle

# Loading 'data' DataFrame from pickle
with open('satCross-info-rho100-90deg.pkl', 'rb') as f:
    loaded_data = pickle.load(f)

# Assuming 'n_lines_detected' and 'impact_param' columns are in loaded_data DataFrame
x = loaded_data['n_lines_detected']
y = loaded_data['trail_angle']

plt.figure(figsize=(8, 6))
plt.scatter(x, y, s=50, alpha=0.5, edgecolors='w')
plt.xlabel('Number of lines detected')
plt.ylabel('Trail Angle')
plt.title('For input impact parameter of 100')
plt.grid(True)

# Calculating the median of the y-axis data
median_y = loaded_data['trail_angle'].median()

# Calculating the mean of the y-axis data
mean_y = loaded_data['trail_angle'].mean()

# Plotting the mean line on the y-axis
plt.axhline(y=mean_y, color='g', linestyle='-', label=f'Mean: {mean_y:.2f}')

# Plotting the median line on the y-axis
plt.axhline(y=median_y, color='r', linestyle='--', label=f'Median: {median_y:.2f}')
plt.legend()


