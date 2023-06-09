from searchAlgorithm import SearchAlgorithm
from queue import Queue
from node import Node


class BidirectionalSearch(SearchAlgorithm):
    def __init__(self, environment):
        super().__init__(environment)
        self.srcVisited = [[False for i in range(self.environment.column)] for j in range(self.environment.row)] # a list that store the visited nodes for the search from the start
        self.desVisited = [[False for i in range(self.environment.column)] for j in range(self.environment.row)]# a list that store the visited nodes for the search from the destination
        self.srcParent = [[None for i in range(self.environment.column)] for j in range(self.environment.row)] # frontier for start search
        self.desParent = [[None for i in range(self.environment.column)] for j in range(self.environment.row)] # frontier for destination search
        self.srcFrontier = Queue()
        self.desFrontier = Queue()

    def getIntersectingNode(self):
        """
        Return the intersection if one exists
        """
        for i in range(self.environment.row):
            for j in range(self.environment.column):
                if self.srcVisited[i][j] and self.desVisited[i][j]:
                    return [j, i]
        return -1

    def getVisited(self):
        """
        Return the combined visited list from both srcVisited and desVisited
        """
        visited = []
        for i in range(self.environment.row):
            for j in range(self.environment.column):
                if self.srcVisited[i][j] or self.desVisited[i][j]:
                    visited.append([j,i])
        return visited

    def search(self):
        startNode = Node(location=self.environment.start, parent=None, direction="", cost = 0)
        endNode = Node(location=self.environment.goals[0], parent=None, direction="", cost = 0) # the destination search will start at the first goal specified in the maze configuration
        self.srcFrontier.put(startNode) # add start node to sourceFrontier
        self.desFrontier.put(endNode) # add goal node to desFrontier
        self.numberOfNodes += 2
        self.srcVisited[startNode.location[1]][startNode.location[0]] = True # mark the start node as visited
        self.desVisited[endNode.location[1]][endNode.location[0]] = True # mark the goal node as visited
        success = False
        while not self.srcFrontier.empty() and not self.desFrontier.empty():
            srcNode = self.srcFrontier.get()
            desNode = self.desFrontier.get()
            intersection = self.getIntersectingNode()
            if intersection != -1:
                success = True
                break # stop the loop when a solution is found
            yield {"finish": False, "success": False, "visited": self.getVisited(), "frontier": [node.location for node in self.srcFrontier.queue] + [node.location for node in self.desFrontier.queue]}

            self.expand(srcNode, "forward") # explore the children node
            self.expand(desNode, "backward")
        if success:
            yield {"finish": True,"success": True, "path" : self.getPath(intersection), "direction" : self.getDirection(intersection), "numberOfNodes":self.numberOfNodes }
            return
        else:
            yield {"finish": True,"success": False, "message": "No solution found"}
            return


    def getPathSource(self, location):
        """
        Return the path from start to intersection
        """
        if location is None:
            return []
        else:
            return self.getPathSource(self.srcParent[location[1]][location[0]]) + [location]

    def getPathDes(self, location):
        """
        Return the path from the intersection to the destination
        """
        if location is None:
            return []
        else:
            return [location] + self.getPathDes(self.desParent[location[1]][location[0]])

    def getPath(self, intersection):
        """
        Return the path from the start to the destination
        """
        return self.getPathSource(self.srcParent[intersection[1]][intersection[0]]) \
               + [intersection] \
               + self.getPathDes(self.desParent[intersection[1]][intersection[0]])

    def getDirection(self, intersection):
        """
        Return the sequence of moves from start to destination
        """
        path = self.getPath(intersection)
        direction = ""
        for i in range(len(path) - 1):
            location = path[i]
            nextLocation = path[i + 1]
            if location[0] == nextLocation[0] and location[1] == nextLocation[1] - 1:
                direction += "down"
            elif location[0] == nextLocation[0] and location[1] == nextLocation[1] + 1:
                direction += "up"
            elif location[1] == nextLocation[1] and location[0] == nextLocation[0] + 1:
                direction += "left"
            elif location[1] == nextLocation[1] and location[0] == nextLocation[0] - 1:
                direction += "right"
            else:
                raise Exception("Cannot calculate the direction to the next move")
            if i != len(path) - 2:
                direction += "; "
        return direction

    def expand(self, node, direction):
        successors = self.environment.getSuccessors(node.location) # get the successors from the node location
        if direction == "forward":
            for action, location in successors.items():
                if not self.srcVisited[location[1]][location[0]]: # skip the node if it is visited
                    self.srcFrontier.put(Node(location=location, parent=node, direction=action, cost = node.cost + 1))
                    self.srcVisited[location[1]][location[0]] = True
                    self.srcParent[location[1]][location[0]] = node.location
                    self.numberOfNodes += 1
        elif direction == "backward":
            for action, location in successors.items():
                if not self.desVisited[location[1]][location[0]]: # skip the node if it is visited
                    self.desFrontier.put(Node(location=location, parent=node, direction=action, cost = node.cost + 1))
                    self.desVisited[location[1]][location[0]] = True
                    self.desParent[location[1]][location[0]] = node.location
                    self.numberOfNodes += 1


