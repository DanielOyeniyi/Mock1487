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

    response = {"color": "#FFD700", "headType": "beluga", "tailType": "curled"}
    #### change the look... it deserves better
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
    next_move(data)
    print("MOVE:", json.dumps(data))

    # Choose a random direction to move in
    directions = ["up", "down", "left", "right"]
    move = random.choice(directions)

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
    head = data["you"]["body"][0]
    snakes = make_snakes(data)
    Rblock = {"x": head["x"] + 1, "y": head["y"]}
    Lblock = {"x": head["x"] - 1, "y": head["y"]}
    Dblock = {"x": head["x"], "y": head["y"] + 1}
    Ublock = {"x": head["x"], "y": head["y"] - 1}
    read_file("data_read.txt",data)


def read_file(filename, data):
    dict = {}
    try:
        file_handle = open(filename, "a")
    except FileNotFoundError:
        print("file not found")
    txt = "\n"
    for item in data["board"]["food"]:
        x = str(item["x"])
        y = str(item["y"])
        txt += "\"" + x + "-" + y + "\","
    txt += "\"end\"*"
    
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            x = str(part["x"])
            y = str(part["y"])
            txt += "\"" + x + "-" + y + "\","
        txt += "\"end\""
    file_handle.write(txt)
        
    file_handle.close()
    
#dict -> list
# returns a list of dicts representing snake locations
def make_snakes(data):
    snakes = []
    for snake in data["board"]["snakes"]:
        for part in snake["body"]:
            if (part != data["you"]["body"][0]):
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