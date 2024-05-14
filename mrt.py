import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import KMeans

# Read the Excel file
ramp_file = pd.read_excel('mrt_ramp.xlsx', sheet_name='2')

# Create a new column representing time points
ramp_file['Time'] = range(len(ramp_file))

# Create subplots
fig, ax = plt.subplots(figsize=(15, 10))

dot_size = 50

# Plot Graph 1 - VE
sns.scatterplot(x='Time', y='VO2', data=ramp_file, color='blue', s=dot_size)

# Perform clustering on the data
X = ramp_file[['Time', 'VO2']]
kmeans = KMeans(n_clusters=2, random_state=0).fit(X)
ramp_file['cluster'] = kmeans.labels_

# Fit regression lines to each cluster
for cluster in range(2):
    cluster_data = ramp_file[ramp_file['cluster'] == cluster]
    sns.regplot(x='Time', y='VO2', data=cluster_data, scatter=False)

ax.set_xlabel('Time')
ax.set_ylabel('L/min')

# Set x-ticks and labels
start_index = ramp_file[ramp_file['power'] == 80].index[0]
end_index = ramp_file[ramp_file['power'] == 80].index[-1]
max_index = ramp_file['power'].idxmax()

ax.set_xticks([start_index, end_index, max_index])
ax.set_xticklabels([ramp_file.loc[start_index, 'power'], ramp_file.loc[end_index, 'power'], ramp_file.loc[max_index, 'power']])

# General title
fig.suptitle("Subject 5", fontsize=16)

# Adjust layout
plt.tight_layout()

# Show plot
plt.show()
