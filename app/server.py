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

    response = {"color": "#00FF7F", "headType": "bendr", "tailType": "round-bum"}
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
    snakes = make_static_snakes(data)
    snakes2 = make_snakes(data)
    moves1 = safe_moves(data, snakes, data["you"]["body"][0])
    moves2 = free_moves(data, make_enemy_heads(data), data["you"]["body"][0])
    along_wall = is_along_wall(data, make_heads(data))
    
    for move in moves1:
        if (move not in moves2):
            moves1.remove(move)
        
    
    for head in along_wall:
        move = destroy(data, snakes2, snakes, head)
        if (move != "no"):
            return move 
    if (data["you"]["health"] < 20):
        return to_target(data, moves1, food)
    return sensor_move(data)


def sensor_move(data):
    moves = []
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    enemy_heads = make_enemy_heads(data)
    
    up = [sensor(data, head, "up"), 0]
    up_right = [sensor(data, head, "up_right"), 1]
    right = [sensor(data, head, "right"), 2]
    down_right = [sensor(data, head, "down_right"), 3]
    down = [sensor(data, head, "down"), 4]
    down_left = [sensor(data, head, "down_left"), 5]
    left = [sensor(data, head, "left"), 6]
    up_left = [sensor(data, head, "up_left"), 7]
   
    
    vals = [up, up_right, right, down_right, down, down_left, left, up_left]
    vals2 = [up, up_right, right, down_right, down, down_left, left, up_left]
    vals3 = [up, up_right, right, down_right, down, down_left, left, up_left]
    
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
        
    if (len(new_vals) != 0):
        max_val = max(new_vals)
    else: 
        max_val = 0
        
    if (max_val != 0):
        if (max_val == up[0] and up in vals):
            return "up"
            
        if (max_val == up_right[0] and up_right in vals):
            if (right[0] != 0 and up[0] != 0):
                return random.choice(["up", "right"])
            
        if (max_val == right[0] and right in vals):
            return "right"
            
        if (max_val == down_right[0] and down_right in vals):
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
                
    tmp = []
        
    if (up in vals):
        tmp.append(up[0])
    if (right in vals): 
        tmp.append(right[0])
    if (down in vals):
        tmp.append(down[0])
    if (left in vals):
        tmp.append(left[0])
    
    if (len(tmp) != 0):
        max_val = max(tmp)
    else: 
        max_val = 0
    
    if (max_val != 0):
        if (max_val == up[0] and up in vals):
            return "up"
            
        if (max_val == right[0] and right in vals):
            return "right"
            
        if (max_val == down[0] and down in vals):
            return "down"
            
        if (max_val == left[0] and left in vals):
            return "left"
        
    

    
    
    # checking for snakes 1 move away
    
    if (is_enemy_head2(data, enemy_heads, head, "up")):
        vals2.remove(up_left)
        vals2.remove(up)
        vals2.remove(up_right)
        
    if (is_enemy_head2(data, enemy_heads, head, "up_right")):
        if (up in vals2):
            vals2.remove(up)
        if (up_right in vals2):
            vals2.remove(up_right)
        vals2.remove(up_left)
        vals2.remove(right)
        vals2.remove(down_right)
        
    if (is_enemy_head2(data, enemy_heads, head, "right")):
        if (up_right in vals2):
            vals2.remove(up_right)
        if (right in vals2):
            vals2.remove(right)
        if (down_right in vals2):
            vals2.remove(down_right)
        
    if (is_enemy_head2(data, enemy_heads, head, "down_right")):
        if (right in vals2):
            vals2.remove(right)
        if (down_right in vals2):   
            vals2.remove(down_right)
        if (down in vals2):
            vals2.remove(down)
        if (down_left in vals2):
            vals2.remove(down_left)
        if (up_right in vals2):
            vals2.remove(up_right)
            
    if (is_enemy_head2(data, enemy_heads, head, "down")):
        if (down_right in vals2):
            vals2.remove(down_right)
        if (down in vals2):
            vals2.remove(down)
        if (down_left in vals2):
            vals2.remove(down_left)
        
    if (is_enemy_head2(data, enemy_heads, head, "down_left")):
        if (down in vals2):
            vals2.remove(down)
        if (down_left in vals2):
            vals2.remove(down_left)
        if (left in vals2):
            vals2.remove(left)
        if (up_left in vals2):
            vals2.remove(up_left)
        if (down_right in vals2):
            vals2.remove(down_right)
        
    if (is_enemy_head2(data, enemy_heads, head, "left")):
        if (down_left in vals2):
            vals2.remove(down_left)
        if (left in vals2):
            vals2.remove(left)
        if (up_left in vals2):
            vals2.remove(up_left)
    
    if (is_enemy_head2(data, enemy_heads, head, "up_left")):
        if (left in vals2):
            vals2.remove(left)
        if (up_left in vals2):
            vals2.remove(up_left)
        if (up in vals2):
            vals2.remove(up)
        if (down_left in vals2):
            vals2.remove(down_left)
        if (up_right in vals2):
            vals2.remove(up_right)
    
    
    
    new_vals2 = []
    for val in vals2:
        new_vals2.append(val[0])
        
    if (len(new_vals2) != 0):
        max_val = max(new_vals2)
    else: 
        max_val = 0

    if (max_val != 0):
        if (max_val == up[0] and up in vals2):
            return "up"
            
        if (max_val == up_right[0] and up_right in vals2):
            if (right[0] != 0 and up[0] != 0):
                return random.choice(["up", "right"])
            
        if (max_val == right[0] and right in vals2):
            return "right"
            
        if (max_val == down_right[0] and down_right in vals2):
            if (down[0] != 0 and right[0] != 0):
                return random.choice(["down", "right"])
            
        if (max_val == down[0] and down in vals2):
            return "down"
        
        if (max_val == down_left[0] and down_left in vals2):
            if (down[0] != 0 and left[0] != 0):
                return random.choice(["down", "left"])
            
        if (max_val == left[0] and left in vals2):
            return "left"
            
        if (max_val == up_left[0] and up_left in vals2):
            if (up[0] != 0 and left[0] != 0):
                return random.choice(["up", "left"])
                
    tmp2 = []
        
    if (up in vals2):
        tmp2.append(up[0])
    if (right in vals2): 
        tmp2.append(right[0])
    if (down in vals2):
        tmp2.append(down[0])
    if (left in vals2):
        tmp2.append(left[0])
    
    if (len(tmp2) != 0):
        max_val = max(tmp2)
    else: 
        max_val = 0
    if (max_val != 0):
        if (max_val == up[0] and up in vals2):
            return "up"
            
        if (max_val == right[0] and right in vals2):
            return "right"
            
        if (max_val == down[0] and down in vals2):
            return "down"
            
        if (max_val == left[0] and left in vals2):
            return "left"
            
        
        
        
    # last options
    new_vals3 = []
    for val in vals3:
        new_vals3.append(val[0])
    max_val = max(new_vals3)
    
    if (max_val == up[0]):
        return "up"  
    
    if (max_val == up_right[0]):
        if (right[0] != 0 and up[0] != 0):
            return random.choice(["up", "right"])
        
    if (max_val == right[0]):
        return "right"
        
    if (max_val == down_right[0]):
        if (down[0] != 0 and right[0] != 0):
            return random.choice(["down", "right"])
        
    if (max_val == down[0]):
        return "down"
    
    if (max_val == down_left[0]):
        if (down[0] != 0 and left[0] != 0):
            return random.choice(["down", "left"])
        
    if (max_val == left[0]):
        return "left"
        
    if (max_val == up_left[0]):
        if (up[0] != 0 and left[0] != 0):
            return random.choice(["up", "left"])
            
    max_val = max(up[0], right[0], down[0], left[0])
    
    if (max_val == up[0]):
        return "up"
        
    if (max_val == right[0]):
        return "right"
        
    if (max_val == down[0]):
        return "down"
        
    if (max_val == left[0]):
        return "left"
    
    
