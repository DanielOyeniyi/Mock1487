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
    print()

    directions = ["right", "left", "down", "up"]
    move = next_move_intense(data)

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
    
    head = data["you"]["body"][0]
    
    # (0, 0)
    # quadrant 2 | quadrant 1
    # -----------------------
    # quadrant 3 | quadrant 4
    #                      (Xmax, Ymax)
    
    
    
    
    
    # theory: if q1 is safest, path directly there if you are in q2, or q4 
    # if you are in q3, path through the safest between q2 and q4
    # more quadrants? 
    q1 = quadrant(data, Xcenter, Xmax, 0, Ycenter)
    q2 = quadrant(data, 0, Xcenter, 0, Ycenter)
    q3 = quadrant(data, 0, Xcenter, Ycenter, Ymax)
    q4 = quadrant(data, Xcenter, Xmax, Ycenter, Ymax)
    
    ordered = [q1, q2, q3, q4]  
    ordered.sort()                  
    
    location = head_location(head, Xcenter, Ycenter) # need to pick the quickest path depending on location

    directions = available_directions(head, data["board"]["snakes"], Xmax+1, Ymax+1)
    
    if (data["you"]["health"] > 20):
        return healthy(q1, q2, q3, q4, ordered, head, directions, Xcenter, Ycenter)
    return hungry(directions, data["board"]["food"], head)

