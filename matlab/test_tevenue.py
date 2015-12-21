from scipy.stats import poisson
import heapq
from datetime import datetime, timedelta
import math

import cPickle as pickle


data_dir = "/Volumes/Transcend/database/"
centroids = pickle.load(open(data_dir + "centroids.pk", "rb"))
g = pickle.load(open(data_dir + "G.pk", "rb"))

taxi_file_name = data_dir + "taxi_green_201506.csv"
output_file_name = data_dir + "june_revenue.csv"




UberX=[3.0, 0.4, 2.15]


output_file = open(output_file_name, 'wb')
input_file=open(taxi_file_name, 'rb')

result=list()
for line in input_file.readlines():
    tripinfo = line.split(',')
    pickhour=tripinfo[0]
    tm=tripinfo[1]
    dist=tripinfo[2]

    pklat=float(tripinfo[3])
    pklong=float(tripinfo[4])
    dflat=float(tripinfo[5])
    dflong=float(tripinfo[6])

    revenue=UberX[0]+UberX[1]*float(tm)/60+UberX[2]*float(dist)
    #if int(pickhour) in range(8,20):
    output_file.write(pickhour + "," + str(revenue)+"," + tm +","+dist+",")
    output_file.write(str(pklat) + "," + str(pklong) + ",")
    output_file.write(str(dflat) + "," + str(dflong) + "\n")


output_file.close()