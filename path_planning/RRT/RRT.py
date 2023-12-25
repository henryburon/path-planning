import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation
import numpy as np
import imageio as iio
import time

np.random.seed(34)

class RRT:
    def __init__(self, q_init, K, delta, domain):
        self.q_init = q_init # Initial configuration (first node)
        self.K = K # Number of vertices/nodes in the RRT
        self.delta = delta # Incremental distance
        self.domain = domain # The size of the game field
        self.G = {"nodes": [{"name": "q1",
                             "coordinate": q_init,
                             "parent": None}]}  
        self.counter = 2
        self.line_segments = []
        self.fig, self.ax = plt.subplots()
        self.scatter = None
        self.lines = None
        self.animation_speed = 75 # Updates every X milliseconds

    def distance(self, point1, point2): # Distance between point1 and point2
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
        
    def random_configuration(self): # Find random coordinate within the domain
        x_rand = round(np.random.uniform(self.domain[0],self.domain[1]), 5)
        y_rand = round(np.random.uniform(self.domain[2],self.domain[3]), 5)
        self.q_rand = (x_rand, y_rand)
        
    def nearest_vertex(self): # Find closest existing node to q_rand. Sets closest coordinate = q_near
        existing_coordinates = []
        for node in self.G["nodes"]: # Iterates through each node in the list of nodes
            coordinate = node["coordinate"] # Retrieves the "coordinate" field
            distance = self.distance(coordinate, self.q_rand) # Uses distance function to find the distance between existing coordinate and random coordinate
            existing_coordinates.append(distance)
        smallest_distance = min(existing_coordinates)
        index = existing_coordinates.index(smallest_distance)
        self.q_near = self.G["nodes"][index]["coordinate"]
        

    def new_configuration(self): # Create a new point 1 unit from the nearest point, in the direction of the random point
        vector = np.array(self.q_rand) - np.array(self.q_near)
        vector_length = np.linalg.norm(vector)
        unit_vector = vector/vector_length
        self.q_new = tuple(round(coord, 3) for coord in (self.q_near + unit_vector))
        self.update_lines()

    def update_tree(self):
        for node in self.G["nodes"]: # Finds parent node name.
            if node["coordinate"] == self.q_near:
                parent_coord = node["name"]
                break

        new_entry = {"name": f"q{self.counter}", # Creates the new entry for the newest point
                     "coordinate": self.q_new,
                     "parent": [parent_coord, self.q_near]}
        
        self.G["nodes"].append(new_entry) # Appends the new entry to self.G
        self.counter += 1

    def update_lines(self): # Everytime a q_new is created, a new entry is added between q_new and q_near
        new_entry = (self.q_near, self.q_new)
        self.line_segments.append(new_entry)

    def create_obstacles(self):
        # Creates the obstacles. Still need to make it so they can't spawn in the center (where q_init is)
        self.circles_list = []
        counter = 0
        for i in range(15):
            x_rand = round(np.random.uniform(self.domain[0],self.domain[1]), 5)
            y_rand = round(np.random.uniform(self.domain[2],self.domain[3]), 5)
            size = np.random.randint(1, 11)
            coord = (x_rand, y_rand)
            new_entry = {"name": f"c{counter}",
                         "coordinate": coord,
                         "size": size}
            self.circles_list.append(new_entry)
            circle = plt.Circle((x_rand, y_rand), size)
            self.ax.add_patch(circle)
            counter += 1

    def initialize_plot(self):
        self.scatter = self.ax.scatter([], [], c='blue', s=5)  # Create an empty scatter plot
        self.lines = LineCollection([], color="blue", linewidth=0.5)  # Create an empty lines plot
        self.ax.add_collection(self.lines)
        self.create_obstacles()

        self.ax.set_title("Rapidly-Exploring Random Tree")
        self.ax.set_xlim(self.domain[0], self.domain[1])
        self.ax.set_ylim(self.domain[2], self.domain[3])

    def update_plot(self, i):
        # Update the scatter plot with points up to index 'i'
        x_data = [node["coordinate"][0] for node in self.G["nodes"][:i]]
        y_data = [node["coordinate"][1] for node in self.G["nodes"][:i]]
        self.scatter.set_offsets(np.column_stack((x_data, y_data)))

        # Update the lines plot with line segments up to index 'i'
        lines_data = self.line_segments[:i]
        self.lines.set_segments(lines_data)

    def animate(self):
        self.initialize_plot()
        anim = FuncAnimation(self.fig, self.update_plot, frames=len(self.G["nodes"]), interval=self.animation_speed)
        plt.show()

    def main(self):
        for i in range(self.K):
            self.random_configuration()  # Generates random point
            self.nearest_vertex()  # Finds closest existing node
            self.new_configuration()  # Creates new node, one unit away
            self.update_tree()  # Adds information node to tree (self.G)
            self.update_lines()  # Adds new line information to list
            
        self.animate()

q_init = (50, 50)
K = 500
delta = 1
domain = (0, 100, 0, 100)  # x_min, x_max, y_min, y_max

robot = RRT(q_init, K, delta, domain)
robot.main()