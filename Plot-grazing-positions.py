import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
file4 = '/Users/otilia/Desktop/angle-90rho.csv'
data4 = pd.read_csv(file4)

# Plot data from the first file
plt.plot(data4['Angle'], data4['Detection_Percentage'],color='purple', label='90 impact')
# Read the first CSV file
file1 = '/Users/otilia/Desktop/angle-95rho.csv'
data1 = pd.read_csv(file1)

# Plot data from the first file
plt.plot(data1['Angle'], data1['Detection_Percentage'], label='95 impact')

# Read the second CSV file
file2 = '/Users/otilia/Desktop/angle-97rho.csv'
data2 = pd.read_csv(file2)

# Plot data from the second file on the same plot
plt.plot(data2['Angle'], data2['Detection_Percentage'], label='97 impact')

file3 = '/Users/otilia/Desktop/angle-100rho.csv'
data3 = pd.read_csv(file3)

# Plot data from the first file
plt.plot(data3['Angle'], data3['Detection_Percentage'], label='100 impact')


# Customize the plot
plt.ylabel('Detection Percentage')
plt.xlabel('Angle (degrees)')
plt.title('Detection Percentage vs. Angle')
plt.xticks(np.arange(0, 181, 20))
# Adjust x-axis ticks and labels
# plt.xticks(np.arange(0, 181, 10))  # Increasing the font size of x-axis ticks

# Adjust grid settings
plt.grid(True, linestyle='--', alpha=0.7)

plt.legend()  # Show legend with labels
plt.show()

