import json
import os
import random

import bottle
from bottle import HTTPResponse

turn = 0
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
    global turn 
    turn += 1
    print(turn)
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

# dict -> string 
# takes a dict representing the game board and returns 
# a string representing the next move of the snake
def next_move(data):
    enemy = closest_head(data)
    if (enemy != {}):
        if (is_smaller(data, enemy)):
            return to_target(data, value(data), enemy)
        else:
            return avoid_target(data, value(data), enemy)
    return to_target(data, value(data), closest_food(data))

"""
just a consideration but we can increase or decrease the depth
depending on what percent of the board is free and how many directions
the snake can move in to ensure peak computing power. It'll be slow
but it should work better. But if a snake dies in the next x turns then 
the percentage of free tiles on the board increases which means that
the time efficiency will take longer. 

However we can use something like # of snakes on the board to ensure
that we never take to long to make a move. Currently a simple way to 
do this would be to check the # of taken spots on the board and the
number of snakes on the board. If there is just one snake then we 
should increase the depth as extra computing power can ensure that we
have the best chances of winning. Also when there are alot of the snakes
on the board more space is taken up and we can increase the computing 
power but that means that it's easier for snakes to suddenly die. But 
later in the game the size of the snakes and the number of free spots
should decrease allowing us to decrease the depth. 

if we can come up with a way to make it recognize when a snake can be
blocked off that should increase our perfomance by a bit

Finding an efficient way to predict the next moves of the snakes could
also be a good concept to branch off from. Making it efficient is the
protruding challenge but it does not need to check all the block as 
it does not work on our algorithm. We just need to check it's next x moves
and put danger values or something if they collide with our snakes next x moves

Again if we restricted the search requirements for the value function to 
just areas that can fit your own body + x more blocks then we would be able
to have an even greater depth and maybe even predict the next moves of 
other snakes. 
"""

# dict -> string
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


def value_helper(data, snakes, body, depth, block):
    tmp_snakes = snakes.copy()
    tmp_body = body.copy()
    tmp_body.insert(0, block)  
    tail = tmp_body.pop()
    if (tmp_body[0] not in data["board"]["food"]):
        tmp_snakes.remove(tail)
    
    if (depth == 3 or not is_free(data, tmp_snakes, block)):
        return 0
    else:
        tmp_snakes.insert(0, block)  

        right_block = {"x": block["x"] + 1, "y": block["y"]}
        left_block = {"x": block["x"] - 1, "y": block["y"]}
        down_block = {"x": block["x"], "y": block["y"] + 1}
        up_block = {"x": block["x"], "y": block["y"] - 1}
        
        right_val = 0
        left_val = 0
        down_val = 0
        up_val = 0
        
        right_val = value_helper(data, tmp_snakes, tmp_body, depth+1, right_block) + num_free(data, right_block)
        left_val = value_helper(data, tmp_snakes, tmp_body, depth+1, left_block) + num_free(data, left_block)
        down_val = value_helper(data, tmp_snakes, tmp_body, depth+1, down_block) + num_free(data, down_block)
        up_val = value_helper(data, tmp_snakes, tmp_body, depth+1, up_block) + num_free(data, up_block)
            
        max_val = max(right_val, left_val, down_val, up_val)
            
        return max_val + 1

# dict, dict -> int
# checks all the free blocks conected to the input block
# and return that number
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
# given a list of available directions and a target
# it returns a direction that will bring the snake
# closer to the target
def to_target(data, directions, target):
    head = data["you"]["body"][0]
    new_directions = []
    
    if (target["x"] > head["x"] and "right" in directions):
        new_directions.append("right")
    if (target["x"] < head["x"] and "left" in directions):
        new_directions.append("left")
    if (target["y"] > head["y"] and "down" in directions):
        new_directions.append("down")
    if (target["y"] < head["y"] and "up" in directions):
        new_directions.append("up")
     
        
    if (len(new_directions) != 0):
        return random.choice(new_directions)
    else: 
        return random.choice(directions)

