from scipy.stats import poisson
import heapq
from datetime import datetime, timedelta
import math
import cPickle as pickle


class UberMax:
	def __init__(self, data_dir, n_clusters=32, time_slots=1, data_date_range=31):
		self.centroids = pickle.load(open(data_dir + "centroids.pk", "rb"))
		self.G = pickle.load(open(data_dir + "G.pk", "rb"))
		self.H = pickle.load(open(data_dir + "H.pk", "rb"))
		self.n_clusters = n_clusters
		self.time_slots = time_slots
		self.cached_cdf = {}
		self.data_date_range = data_date_range
		# base, per_minute, per_mile
		self.car_fare = {"UberX": [3.0, 0.4, 2.15],
		                 "UberXL": [4.5, 0.6, 3.25],
		                 "UberBlack": [7.0, 0.65, 3.75],
		                 "UberSUV": [14.0, 0.8, 4.5]}

	def compute_fare(self, time, distance, car_type="UberX"):
		if car_type not in self.car_fare:
			print "Warning: car type %s not found in database. Use UberX instead." % car_type
			car_type = "UberX"
		fare_model = self.car_fare[car_type]
		return fare_model[0] + fare_model[1] * time / 60 + fare_model[2] * distance

	def lookup_zone(self, latitude, longitude):
		min_dist, min_idx = (self.centroids[0][0] - latitude) ** 2 + (self.centroids[0][1] - longitude) ** 2, -1
		for zone, c in enumerate(self.centroids):
			dist_sq = (c[0] - latitude) ** 2 + (c[1] - longitude) ** 2
			if dist_sq < min_dist:
				min_dist = dist_sq
				min_idx = zone
		return min_idx

	def resolve_zone(self, zone_id):
		return self.centroids[zone_id][0], self.centroids[zone_id][1]

	def time_to_index(self, time):
		return time.hour / self.time_slots

	def estimate_revenue(self, st_time, pk_zone, dp_zone, th, car_type="UberX", zero_threshold=0.1):
		info = self.G[self.time_to_index(st_time)][pk_zone][dp_zone]
		mu = float(info[0]) / self.data_date_range
		prob = 1.0 - poisson.cdf(th, mu)
		if math.isnan(prob) or prob < zero_threshold:
			return 0
		revenue = self.compute_fare(info[1], info[2], car_type)
		return prob * revenue

	def estimate_revenue2(self, st_time_index, pk_zone, dp_zone, th, car_type="UberX", zero_threshold=0.1):
		info = self.G[st_time_index][pk_zone][dp_zone]
		mu = float(info[0]) / self.data_date_range
		key_tuple = (th, mu)
		if key_tuple not in self.cached_cdf:
			self.cached_cdf[key_tuple] = 1.0 - poisson.cdf(*key_tuple)
		prob = self.cached_cdf[key_tuple]
		if math.isnan(prob) or prob < zero_threshold:
			return 0
		revenue = self.compute_fare(info[1], info[2], car_type)
		return prob * revenue

	def incremental_compute(self, max_hop=5, accuracy=5, max_shift=6, th=12, grace_period_seconds=500):
		time_unit = 3600 / accuracy
		S = []
		for i in range(self.n_clusters):
			arr_j = []
			for j in range(self.n_clusters):
				arr_k = []
				for k in range(24 * accuracy):
					arr_h = []
					for h in range(max_shift * accuracy):
						arr_h.append(0)
					arr_k.append(arr_h)
				arr_j.append(arr_k)
			S.append(arr_j)
		for hop in range(max_hop):
			for pk_zone in range(self.n_clusters):
				print "PK_ZONE " + str(pk_zone)
				for df_zone in range(self.n_clusters):
					print "DF_ZONE " + str(df_zone)
					for t1_z in range(24 * accuracy):
						pk_time_idx = t1_z / accuracy / self.time_slots
						for shift_z in range(max_shift * accuracy):
							df_time_z = t1_z + shift_z
							if df_time_z > 24 * accuracy:
								continue
							actual_df_time = (t1_z + shift_z) * time_unit
							for next_stop in range(self.n_clusters):
								demands_1, trip_time_1, distance_1 = self.G[pk_time_idx][pk_zone][next_stop]
								if trip_time_1 > shift_z * time_unit:
									continue
								seconds_left = int(shift_z * time_unit - trip_time_1 - grace_period_seconds)
								if seconds_left < 0:
									continue
								depart_time_2 = actual_df_time - seconds_left
								t2_z = depart_time_2 / time_unit
								new_revenue = S[next_stop][df_zone][t2_z][seconds_left/time_unit] + \
											self.estimate_revenue2(pk_time_idx, pk_zone, next_stop, th)
								if new_revenue > S[pk_zone][df_zone][t1_z][shift_z]:
									S[pk_zone][df_zone][t1_z][shift_z] = new_revenue
		return S

	@staticmethod
	def time_to_tz(time, accuracy):
		return (time.hour * 3600 + time.minute * 60 + time.second) * accuracy / 3600

	def plan_route2(self, S, accuracy, start, start_time, dest, dest_time, th=12, grace_period_seconds=500):
		time_unit = 3600 / accuracy
		start_zone = self.lookup_zone(*start)
		dest_zone = self.lookup_zone(*dest)
		total_seconds = (dest_time - start_time).total_seconds()
		rank = []
		for next_stop in range(self.n_clusters):
			demands_1, trip_time_1, distance_1 = self.G[self.time_to_index(start_time)][start_zone][next_stop]
			seconds_left = int(trip_time_1 - total_seconds)
			if seconds_left < 0:
				continue
			depart_time_2 = start_time + timedelta(seconds=trip_time_1)
			t2_z = self.time_to_tz(depart_time_2, accuracy)
			total_revenue = S[next_stop][dest_zone][t2_z][seconds_left/time_unit] + \
			                self.estimate_revenue(start_time, start_zone, next_stop, th)
			rank.append((self.resolve_zone(next_stop), total_revenue))
		rank = sorted(rank, key=lambda x: x[0], reverse=True)
		return rank


	def plan_route(self, start, start_time, dest, dest_time, th=12, grace_period_seconds=500, soft_margin=0.8):
		start_zone = self.lookup_zone(*start)
		dest_zone = self.lookup_zone(*dest)
		timeline = []
		max_exp_rev = 0.0
		# time (in seconds) before dest_time, pk_zone, dp_zone, mer
		to_process = [(grace_period_seconds, dest_zone, None, max_exp_rev)]
		while len(to_process) > 0:
			current = heapq.heappop(to_process)
			time_left, dp_zone, mer = current[0], current[1], current[3]
			dp_time = dest_time - timedelta(seconds=time_left)
			if dp_time < start_time:  # + timedelta(seconds=grace_period_seconds):
				break
			if dp_time < start_time + timedelta(seconds=self.G[self.time_to_index(start_time)][start_zone][dp_zone][1]):
				continue
			if mer < max_exp_rev * soft_margin:
				continue
			timeline.append(current)
			for pk_zone, trip_info in enumerate(self.H[self.time_to_index(dp_time)][dp_zone]):
				n_time_left = time_left + trip_info[1] + grace_period_seconds
				exp_revenue = self.estimate_revenue(dest_time - timedelta(seconds=n_time_left), pk_zone, dp_zone, th)
				heapq.heappush(to_process, (n_time_left, pk_zone, dp_zone, mer + exp_revenue))
				if mer + exp_revenue > max_exp_rev:
					max_exp_rev = mer + exp_revenue
		next_dest = []
		# first_total_seconds = (dest_time - start_time).total_seconds()
		for n in timeline:
			first_trip_revenue = self.estimate_revenue(start_time, start_zone, n[1], th)
			next_dest.append((n[1], n[3] + first_trip_revenue))
		next_dest = sorted(next_dest, key=lambda k: k[1], reverse=True)
		results = []
		hops = {}
		for n in next_dest:
			if n[0] not in hops:
				results.append((self.resolve_zone(n[0]), n[1]))
				hops[n[0]] = 1
		return results


def test():
	planner = UberMax("/Users/ecsark/Documents/bigdata/project/data/")
	next_dests = planner.plan_route((40.8047413, -73.9653582),  # 40.795675, -73.970410
	                                datetime.now(),
	                                (40.7089968, -73.9543139),  # (40.6413151, -73.7803278),
	                                datetime.now() + timedelta(hours=3))
	print next_dests


"""
planner = UberMax("/Users/ecsark/Documents/bigdata/project/data/")
S = planner.incremental_compute()
pickle.dump(S, open("/Users/ecsark/Documents/bigdata/project/data/" + "S.pk", "wb"))
"""