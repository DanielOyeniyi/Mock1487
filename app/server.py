import json
import os
import random

import bottle
from bottle import HTTPResponse


@bottle.route("/")
def index():
    return "Your Battlesnake is alive!"


@bottle.post("/ping")
def ping():
    """
    Used by the Battlesnake Engine to make sure your snake is still working.
    """
    return HTTPResponse(status=200)


@bottle.post("/start")
def start():
    """
    Called every time a new Battlesnake game starts and your snake is in it.
    Your response will control how your snake is displayed on the board.
    """
    data = bottle.request.json
    print("START:", json.dumps(data))

    response = {"color": "#FF00FF", "headType": "sand-worm", "tailType": "sharp"}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )


@bottle.post("/move")
def move():
    """
    Called when the Battlesnake Engine needs to know your next move.
    The data parameter will contain information about the board.
    Your response must include your move of up, down, left, or right.
    """
    data = bottle.request.json
    print("MOVE:", json.dumps(data))

    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    move = next_move(data)

    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )

def next_move(data):
    Xmax = data["board"]["height"] - 1
    Ymax = data["board"]["width"] - 1
    Xcenter = Xmax // 2
    Ycenter = Ymax // 2
    
    Xcenter1 = Xcenter // 2
    Ycenter1 = Ycenter // 2 
    
    Xcenter2 = Xcenter + Xcenter1 + 1  
    Ycenter2 = Ycenter + Xcenter1 + 1
    
    Xcenter3 = Xcenter // 2 - 1
    Ycenter3 = Ycenter // 2 - 1
    
    Xcenter4 = Xcenter // 2 + Xcenter3 + 1
    Ycenter4 = Ycenter // 2 + Ycenter3 + 1
    
    Xcenter5 = Xcenter + Xcenter3 
    Ycenter5 = Ycenter  + Ycenter3
    
    Xcenter6 = Xcenter2 + Ycenter3
    Ycenter6 = Ycenter2 + Ycenter3

    head = data["you"]["body"][0]
    location = head_location(head, Xcenter, Ycenter) # need to pick the quickest path depending on location
    directions = optimal_directions(data)
    directions = avoid_heads(data, head, directions)
    
    q1 = quadrant(data, Xcenter, Xmax, 0, Ycenter)
    q2 = quadrant(data, 0, Xcenter, 0, Ycenter)
    q3 = quadrant(data, 0, Xcenter, Ycenter, Ymax)
    q4 = quadrant(data, Xcenter, Xmax, Ycenter, Ymax)
    
    q1a = quadrant(data, Xcenter2, Xmax, 0, Ycenter1)
    q1b = quadrant(data, Xcenter, Xcenter2 - 1, 0, Ycenter1)
    q1c = quadrant(data, Xcenter, Xcenter2 - 1, Ycenter1 + 1, Ycenter)
    q1d = quadrant(data, Xcenter2, Xmax, Ycenter1 + 1, Ycenter)
    
    q2a = quadrant(data, Xcenter1 + 1, Xcenter, 0, Ycenter1)
    q2b = quadrant(data, 0, Xcenter1, 0, Ycenter1)
    q2c = quadrant(data, 0, Xcenter1, Ycenter1 + 1, Ycenter)
    q2d = quadrant(data, Xcenter1 + 1, Xcenter, Ycenter1 + 1, Ycenter)
    
    q3a = quadrant(data, Xcenter1 + 1, Xcenter, Ycenter + 1, Ycenter2)
    q3b = quadrant(data, 0, Xcenter1, Ycenter + 1, Ycenter2)
    q3c = quadrant(data, 0, Xcenter1, Ycenter2, Ymax)
    q3d = quadrant(data, Xcenter1 + 1, Xcenter, Ycenter2, Ymax)
    
    q4a = quadrant(data, Xcenter2, Xmax, Ycenter, Ycenter2 - 1)
    q4b = quadrant(data, Xcenter, Xcenter2 - 1, Ycenter, Ycenter2 - 1)
    q4c = quadrant(data, Xcenter, Xcenter2 - 1, Ycenter2, Ymax)
    q4d = quadrant(data, Xcenter2, Xmax, Ycenter2, Ymax)
  
    ordered = [q1, q2, q3, q4] 
    if (ordered[0] == q1):
        if (data["you"]["health"] > 40):
            if (location != "q1" and location != "q1 & q2" and location != "q1 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(data, head, directions, Xcenter, Ycenter1)
                
            if (sorted[0] == q1a):
                return healthy(data, head, directions, Xcenter6, Ycenter3)
            if (sorted[0] == q1b):
                return healthy(data, head, directions, Xcenter5, Ycenter3)
            if (sorted[0] == q1c):
                return healthy(data, head, directions, Xcenter5, Ycenter4)
            if (sorted[0] == q1d):
                return healthy(data, head, directions, Xcenter6, Ycenter4)
        return hungry(data, directions, data["board"]["food"], head)
       
        
    if (ordered[0] == q2):
        sorted = [q2a, q2b, q2c, q2d]
        sorted.sort()
        if (data["you"]["health"] > 40):
            if (location != "q2" and location != "q2 & q3" and location != "q1 & q2" and location != "q1 & q2 & q3 & q4"):
                return healthy(data, head, directions, Xcenter1, Ycenter1)
                
            if (sorted[0] == q2a):
                return healthy(data, head, directions, Xcenter4, Ycenter3)
            if (sorted[0] == q2b):
                return healthy(data, head, directions, Xcenter3, Ycenter3)
            if (sorted[0] == q2c):
                return healthy(data, head, directions, Xcenter3, Ycenter4)
            if (sorted[0] == q2d):
                return healthy(data, head, directions, Xcenter4, Ycenter4)          
        return hungry(data, directions, data["board"]["food"], head)
        
      
    if (ordered[0] == q3):
        if (data["you"]["health"] > 40):
            if (location != "q3" and location != "q2 & q3" and location != "q3 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(data, head, directions, Xcenter1, Ycenter2)
                
            if (sorted[0] == q3a):
                return healthy(data, head, directions, Xcenter4, Ycenter5)
            if (sorted[0] == q3b):
                return healthy(data, head, directions, Xcenter3, Ycenter5)
            if (sorted[0] == q3c):
                return healthy(data, head, directions, Xcenter3, Ycenter6)
            if (sorted[0] == q3d):
                return healthy(data, head, directions, Xcenter4, Ycenter6)
        return hungry(data, directions, data["board"]["food"], head)
        
    else:
        if (data["you"]["health"] > 40):
            if (location != "q4" and location != "q1 & q4" and location != "q3 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(data, head, directions, Xcenter2, Ycenter2)
                
            if (sorted[0] == q4a):
                return healthy(data, head, directions, Xcenter6, Ycenter5)
            if (sorted[0] == q4b):
                return healthy(data, head, directions, Xcenter5, Ycenter5)
            if (sorted[0] == q4c):
                return healthy(data, head, directions, Xcenter5, Ycenter6)
            if (sorted[0] == q4d):
                return healthy(data, head, directions, Xcenter6, Ycenter6)
        return hungry(data, directions, data["board"]["food"], head)

def healthy(data, head, directions, Xcenter, Ycenter):
    target = {"x": Xcenter, "y": Ycenter}
    pathX = abs(target["x"] - head["x"])
    pathY = abs(target["y"] - head["y"])
    return pathing(data, head, target, directions, pathX, pathY)
    
# list, list, dict -> string
# takes a list of possible directions and 
# picks a direction that will goes towards food
def hungry(data, directions, food, head):
    path = 100   
    pathx = 100
    pathy = 100
    target = {}
    
    for item in food: 
        x = abs(item["x"] - head["x"])
        y = abs(item["y"] - head["y"])
        distance = x + y 
        if (distance < path):
            path = distance
            pathX = x
            pathY = y
            target = item
    return pathing(data, head, targete, direction, pathX, pathY)

def pathing(data, head, target, directions, pathX, pathY): 
    if (head["x"] <= target["x"] and head["y"] <= target["y"]):
        if ("right" in directions and "down" in directions):
            if (pathX > pathY):
                return "right"
            if (pathX < pathY):
                return "down" 
            return random.choice(["right", "down"])
            
        if ("down" in directions):  
            return "down"
            
        if ("right" in directions):
            return "right"
        
    if (head["x"] <= target["x"] and head["y"] >= target["y"]):
        if ("right" in directions and "up" in directions):
            if (pathX > pathY):
                return "right"
            if (pathX < pathY):
                return "up" 
            return random.choice(["right", "up"])
            
        if ("up" in directions):  
            return "up"
            
        if ("right" in directions):
            return "right"
            
    if (head["x"] >= target["x"] and head["y"] <= target["y"]):
        if ("left" in directions and "down" in directions):
            if (pathX > pathY):
                return "left"
            if (pathX < pathY):
                return "down" 
            return random.choice(["left", "down"])
            
        if ("down" in directions):  
            return "down"
            
        if ("left" in directions):
            return "left"
            
    if (head["x"] >= target["x"] and head["y"] >= target["y"]):
        if ("left" in directions and "up" in directions):
            if (pathX > pathY):
                return "left"
            if (pathX < pathY):
                return "up" 
            return random.choice(["left", "up"])
            
        if ("up" in directions):  
            return "up"
            
        if ("left" in directions):
            return "left"
    if (len(directions) != 0):
        return random.choice(directions)
    return "up"

# dict, int, int -> String
# takes a dict representing the ehad location and returns
# a string representing the quadrant it is in
def head_location(head, Xcenter, Ycenter):
    if (head["x"] > Xcenter and head["y"] < Ycenter):
        return "q1"
        
    elif (head["x"] < Xcenter and head["y"] < Ycenter):
        return "q2"
        
    elif (head["x"] < Xcenter and head["y"] > Ycenter):
        return "q3"
        
    elif (head["x"] > Xcenter and head ["y"] > Ycenter):
        return "q4"
        
    elif (head["x"] > Xcenter):
        return "q1 & q4"
        
    elif (head["x"] < Xcenter):
        return "q2 & q3"
        
    elif (head["y"] < Ycenter):
        return "q1 & q2"
        
    elif (head["y"] > Ycenter):
        return "q3 & q4"
        
    else:
        return "q1 & q2 & q3 & q4"

# dict , int, int-> list
# takes a list representing a block on the map and 
# returns a list of available directions
def avoid_heads(data, head, directions):
    right_block = {"x": head["x"] + 1, "y": head["y"]}
    left_block = {"x": head["x"] - 1, "y": head["y"]}
    down_block = {"x": head["x"], "y": head["y"] + 1}
    up_block = {"x": head["x"], "y": head["y"] - 1}
    
    snakes = make_snakes(data)
    tails = make_tails(data)
    enemy_heads = make_enemy_heads(data, head)
    
    if (check_around(data, right_block, enemy_heads) != True and "right" in directions):
        directions.remove("right")
    if (check_around(data, left_block, enemy_heads) != True and "left" in directions):
        directions.remove("left")
    if (check_around(data, down_block, enemy_heads) != True and "down" in directions):
        directions.remove("down")
    if (check_around(data, up_block, enemy_heads) != True and "up" in directions):
        directions.remove("up")

    if (len(directions)==0):
        directions = optimal_directions_tails(data)
        if (check_around(data, right_block, enemy_heads) != True and "right" in directions):
            directions.remove("right")
        if (check_around(data, left_block, enemy_heads) != True and "left" in directions):
            directions.remove("left")
        if (check_around(data, down_block, enemy_heads) != True and "down" in directions):
            directions.remove("down")
        if (check_around(data, up_block, enemy_heads) != True and "up" in directions):
            directions.remove("up")

    if (len(directions)==0):
        if (right_block in tails):
            directions.append("right") 
        if (left_block in tails):
            directions.append("left")
        if (down_block in tails):
            directions.append("down")
        if (up_block in tails):
            directions.append("up")
            
    if (len(directions)==0):
        if (check_around_surrounded(data, right_block, enemy_heads) != True and right_block not in snakes):
            directions.append("right")
        if (check_around_surrounded(data, left_block, enemy_heads) != True and left_block not in snakes):
            directions.append("left")
        if (check_around_surrounded(data, down_block, enemy_heads) != True and down_block not in snakes):
            directions.append("down")
        if (check_around_surrounded(data, up_block, enemy_heads) != True and up_block not in snakes):
            directions.append("up")
        
    if (len(directions)==0):
        if (check_around(data, right_block, enemy_heads) != True and right_block not in snakes):
            directions.append("right")
        if (check_around(data, left_block, enemy_heads) != True and left_block not in snakes):
            directions.append("left")
        if (check_around(data, down_block, enemy_heads) != True and down_block not in snakes):
            directions.append("down")
        if (check_around(data, up_block, enemy_heads) != True and up_block not in snakes):
            directions.append("up")
    return directions

# dict, list -> bool
# takes a dicts and returns true if the block is safe
# returns false if the block is dangerous
def check_around(data, block, heads):
    right_block = {"x": block["x"]+1, "y": block["y"]}
    left_block = {"x": block["x"]-1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"]+1}
    up_block = {"x": block["x"], "y": block["y"]-1}
    
    own_size = len(data["you"]["body"])
    sizes = make_sizes(data)
    heads = make_enemy_heads(data, data["you"]["body"][0])
    
    # makes it so that if you are surrounded, go towards the snake
    # that is of equal size
    
    safe = True 
    counter = 0
    for head in heads:
        if (own_size <= sizes[counter]):
            if (right_block == head):
                safe = False
            if (left_block == head):
                safe = False
            if (down_block == head):
                safe = False
            if (up_block == head):
                safe = False
        counter += 1
    return safe
    
# dict, list -> bool
# takes a dicts and returns true if the block is safe
# returns false if the block is dangerous
def check_around_surrounded(data, block, heads):
    right_block = {"x": block["x"]+1, "y": block["y"]}
    left_block = {"x": block["x"]-1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"]+1}
    up_block = {"x": block["x"], "y": block["y"]-1}
    
    own_size = len(data["you"]["body"])
    sizes = make_sizes(data)
    heads = make_enemy_heads(data, data["you"]["body"][0])
    
    # makes it so that if you are surrounded, go towards the snake
    # that is of equal size
    
    safe = True 
    counter = 0
    for head in heads:
        if (own_size == sizes[counter]):
            if (right_block == head):
                safe = False
            if (left_block == head):
                safe = False
            if (down_block == head):
                safe = False
            if (up_block == head):
                safe = False
        counter += 1
    return safe
    
checked = []
def optimal_directions(data):
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    
    right_block = {"x": head["x"] + 1, "y": head["y"]}
    left_block = {"x": head["x"] - 1, "y": head["y"]}
    down_block = {"x": head["x"], "y": head["y"] + 1}
    up_block = {"x": head["x"], "y": head["y"] - 1}
    
    checked.clear()
    right = links(data, head, snakes, "right")
    checked.clear()
    left = links(data, head, snakes, "left")
    checked.clear()
    down = links(data, head, snakes, "down")
    checked.clear()
    up = links(data, head, snakes, "up")
    
    values = [right, left, down, up]
    values.sort(reverse=True)
    directions = []
    
    for num in range(4):
        if (values[num] == right and "right" not in directions):
            directions.append("right")
        if (values[num] == left and "left" not in directions):
            directions.append("left")
        if (values[num] == down and "down" not in directions):
            directions.append("down")
        if (values[num] == up and "up" not in directions):
            directions.append("up")
    
    
    if (values[0] > values[1]):
        return [directions[0]]
    if (values[0] > values[2]):
        return [directions[0], directions[1]]
    if (values[0] > values[3]):
        return [directions[0], directions[1], directions[2]]
    return directions  
   
def links(data, block, snakes, direction):
    counter = 0
    if (direction == "right"):
        counter += links_v2(data, block, snakes, "right", 0)
        
    if (direction == "left"):
        counter += links_v2(data, block, snakes, "left", 0)
    
    if (direction == "down"):
        counter += links_v2(data, block, snakes, "down", 0)
    
    if (direction == "up"):
        counter += links_v2(data, block, snakes, "up", 0)
    return counter     

def links_v2(data, block, snakes, direction, count):
    right_block = {"x": block["x"] + 1, "y": block["y"]}
    left_block = {"x": block["x"] - 1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"] + 1}
    up_block = {"x": block["x"], "y": block["y"] - 1}
    
    
    if (direction == "right"):
        if (right_block in snakes or right_block["x"] == data["board"]["width"] or right_block in checked):
            return count
        checked.append(right_block)
        return links_v2(data, right_block, snakes, direction, count + 1) + links(data, right_block, snakes, "down") + links(data, right_block, snakes, "up")
        
    if (direction == "left"):
        if (left_block in snakes or left_block["x"] == -1 or left_block in checked):
            return count
        checked.append(left_block)
        return links_v2(data, left_block, snakes, direction, count + 1) + links(data, left_block, snakes, "down") + links(data, left_block, snakes, "up")
        
    if (direction == "down"):
        if (down_block in snakes or down_block["y"] == data["board"]["height"] or down_block in checked):
            return count
        checked.append(down_block)
        return links_v2(data, down_block, snakes, direction, count + 1)  + links(data, down_block, snakes, "right") + links(data, down_block, snakes, "left")
        
    if (direction == "up"):
        if (up_block in snakes or up_block["y"] == -1 or up_block in checked):
            return count
        checked.append(up_block)
        return links_v2(data, up_block, snakes, direction, count + 1) + links(data, up_block, snakes, "right") + links(data, up_block, snakes, "left")

def optimal_directions_tails(data):
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    
    right_block = {"x": head["x"] + 1, "y": head["y"]}
    left_block = {"x": head["x"] - 1, "y": head["y"]}
    down_block = {"x": head["x"], "y": head["y"] + 1}
    up_block = {"x": head["x"], "y": head["y"] - 1}
    
    checked.clear()
    right = links_tails(data, head, snakes, "right")
    checked.clear()
    left = links_tails(data, head, snakes, "left")
    checked.clear()
    down = links_tails(data, head, snakes, "down")
    checked.clear()
    up = links_tails(data, head, snakes, "up")
    
    values = [right, left, down, up]
    values.sort(reverse=True)
    directions = []
    
    for num in range(4):
        if (values[num] == right and "right" not in directions):
            directions.append("right")
        if (values[num] == left and "left" not in directions):
            directions.append("left")
        if (values[num] == down and "down" not in directions):
            directions.append("down")
        if (values[num] == up and "up" not in directions):
            directions.append("up")
    
    
    if (values[0] > values[1]):
        return [directions[0]]
    if (values[0] > values[2]):
        return [directions[0], directions[1]]
    if (values[0] > values[3]):
        return [directions[0], directions[1], directions[2]]
    return directions

def links_tails(data, block, snakes, direction):
    counter = 0
    if (direction == "right"):
        counter += links_v2_tails(data, block, snakes, "right", 0)
        
    if (direction == "left"):
        counter += links_v2_tails(data, block, snakes, "left", 0)
    
    if (direction == "down"):
        counter += links_v2_tails(data, block, snakes, "down", 0)
    
    if (direction == "up"):
        counter += links_v2_tails(data, block, snakes, "up", 0)
    return counter 

def links_v2_tails(data, block, snakes, direction, count):
    right_block = {"x": block["x"] + 1, "y": block["y"]}
    left_block = {"x": block["x"] - 1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"] + 1}
    up_block = {"x": block["x"], "y": block["y"] - 1}
    
    tails = make_tails(data)
    
    
    if (direction == "right"):
        if ((right_block in snakes or right_block["x"] == data["board"]["width"] or right_block in checked) and right_block not in tails):
            return count
        checked.append(right_block)
        return links_v2_tails(data, right_block, snakes, direction, count + 1) + links_tails(data, right_block, snakes, "down") + links_tails(data, right_block, snakes, "up")
        
    if (direction == "left"):
        if ((left_block in snakes or left_block["x"] == -1 or left_block in checked) and left_block not in tails):
            return count
        checked.append(left_block)
        return links_v2_tails(data, left_block, snakes, direction, count + 1) + links_tails(data, left_block, snakes, "down") + links_tails(data, left_block, snakes, "up")
        
    if (direction == "down"):
        if ((down_block in snakes or down_block["y"] == data["board"]["height"] or down_block in checked) and down_block not in tails):
            return count
        checked.append(down_block)
        return links_v2_tails(data, down_block, snakes, direction, count + 1)  + links_tails(data, down_block, snakes, "right") + links_tails(data, down_block, snakes, "left")
        
    if (direction == "up"):
        if ((up_block in snakes or up_block["y"] == -1 or up_block in checked) and up_block not in tails):
            return count
        checked.append(up_block)
        return links_v2_tails(data, up_block, snakes, direction, count + 1) + links_tails(data, up_block, snakes, "right") + links_tails(data, up_block, snakes, "left")
   
# dict, int, int, int, int -> int
# takes a dict representing the board data and the bounds
# of quadrant 
def quadrant(data, Xstart, Xfinish, Ystart, Yfinish):
    heads = make_enemy_heads(data, data["you"]["body"][0])
    bodies = make_bodies(data, heads, data["you"]["body"][0])
    return danger_level(heads, bodies, data["board"]["food"], Xstart, Xfinish, Ystart, Yfinish)
    
# list, list, list, int, int, int, int -> int
# takes list containing board info and numbers 
# representing the section of the board (board is split in half) you are on and 
# returns a number representing the danger in the area
def danger_level(heads, bodies, food, Xstart, Xfinish, Ystart, Yfinish):
    danger = 0
    for x in range(Xstart, Xfinish+1):
        for y in range(Ystart, Yfinish+1):
            block = {"x": x, "y": y}
            if (block in heads):
                danger += 3
            if (block in bodies):
                danger += 1
    return danger
    
def make_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            snakes.append(part)
    return snakes
    
# list, list -> list
# makes a list of enemy snake heads 
def make_heads(data):
    heads = []
    for snake in data["board"]["snakes"]:
        heads.append(snake["body"][0])
    return heads
    
# list, list -> list
# makes a list of enemy snake heads 
def make_enemy_heads(data, head):
    heads = []
    for snake in data["board"]["snakes"]:
        if (snake["body"][0] != head):
            heads.append(snake["body"][0])
    return heads

# list, list, dict -> list 
# makes a list of bodies
def make_bodies(data, heads, head):    
    bodies = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            if (part not in heads and part != head):
                bodies.append(part)
    return bodies

# list -> list
# makes a list of tails
def make_tails(data):
    tails = []
    for snake in data["board"]["snakes"]: 
        tails.append(snake["body"][-1])
    return tails
    
# list -> list
# makes a list of all the snakes sizes
def make_sizes(data): 
    sizes = []
    for snake in data["board"]["snakes"]: 
        body = snake["body"]
        size = len(body)
        sizes.append(size)
    return sizes
    
@bottle.post("/end")
def end():
    """
    Called every time a game with your snake in it ends.
    """
    data = bottle.request.json
    print("END:", json.dumps(data))
    return HTTPResponse(status=200)


def main():
    bottle.run(
        application,
        host=os.getenv("IP", "0.0.0.0"),
        port=os.getenv("PORT", "8080"),
        debug=os.getenv("DEBUG", True),
    )


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == "__main__":
    main()