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


######
    # make it so that it only chases if there is an open path 
    # to the target
######

# dict -> string
# returns the next move the snake should make
def next_move(data):
    head_list = paths(data, data["you"]["body"][0])
    tail_list = paths(data, data["you"]["body"][-1])
    directions = not_instant_death(data, data["you"]["body"][0])
    
    if (max(head_list) < max(tail_list)):
        return chase_tail(data, directions)
    return avoid_head(data, directions)
    
checked = []
# dict -> list
# return directions that don't result in instant death
def not_instant_death(data, block):
    snakes = make_snakes_free_tails(data)
    
    checked.clear()
    right = links(data, block, snakes, "right")
    checked.clear()
    left = links(data, block, snakes, "left")
    checked.clear()
    down = links(data, block, snakes, "down")
    checked.clear()
    up = links(data, block, snakes, "up")
    
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
    
# dict, list -> string
# takes all possible directions and chases the target
def chase_tail(data, directions):  
    head = data["you"]["body"][0]
    target = data["you"]["body"][-1]  
    pathX = abs(target["x"] - head["x"])
    pathY = abs(target["y"] - head["y"])
    return path_towards(data, target, directions, pathX, pathY)

# dict, list -> string
# takes all possible directions and avoids the target
def avoid_head(data, directions):
    head = data["you"]["body"][0]
    heads = make_enemy_heads(data)
    sizes = make_sizes(data)
    own_size = len(data["you"]["body"])
    
    target = {}
    pathX = 3
    pathY = 3
    
    counter = 0
    for bad_head in heads: 
        if (own_size <= sizes[counter]):
            x = abs(bad_head["x"] - head["x"])
            y = abs(bad_head["y"] - head["y"])
            if (x <= pathX and y <= pathY):
                target = bad_head
                pathX = x
                pathY = y
                
                
    if (len(target) != 0):
        return path_away(data, target, directions, pathX, pathY) 
    return chase_head(data, directions)

# dict, list -> string
# takes all possible directions and chases the target
def chase_head(data, directions):
    head = data["you"]["body"][0]
    heads = make_enemy_heads(data)
    sizes = make_sizes(data)
    own_size = len(data["you"]["body"])
    
    target = {}
    pathX = 100
    pathY = 100
    sizing = 0
    
    counter = 0
    for bad_head in heads: 
        if (own_size > sizes[counter]):
            difference = own_size - sizes[counter]
            x = abs(bad_head["x"] - head["x"])
            y = abs(bad_head["y"] - head["y"])
            if (difference > sizing):
                sizing = difference
                target = bad_head
                pathX = x
                pathY = y
    
    if (len(target) != 0):
        return path_towards(data, target, directions, pathX, pathY) 
    return chase_food(data, directions)
    
# list, list, dict -> string
# takes all possible directions and chases the target
def chase_food(data, directions):
    food = data["board"]["food"]
    head = data["you"]["body"][0]
    path = 100   
    pathX = 100
    pathY = 100
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
            
    return path_towards(data, target, directions, pathX, pathY)

# dict, dict, list, int, int -> string
# takes target location and pick the most optimal path to get there
def path_towards(data, target, directions, pathX, pathY): 
    head = data["you"]["body"][0]
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

# dict, dict, list, int, int -> string
# takes target location and pick the most optimal path to run away from it
def path_away(data, target, directions, pathX, pathY): 
    head = data["you"]["body"][0]
    
    if (head["x"] >= target["x"] and head["y"] >= target["y"]):
        if ("right" in directions and "down" in directions):
            if (pathX < pathY):
                return "right"
            if (pathX > pathY):
                return "down" 
            return random.choice(["right", "down"])
            
        if ("right" in directions):  
            return "right"
            
        if ("down" in directions):
            return "down"
            
    if (head["x"] >= target["x"] and head["y"] <= target["y"]):
        if ("right" in directions and "up" in directions):
            if (pathX < pathY):
                return "right"
            if (pathX > pathY):
                return "up" 
            return random.choice(["right", "up"])
            
        if ("right" in directions):
            return "right"
            
        if ("up" in directions):  
            return "up"
            
    if (head["x"] <= target["x"] and head["y"] >= target["y"]):
        if ("left" in directions and "down" in directions):
            if (pathX < pathY):
                return "left"
            if (pathX > pathY):
                return "left" 
            return random.choice(["left", "down"])
            
        if ("left" in directions):
            return "left"
            
        if ("down" in directions):  
            return "down"
    
    if (head["x"] <= target["x"] and head["y"] <= target["y"]):
        if ("left" in directions and "up" in directions):
            if (pathX < pathY):
                return "left"
            if (pathX > pathY):
                return "up" 
            return random.choice(["left", "up"])
            
        if ("left" in directions):
            return "left"            

        if ("up" in directions):  
            return "up"
        

            
    if (len(directions) != 0):
        return random.choice(directions)
    return "up"