'''
- attack stratagies
- algorithm balance between efficiency and complexity 
  (rather than calculating the highest blocks, why not pick a 
   direction that will give you access to all the blocks? it 
   enables you to have more and better moves if there is an enemy 
   head or food in range) (or forcing snakes into corners and or 
   tight spaces)

- we haven't really gone into more complex attack strats other 
  than just chasing the head if bigger. It may be more intersting
  and you might learn more by focusing on this.
'''

# dict, list, dict -> directions
# given a list of available directions and a target
# it returns a direction that will bring the snake
# farter away from the target
def avoid_target(data, directions, target):
    head = data["you"]["body"][0]
    new_directions = []
    targets_directions = targets_moves(data, target)
    
    if (target["x"] > head["x"] and abs(target["x"] - head["x"]) <= 2 and "left" in directions):
        new_directions.append("left")
    if (target["x"] < head["x"] and abs(target["x"] - head["x"]) <= 2 and "right" in directions):
        new_directions.append("right")
    if (target["y"] > head["y"] and abs(target["y"] - head["y"]) <= 2 and "up" in directions):
        new_directions.append("up")
    if (target["y"] < head["y"] and abs(target["y"] - head["y"]) <= 2 and "down" in directions):
        new_directions.append("down")
        
    if (target["x"] == head["x"] and abs(target["y"] - head["y"]) <= 2):
        if ("right" in directions and "right" not in targets_directions):
            return "right"
        if ("left" in directions and "left" not in targets_directions):
            return "left"
        if ("right" in directions and "right" not in new_directions):
            new_directions.append("right")
        if ("left" in directions and "left" not in new_directions):
            new_directions.append("left")
        
    if (target["y"] == head["y"] and abs(target["x"] - head["x"]) <= 2):
        if ("down" in directions and "down" not in targets_directions):
            return "down"
        if ("up" in directions and "up" not in targets_directions):
            return "up"
        if ("down" in directions and "down" not in new_directions):
            new_directions.append("down")
        if ("up" in directions and "up" not in new_directions):
            new_directions.append("up")
       
    """    
    or predict the next possible moves of the snakes. maybe once we
    have our next possible direcions we run another version of 
    value(data) where it plays out all the next x moves of the other
    snakes and the algorithm picks the safest move.
    
    we can predict enemy moves by simply doing a surrounding block check 
    to eleminate the moves they can't make for sure. So if you are running 
    away and the snake can't go right but right is available to you then 
    turn right rather than left
    
    could increase the range of chasing snakes
    
    we could instead make our value function recognize if a space
    is big enough to not die rather than just picking the path with 
    the most blocks. This way it saves computing power if the condition 
    is met and we can instead use that computing power to predict the 
    other moves of snakes.
    
    complete the predicting moves and use it to avoid snakes first 
    then consider starting on another snake/working on more efficient 
    versions of algorithms with simmilar goals
    
    if target is 2 blocks to a wall and you are in line with it go
    towards the wall to block it off
    
    we need a smarter chasing algorithm. one that won't chase along
    a wall or into a tight space. maybe chasing it's tail or something 
    
    make snake avoid making moves that can result in it being blocked off
    """
        
        
    if (len(new_directions) != 0):
        return random.choice(new_directions)
    else: 
        return to_target(data, directions, closest_food(data))

# dict, dict -> list
# takes a dict representing the game board and a dict
# representing an enemy head and returns its available moves
def targets_moves(data, target):
    directions = []
    snakes = make_snakes(data)
    
    right_block = {"x": target["x"] + 1, "y": target["y"]}
    left_block = {"x": target["x"] - 1, "y": target["y"]}
    down_block = {"x": target["x"], "y": target["y"] + 1}
    up_block = {"x": target["x"], "y": target["y"] - 1}
    
    if (is_free(data, snakes, right_block)):
        directions.append("right")
    if (is_free(data, snakes, left_block)):
        directions.append("left")
    if (is_free(data, snakes, down_block)):
        directions.append("down")
    if (is_free(data, snakes, up_block)):
        directions.append("up")
        
    return directions   

# dict -> dict
# returns closest enemy head to own head
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
# returns the closest food item to head
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
# returns true if enemy snake is smaller than own head
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