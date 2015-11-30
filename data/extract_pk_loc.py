taxi_file_name = "green_tripdata_2015-01.csv"
output_file_name = "green_2015-01_location.csv"
total = 1000
counter = -1
pickup = True


output_file = open(output_file_name, 'wb')
with open(taxi_file_name, 'rb') as taxi_file:
	for line in taxi_file:
		counter += 1
		if counter == 0:
			continue
		if counter <= total:
			tokens = line.split(',')
			if pickup:
				output_file.write(tokens[6] + "," + tokens[5] + "\n")
			else:
				output_file.write(tokens[8] + "," + tokens[7] + "\n")
		else:
			break

output_file.close()