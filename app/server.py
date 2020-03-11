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

'''
Key things to add
1. proper chasing algorithm (combined with direction dettection)
2. only chase if there is an open path to target (pairs up with #3)
3. recognize if a block will be gone after x number of moves
4. smarter head avoidance algorithm (should take own position into account)
5. smarter in what it chooses to chase e.g. heads vs food, vs tailType
6. remove directions that guarentee death rather than the one with the most open paths 


When done key things
1. pridict directions of other snakes
2. efficient pathing in tight corneres 
'''



# dict -> string
# returns the next move the snake should make
def next_move(data):
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    directions = []
    
    Rblock = {"x": head["x"] + 1, "y": head["y"]}
    Lblock = {"x": head["x"] - 1, "y": head["y"]}
    Dblock = {"x": head["x"], "y": head["y"] + 1}
    Ublock = {"x": head["x"], "y": head["y"] - 1}
    
    if (is_free(data, Rblock, 1) and Rblock["x"] != data["board"]["width"]):
        directions.append("right")
    if (is_free(data, Lblock, 1) and Lblock["x"] != -1):
        directions.append("left")
    if (is_free(data, Dblock, 1)and Dblock["y"] != data["board"]["height"]):
        directions.append("down")
    if (is_free(data, Ublock, 1)and Ublock["y"] != -1):
        directions.append("up")

    avoid = head_to_avoid(data)
    kill = head_to_chase(data) 
    eat = food_to_eat(data)
    tail = data["you"]["body"][-1]
    
    if (len(avoid) != 0):
        avoid_directions = head_zone(data, directions, avoid)
        tail_directions = directions_to_target(data,tail)
        new_directions = []
        if ("right" in avoid_directions and "right" in tail_directions):
            new_directions.append("right")
        if ("left" in avoid_directions and "left" in tail_directions):
            new_directions.append("left")
        if ("down" in avoid_directions and "down" in tail_directions):
            new_directions.append("down")
        if ("up" in avoid_directions and "up" in tail_directions):
            new_directions.append("up")
        if (len(kill) != 0):
            return path_towards(data, kill, path_away(data, avoid, new_directions))
        if (len(eat) != 0):
            return path_towards(data, eat, path_away(data, avoid, new_directions))
        return random.choice(path_away(data, avoid, new_directions))
        
        ## we switched this with kill to make it eat first
    if (len(eat) != 0):
        eat_directions = directions_to_target(data, eat)
        tail_directions = directions_to_target(data,tail)
        new_directions = []
        if ("right" in eat_directions and "right" in tail_directions):
            new_directions.append("right")
        if ("left" in eat_directions and "left" in tail_directions):
            new_directions.append("left")
        if ("down" in eat_directions and "down" in tail_directions):
            new_directions.append("down")
        if ("up" in eat_directions and "up" in tail_directions):
            new_directions.append("up")    
        if (len(new_directions) == 0):
            return path_towards(data, eat, directions)
        return path_towards(data, eat, new_directions)
        
    if (len(kill) != 0):
        kill_directions = directions_to_target(data, kill)
        tail_directions = directions_to_target(data,tail)
        new_directions = []
        if ("right" in kill_directions and "right" in tail_directions):
            new_directions.append("right")
        if ("left" in kill_directions and "left" in tail_directions):
            new_directions.append("left")
        if ("down" in kill_directions and "down" in tail_directions):
            new_directions.append("down")
        if ("up" in kill_directions and "up" in tail_directions):
            new_directions.append("up")
        return path_towards(data, kill, new_directions)
        
    if (len(directions_to_target(data, tail)) != 0):
        tail_directions = directions_to_target(data, tail)
        return path_towards(data, tail, tail_directions)
        
    if (len(directions) != 0):
        return random.choice(directions)
    return "up"
 
 
checked = []
# dict, dict -> list 
# returns list of possible directions to target
def directions_to_target(data, target):
    head = data["you"]["body"][0]
    directions = []
    
    checked.clear()
    if (links(data, head, target, 1, "right")): 
        directions.append("right")
    checked.clear()
    if (links(data, head, target, 1, "left")):
        directions.append("left")
    checked.clear()
    if (links(data, head, target, 1, "down")):
        directions.append("down")
    checked.clear()
    if (links(data, head, target, 1, "up")):
        directions.append("up")
    return directions
 
 