def next_move_intense(data):
    Xmax = data["board"]["height"] - 1
    Ymax = data["board"]["width"] - 1
    Xcenter = Xmax // 2
    Ycenter = Ymax // 2
    Xcenter1 = Xcenter // 2
    Ycenter1 = Ycenter // 2 
    
    Xcenter2 = Xcenter + Xcenter1 + 1   # middle of quadrant 1
    Ycenter2 = Ycenter + Xcenter1 + 1
    

    head = data["you"]["body"][0]
    directions = available_directions(head, data["board"]["snakes"], Xmax+1, Ymax+1)
    location = head_location(head, Xcenter, Ycenter) # need to pick the quickest path depending on location
    
    # (0, 0)
    # quadrant 2 | quadrant 1
    # -----------------------
    # quadrant 3 | quadrant 4
    #                      (Xmax, Ymax)
    
    # if snake in bottom half, and top 2 quandrants are most dangerous
    # make the snake avoid going up
    
    
    # qb  |  qa
    # ---------
    # qc  | qd
    
    # theory: if q1 is safest, path directly there if you are in q2, or q4 
    # if you are in q3, path through the safest between q2 and q4
    # more quadrants? 
    
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
    ordered.sort()       
   
    
    if (ordered[0] == q1):
        sorted = [q1a, q1b, q1c, q1d]
        sorted.sort()
        if (data["you"]["health"] > 20):
            if (location != "q1" and location != "q1 & q2" and location != "q1 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(q1, q2, q3, q4, ordered[0], head, directions, Xcenter, Ycenter) 
            return healthy_intense(q1a, q1b, q1c, q1d, sorted[0], head, directions, Xcenter2, Ycenter1)
        return hungry(directions, data["board"]["food"], head)
        
    if (ordered[0] == q2):
        sorted = [q2a, q2b, q2c, q2d]
        sorted.sort()
        if (data["you"]["health"] > 20):
            if (location != "q2" and location != "q2 & q3" and location != "q1 & q2" and location != "q1 & q2 & q3 & q4"):
                return healthy(q1, q2, q3, q4, ordered[0], head, directions, Xcenter, Ycenter) 
            return healthy_intense(q2a, q2b, q2c, q2d, sorted[0], head, directions, Xcenter1, Ycenter1)
        return hungry(directions, data["board"]["food"], head)
        
    if (ordered[0] == q3):
        sorted = [q3a, q3b, q3c, q3d]
        sorted.sort()
        if (data["you"]["health"] > 20):
            if (location != "q3" and location != "q2 & q3" and location != "q3 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(q1, q2, q3, q4, ordered[0], head, directions, Xcenter, Ycenter) 
            return healthy_intense(q3a, q3b, q3c, q3d, sorted[0], head, directions, Xcenter1, Ycenter2)
        return hungry(directions, data["board"]["food"], head)
        
    else:
        sorted = [q4a, q4b, q4c, q4d]
        sorted.sort()
        if (data["you"]["health"] > 20):
            if (location != "q4" and location != "q1 & q4" and location != "q3 & q4" and location != "q1 & q2 & q3 & q4"):
                return healthy(q1, q2, q3, q4, ordered[0], head, directions, Xcenter, Ycenter) 
            return healthy_intense(q4a, q4b, q4c, q4d, sorted[0], head, directions, Xcenter2, Ycenter2)
        return hungry(directions, data["board"]["food"], head)

   
    # it seems like the chase and kill method is pretty good, do that after tho
    # we need head sensors, attack and destroy or beta
 
def healthy_intense(qa, qb, qc, qd, biggest, head, directions, Xcenter, Ycenter):
    if (biggest == qa):
        if (head["x"] <= Xcenter and "right" in directions):
            return "right"
        if (head["y"] >= Ycenter and "up" in directions):
            return "up"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"

    elif (biggest == qb): 
        if (head["x"] >= Xcenter and "left" in directions):
            return "left"
        if (head["y"] >= Ycenter and "up" in directions):
            return "up"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"
            
    elif (biggest == qc):
        if (head["x"] >= Xcenter and "left" in directions):
            return "left"
        if (head["y"] <= Ycenter and "down" in directions):
            return "down"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"
        
    else:
        if (head["x"] <= Xcenter and "right" in directions):
            return "right"
        if (head["y"] <= Ycenter and "down" in directions): 
            return "down"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"



def healthy(q1, q2, q3, q4, biggest, head, directions, Xcenter, Ycenter):
    if (biggest == q1):
        if (head["x"] <= Xcenter and "right" in directions):
            return "right"
        if (head["y"] >= Ycenter and "up" in directions):
            return "up"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"

    elif (biggest == q2): 
        if (head["x"] >= Xcenter and "left" in directions):
            return "left"
        if (head["y"] >= Ycenter and "up" in directions):
            return "up"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"
            
    elif (biggest == q3):
        if (head["x"] >= Xcenter and "left" in directions):
            return "left"
        if (head["y"] <= Ycenter and "down" in directions):
            return "down"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"
        
    else:
        if (head["x"] <= Xcenter and "right" in directions):
            return "right"
        if (head["y"] <= Ycenter and "down" in directions): 
            return "down"
        if (len(directions) != 0):
            return random.choice(directions)
        print("uh oh...")
        return "up"

# list, list, dict -> string
# takes a list of possible directions and 
# picks a direction that will goes towards food
def hungry(directions, food, head):
    path = 100   
    nearest = {}
    
    for item in food: 
        x = abs(item["x"] - head["x"])
        y = abs(item["y"] - head["y"])
        distance = x + y 
        if (distance < path):
            path = distance
            nearest = item
            
    if (head["x"] < nearest["x"] and "right" in directions):
            return "right"
    if (head["x"] > nearest["x"] and "left" in directions):
            return "left"
    if (head["y"] < nearest["y"] and "down" in directions):
            return "down"
    if (head["y"] < nearest["y"] and "up" in directions):
            return "up"
    if (len(directions) != 0):
        return random.choice(directions)
    print("Uh oh...")
    return "up"    
    
    
# dict , int, int-> list
# takes a list representing a block on the map and 
# returns a list of available directions
def available_directions(block, snakes, Xmax, Ymax):
    right_block = {"x": block["x"]+1, "y": block["y"]}
    left_block = {"x": block["x"]-1, "y": block["y"]}
    down_block = {"x": block["x"], "y": block["y"]+1}
    up_block = {"x": block["x"], "y": block["y"]-1}
    
    directions = ["right", "left", "down", "up"]
    
    # rather than checking all the blocks around head(in advanced) why not just 
    # check the next two blocks adjacent e.g. (up -> up)
    ###### TRY IT!!!! ######
    
    if (right_block["x"] == Xmax):
        directions.remove("right") 
    if (left_block["x"] == -1):
        directions.remove("left")
    if (down_block["y"] == Ymax):
        directions.remove("down")
    if (up_block["y"] == -1):
        directions.remove("up")
        
    for snake in snakes:
        for part in snake["body"]:
            if (right_block == part and "right" in directions):
                directions.remove("right")
            if (left_block == part and "left" in directions):
                directions.remove("left")
            if (down_block == part and "down" in directions):
                directions.remove("down")
            if (up_block == part and "up" in directions):
                directions.remove("up")
    
    
    tails = make_tails(snakes)
    
    # you can make it not include the tail if and only if the body is not next to food
    if (len(directions)==0): # should now check for tails
        if (right_block in tails):
            directions.append("right") 
        if (left_block in tails):
            directions.append("left")
        if (down_block in tails):
            directions.append("down")
        if (up_block in tails):
            directions.append("up")
        return directions
    return directions
    

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


# dict, int, int, int, int -> int
# takes a dict representing the board data and the bounds
# of quadrant 
def quadrant(data, Xstart, Xfinish, Ystart, Yfinish):
    snakes = data["board"]["snakes"]
    own_head = data["you"]["body"][0]
    food = data["board"]["food"]
    heads = make_heads(snakes, own_head)
    bodies = make_bodies(snakes, heads, own_head)
    return danger_level(heads, bodies, food, Xstart, Xfinish, Ystart, Yfinish)
    
# list, list -> list
# makes a list of enemy snake heads 
def make_heads(snakes, own_head):
    heads = []
    for snake in snakes:
        if (snake["body"][0] != own_head):
            heads.append(snake["body"][0])
    return heads
    
# list, list, dict -> list 
# makes a list of bodies
def make_bodies(snakes, heads, own_head):    
    bodies = []
    for snake in snakes:
        for part in snake["body"]:
            if (part not in heads and part != own_head):
                bodies.append(part)
    return bodies
        
# list -> list
# makes a list of tails
def make_tails(snakes):
    tails = []
    for snake in snakes: 
        tails.append(snake["body"][-1])
    return tails
    
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
                danger += 5
            if (block in bodies):
                danger += 3
            if (block in food):
                danger += 1
    return danger



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
    