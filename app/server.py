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

    moves = ["right", "left", "down", "up"]

    #FIRST PRIORITY - Snake should avoid hitting walls 
    heightBoard = data["board"]["height"] #retrieve height 
    widthBoard = data["board"]["width"]  #retrieve width 

    halfHeight = heightBoard / 2
    halfWidth = widthBoard / 2

    # LOCATION: of snake head
    locHeadX = data["you"]["body"][0]["x"]
    locHeadY = data["you"]["body"][0]["y"]

    #If statement to force snake away from boundaries/wall
    #x boundary/walls/corners
    if (locHeadX == widthBoard-1):  #farthest x-axis length, a length of 11 is represented by index 10  
        moves.remove("right")
        
        # LOCATION: of neck1 
       # neck1X = data["you"]["body"][1]["x"]
       # if(neck1X ==(widthBoard-2)):   #if body is in the left column next to the farthest length value
        #    move = "up"
       # else:
        #    move = "left"

    if (locHeadX == 0):  #closest x-axis length
        moves.remove("left")
      
     #   neck1X = data["you"]["body"][1]["x"]
      #  if(neck1X ==(1)):
       #   move = "up"
        #else:
         # move = "right"


    #y boundary/walls/corners
    if (locHeadY == heightBoard-1):
        moves.remove("down")
        
        #neck1Y = data["you"]["body"][1]["y"]
        #if (neck1Y == heightBoard-2):
         #   move = "right"
        #else:
         #   move = "up"

    if (locHeadY == 0):
        moves.remove("up")
      
      #neck1Y = data["you"]["body"][1]["y"]
      # if (neck1Y == 1):
        #  move = "right"
        #else:
         # move = "down"


    #END OF FIRST PRIORITY #############################################


    #SECOND PRIORITY - Snake should avoid hitting itself

    #Checks 1 block to the right,left,up,down to see if any of the snake's body part is in there (using the snake head location + or - 1 as a reference), if it is then it will remove the direction from the moves list.

    allSnakes = []

    for snakes in data["board"]["snakes"]:
        for snakesBody in snakes["body"]:
            allSnakes.append(snakesBody)





    right = {"x": locHeadX + 1, "y": locHeadY}
    left = {"x": locHeadX - 1, "y": locHeadY} 
    up = {"x": locHeadX, "y": locHeadY-1}
    down = {"x": locHeadX, "y": locHeadY+1}

    if (right in allSnakes):  #checks to see if body part is 1 RIGHT to the head.
        moves.remove("right")
        
    if (left in allSnakes):  #checks to see if body part is 1 LEFT to the head.
        moves.remove("left")
          
    if (up in allSnakes): #checks to see if body part is 1 UP to the head.
        moves.remove("up")
        
    if (down in allSnakes): #checks to see if body part is 1 DOWN to the head.
        moves.remove("down")
      
    # prevents snake from getting blocked: Checks to see if snake head will be blocked up by body in all options after moving 1 to right, left, up, down
      
    right2 = {"x": locHeadX + 2, "y": locHeadY}
    right1up1 = {"x": locHeadX + 1, "y": locHeadY + 1}
    right1down1 = {"x": locHeadX + 1, "y": locHeadY - 1}

    left2 = {"x": locHeadX - 2, "y": locHeadY} 
    left1up1 = {"x": locHeadX - 1, "y": locHeadY + 1}
    left1down1 = {"x": locHeadX - 1, "y": locHeadY - 1}

    up2 = {"x": locHeadX, "y": locHeadY-2}
    up1right1 = {"x": locHeadX + 1, "y": locHeadY - 1}
    up1left1 = {"x": locHeadX - 1, "y": locHeadY - 1}

    down2 = {"x": locHeadX, "y": locHeadY+2}
    down1right1 = {"x": locHeadX + 1, "y": locHeadY + 1}
    down1left1 = {"x": locHeadX - 1, "y": locHeadY + 1}

    # if(condition1 and condition2 and condition3)

    if ("right" in moves and right2 in data["you"]["body"]) and (right1up1 in data["you"]["body"]) and (right1down1 in data["you"]["body"]):  #checks to see if body part is 2 right AND 1right 1up AND 1right 1down, to the head.
        moves.remove("right")
      
    if ("left" in moves and left2 in data["you"]["body"]) and (left1up1 in data["you"]["body"]) and (left1down1 in data["you"]["body"]):  #checks to see if body part is 2 left AND 1left 1up AND 1left 1down, to the head.
        moves.remove("left")
        
    if ("up" in moves and up2 in data["you"]["body"]) and (up1right1 in data["you"]["body"]) and (up1left1 in data["you"]["body"]):  #checks to see if body part is 2 up AND 1left 1up AND 1right 1up, to the head.
        moves.remove("up") 
        
    if ("down" in moves and down2 in data ["you"]["body"] and down1right1 in data["you"]["body"] and down1left1 in data["you"]["body"]): #checks to see if body part is 2 down AND 1left 1down AND 1right 1down, to the head.
        moves.remove("down")
      

    #END OF SECOND PRIORITY #############################################






    # THIRD PRIORITY - Snake should find shortest path to fruit

    """
    1. find the closest fruit 
    2. go to the closest fruit 

    """

    head = data["you"]["body"][0]
        
        
    min_distance = 999
    closest = {"x": 0, "y": 0}

        
        # each food item = {"x": 9, "y": 5}
    for food in data["board"]["food"]:
        diffx = abs(food["x"]-head["x"])
        diffy = abs(food["y"]-head["y"])
        foodDistance = diffx + diffy
        if (foodDistance < min_distance):
            min_distance = foodDistance  # replaces the shortest distance
            closest = food   # closest now equal; saves the x and y value of current min_distance

        
        
    # eat_food(closest) # go towards closest food
        
    # snake(3,2) and food(4,5)
    # 4>3 = right 4<3 = left 5>2 = up  5<2 = down, right/left by diffx and up/down by difffy
        
    if (closest["x"] > head["x"]): 
        if ("right" in moves):
            move = "right"
        else:
          move = ""
    elif (closest["x"] < head["x"]): 
        if ("left" in moves):
            move = "left"
        else:
          move = ""
    else: # if x is not greater than or less than then it must be equal
        if (closest["y"] < head["y"]): 
            if ("up" in moves):
                move = "up"
            else:
              move = ""
        elif(closest["y"] > head["y"]): 
            if ("down" in moves):
                move = "down"
            else:
              move = ""
        
        

    # END OF THIRD PRIORITY #############################################



    # Shouts are messages sent to all the other snakes in the game.
    # Shouts are not displayed on the game board.
    shout = "I am a python snake!"
            
    
    if (move == ""):
        move = random.choice(moves) # Notmove > halfWidth to centerB x and Notmove > halfWidth to centerB y
        
        
    response = {"move": move, "shout": shout}
    return HTTPResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body=json.dumps(response),
    )
    
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