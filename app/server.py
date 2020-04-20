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

    move = next_move(data)
    num_loops = 0
    
    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"

    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )

# we want to map out all the possible moves. recursion 
# sounds like a great way to do it
# first take into account all of our moves then 
# we take into account the possible moves of other snakes
def next_move(data):
    enemy = closest_head(data)
    if (enemy != {}):
        if (is_smaller(data, enemy)):
            return to_target(data, value(data), enemy)
        else:
            return avoid_target(data, value(data), enemy)
    return to_target(data, value(data), closest_food(data))

"""
we could do that check every available spot with the next 6 moves
but the sizing would have to change as that would take too 
long to compute


we need to make it remember it's last moves so that it
does't count more than once. maybe add the block into 
a temp list of snakes
could make add the new move to the list of snakes
every move you  remove the last part of your own 
snake from the list. unless you ate food then you skip 
it for the current turn

we could add the # of available blocks to the score for
each entry. It might just mean that we sacrifice 
move depth. this could be accomplished by leveraging off of
our older code

just a consideration but we can increase or decrease the depth
depending on what percent of the board is free and how many directions
the snake can move in

it now has decent spacial awareness (as in it won't run into a dead end)
now we just need to hone our targeting and priorities.
"""

# dict, dict -> string
# function checks all the moves up to a certain depth
def value(data):
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    directions = []
    
    right_block = {"x": head["x"] + 1, "y": head["y"]}
    left_block = {"x": head["x"] - 1, "y": head["y"]}
    down_block = {"x": head["x"], "y": head["y"] + 1}
    up_block = {"x": head["x"], "y": head["y"] - 1}
    
    right_val = 0
    left_val = 0
    down_val = 0
    up_val = 0
    
    depth = 0
    if (is_free(data, snakes, right_block) and is_free(data, snakes, left_block) and 
        is_free(data, snakes, down_block) and is_free(data, snakes, up_block)):
        depth = 1
    
    right_val = value_helper(data, snakes, data["you"]["body"], depth, right_block)
    left_val = value_helper(data, snakes, data["you"]["body"], depth, left_block)
    down_val = value_helper(data, snakes, data["you"]["body"], depth, down_block)
    up_val = value_helper(data, snakes, data["you"]["body"], depth, up_block)
    
    max_val = max(right_val, left_val, down_val, up_val)
    if (max_val == right_val):
        directions.append("right")
    if (max_val == left_val):
        directions.append("left")
    if (max_val == down_val):
        directions.append("down")
    if (max_val == up_val):
        directions.append("up")
    return directions

# for enemy snake moves we can call this but 
# add a bool that determins if numberes will be added or
# subtracted
# also that would multiply our runtime by x number of snakes
# but they don't follow the same algorithm 
# we can still sort of predict the moves 
def value_helper(data, snakes, body, depth, block):
    if (depth == 3 or not is_free(data, snakes, block)):
        return 0
    else:
        tmp_snakes = snakes.copy()
        tmp_snakes.insert(0, block)
        
        tmp_body = body.copy()
        tmp_body.insert(0, block)
        tail = tmp_body.pop()
        
        tmp_snakes.remove(tail)
        
        
        right_block = {"x": block["x"] + 1, "y": block["y"]}
        left_block = {"x": block["x"] - 1, "y": block["y"]}
        down_block = {"x": block["x"], "y": block["y"] + 1}
        up_block = {"x": block["x"], "y": block["y"] - 1}
        
        right_val = 0
        left_val = 0
        down_val = 0
        up_val = 0
        
        
        # think of proper score calculations, i.e if you can kill a snake
        # then that is worth more than just surviving, food score 
        # should be considered too
        
        
        # currently the tmp_snakes just adds the last block
        # it doesn't remove the tail block. or just past blocks
        right_val = value_helper(data, tmp_snakes, tmp_body, depth+1, right_block) + num_free(data, right_block)
        left_val = value_helper(data, tmp_snakes, tmp_body, depth+1, left_block) + num_free(data, left_block)
        down_val = value_helper(data, tmp_snakes, tmp_body, depth+1, down_block) + num_free(data, down_block)
        up_val = value_helper(data, tmp_snakes, tmp_body, depth+1, up_block) + num_free(data, up_block)
            
        max_val = max(right_val, left_val, down_val, up_val)
            
        return max_val + 1

