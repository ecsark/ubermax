from sklearn.cluster import MiniBatchKMeans#, KMeans
from datetime import datetime, timedelta
import cPickle as pickle

#kmeans = KMeans(n_clusters=50, n_jobs=-1)
n_clusters = 75
time_slots = 1
data_date_range = 31

kmeans = MiniBatchKMeans(n_clusters=n_clusters)
data_pk, data_df, data_dist, data_tm, data_st_tm, data_ed_tm = [], [], [], [], [], []

print "Importing"

date_format = '%Y-%m-%d %H:%M:%S'

data_dir = "/Users/ecsark/Documents/bigdata/project/data/"

def read_data(file_name):
	with open(file_name, 'rb') as f:
		for line in f:
			s = line.split(",")
			data_pk.append([float(s[3]), float(s[4])])
			data_df.append([float(s[5]), float(s[6])])
			data_dist.append(float(s[2]))
			pickup_time = datetime.strptime(s[0], date_format)
			dropoff_time = datetime.strptime(s[1], date_format)
			delta = (dropoff_time - pickup_time).total_seconds()
			data_tm.append(delta)
			data_st_tm.append((pickup_time).hour/time_slots)
			data_ed_tm.append((dropoff_time).hour/time_slots)

read_data(data_dir + "taxi_green_201505.csv")
read_data(data_dir + "taxi_yellow_201505.csv")

print "Clustering"

kmeans.fit(data_pk+data_df)

pickle.dump(kmeans.cluster_centers_, open(data_dir + "centroids.pk", "wb"))
pickle.dump(kmeans, open(data_dir + "clust_model.pk", "wb"))

# count, trip time in seconds, distance
G, H = [], []
for i in range(24/time_slots):
	GA, HA = [], []
	for j in range(n_clusters):
		GB, HB = [], []
		for k in range(n_clusters):
			GB.append((0, 0.0, 0.0))
			HB.append((0, 0.0, 0.0))
		GA.append(GB)
		HA.append(HB)
	G.append(GA)
	H.append(HA)


data_size = len(data_pk)

print "Statistics"

for i in range(data_size):
	pk, dp = kmeans.labels_[i], kmeans.labels_[i+data_size]
	st_tm, ed_tm = data_st_tm[i], data_ed_tm[i]
	c, t, d = G[st_tm][pk][dp]
	G[st_tm][pk][dp] = c+1, t*float(c)/(c+1)+data_tm[i]/float(c+1), d*float(c)/(c+1)+data_dist[i]/float(c+1)
	c, t, d = H[ed_tm][dp][pk]
	H[ed_tm][dp][pk] = c+1, t*float(c)/(c+1)+data_tm[i]/float(c+1), d*float(c)/(c+1)+data_dist[i]/float(c+1)


pickle.dump(G, open(data_dir + "G.pk", "wb"))
pickle.dump(H, open(data_dir + "H.pk", "wb"))