# dict -> dict
# returns the closest enemy head that poses a threat 
def head_to_avoid(data):
    head = data["you"]["body"][0]
    heads = make_enemy_heads(data)
    sizes = make_sizes(data)
    own_size = len(data["you"]["body"])
    
    
    target = {}
    pathX = 3
    pathY = 3
    distance = 6
    
    counter = 0
    for bad_head in heads: 
        if (own_size < sizes[counter]):
            x = abs(bad_head["x"] - head["x"])
            y = abs(bad_head["y"] - head["y"])
            tmp = x + y
            if ((x <= 3 and y <= 3) and tmp < distance):
                target = bad_head
        if (own_size <= sizes[counter]):
            x = abs(bad_head["x"] - head["x"])
            y = abs(bad_head["y"] - head["y"])
            tmp = x + y
            if ((x <= 2 and y <= 2) and tmp < distance):
                target = bad_head
        counter += 1
    return target
    
# dict, list -> string
# returns the closest targetable head
def head_to_chase(data):
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
        counter += 1
    return target
    
# dict -> dict
# returs the closest targetable food
def food_to_eat(data):
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
        if (distance < path and len(directions_to_target(data, item)) != 0):
            path = distance
            target = item
    return target
 
 
# dict, dict, int -> bool 
# returns true if the block will be gone before you reach it
# returns false otherwise 
def is_free(data, block, distance):    
    head = data["you"]["body"][0]
    count = 0
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            if (block == part):
                try:
                    snake["body"][count+distance]
                    return False
                except IndexError:
                    return True
            count += 1
        count = 0
    return True
    

# dict, dict, dict, list, int,string -> bool
# returns True if direction is linked to target
# False if otherwise
def links(data, block, target, distance, direction):
    state = 0
    if (direction == "right"):
        state += links_helper(data, block, target, distance, "right")
        
    if (direction == "left"):
        state += links_helper(data, block, target, distance, "left")
    
    if (direction == "down"):
       state += links_helper(data, block, target, distance, "down")
    
    if (direction == "up"):
        state += links_helper(data, block, target, distance, "up")
    if (state > 0):
        return True
    return False


# dict, dict, dict, , int, string -> int 
# returns a count of all the blocks that 
# the input block is linked with
def links_helper(data, block, target, distance, direction):
    Rblock = {"x": block["x"] + 1, "y": block["y"]}
    Lblock = {"x": block["x"] - 1, "y": block["y"]}
    Dblock = {"x": block["x"], "y": block["y"] + 1}
    Ublock = {"x": block["x"], "y": block["y"] - 1}
    
    
    state = 0
    if ((Rblock == target or Lblock == target or Dblock == target or Ublock == target) and is_free(data, block, distance)):
        return 1
    
    if (direction == "right"):
        if (is_free(data, Rblock, distance) != True or Rblock["x"] == data["board"]["width"] or Rblock in checked):
            return 0
        checked.append(Rblock)
        state += links_helper(data, Rblock, target, distance+1, direction) + links(data, Rblock, target, distance+1, "down") + links(data, Rblock, target, distance+1, "up")
        
    if (direction == "left"):
        if (is_free(data, Lblock, distance) != True or Lblock["x"] == -1 or Lblock in checked):
            return 0
        checked.append(Lblock)
        state += links_helper(data, Lblock, target, distance+1, direction) + links(data, Lblock, target, distance+1, "down") + links(data, Lblock, target, distance+1, "up")
        
    if (direction == "down"):
        if (is_free(data, Dblock, distance) != True or Dblock["y"] == data["board"]["height"] or Dblock in checked):
            return 0
        checked.append(Dblock)
        state += links_helper(data, Dblock, target, distance+1, direction)  + links(data, Dblock, target, distance+1, "right") + links(data, Dblock, target, distance+1, "left")
        
    if (direction == "up"):
        if (is_free(data, Ublock, distance) != True or Ublock["y"] == -1 or Ublock in checked):
            return 0
        checked.append(Ublock)
        state += links_helper(data, Ublock, target, distance+1, direction) + links(data, Ublock, target, distance+1, "right") + links(data, Ublock, target, distance+1, "left")
    return state 


# dict, dict, list -> string
# takes target location and pick the most optimal path to get there
def path_towards(data, target, directions): 
    head = data["you"]["body"][0]
    
    Rblock = {"x": head["x"] + 1, "y": head["y"]}
    Lblock = {"x": head["x"] - 1, "y": head["y"]}
    Dblock = {"x": head["x"], "y": head["y"] + 1}
    Ublock = {"x": head["x"], "y": head["y"] - 1}
    
    pathX = abs(head["x"] - target["x"])
    pathY = abs(head["y"] - target["y"])
    if (head["x"] <= target["x"] and head["y"] <= target["y"]):
        if ("right" in directions and "down" in directions):
            if (Rblock["x"] == data["board"]["width"]-1 ):
                return "down"
            if (Dblock["y"] == data["board"]["height"]-1):
                return "right"
                
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
            if (Rblock["x"] == data["board"]["width"]-1 ):
                return "up"
            if (Ublock["y"] == 0):
                return "right"
                
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
            if (Lblock["x"] == 0):
                return "down"
            if (Dblock["y"] == data["board"]["height"]-1):
                return "left"
                
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
            if (Lblock["x"] == 0):
                return "up"
            if (Ublock["y"] == 0):
                return "left"
                
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

