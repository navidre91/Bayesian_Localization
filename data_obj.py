import yaml


class Tag:
    """Tag data object.

    Data type which contains the ids contained in a grid-space and the current f(X=current) probability.

    Attributes:
        id: the ids of the grid_tags in the current_grid space.
        probability: the probability that the target tag is near this tag.
    """

    def __init__(self, tag_id, initial_prob):
        """
        Initializes with given id and probability.
        :param tag_id: the ids of the tag.
        :param initial_prob: double of initial probability (based on the number of tags total).
        """
        self.id = tag_id
        self.probability = initial_prob

    def __getattr__(self, item):
        """
        Allows accessing the values of attributes.
        :param item: string of the object being accessed.
        :return: the value of the value being asked for.
        """
        if item is 'id':
            return self.id
        elif item is 'probability':
            return self.probability
        else:
            raise AttributeError

    def __eq__(self, other):
        """
        Tests equivalence with a tag.
        :param other: the other value to check equivalence to.
        :return: boolean of equivalence.
        """
        if type(other) is Tag:
            if self.id == other.id:
                return True
        elif self.id == other:
            return True
        return False

    def set_prob(self, new_prob):
        """
        Sets probability.
        :param new_prob: probability to be set.
        :return: None
        """
        self.probability = new_prob

    def update_probability(self, probability):
        """
        Multiplies given probability with current probability.
        :param probability: prob to be multiplied to self probability.
        :return: None
        """
        self.probability = self.probability * probability

    def __contains__(self, item):
        """
        Checks whether or not the item is in the self ids.
        :param item: String of RFID id.
        :return: boolean of whether the item is in the self ids or not.
        """
        if item in self.id:
            return True
        return False


class Grid:
    """Grid object.

    Data type which contains a 2d array of tag objects in their real-world locations.

    Attributes:
        grid: 2d array of tag objects.
        grid_size: int of total number of spaces.
    """

    def __init__(self, tags, grid_size):
        """
        Initializes the grid data object.
        :param tags: the RFID tags to populate the grid.
        :param grid_size: the total number of grid spaces.
        """
        self.grid = self.generate_grid(tags, grid_size)
        self.grid_size = grid_size

    def generate_grid(self, tag_list, grid_size):
        """
        Generates the 2d array of Tag objects using the tag ids given .
        :param tag_list: list of tag ids.
        :param grid_size: int of total number of grid spaces.
        :return: 2d list grid populated with tag objects.
        """
        temp_grid = []
        for row in tag_list:
            temp_row = []
            for tag in row:
                temp_row.append(Tag(tag, 1 / grid_size))
            temp_grid.append(temp_row)
        return temp_grid

    def update_probabilities(self, new_probability_grid):
        """
        Updates the probabilities of every tag object in the grid.
        :param new_probability_grid: grid of probabilities to update all tags.
        :return: None
        """
        for prob_row, row in zip(new_probability_grid, self.grid):
            for prob_value, tag in zip(prob_row, row):
                tag.set_prob(prob_value)

    def __getattr__(self, item):
        """
        Allows for accessing the nested probabilities of every tag in the grid.
        :param item: String of the name of the attribute being accessed.
        :return: 2d array of the probabilities of tags.
        """
        if item is 'probabilities':
            temp_grid = []
            for row in self.grid:
                temp_row = []
                for tag in row:
                    temp_row.append(tag.probability)
                temp_grid.append(temp_row)
            return temp_grid
        else:
            raise AttributeError

    def __getitem__(self, item):
        """
        Access the coordinate of a tag object or the tag object from a tag id.
        :param item: Tag id or a Tag object.
        :return: String of tuple of coordinate or tag object.
        """
        if type(item) is Tag:
            x = 0
            for row in self.grid:
                y = 0
                for tag in row:
                    if item == tag:
                        return f'{(x,y)}'
                    y = y + 1
                x = x + 1
            return 'none'
        else:
            for row in self.grid:
                for tags in row:
                    if item in tags:
                        return tags
            return 'none'

    def __len__(self):
        """
        Access the gridsize
        :return: int of the grid_size.
        """
        return self.grid_size

    def __iter__(self):
        return iter(self.grid)


class Config:
    """Config object.

    Contains all information from the yaml config object.

    Attributes:
        tag_ids: the ids of the grid_tags.
        ips: the ips to connect to the arduino and reader.
        cycles: the number of cycles to run the algorithm.
        grid_size: the size of the grid.
        search_profile: list of the angles to take readings.
        vision_profile: the expected tags at each search profile.
        p1: p1 for the algorithm.
        p2: p2 for the algorithm.
        target: target tag ids.
    """

    def __init__(self, location):
        """
        Initializes the the config object.
        :param location: the url of the config file.
        """
        with open(location) as config:
            config_data = yaml.load(config)
            self.tag_ids = self.get_tags(config_data['tags']['grid_tags'])
            self.ips = config_data['ips']
            self.cycles = config_data['cycles']
            self.grid_size = config_data['tags']['grid_size']
            self.search_profile = config_data['search_profile']
            self.vision_profile = config_data['vision_profile']
            self.p1 = config_data['probabilities']['p1']
            self.p2 = config_data['probabilities']['p2']
            self.target = config_data['tags']['target_tag']
            config.close()

    def __getattr__(self, item):
        """
        Allows the Accessing of the information held in the Config object.
        :param item: String of the item being accessed.
        :return: value of the item being accessed.
        """
        if item is 'mercury':
            return self.ips[item]
        elif item is 'arduino':
            return self.ips[item]
        elif item is 'cycles':
            return self.cycles
        elif item is 'p1':
            return self.p1
        elif item is 'p2':
            return self.p2
        elif item is 'grid_size':
            return self.grid_size
        elif item is 'tag_ids':
            return self.tag_ids
        elif item is 'search_profile':
            return self.search_profile
        elif item is 'vision_profile':
            return self.vision_profile
        elif item is 'target':
            return self.target
        else:
            raise AttributeError

    def get_tags(self, config_data):
        """
        Pulls the tags from the config data for the grid.
        :param config_data: the dictionary of the arrays of tags.
        :return: 2d array of tag ids.
        """
        grid = []
        for key in config_data.keys():
            row = []
            for tag in config_data[key]:
                row.append(tag)
            grid.append(row)
        return grid

