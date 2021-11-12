class Algorithm:
    """Algorithm object

    Contains a function that will process the information to find the probabilities of
    each location space containing the target tag.

    Attributes:
        readings: the current readings from the rfid reader in question.
        grid: the grid of Tag objects.
        config: a config object that holds all relevant information from the config file.
        prob_grid: a 2d array of all current probabilities.

    """
    def __init__(self, grid, config):
        self.readings = []
        self.grid = grid
        self.config = config
        self.prob_grid = []

    def __getattr__(self, item):
        if item is 'probabilities':
            prob_grid = []
            for row in self.grid:
                temp_row = []
                for tag in row:
                    temp_row.append(tag.probability)
                prob_grid.append(temp_row)
            return prob_grid

    def main(self, readings):
        self.readings = readings
        self.update_probability_grid()
        sum_of_probability_grid = self.find_probability_grid_sum()
        self.finalize_probability_grid(sum_of_probability_grid)

    def finalize_probability_grid(self, denominator_sum):
        temp_grid = []
        for row in self.prob_grid:
            temp_row = []
            for probability in row:
                temp_row.append(probability/denominator_sum)
            temp_grid.append(temp_row)
        self.grid.update_probabilities(temp_grid)

    def find_probability_grid_sum(self):
        prob_sum = 0
        for row in self.grid:
            for tag in row:
                prob_sum = prob_sum + tag.probability
        return prob_sum

    def update_probability_grid(self):
        for reading1,expected1 in zip(self.readings, self.config.vision_profile):
            print(f'expected tags : {expected1}, read tags : ', end='')
            for tag1 in reading1:
                print(f'{self.grid[tag1]}, ', end='')
            print(' ', end='\n')

        x = 0
        temp_grid = []
        for row in self.grid:
            y = 0
            temp_row = []
            for tag in row:
                if not isinstance(tag, str):
                    prob_sum = 0
                    for reading, expected in zip(self.readings, self.config.vision_profile):
                        prob = self.final_probability(reading, (x, y), tag, expected)
                        prob_sum = prob_sum + prob
                    temp_row.append(tag.probability*prob_sum*(1/16))
                    y = y+1
            temp_grid.append(temp_row)
            x = x+1
        self.prob_grid = temp_grid

    def final_probability(self, reading, current_tag_location, current_tag, expected):
        p1 = self.config.p1
        p2 = self.config.p2
        r = 0
        if current_tag in reading:
            r = 1
        v1 = 0
        if str(current_tag_location) in expected:
            v1 = 1
        v2 = 0
        v3 = 0
        for tag in reading:
            if self.grid[tag] in expected:
                v2 = v2+1
            elif self.grid[tag] not in expected and tag is not 'none' and tag is not 'target':
                v3 = v3+1
        v4 = 0
        for location in expected:
            is_in = 0
            for tag in reading:
                if self.grid[tag] == location:
                    is_in = 1
                    break
            if not is_in:
                v4 = v4+1

        v5 = len(self.grid) - (v2+v3+v4)

        probability = ((p1 ** (r * v1)) * ((1 - p1) ** ((1 - r) * v1)) * (p2 ** (r * (1-v1))) *
                       ((1 - p2) ** ((1 - r) * (1 - v1))) * (p1 ** v2) * ((1 - p1) ** v4) *
                       (p2 ** v3) * ((1 - p2) ** v5))

        print(f'r = {r}, v1 = {v1}, v2 = {v2}, v3 = {v3}, v4 = {v4}, v5 = {v5}')

        return probability
