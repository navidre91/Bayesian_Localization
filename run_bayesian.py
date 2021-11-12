import plotly
import plotly.graph_objs as go

from algo import Algorithm
from communication import ArduinoHandler
from communication import MercuryHandler
from data_obj import Config
from data_obj import Grid


def run():
	"""
	Runs the core program
	:return: None
	"""
	config = Config('config.yaml')
	arduino = ArduinoHandler(config.arduino)
	mercury = MercuryHandler(config.mercury, base_read_power=2900)
	grid = Grid(config.tag_ids, config.grid_size)
	algorithm = Algorithm(grid, config)
	print("how many times would you like to run the algorithm? : ")
	loops = int(input())
	for x in range(loops):
		readings = []
		for facing in config.search_profile:
			readings.append(take_reading(arduino, mercury, facing, grid, config))
		algorithm.main(readings)
	normalized_probability_grid = normalize_probabilities(algorithm.probabilities)
	plot_data(normalized_probability_grid)


def normalize_probabilities(probabilities):
	"""
	Takes the probabilities found in the algorithm and creates conditional probabilities which sum to 1
	while ensuring that relative proportions remain constant.
	:param probabilities: the existing probability heatmap of grid spaces
	:return: normalized heat_map of conditional probabilities (ensures the sum of probabilities in the map equals 1)
	"""
	prob_sum = 0
	for row in probabilities:
		for prob in row:
			prob_sum = prob_sum + prob
	normalized = []
	for row in probabilities:
		temp_row = []
		for prob in row:
			temp_row.append(prob/prob_sum)
		normalized.append(temp_row)
	return normalized


def take_reading(arduino, mercury, angle, grid, config):
	"""
	Handles communication with the sensors and servos to take a reading
	:param arduino: arduino handling object
	:param mercury: mercury RFID reader handling object
	:param angle: angle to pass to the arduino for movement
	:param grid: known grid setup for understanding which tag spaces were read
	:param config: used only to access the target tag ids
	:return: returns a call to parse_reading which returns the tag objects read
	"""
	print('before sending')
	arduino.send_angles(angle)
	print('after sending')
	reading = []
	for i in range(6):
		reading.extend(mercury.make_read())
	return parse_reading(reading, grid, config)


def parse_reading(reading, grid, config):
	"""
	Parses the raw reading taken by the mercury RFID reader.
	:param reading: the raw reading taken (the tag ids that were read)
	:param grid: the known grid setup which allows to match ids to gridspaces
	:param config: used to access the target tag id
	:return: a list of the tag objects read
	"""
	tags_read = []
	for tag in reading:
		if tag in config.target and 'target' not in tags_read:
			tags_read.append('target')
		elif grid[tag] not in tags_read:
			tags_read.append(grid[tag])
	return tags_read


def plot_data(data):
	"""
	plots data into an html heatmap using the free service plotly
	:param data: the 2d array of probability values to read
	:return: None
	"""
	graph = [go.Heatmap(z=data)]
	plotly.offline.plot(graph, filename='heatMap.html')

	
if __name__ == '__main__':
	run()
