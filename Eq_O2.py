import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Read the Excel file
ramp_file = pd.read_excel('ramp_processed.xlsx', sheet_name='2')

# Create subplots
fig, ax = plt.subplots(figsize=(10, 15))

dot_size = 50

# Plot Graph 1 - VE
sns.scatterplot(x='power', y='eq_o2', data=ramp_file, color='blue', label='Eq_O2', s=dot_size)

# Perform clustering on the data
X = ramp_file[['power', 'eq_o2']]
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
ramp_file['cluster'] = kmeans.labels_

# Define colors for regression lines
colors = ['green', 'blue']  # Example colors

# Fit regression lines to each cluster
for cluster in range(2):
    cluster_data = ramp_file[ramp_file['cluster'] == cluster]
    sns.regplot(x='power', y='eq_o2', data=cluster_data, scatter=False, color=colors[cluster])

ax.set_xlabel('Power (Watt)', fontweight='bold')
ax.set_ylabel('Equivalent O2 (VE/VO2)', fontweight='bold')

#Based on the regression lines, treshold can be visualized using vertical lines and x-ticks
# Draw dashed green line at x=170
plt.axvline(x=160, color='green', linestyle='--', label='Aerobic Treshold')
# Add tick for the Aerobic Treshold
ticks = [160]

# Add highest and lowest x-axis values
ticks.extend([ramp_file['power'].min(), ramp_file['power'].max()])

ax.set_xticks(ticks)

# General title
fig.suptitle("Equivalent O2", fontsize=16)

# Add legend
ax.legend()

# Adjust layout
plt.tight_layout()

# Show plot
plt.show()