def sensor(data, pos, direction):
    tmp_snakes = make_tmp_snakes(data)
    return sensor_helper(data, tmp_snakes, pos, direction)
    
def sensor_helper(data, tmp_snakes, pos, direction):
    new_pos = {"x": pos["x"], "y": pos["y"]}
    if (not is_free_tmp(data, tmp_snakes, pos) and pos != data["you"]["body"][0]):
        return -1
    else: 
        remove_tails(tmp_snakes)
        if (direction == "up"):
            new_pos["y"] -= 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "up_right"):
            new_pos["y"] -= 1
            new_pos["x"] += 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "right"):
            new_pos["x"] += 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "down_right"):
            new_pos["y"] += 1
            new_pos["x"] += 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "down"):
            new_pos["y"] += 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "down_left"):
            new_pos["y"] += 1
            new_pos["x"] -= 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "left"):
            new_pos["x"] -= 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1
            
        if (direction == "up_left"):
            new_pos["y"] -= 1
            new_pos["x"] -= 1
            return sensor_helper(data, tmp_snakes, new_pos, direction) + 1


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
    

def is_enemy_head2(data, enemy_heads, pos, direction):
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

    
def free_moves(data, enemy_heads, pos):
    moves = ["right", "left", "down", "up"]
    
    
    if (is_enemy_head(data, enemy_heads, pos, "right")):
        moves.remove("right")
    if (is_enemy_head(data, enemy_heads, pos, "left")):
        moves.remove("left")
    if (is_enemy_head(data, enemy_heads, pos, "down")):
        moves.remove("down")
    if (is_enemy_head(data, enemy_heads, pos, "up")):
        moves.remove("up")
        
    if (is_enemy_head(data, enemy_heads, pos, "up_right")):
        if ("up" in moves):
            moves.remove("up")
        if ("right" in moves):
            moves.remove("right")
            
    if (is_enemy_head(data, enemy_heads, pos, "up_left")):
        if ("up" in moves):
            moves.remove("up")
        if ("left" in moves):
            moves.remove("left")
        
    if (is_enemy_head(data, enemy_heads, pos, "down_right")):
        if ("down" in moves):
            moves.remove("down")
        if ("right" in moves):
            moves.remove("right")
    
    if (is_enemy_head(data, enemy_heads, pos, "down_left")):
        if ("down" in moves):
            moves.remove("down")
        if ("left" in moves):
            moves.remove("left")
        
    return moves
 
