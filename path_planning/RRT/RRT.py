import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
from matplotlib.animation import FuncAnimation
import numpy as np
import imageio as iio

np.random.seed(19483)

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
        self.path_exists = None
        self.circles_list = []
        self.game_over = False
        self.iterations = 0
        self.animation_speed = 60 # Updates every X milliseconds
        self.fig, self.ax = plt.subplots(figsize=(10,10))
        self.initialize_obstacles()
        self.initialize_goal()
        self.initialize_plot()
        self.find_random_seed()
        self.spotted_flag = False
        self.counter1 = 0


    def transition_to(self, new_state):
        self.state = new_state

    def distance(self, point1, point2):
        # Distance between point1 and point2 in 3D
        return np.sqrt((point2[0] - point1[0])**2 + (point2[1] - point1[1])**2)
    
    def find_random_seed(self):
        random_state = np.random.get_state()
        seed = random_state[1][0]
        print("Random Seed:", seed)
    
    def initialize_obstacles(self):
        self.circles_list = []
        counter = 0
        for i in range(30):
            x_rand = round(np.random.uniform(self.domain[0],self.domain[1]), 5)
            y_rand = round(np.random.uniform(self.domain[2],self.domain[3]), 5)
            size = np.random.randint(1, 11)
            coord = (x_rand, y_rand)
            new_entry = {"name": f"c{counter}",
                         "coordinate": coord,
                         "size": size}
            self.circles_list.append(new_entry)

    def create_obstacles(self):
        for circle in self.circles_list:
            circle = plt.Circle((circle["coordinate"][0], circle["coordinate"][1]), circle["size"], color='darkblue')
            self.ax.add_patch(circle)
            # counter += 1
    
    def initialize_plot(self):
        self.scatter = self.ax.scatter([], [], c='blue', s=5)  # Create an empty scatter plot
        self.lines = LineCollection([], color="blue", linewidth=0.5)  # Create an empty lines plot
        self.ax.add_collection(self.lines)
        self.create_obstacles()

        self.ax.set_title("Rapidly-Exploring Random Tree", fontsize=16, fontweight='bold')
        self.ax.set_xlim(self.domain[0], self.domain[1])
        self.ax.set_ylim(self.domain[2], self.domain[3])

        self.ax.scatter(self.x_goal, self.y_goal, c='red', s=100)

    def initialize_goal(self):
        acceptable_goal = False
        
        while acceptable_goal == False:
            check1 = False
            check2 = False
            self.x_goal = round(np.random.uniform(self.domain[0],self.domain[1]), 5)
            self.y_goal = round(np.random.uniform(self.domain[2],self.domain[3]), 5)

            if abs(50 - self.x_goal) > 35 and abs(50 - self.y_goal) > 35:
                check1 = True
            for circle in self.circles_list:
                 coord = circle["coordinate"]
                 goal_coord = (self.x_goal, self.y_goal)
                 distance = self.distance(coord, goal_coord)
                 if distance > circle["size"]:
                      check2 = True
            if check1 and check2:
                acceptable_goal = True
                print(f"Goal: ({self.x_goal},{self.y_goal})")
        
    def update_plot(self, i):
        # Update the scatter plot with points up to index 'i'
        x_data = [node["coordinate"][0] for node in self.G["nodes"][:i]]
        y_data = [node["coordinate"][1] for node in self.G["nodes"][:i]]
        self.scatter.set_offsets(np.column_stack((x_data, y_data)))

        # Update the lines plot with line segments up to index 'i'
        lines_data = self.line_segments[:i]
        self.lines.set_segments(lines_data)

#######################################################################################################

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
            self.transition_to("CHECK_COLLISIONS")

        elif self.state == "CHECK_COLLISIONS":
            for circle in self.circles_list: # check each circle in the list
                coord = circle["coordinate"] # get the center coordinate of the circle
                distance = self.distance(coord, self.q_new) # find distance between center of circle and the new coordinate
                if distance < circle["size"]:
                    self.state = "RANDOM_CONFIG"
                    return
                
                else:
                    self.state = "CHECK_FOR_GOAL"

        elif self.state == "CHECK_FOR_GOAL":
            # Checks if goal is in sight (not blocked by obstacles)
            # Not an optimal solution, but should work for this implementation
            # This functionality is currently incomplete
            # Sometimes gives false positives, sometimes doesn't give true positives
            goal_coord = (self.x_goal, self.y_goal)
            points_on_line = np.linspace(np.array(self.q_new), np.array(goal_coord), 50) # Creates 50 coordinates between the points.

            self.path_exists = True
            for point in points_on_line: # For each point in the list
                for circle in self.circles_list: # check each obstacle
                    circle_coord = circle["coordinate"]
                    distance = self.distance(point, circle_coord)
                    if distance < circle["size"]:
                        self.path_exists = False
                        
            if self.path_exists == True:
                print("Goal Spotted!")
                if self.spotted_flag == False:
                    self.q_spotted = self.q_new
                    self.spotted_flag = True
                    # Search for index of self.q_spotted
                    for node in self.G["nodes"]:
                        if node["coordinate"] == self.q_spotted:
                            index = node
                    
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
            anim = FuncAnimation(self.fig, self.update_plot, frames=len(self.G["nodes"]), interval=self.animation_speed)
            plt.show()
            

q_init = (50, 50)
K = 500
delta = 1
domain = (0, 100, 0, 100)

my_rrt = RRT(q_init, K, delta, domain)
try:
    while not my_rrt.game_over:
        my_rrt.process()
except KeyboardInterrupt:
    print("Closing program.")
