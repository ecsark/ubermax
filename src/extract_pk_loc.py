data_dir = "/Users/ecsark/Documents/bigdata/project/data/"

taxi_file_name = data_dir + "green_tripdata_2015-05.csv"
output_file_name = data_dir + "taxi_green_201505.csv"
if "yellow" in taxi_file_name:
	pk_time, dp_time = 1, 2
	dist = 4
	pk_long, pk_lati = 5, 6
	dp_long, dp_lati = 9, 10
elif "green" in taxi_file_name:
	pk_time, dp_time = 1, 2
	dist = 10
	pk_long, pk_lati = 5, 6
	dp_long, dp_lati = 7, 8
total = -1
counter = -1

date_format = '%Y-%m-%d %H:%M:%S'

output_file = open(output_file_name, 'wb')
with open(taxi_file_name, 'rb') as taxi_file:
	for line in taxi_file:
		counter += 1
		if counter == 0:
			continue
		if 0 < total <= counter:
			break
		tokens = line.split(',')
		if float(tokens[pk_long]) == 0.0 or float(tokens[pk_lati]) == 0.0 or float(tokens[dp_long]) == 0.0 or float(tokens[dp_lati]) == 0.0:
			continue
		#pickup_time = datetime.strptime(tokens[pk_time], date_format)
		#dropoff_time = datetime.strptime(tokens[dp_time], date_format)
		#delta = (dropoff_time - pickup_time).total_seconds()
		output_file.write(tokens[pk_time] + "," + tokens[dp_time] + "," + tokens[dist] + ",")
		output_file.write(tokens[pk_lati] + "," + tokens[pk_long] + ",")
		output_file.write(tokens[dp_lati] + "," + tokens[dp_long] + "\n")

output_file.close()