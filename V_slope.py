import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression

# Read the Excel file
ramp_file = pd.read_excel('ramp_processed.xlsx', sheet_name='2')

# Filter data for power between MRT and AeT
ramp_file = ramp_file[(ramp_file['power'] > 100) & (ramp_file['power'] < 160)]


# Create subplots
fig, ax = plt.subplots(figsize=(10, 15))

dot_size = 50

# Modify 'VO2' values by dividing by 1000
ramp_file['VO2'] /= 1000

# Plot Graph 1 - VE
sns.scatterplot(x='power', y='VO2', data=ramp_file, color='blue', label='VO2', s=dot_size)

# Add regression line
sns.regplot(x='power', y='VO2', data=ramp_file, scatter=False, ax=ax, color='red', label='Regression Line')

# Fit regression line
X = ramp_file[['power']]  
y = ramp_file['VO2']  
regressor = LinearRegression()
regressor.fit(X, y)

# Retrieve coefficients
slope = regressor.coef_[0]
intercept = regressor.intercept_

# Print regression line formula
regression_formula = f'VO2 = {slope:.4f} * power + {intercept:.4f}'
print("Regression Line Formula:", regression_formula)

# Add regression formula text to the plot
ax.text(0.1, 0.9, regression_formula, transform=ax.transAxes, fontsize=12, verticalalignment='top')

ax.set_xlabel('Power (Watt)')
ax.set_ylabel('VO2 (L/min)')  # Adjust the y-axis label

# General title
fig.suptitle("V-slope", fontsize=16)

plt.show()
