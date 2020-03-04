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

    response = {"color": "#00FF00", "headType": "regular", "tailType": "regular"}
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
    
    head = data["you"]["body"][0]
    
    # (0, 0)
    # quadrant 2 | quadrant 1
    # -----------------------
    # quadrant 3 | quadrant 4
    #                      (Xmax, Ymax)
    
    
    # theory: if q1 is safest, path directly there if you are in q2, or q4 
    # if you are in q3, path through the safest between q2 and q4
    q1 = quadrant(data, Xcenter, Xmax, 0, Ycenter)
    q2 = quadrant(data, 0, Xcenter, 0, Ycenter)
    q3 = quadrant(data, 0, Xcenter, Ycenter, Ymax)
    q4 = quadrant(data, Xcenter, Xmax, Ycenter, Ymax)
    
    ordered = [q1, q2, q3, q4]  # randomize the one it picks if [0]==[1]  or [0]==[1]==[2]
    ordered.sort()              # then focus on pathing through the safest quadrant    
    target = ordered[0] 
    
    right_block = {"x": head["x"]+1, "y": head["y"]}    
    left_block = {"x": head["x"]-1, "y": head["y"]}      
    down_block = {"x": head["x"], "y": head["y"]+1}   
    up_block = {"x": head["x"], "y": head["y"]-1}  
    
    
    # this is just to test if it is going to the correct quadrant
    if (target == q1):
        if (head["x"] < Xcenter and right_block != data["you"]["body"][1]):
            return "right"
        if (head["y"] > Ycenter and up_block != data["you"]["body"][1]):
            return "up"
        return random.choice(["left", "down"])

    elif (target == q2): 
        if (head["x"] > Xcenter and left_block != data["you"]["body"][1]):
            return "left"
        if (head["y"] > Ycenter and up_block != data["you"]["body"][1]):
            return "up"
        return random.choice(["right", "down"])
            
    elif (target == q3):
        if (head["x"] > Xcenter and left_block != data["you"]["body"][1]):
            return "left"
        if (head["y"] < Ycenter and down_block != data["you"]["body"][1]):
            return "down"
        return random.choice(["right", "up"])
        
    else:
        if (head["x"] < Xcenter and right_block != data["you"]["body"][1]):
            return "right"
        if (head["y"] < Ycenter and down_block != data["you"]["body"][1]): 
            return "down"
        return random.choice(["left", "up"])
    
    
    location = head_location(head, Xcenter, Ycenter) 
    # now we want to avoid walls while pathing to the safest quadrant
    
    

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
# makes a llist of bodies
def make_bodies(snakes, heads, own_head):    
    bodies = []
    for snake in snakes:
        for part in snake["body"]:
            if (part not in heads and part != own_head):
                bodies.append(part)
    return bodies
    
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
                danger += 2
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
    