from datetime import datetime, timedelta

taxi_file_name = "green_tripdata_2015-01.csv"
output_file_name = "green_2015-01_location_comp.csv"
total = 90000000
counter = -1
pickup = True

date_format = '%Y-%m-%d %H:%M:%S'

output_file = open(output_file_name, 'wb')
with open(taxi_file_name, 'rb') as taxi_file:
	for line in taxi_file:
		counter += 1
		if counter == 0:
			continue
		if counter <= total:
			tokens = line.split(',')
			if float(tokens[6]) == 0.0 or float(tokens[5]) == 0.0 or float(tokens[8]) == 0.0 or float(tokens[7]) == 0.0:
				continue
			pickup_time = datetime.strptime(tokens[1], date_format)
			dropoff_time = datetime.strptime(tokens[2], date_format)
			delta = (dropoff_time - pickup_time).total_seconds()
			output_file.write(tokens[1] + "," + str(delta) + "," + tokens[10] + ",")
			output_file.write(tokens[6] + "," + tokens[5] + ",")
			output_file.write(tokens[8] + "," + tokens[7] + "\n")
		else:
			break

output_file.close()