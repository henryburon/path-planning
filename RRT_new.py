import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation
import numpy as np
import imageio as iio
import time

# np.random.seed(34)

class RRT:
    def __init__(self, q_init, K, delta, domain):
        self.state = "RANDOM_CONFIG"
        self.q_init = q_init # Initial configuration (first node)
        self.K = K # Number of vertices/nodes in the RRT
        self.delta = delta # Incremental distance
        self.domain = domain # The size of the game field
        self.G = {"nodes": [{"name": "q1",
                             "coordinate": q_init,
                             "parent": None}]}  
        self.counter = 2
        self.line_segments = []
        self.scatter = None
        self.lines = None
        self.circles_list = []
        self.game_over = False
        self.iterations = 0
        self.animation_speed = 75 # Updates every X milliseconds
        self.fig, self.ax = plt.subplots()



        
        
        # self.initialize_plot()


    def transition_to(self, new_state):
        self.state = new_state

    def distance(self, point1, point2):
        # Distance between point1 and point2 in 3D
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def initialize_plot(self):
        self.scatter = self.ax.scatter([], [], c='blue', s=5)  # Create an empty scatter plot
        self.lines = LineCollection([], color="blue", linewidth=0.5)  # Create an empty lines plot
        self.ax.add_collection(self.lines)

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


    def process(self):
        if self.state == "RANDOM_CONFIG":
            # Finds a random point in 2D
            x_rand = round(np.random.uniform(self.domain[0], self.domain[1]), 5)
            y_rand = round(np.random.uniform(self.domain[2], self.domain[3]), 5)
            self.q_rand = (x_rand, y_rand)
            self.transition_to("FIND_NEAREST_NODE")
        
        elif self.state == "FIND_NEAREST_NODE":
            # Finds closest existing node to q_rand. Sets closest node to q_near.
            coord_distance = []
            for node in self.G["nodes"]:
                coordinate = node["coordinate"]
                distance = self.distance(coordinate, self.q_rand)
                coord_distance.append(distance)
            smallest_distance = min(coord_distance)
            index = coord_distance.index(smallest_distance)
            self.q_near = self.G["nodes"][index]["coordinate"]
            self.transition_to("NEW_NODE")
        
        elif self.state == "NEW_NODE":
            # Creates a new point 1 unit from the nearest point, in the direction of the random point
            vector = np.array(self.q_rand) - np.array(self.q_near)
            vector_length = np.linalg.norm(vector)
            unit_vector = vector/vector_length
            self.q_new = tuple(round(coord, 3) for coord in (self.q_near + unit_vector))
            self.transition_to("UPDATE_TREE")

        elif self.state == "UPDATE_TREE":
            for node in self.G["nodes"]:
                if node["coordinate"] == self.q_near:
                    parent_node = node["name"]
                    break
            
            new_entry = {"name": f"q{self.counter}", # Creates the new entry for the newest point
                     "coordinate": self.q_new,
                     "parent": [parent_node, self.q_near]}
            
            self.G["nodes"].append(new_entry) # Appends the new entry to self.G
            self.counter += 1
            self.transition_to("UPDATE_LINES")

        elif self.state == "UPDATE_LINES":
            # Every time a q_new is created, a new line is added between q_new and q_near
            new_entry = (self.q_near, self.q_new)
            self.line_segments.append(new_entry)
            self.iterations += 1
            if self.iterations > self.K - 2:
                self.transition_to("ANIMATE")
            else:
                self.transition_to("RANDOM_CONFIG")

        elif self.state == "ANIMATE":
            # x_data = [node["coordinate"][0] for node in self.G["nodes"]]
            # y_data = [node["coordinate"][1] for node in self.G["nodes"]]
            # self.scatter.set_offsets(np.column_stack((x_data, y_data)))
            self.initialize_plot()
            anim = FuncAnimation(self.fig, self.update_plot, frames=len(self.G["nodes"]), interval=self.animation_speed)

            
            plt.show()
            
         
        

        
            
        
        
            

            
        




q_init = (50, 50)
K = 500
delta = 1
domain = (0, 100, 0, 100)

my_rrt = RRT(q_init, K, delta, domain)
while not my_rrt.game_over:
    my_rrt.process()