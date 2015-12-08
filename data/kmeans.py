from sklearn.cluster import MiniBatchKMeans#, KMeans

#kmeans = KMeans(n_clusters=50, n_jobs=-1)
n_clusters = 80

kmeans = MiniBatchKMeans(n_clusters=n_clusters)
data_pk, data_df, data_dist, data_tm = [], [], [], []

print "Importing"

with open ("/Users/ecsark/Documents/bigdata/project/data/green_2015-01_location_comp.csv", 'rb') as f:
	for line in f:
		s = line.split(",")
		data_pk.append([float(s[3]), float(s[4])])
		data_df.append([float(s[5]), float(s[6])])
		data_dist.append(float(s[2]))
		data_tm.append(float(s[1]))

print "Clustering"

kmeans.fit(data_pk+data_df)

count, dist, tm = [[0] * n_clusters] * n_clusters, [[0.0] * n_clusters] * n_clusters, [[0.0] * n_clusters] * n_clusters
data_size = len(data_pk)

print "Statistics"

for i in range(data_size):
	pk, df = kmeans.labels_[i], kmeans.labels_[i+data_size]
	c = count[pk][df]
	dist[pk][df] = dist[pk][df] * float(c)/(c+1) + data_dist[i]/(c+1)
	tm[pk][df] = tm[pk][df] * float(c)/(c+1)  + data_tm[i]/(c+1)
	count[pk][df] = c+1

def planRoute(start, dest, remain_time):
	start_zone = kmeans.predict(start)[0]
	dest_zone = kmeans.predict(dest)[0]
	pass