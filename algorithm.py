class BayesianAlgorithm:
    def __init__(self, history, arduino, mercury, config, grid):
        self.readings = []
        self.config = config
        self.history = history
        self.grid = grid
        self.arduino = arduino
        self.mercury = mercury

    def search_algorithm(self):
        self.readings = self.make_readings()
        prob_of_t_given_prior_data = self.history.most_recent_grid
        prob_solution_of_all_numerators = self.find_numerator(prob_of_t_given_prior_data)
        prob_solution_of_all_denominators = self.find_denominator(prob_of_t_given_prior_data)
        prob_grid = []
        for numerators, row in zip(prob_solution_of_all_numerators, self.grid):
            temp_row = []
            for numerator, tag in zip(numerators, row):
                temp_row.append(numerator / prob_solution_of_all_denominators)
            prob_grid.append(temp_row)
        self.grid.update_probabilities(prob_grid)
        self.history.append(self.grid)
        return self.grid

    def make_readings(self):
        readings = []
        for angles in self.config.search_profile:
            self.arduino.send_angles(angles)

            readings.append(self.parse_reading(self.mercury.make_read(base_read_power=2800)))
        return readings

    def parse_reading(self, reading):
        tags_read = []
        for tag in reading:
            if tag in self.config.target and 'target' not in tags_read:
                tags_read.append('target')
            elif self.grid[tag] not in tags_read:
                tags_read.append(self.grid[tag])
        return tags_read

    def find_numerator(self, prob_of_t_given_prior_data):
        probs_of_numerators_of_all_tags = []
        for row in prob_of_t_given_prior_data:
            temp_row = []
            for tag in row:
                temp_row.append(self.prob_of_numerator_for_single_tag(tag.probability))
            probs_of_numerators_of_all_tags.append(temp_row)
        return probs_of_numerators_of_all_tags

    def prob_of_numerator_for_single_tag(self, prior_probability_of_tag):
        return self.prob_of_z_given_t() * prior_probability_of_tag

    def find_denominator(self, prob_of_t_given_prior_data):
        prob_of_denominator = 0
        for row in prob_of_t_given_prior_data:
            for tag in row:
                prob_of_denominator = prob_of_denominator + self.prob_of_denominator_for_single_tag(tag.probability)
        return prob_of_denominator

    def prob_of_denominator_for_single_tag(self, prior_probability_of_tag):
        return self.prob_of_z_given_t() * prior_probability_of_tag

    def prob_of_z_given_t(self):
        probability_sum = 0
        prob_of_f_n = 1 / (len(self.readings))
        for reading, sight in zip(self.readings, self.config.vision_profile):
            probability_sum = probability_sum + (self.prob_of_z_given_t_and_f(reading, sight) * prob_of_f_n)
        return probability_sum

    def prob_of_z_given_t_and_f(self, reading, expected):
        """
        ##@param reading is the current reading made
        ##@param expected is the expected
        ##Figure out if expected is needed or if the actual angles are needed.
        ##If the expected are needed, leave as is, if the angles are needed then just
        ##zip the searchprofile instead of visionprofile
        #TODO base this off of Navid's corrected equation
        """
        p1 = self.config.p1
        p2 = self.config.p2
        r = 0
        if 'target' in reading:
            r = 1
        probability = (p1**r) * ((1-p1)**(1-r)) * (p2**r) * ((1-p2)**(1-r)) * p1 * (1-p1) * p2 * (1-p2)
        return probability