checked1 = []
# dict, dict -> list 
# returns a list of values that coresponds to the 
# number of block linked to a block, each index is 
# a direction
def paths(data, block):
    snakes = make_snakes_free_tails(data)
    
    checked1.clear()
    right = links(data, block, snakes, "right")
    checked1.clear()
    left = links(data, block, snakes, "left")
    checked1.clear()
    down = links(data, block, snakes, "down")
    checked1.clear()
    up = links(data, block, snakes, "up")
    
    path_list = [right, left, down, up]
    
    return path_list

# dict, dict, list, string -> int 
# returns a count of all the blocks that 
# the input block is linked with
def links(data, block, snakes, direction):
    counter = 0
    if (direction == "right"):
        counter += links_helper(data, block, snakes, "right", 0)
        
    if (direction == "left"):
        counter += links_helper(data, block, snakes, "left", 0)
    
    if (direction == "down"):
        counter += links_helper(data, block, snakes, "down", 0)
    
    if (direction == "up"):
        counter += links_helper(data, block, snakes, "up", 0)
    return counter 
    
# dict, dict, list, string, int -> int 
# returns a count of all the blocks that 
# the input block is linked with
def links_helper(data, block, snakes, direction, count):
    right_block = {"x": block["x"] + 1, "y": block["y"]}
    left_block = {"x": block["x"] - 1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"] + 1}
    up_block = {"x": block["x"], "y": block["y"] - 1}
    
    
    if (direction == "right"):
        if (right_block in snakes or right_block["x"] == data["board"]["width"] or right_block in checked):
            return count
        checked.append(right_block)
        return links_helper(data, right_block, snakes, direction, count + 1) + links(data, right_block, snakes, "down") + links(data, right_block, snakes, "up")
        
    if (direction == "left"):
        if (left_block in snakes or left_block["x"] == -1 or left_block in checked):
            return count
        checked.append(left_block)
        return links_helper(data, left_block, snakes, direction, count + 1) + links(data, left_block, snakes, "down") + links(data, left_block, snakes, "up")
        
    if (direction == "down"):
        if (down_block in snakes or down_block["y"] == data["board"]["height"] or down_block in checked):
            return count
        checked.append(down_block)
        return links_helper(data, down_block, snakes, direction, count + 1)  + links(data, down_block, snakes, "right") + links(data, down_block, snakes, "left")
        
    if (direction == "up"):
        if (up_block in snakes or up_block["y"] == -1 or up_block in checked):
            return count
        checked.append(up_block)
        return links_helper(data, up_block, snakes, direction, count + 1) + links(data, up_block, snakes, "right") + links(data, up_block, snakes, "left")

# dict -> list 
# returns a list of dicts representing snake bodies 
# without tails if the tail won't grow next turn
def make_snakes_free_tails(data):
    snakes = []
    growing = make_growing_tails(data)
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            if (part != snake["body"][-1] or part in growing):
                snakes.append(part)
    return snakes
    
# dict -> list
# returns a list of dicts representing snake tails 
# that might grow in the next turn
def make_growing_tails(data):
    growing = []
    food = make_food(data)
    tails = make_tails(data)
    for snake in data["board"]["snakes"]:
        part = snake["body"][0]
        Rblock = {"x": part["x"] + 1, "y": part["y"]}
        Lblock = {"x": part["x"] - 1, "y": part["y"]}
        Dblock = {"x": part["x"], "y": part["y"] + 1}
        Ublock = {"x": part["x"], "y": part["y"] - 1}
        
        if (Rblock in food or Lblock in food or Dblock in food or Ublock in food or snake["body"][-1] == snake["body"][-2]):
            growing.append(snake["body"][-1])
    return growing

# list -> list
# makes a list of tails
def make_tails(data):
    tails = []
    for snake in data["board"]["snakes"]: 
        tails.append(snake["body"][-1])
    return tails

# dict -> list
# returns a list of dicts representing food location
def make_food(data):
    food = []
    for item in data["board"]["food"]:
        food.append(item)
    return food

#dict -> list
# returns a list of dicts representing snake locations
def make_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            snakes.append(part)
    return snakes
    
# list -> list
# makes a list of all the snakes sizes
def make_sizes(data): 
    sizes = []
    for snake in data["board"]["snakes"]: 
        body = snake["body"]
        size = len(body)
        sizes.append(size)
    return sizes

# list, list -> list
# makes a list of enemy snake heads 
def make_enemy_heads(data):
    head = data["you"]["body"][0]
    heads = []
    for snake in data["board"]["snakes"]:
        if (snake["body"][0] != head):
            heads.append(snake["body"][0])
    return heads
    
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