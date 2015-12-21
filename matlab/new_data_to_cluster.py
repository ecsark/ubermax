from scipy.stats import poisson
import heapq
from datetime import datetime, timedelta
import math

import cPickle as pickle


data_dir = "/Volumes/Transcend/database/"
centroids = pickle.load(open(data_dir + "centroids.pk", "rb"))

taxi_file_name = data_dir + "june_revenue.csv"
output_file_name = data_dir + "juneaggregate.csv"

def lookup_zone(latitude, longitude):
	mindist, minidx = (centroids[0][0] - latitude) ** 2 + (centroids[0][1] - longitude) ** 2, -1
	for zone, c in enumerate(centroids):
		distsq = (c[0] - latitude) ** 2 + (c[1] - longitude) ** 2
		if distsq < mindist:
			mindist = distsq
			minidx = zone
	return minidx

output_file = open(output_file_name, 'wb')
input_file=open(taxi_file_name, 'rb')

result=list()
for line in input_file.readlines():
    tripinfo = line.split(',')
    pickhour=tripinfo[0]
    revenue=tripinfo[1]
    tm=tripinfo[2]
    dist=tripinfo[3]

    pklat=float(tripinfo[4])
    pklong=float(tripinfo[5])
    pkzone=lookup_zone(pklat,pklong)
    #pkcenterlat=centroids[pkzone][0]
    #pkcenterlong=centroids[pkzone][1]

    dflat=float(tripinfo[6])
    dflong=float(tripinfo[7])
    dfzone=lookup_zone(dflat,dflong)
    #dfcenterlat=centroids[dfzone][0]
    #dfcenterlong=centroids[dfzone][1]

    print pkzone,dfzone
    output_file.write(pickhour + "," + str(revenue)+"," + tm +","+dist+",")
    output_file.write(str(pkzone) + "," + str(dfzone) + ","+"\n")
    #output_file.write(str(dfcenterlat) + "," + str(dfcenterlong) + "\n")


output_file.close()