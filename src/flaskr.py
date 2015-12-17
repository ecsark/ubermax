from flask import Flask
from flask_restful import Resource, Api
from werkzeug.routing import BaseConverter
from uber_max import UberMax
from datetime import datetime
import json

app = Flask(__name__)
app.config.from_object(__name__)
api = Api(app)
planner = UberMax("/Users/ecsark/Documents/bigdata/project/data/")


class LocationTimeConverter(BaseConverter):
	@staticmethod
	def convert_location_time(input):
		locations, time = input.split("@")
		latitude, longitude = locations.split(",")
		dt = datetime.fromtimestamp(int(time) / 1e3)
		return float(latitude), float(longitude), dt

	def to_python(self, value):
		# start, dest = value.split(';')
		# st, ed = self.convert_location_time(start), self.convert_location_time(dest)
		# return st + ed
		return self.convert_location_time(value)

	def to_url(self, values):
		return values[0] + ',' + values[1] + '@' + values[2]


class NextStopPlanner(Resource):
	def get(self, start, end):
		st_latitude, st_longitude, st_time = start
		ed_latitude, ed_longitude, ed_time = end
		next_dest = planner.plan_route((st_latitude, st_longitude), st_time, (ed_latitude, ed_longitude), ed_time)
		return json.dumps(next_dest)


app.url_map.converters['location_tm'] = LocationTimeConverter
api.add_resource(NextStopPlanner, '/next/<location_tm:start>/<location_tm:end>')

if __name__ == '__main__':
	app.run(debug=True)
