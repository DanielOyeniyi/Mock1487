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
    food = closest_food(data)
    moves = []
    block = data["you"]["body"][0]
    snakes = make_snakes(data)
    
    right_block = {"x": block["x"] + 1, "y": block["y"]}
    left_block = {"x": block["x"] - 1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"] + 1}
    up_block = {"x": block["x"], "y": block["y"] - 1}    

    if (is_free(data, snakes, right_block)):
        moves.append("right")
    if (is_free(data, snakes, left_block)):
        moves.append("left")
    if (is_free(data, snakes, down_block)):
        moves.append("down")
    if (is_free(data, snakes, up_block)):
        moves.append("up")
    
    if (data["you"]["health"] < 50):
        return to_target(data, moves, food)
    return sensor_move(data)


def sensor_move(data):
    moves = []
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    enemy_heads = make_enemy_heads(data)
    
    up = [sensor(data, snakes, head, "up"), 0]
    up_right = [sensor(data, snakes, head, "up_right"), 1]
    right = [sensor(data, snakes, head, "right"), 2]
    down_right = [sensor(data, snakes, head, "down_right"), 3]
    down = [sensor(data, snakes, head, "down"), 4]
    down_left = [sensor(data, snakes, head, "down_left"), 5]
    left = [sensor(data, snakes, head, "left"), 6]
    up_left = [sensor(data, snakes, head, "up_left"), 7]
    
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
        vals.remove(up_left)
        vals.remove(right)
        vals.remove(down_right)
        print("here")
        
    if (is_enemy_head(data, enemy_heads, head, "right")):
        if (up_right in vals):
            vals.remove(up_right)
        if (right in vals):
            vals.remove(right)
        if (down_right in vals):
            vals.remove(down_right)
        
    if (is_enemy_head(data, enemy_heads, head, "down_right")):
        if (right in vals):
            vals.remove(right)
        if (down_right in vals):   
            vals.remove(down_right)
        if (down in vals):
            vals.remove(down)
        if (down_left in vals):
            vals.remove(down_left)
        if (up_right in vals):
            vals.remove(up_right)
        
        
    if (is_enemy_head(data, enemy_heads, head, "down")):
        if (down_right in vals):
            vals.remove(down_right)
        if (down in vals):
            vals.remove(down)
        if (down_left in vals):
            vals.remove(down_left)
        
    if (is_enemy_head(data, enemy_heads, head, "down_left")):
        if (down in vals):
            vals.remove(down)
        if (down_left in vals):
            vals.remove(down_left)
        if (left in vals):
            vals.remove(left)
        if (up_left in vals):
            vals.remove(up_left)
        if (down_right in vals):
            vals.remove(down_right)
        
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
        if (down_left in vals):
            vals.remove(down_left)
        if (up_right in vals):
            vals.remove(up_right)
    
    new_vals = []
    for val in vals:
        new_vals.append(val[0])
        
    max_val = max(new_vals)
    
    if (max_val == up[0] and up in vals):
        return "up"
        
    if (max_val == up_right[0] and up_right in vals):
        if (right[0] != 0 and up[0] != 0):
            return random.choice(["up", "right"])
        
    if (max_val == right[0] and right in vals):
        return "right"
        
    if (max_val == down_right[0] and down_right in vals):
        print("here")
        print(right)
        if (down[0] != 0 and right[0] != 0):
            return random.choice(["down", "right"])
        
    if (max_val == down[0] and down in vals):
        return "down"
    
    if (max_val == down_left[0] and down_left in vals):
        if (down[0] != 0 and left[0] != 0):
            return random.choice(["down", "left"])
        
    if (max_val == left[0] and left in vals):
        return "left"
        
    if (max_val == up_left[0] and up_left in vals):
        if (up[0] != 0 and left[0] != 0):
            return random.choice(["up", "left"])
            
    max_val = max(up[0], right[0], down[0], left[0])
    
    if (max_val == up[0] and up in vals):
        return "up"
        
    if (max_val == right[0] and right in vals):
        return "right"
        
    if (max_val == down[0] and down in vals):
        return "down"
        
    if (max_val == left[0] and left in vals):
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
        if (new_pos in enemy_heads):
            return True
        new_pos["y"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "up_right"):
        new_pos["y"] -= 1
        new_pos["x"] += 1
        if (new_pos in enemy_heads):
            return True
        new_pos["y"] -= 1
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "right"):
        new_pos["x"] += 1
        if (new_pos in enemy_heads):
            return True
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down_right"):
        new_pos["y"] += 1
        new_pos["x"] += 1
        if (new_pos in enemy_heads):
            return True
        new_pos["y"] += 1
        new_pos["x"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down"):
        new_pos["y"] += 1
        if (new_pos in enemy_heads):
            return True
        new_pos["y"] += 1
        return new_pos in enemy_heads
            
    if (direction == "down_left"):
        new_pos["y"] += 1
        new_pos["x"] -= 1
        if (new_pos in enemy_heads):
            return True
        new_pos["y"] += 1
        new_pos["x"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "left"):
        new_pos["x"] -= 1
        if (new_pos in enemy_heads):
            return True
        new_pos["x"] -= 1
        return new_pos in enemy_heads
            
    if (direction == "up_left"):
        new_pos["y"] -= 1
        new_pos["x"] -= 1
        if (new_pos in enemy_heads):
            return True
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
        if (data["you"]["body"][0] != snake["body"][0] and 
            len(data["you"]["body"]) <= len(snake["body"])):
            enemies.append(snake["body"][0])
    return enemies

#dict -> list
# returns a list of dicts representing snake locations
def make_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            snakes.append(part)
        if (len(snake) >= 2):
            if (snake["body"][-1] != snake["body"][-2]):
                snakes.remove(snake["body"][-1])
    return snakes
    

# dict, list, dict -> directions
# given a list of available directions and a target
# it returns a direction that will bring the snake
# closer to the target
def to_target(data, directions, target):
    if (len(directions) == 0):
        return "up"
        
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
        return sensor_move(data)
    
    
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