# dict, dict -> int
# checks all the free blocks conected to the input block
def num_free(data, block):
    checked = []
    snakes = make_snakes(data)
    return num_free_helper(data, snakes, checked, block)
    
def num_free_helper(data, snakes, checked, block):
    if (not is_free(data, snakes, block) or block in checked):
        return 0
    else: 
        checked.append(block)
        right_block = {"x": block["x"] + 1, "y": block["y"]}
        left_block = {"x": block["x"] - 1, "y": block["y"]}
        down_block = {"x": block["x"], "y": block["y"] + 1}
        up_block = {"x": block["x"], "y": block["y"] - 1}
        
        return (num_free_helper(data, snakes, checked, right_block) +
                num_free_helper(data, snakes, checked, left_block) +
                num_free_helper(data, snakes, checked, down_block) +
                num_free_helper(data, snakes, checked, up_block) + 1)   

# dict, list, dict -> directions
def to_target(data, directions, target):
    head = data["you"]["body"][0]
    new_directions = []
    
    if (target["x"] > head["x"] and "right" in directions):
        new_directions.append("right")
    if (target["x"] < head["y"] and "left" in directions):
        new_directions.append("left")
    if (target["y"] > head["y"] and "down" in directions):
        new_directions.append("down")
    if (target["y"] < head["y"] and "up" in directions):
        new_directions.append("up")
        
    if (len(new_directions) != 0):
        return random.choice(new_directions)
    else: 
        return random.choice(directions)

# dict, list, dict -> directions
def avoid_target(data, directions, target):
    head = data["you"]["body"][0]
    new_directions = []
    
    if (target["x"] > head["x"] and abs(target["x"] - head["x"]) <= 2 and "left" in directions):
        new_directions.append("left")
    if (target["x"] < head["x"] and abs(target["x"] - head["x"]) <= 2 and "right" in directions):
        new_directions.append("right")
    if (target["y"] > head["y"] and abs(target["y"] - head["y"]) <= 2 and "up" in directions):
        new_directions.append("up")
    if (target["y"] < head["y"] and abs(target["y"] - head["y"]) <= 2 and "down" in directions):
        new_directions.append("down")
        
    if (len(new_directions) != 0):
        return random.choice(new_directions)
    else: 
        return random.choice(directions)

# dict -> dict
# returns closest food item
def closest_head(data):
    closest = {}
    max = 100
    for snake in data["board"]["snakes"]:
        x = abs(data["you"]["body"][0]["x"] - snake["body"][0]["x"])
        y = abs(data["you"]["body"][0]["y"] - snake["body"][0]["y"])
        distance  = x + y
        if (data["you"]["body"][0] != snake["body"][0] and distance <= max):
            max = distance
            closest = snake["body"][0]
    if (max <= 4):
        return closest
    else:
        return {}

# dict -> dict
# returns the closest food item
def closest_food(data):
    closest = {}
    max = 100
    for food in data["board"]["food"]:
        x = abs(data["you"]["body"][0]["x"] - food["x"])
        y = abs(data["you"]["body"][0]["y"] - food["y"])
        distance = x + y
        if (distance <= max):
            max = distance
            closest = food
    return closest

# dict, dict -> dict
# returns true if enemy snake is smalles
# returns false otherwhise
def is_smaller(data, enemy):
    for snake in data["board"]["snakes"]:
        if (enemy in snake["body"]):
            if (len(data["you"]["body"][0]) > len(snake)):
                return True
    return False

# dict, dict -> bool
# takes game board and a dict with x,y coordinates 
# then returns a bool corresponding to the coordinates 
# location on the board. i.e. false if pos is in snakes 
# or a wall, false otherwise
def is_free(data, snakes, pos):
    if (pos in snakes):
        return False
    if (pos["x"] == -1 or pos["x"] == data["board"]["width"]):
        return False
    if (pos["y"] == -1 or pos["y"] == data["board"]["width"]):
        return False
    return True

#dict -> list
# returns a list of dicts representing snake locations
def make_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            snakes.append(part)
    return snakes
    
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