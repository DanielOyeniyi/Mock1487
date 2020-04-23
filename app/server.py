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
    return sensor_move(data)
    #if (data["you"]["health"] > 50):


def sensor_move(data):
    moves = []
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    enemy_heads = make_enemy_heads(data)
    
    up = sensor(data, snakes, head, "up")
    up_right = sensor(data, snakes, head, "up_right")
    right = sensor(data, snakes, head, "right")
    down_right = sensor(data, snakes, head, "down_right")
    down = sensor(data, snakes, head, "down")
    down_left = sensor(data, snakes, head, "down_left")
    left = sensor(data, snakes, head, "left")
    up_left = sensor(data, snakes, head, "up_left")
    
    vals = [up, up_right, right, down_right, down, down_left, left, up_left]
    
    if (is_enemy_head(data, enemy_heads, head, "up")):
        vals.remove(up_left)
        vals.remove(up)
        vals.remove(up_right)
        
    if (is_enemy_head(data, enemy_heads, head, "up_right")):
        if (up in vals):
            vals.remove(up)
        if (up_right in vals):
            vals.remove(up_right)
        vals.remove(right)
        
    if (is_enemy_head(data, enemy_heads, head, "right")):
        if (up_right in vals):
            vals.remove(up_right)
        if (right in vals):
            vals.remove(right)
        vals.remove(down_right)
        
    if (is_enemy_head(data, enemy_heads, head, "down_right")):
        if (right in vals):
            vals.remove(right)
        if (down_right in vals):   
            vals.remove(down_right)
        vals.remove(down)
        
    if (is_enemy_head(data, enemy_heads, head, "down")):
        if (down_right in vals):
            vals.remove(down_right)
        if (down in vals):
            vals.remove(down)
        vals.remove(down_left)
        
    if (is_enemy_head(data, enemy_heads, head, "down_left")):
        if (down in vals):
            vals.remove (down)
        if (down_left in vals):
            vals.remove(down_left)
        vals.remove(left)
        
    if (is_enemy_head(data, enemy_heads, head, "left")):
        if (down_left in vals):
            vals.remove(down_left)
        if (left in vals):
            vals.remove(left)
        if (up_left in vals):
            vals.remove(up_left)
    
    if (is_enemy_head(data, enemy_heads, head, "up_left")):
        if (left in vals):
            vals.remove(left)
        if (up_left in vals):
            vals.remove(up_left)
        if (up in vals):
            vals.remove(up)
    
    
    max_val = max(vals)
    
    if (max_val == up):
        return "up"
        
    if (max_val == up_right):
        if (right != 0 and up != 0):
            return random.choice(["up", "right"])
        
    if (max_val == right):
        return "right"
        
    if (max_val == down_right):
        if (down != 0 and right != 0):
            return random.choice(["down", "right"])
        
    if (max_val == down):
        return "down"
    
    if (max_val == down_left):
        if (down != 0 and left != 0):
            return random.choice(["down", "left"])
        
    if (max_val == left):
        return "left"
        
    if (max_val == up_left):
        if (up != 0 and left != 0):
            return random.choice(["up", "left"])
            
    max_val = max(up, right, down, left)
    
    if (max_val == up):
        return "up"
        
    if (max_val == right):
        return "right"
        
    if (max_val == down):
        return "down"
        
    if (max_val == left):
        return "left"
    
    
def sensor(data, snakes, pos, direction):
    return sensor_helper(data, snakes, pos, direction)
    
def sensor_helper(data, snakes, pos, direction):
    new_pos = {"x": pos["x"], "y": pos["y"]}
    if (not is_free(data, snakes, pos) and pos != data["you"]["body"][0]):
        return -1
    else: 
        if (direction == "up"):
            new_pos["y"] -= 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "up_right"):
            new_pos["y"] -= 1
            new_pos["x"] += 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "right"):
            new_pos["x"] += 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "down_right"):
            new_pos["y"] += 1
            new_pos["x"] += 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "down"):
            new_pos["y"] += 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "down_left"):
            new_pos["y"] += 1
            new_pos["x"] -= 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "left"):
            new_pos["x"] -= 1
            return sensor_helper(data, snakes, new_pos, direction) + 1
            
        if (direction == "up_left"):
            new_pos["y"] -= 1
            new_pos["x"] -= 1
            return sensor_helper(data, snakes, new_pos, direction) + 1


def is_enemy_head(data, enemy_heads, pos, direction):
    new_pos = {"x": pos["x"], "y": pos["y"]}
    if (direction == "up"):
        new_pos["y"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "up_right"):
        new_pos["y"] -= 1
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "right"):
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down_right"):
        new_pos["y"] += 1
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down"):
        new_pos["y"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down_left"):
        new_pos["y"] += 1
        new_pos["x"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "left"):
        new_pos["x"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "up_left"):
        new_pos["y"] -= 1
        new_pos["x"] -= 1
        return new_pos in enemy_heads
    

# dict, list, dict -> bool
# return true if the block is not in any snake body parts and 
# outside of the game board
def is_free(data, snakes, pos):
    return not (pos in snakes or
                pos["x"] == data["board"]["height"] or 
                pos["y"] == data["board"]["width"] or 
                pos["x"] == -1 or pos["y"] == -1)

def make_enemy_heads(data):
    enemies = []
    for snake in data["board"]["snakes"]:
        if (data["you"]["body"][0] != snake["body"][0]):
            enemies.append(snake["body"][0])
    return enemies

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