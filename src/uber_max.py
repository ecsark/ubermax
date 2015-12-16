from scipy.stats import poisson
import heapq
from datetime import datetime, timedelta
import math

import cPickle as pickle

data_dir = "/Users/ecsark/Documents/bigdata/project/data/"
centroids = pickle.load(open(data_dir + "centroids.pk", "rb"))
G = pickle.load(open(data_dir + "G.pk", "rb"))
H = pickle.load(open(data_dir + "H.pk", "rb"))

n_clusters = 75
time_slots = 1
data_date_range = 31

# base, per_minute, per_mile
car_fare = {"UberX": [3.0, 0.4, 2.15],
            "UberXL": [4.5, 0.6, 3.25],
            "UberBlack": [7.0, 0.65, 3.75],
            "UberSUV": [14.0, 0.8, 4.5]}


def compute_fare(time, distance, car_type="UberX"):
	if car_type not in car_fare:
		print "Warning: car type %s not found in database. Use UberX instead." % car_type
		car_type = "UberX"
	fare_model = car_fare[car_type]
	return fare_model[0] + fare_model[1] * time / 60 + fare_model[2] * distance


def lookup_zone(latitude, longitude):
	mindist, minidx = (centroids[0][0] - latitude) ** 2 + (centroids[0][1] - longitude) ** 2, -1
	for zone, c in enumerate(centroids):
		distsq = (c[0] - latitude) ** 2 + (c[1] - longitude) ** 2
		if distsq < mindist:
			mindist = distsq
			minidx = zone
	return minidx


def time_to_index(time):
	return time.hour / time_slots


def estimate_revenue(st_time, pk_zone, dp_zone, th, car_type="UberX"):
	info = G[time_to_index(st_time)][pk_zone][dp_zone]
	mu = float(info[0]) / data_date_range
	prob = 1.0 - poisson.cdf(th, mu)
	if math.isnan(prob) or prob < 0.1:
		return 0
	revenue = compute_fare(info[1], info[2], car_type)
	return prob * revenue


def plan_route(start, start_time, dest, dest_time, th=6, grace_period_seconds=500):
	start_zone = lookup_zone(*start)
	dest_zone = lookup_zone(*dest)
	timeline = []
	max_exp_rev = 0.0
	# time (in seconds) before dest_time, pk_zone, dp_zone, mer
	to_process = [(grace_period_seconds, dest_zone, None, max_exp_rev)]
	while len(to_process) > 0:
		current = heapq.heappop(to_process)
		time_left, dp_zone, mer = current[0], current[1], current[3]
		dp_time = dest_time - timedelta(seconds=time_left)
		if dp_time < start_time: # + timedelta(seconds=grace_period_seconds):
			break
		if dp_time < start_time + \
					timedelta(seconds=G[time_to_index(start_time)][start_zone][dp_zone][1]): # + \
					# grace_period_seconds):
			continue
		if mer < max_exp_rev * 0.8:
			continue
		timeline.append(current)
		for pk_zone, trip_info in enumerate(H[time_to_index(dp_time)][dp_zone]):
			n_time_left = time_left + trip_info[1] + grace_period_seconds
			expectedRevenue = estimate_revenue(dest_time-timedelta(seconds=n_time_left), pk_zone, dp_zone, th)
			heapq.heappush(to_process, (n_time_left, pk_zone, dp_zone, mer + expectedRevenue))
			if mer + expectedRevenue > max_exp_rev:
				max_exp_rev = mer + expectedRevenue
	next_dest = []
	first_total_seconds = (dest_time - start_time).total_seconds()
	for n in timeline:
		if start_zone == n[1]:
			next_dest.append(n)
		first_trip_revenue = estimate_revenue(start_time, start_zone, n[1], th)
		next_dest.append((first_total_seconds, start_zone, n[2], n[3] + first_trip_revenue))
	next_dest = sorted(next_dest, key=lambda k: k[3], reverse=True)
	return next_dest


next_dests = plan_route((40.8047413, -73.9653582), # 40.795675, -73.970410
                       datetime.now(),
                       (40.6413151, -73.7803278),
                       datetime.now() + timedelta(hours=4))