# dict, dict, list -> list
# takes target location and pick the most optimal directions to run away from it
def path_away(data, target, directions): 
    head = data["you"]["body"][0]
    Rblock = {"x": head["x"] + 1, "y": head["y"]}
    Lblock = {"x": head["x"] - 1, "y": head["y"]}
    Dblock = {"x": head["x"], "y": head["y"] + 1}
    Ublock = {"x": head["x"], "y": head["y"] - 1}
    
    if (head["x"] <= target["x"] and head["y"] >= target["y"]): # target in q1
        if ("left" in directions and "down" in directions):
            if (Lblock["x"] == 0):
                return ["down"]
            if (Dblock["y"] == data["board"]["height"]-1):
                return ["left"]
            return ["left", "down"]
            
        if ("left" in directions):
            return ["left"]
            
        if ("down" in directions):  
            return ["down"]
        
        if ("right" in directions):
            return ["right"]
            
    if (head["x"] >= target["x"] and head["y"] <= target["y"]): # target in q2
        if ("right" in directions and "up" in directions):
            if (Rblock["x"] == data["board"]["width"]-1 ):
                return ["up"]
            if (Ublock["y"] == 0):
                return ["right"]
            return ["right", "up"]
            
        if ("right" in directions):
            return ["right"]
            
        if ("up" in directions):
            return ["up"]
            
        if ("down" in directions):
            return ["down"]
    
    if (head["x"] >= target["x"] and head["y"] >= target["y"]): # target in q3
        if ("right" in directions and "down" in directions):
            if (Rblock["x"] == data["board"]["width"]-1 ):
                return ["down"]
            if (Dblock["y"] == data["board"]["height"]-1):
                return ["right"]
            return ["right", "down"]
            
        if ("right" in directions):  
            return ["right"]
            
        if ("down" in directions):
            return ["down"]
            
        if ("up" in directions):
            return ["up"]
                     
    
    if (head["x"] <= target["x"] and head["y"] <= target["y"]):  # target in q4
        if ("left" in directions and "up" in directions):
            if (Lblock["x"] == 0):
                return ["up"]
            if (Ublock["y"] == 0):
                return ["left"]
            return ["left", "up"]
            
        if ("left" in directions):
            return ["left"]            

        if ("up" in directions):  
            return ["up"]
                
        if ("right" in directions):
            return ["right"]
            
    if (len(directions) != 0):
        return random.choice(directions)
    return "up"

# dict, list, dict -> list
# returns the safest directions to go to avoid snake heads
def head_zone(data, directions, target):
    head = data["you"]["body"][0]
    new_directions = []
    if (target["x"] > head["x"] and target["y"] < head["y"]):
        if ("left" in directions):
            new_directions.append("left")
        if ("down" in directions):
            new_directions.append("down")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["x"] < head["x"] and target["y"] < head["y"]):
        if ("right" in directions):
            new_directions.append("right")
        if ("down" in directions):
            new_directions.append("down")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["x"] < head["x"] and target["y"] > head["y"]):
        if ("right" in directions):
            new_directions.append("right")
        if ("up" in directions):
            new_directions.append("up")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["x"] > head["x"] and target["y"] > head["y"]):
        if ("left" in directions):
            new_directions.append("left")
        if ("up" in directions):
            new_directions.append("up")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["x"] > head["x"]):
        if ("left" in directions):
            new_directions.append("left")
        if ("down" in directions):
            new_directions.append("down")
        if ("up" in directions):
            new_directions.append("up")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["x"] < head["x"]):
        if ("right" in directions):
            new_directions.append("right")
        if ("down" in directions):
            new_directions.append("down")
        if ("up" in directions):
            new_directions.append("up")
        if (len(new_directions) != 0):
            return new_directions
    
    if (target["y"] > head["y"]):
        if ("right" in directions):
            new_directions.append("right")
        if ("left" in directions):
            new_directions.append("left")
        if ("up" in directions):
            new_directions.append("up")
        if (len(new_directions) != 0):
            return new_directions
        
    if (target["y"] < head["y"]):
        if ("right" in directions):
            new_directions.append("right")
        if ("left" in directions):
            new_directions.append("left")
        if ("down" in directions):
            new_directions.append("down")
        if (len(new_directions) != 0):
            return new_directions
    return directions    

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
            if (part != data["you"]["body"][0]):
                snakes.append(part)
    return snakes
    
# list -> list
# makes a list of all the snakes sizes
def make_sizes(data): 
    sizes = []
    you = data["you"]
    for snake in data["board"]["snakes"]: 
        if (snake != you):
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