def safe_moves(data, snakes, pos):
    moves = []
    
    right = {"x": pos["x"] + 1, "y": pos["y"]}
    left = {"x": pos["x"] - 1, "y": pos["y"]}
    down = {"x": pos["x"], "y": pos["y"] + 1}
    up = {"x": pos["x"], "y": pos["y"] - 1}
    
    if (is_free(data, snakes, right)):
        moves.append("right")
    if (is_free(data, snakes, left)):
        moves.append("left")
    if (is_free(data, snakes, up)):
        moves.append("up")
    if (is_free(data, snakes, down)):
        moves.append("down")
        
    return moves
 
def destroy(data, snakes, snakes_static, pos):
    head = data["you"]["body"][0]
    target_moves = safe_moves(data, snakes_static, pos)

    moves1 = safe_moves(data, snakes, data["you"]["body"][0])
    moves2 = free_moves(data, make_enemy_heads(data), data["you"]["body"][0])
    
    for move in moves1:
        if (move not in moves2):
            moves1.remove(move)
    
    head_moves = moves1
    

    # top_wall
    if (pos["y"] == 0):
        y_distance = head["y"] - pos["y"]
        if ("right" in target_moves and "left" not in target_moves):
            print("here")
            x_distance = head["x"] - pos["x"]
            # if head is close enough and to the right the enemy head
            if (y_distance <= 3 and x_distance >= 0):
                if (y_distance < x_distance and "up" in head_moves):
                    return "up"
                elif (y_distance == x_distance and "up" in head_moves and pos not in enemy_heads):
                    return "up"
                else: 
                    if ("right" in head_moves and head["y"] != 0):
                        return "right"
        
        if ("left" in target_moves and "right" not in target_moves):
            x_distance = pos["x"] - head["x"]
            # if head is close enough and to the left the enemy head
            if (y_distance <= 3 and x_distance >= 0):
                if (y_distance < x_distance and "up" in head_moves):
                    return "up"
                elif (y_distance == x_distance and "up" in head_moves and pos not in enemy_heads):
                    return "up"
                else: 
                    if ("left" in head_moves and head["y"] != 0):
                        return "left"
    
    # right_wall
    if (pos["x"] == data["board"]["width"] - 1):
        x_distance = pos["x"] - head["x"]
        if ("up" in target_moves and "down" not in target_moves):
            y_distance = pos["y"] - head["y"]
            # if head is close enough and above the enemy head
            if (x_distance <= 3 and y_distance >= 0):
                if (x_distance < y_distance and "right" in head_moves):
                    return "right"
                elif (x_distance == y_distance and "right" in head_moves and pos not in enemy_heads):
                    return "right"
                else: 
                    if ("up" in head_moves and head["x"] != data["board"]["width"] - 1):
                        return "up"
        
        if ("down" in target_moves and "up" not in target_moves):
            y_distance = head["y"] - pos["y"]
            # if head is close enough and below the enemy head
            if (x_distance <= 3 and y_distance >= 0):
                if (x_distance < y_distance and "right" in head_moves):
                    return "right"
                elif (x_distance == y_distance and "right" in head_moves and pos not in enemy_heads):
                    return "right"
                else: 
                    if ("down" in head_moves and head["x"] != data["board"]["width"] - 1):
                        return "down"
                
            
    # bottom_wall
    if (pos["y"] == data["board"]["height"] - 1):
        y_distance = pos["y"] - head["y"]
        if ("right" in target_moves and "left" not in target_moves):
            x_distance = head["x"] - pos["x"]
            # if head is close enough and to the right the enemy head
            if (y_distance <= 3 and x_distance >= 0):
                if (y_distance < x_distance and "down" in head_moves):
                    return "down"
                elif (y_distance == x_distance and "down" in head_moves and pos not in enemy_heads):
                    return "down"
                else: 
                    if ("right" in head_moves and head["y"] != data["board"]["height"] - 1):
                        return "right"
        
        if ("left" in target_moves and "right" not in target_moves):
            x_distance = pos["x"] - head["x"]
            # if head is close enough and to the left the enemy head
            if (y_distance <= 3 and x_distance >= 0):
                if (y_distance < x_distance and "down" in head_moves):
                    return "down"
                elif (y_distance == x_distance and "down" in head_moves and pos not in enemy_heads):
                    return "down"
                else: 
                    if ("left" in head_moves and head["y"] != data["board"]["height"] - 1):
                        return "left"
        
    # left_wall
    if (pos["x"] == 0):
        x_distance = head["x"] - pos["x"]
        if ("up" in target_moves and "down" not in target_moves):
            y_distance = pos["y"] - head["y"]
            # if head is close enough and above the enemy head
            if (x_distance <= 3 and y_distance >= 0):
                if (x_distance < y_distance and "left" in head_moves):
                    return "left"
                elif (x_distance == y_distance and "left" in head_moves and pos not in enemy_heads):
                    return "left"
                else: 
                    if ("up" in head_moves and head["x"] != 0):
                        return "up"
        
        if ("down" in target_moves and "up" not in target_moves):
            y_distance = head["y"] - pos["y"]
            # if head is close enough and below the enemy head
            if (x_distance <= 3 and y_distance >= 0):
                if (x_distance < y_distance and "left" in head_moves):
                    return "left"
                elif (x_distance == y_distance and "left" in head_moves and pos not in enemy_heads):
                    return "left"
                else: 
                    if ("down" in head_moves and head["x"] != 0):
                        return "down"
        
    return "no"     
    

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
    
    
def is_along_wall(data, enemies):
    along_wall = []
    for head in enemies:
        if (head["x"] == data["board"]["width"] - 1 or 
            head["y"] == data["board"]["height"] -1 or 
            head["x"] == 0 or head["y"] == 0):
            along_wall.append(head)
    return along_wall

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
    
def make_tmp_snakes(data):
    tmp_snakes = []
    for snake in data["board"]["snakes"]:
        tmp_snake = []
        for part in snake["body"]:
            tmp_part = {"x": part["x"], "y": part["y"]}
            tmp_snake.append(tmp_part)
        tmp_snakes.append(tmp_snake)
    return tmp_snakes
    
def remove_tails(tmp_snakes):
    for tmp_snake in tmp_snakes:
        if (len(tmp_snake) != 0):
            tmp_snake.pop()
            
def is_free_tmp(data, tmp_snakes, pos):
    for tmp_snake in tmp_snakes:
        if (pos in tmp_snake):
            return False
    return not(pos["x"] == data["board"]["height"] or 
               pos["y"] == data["board"]["width"] or 
               pos["x"] == -1 or pos["y"] == -1)

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
   
def make_static_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            snakes.append(part)
    return snakes
   
def make_heads(data):
    heads = []
    for snake in data["board"]["snakes"]:
        if (snake != data["you"]):
            heads.append(snake["body"][0])
    return heads
    
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