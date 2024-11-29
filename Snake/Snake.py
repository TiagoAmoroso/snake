#Creating a grid based snake game
import pygame
import random
import os

'''
Additions

Rainbow gradient for the snake's body  -  COMPLETE
Make the colour gradient a bit prettier
Menu screen
Pause screen
AI to control the snake  -  COMPLETE
Death animation  -  COMPLETE
Variable animation length  -  by this I mean, I want the animation to last longer if the snake is long, and be shorter if the snake is shorter
Better start screen  -  for example, the head grows out of the centre of the screen and then starts to move instead of just appearing and then moving immediately
Highscore system  -  COMPLETE
Screen Frame rate independant of game frame rate  -  COMPLETE
'''

#Snake buffer = 3, food Buffer = 7, max food amount = 3, grid size = 10, game frame rate = 5, screen frame rate = 60

#Constants
THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
HIGHSCORES_FILE = 'highscores.txt'

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600

GRID_SIZE = 10 #23,26,27,28 etc produce odd results

CELL_WIDTH = SCREEN_WIDTH / GRID_SIZE #Width of each cell on the board
CELL_HEIGHT = SCREEN_HEIGHT / GRID_SIZE #Height of each cell on the board

FRAME_RATE = 60 #Frame rate of the screen. The amount of frame changes per second
GAME_FRAME_RATE = 5 #Frame rate of the game. The amount of game state changes per second - This indicates the movement speed of the snake
DISPLAY_RATE = FRAME_RATE / GAME_FRAME_RATE #Calculation to find the amount of screen frames to wait before we update the game frame

#These are vector additions for moving the snake
#Pos (0,0) is the top left of the screen which is why the up/down additions are inverted to what... 
#you would expect from a graph with point (0,0) in the bottom left
LEFT = [-1,0]
RIGHT = [1,0]
UP = [0,-1]
DOWN = [0,1]





class Snake(object):
    def __init__(self):
        self.snakePos = [[int(GRID_SIZE/2),int(GRID_SIZE/2)]] #This holds the positions of every part of the snake, the top position is the head
        self.snakeColours = [[0,0,0]] #This holds the RGB values corresponding to each individual snake body part
        self.colourDirection = 1
        self.bodyBuffer = 3 #This the amount of pixels that buffer each snake body part from its surrounding cell
        self.direction = random.choice(['UP', 'DOWN', 'LEFT', 'RIGHT']) #This is the current direction that the snake is moving
        self.eatingFood = False #The snake's eating state
        self.length = len(self.snakePos) #Length of the snake
        self.alive = True #The life state of the snake
        self.deathAnimationDuration = 3 #Amount of time in seconds that the death animation of the snake takes


    def drawSnake(self, surface):

        for bodyPart in self.snakePos: #Iterates through each part of the snake, creates a rect object for it and  then, draws that
            bodyRect = pygame.Rect((bodyPart[0] * CELL_WIDTH + self.bodyBuffer, bodyPart[1] * CELL_HEIGHT + self.bodyBuffer), (CELL_WIDTH - self.bodyBuffer * 2, CELL_HEIGHT - self.bodyBuffer * 2)) #Creating the rectangle object
            bodyPartIndex = self.snakePos.index(bodyPart) #Finding the index of the body part in question
            pygame.draw.rect(surface, self.snakeColours[bodyPartIndex], bodyRect) #Drawing the rectangle in a specific location with a specific colour and size


    def setDirection(self, event):
        startDirection = self.direction

        if event.key == pygame.K_UP:
            self.direction = 'UP'
        elif event.key == pygame.K_DOWN:
            self.direction = 'DOWN'
        elif event.key == pygame.K_LEFT:
            self.direction = 'LEFT'
        elif event.key == pygame.K_RIGHT:
            self.direction = 'RIGHT'

        self.invertDirectionCheck(startDirection) #Ensures that the snake is not going back on itself
                

    def moveSnake(self):
        head = self.snakePos[0].copy() #Creates a variable holding the position of the head of the snake

        #Adds the relevant vector to the head position
        if self.direction == 'LEFT':
            head[0] += LEFT[0]
            head[1] += LEFT[1]
        elif self.direction == 'RIGHT':
            head[0] += RIGHT[0]
            head[1] += RIGHT[1] 
        elif self.direction == 'UP':
            head[0] += UP[0]
            head[1] += UP[1]
        elif self.direction == 'DOWN':
            head[0] += DOWN[0]
            head[1] += DOWN[1]
        else:
            print('Direction error')
            pygame.quit()
            quit()

        self.snakePos.insert(0,head) #Inserting this new position to the front of the list

        #Checks if the snake is eating food so that we can leave the last part of the snake and not pop it, giving the impression of growth
        if self.eatingFood:
            self.eatingFood = False #Resets the snakes state to not eating food
        else:
            self.snakePos.pop() #Removing the last part of the snake to give the impression of movement


    def addNewColour(self):
        newColour = [0,0,0]

        '''
        I prefer the other effect so will just comment this out for now
        #Generates a random colour
        for i in range(len(newColour)-1): #Iterates over each RGB value
            newColour[i] = random.randint(0, 255) #Generates a random value for R, G, and B
        '''

        #Generates colours based on the colour of the prior body part
        priorColour = self.snakeColours[len(self.snakeColours)-1]

        for i in range(len(newColour)-1): #Iterates over each RGB value
            newColour[i] = priorColour[i] + (random.randint(10, 30) * self.colourDirection) #Generates a random value for R, G, and B

            #Ensuring that the RGB values do not go out of range
            if newColour[i] > 255:
                self.colourDirection = -1
                newColour[i] = 255
            if newColour[i] < 0:
                self.colourDirection = 1
                newColour[i] = 0


        self.snakeColours.append(newColour)


    def eatFood(self, foodObj, foodPos):
        foodObj.removeFood(foodPos) #Remove the food that the snake collided with from the list of food positions
        self.eatingFood = True #Set eatingFood to true so that the snake's size grows. This is done at the end of the moveSnake function
        self.length += 1 #Adds to the user's length
        self.addNewColour() #Adds a new colour corresponding to the new snake piece being created by eating the food


    def foodCollisionCheck(self, foodObj):
        for foodPos in foodObj.foodPos: #Iterates over each food position
            if self.snakePos[0] == foodPos: #Checks if the head of the snake is colliding with the food
                self.eatFood(foodObj, foodPos) #Eats the food


    def wallCollisionCheck(self):
        if self.snakePos[0][0] < 0 or self.snakePos[0][0] > GRID_SIZE - 1 or self.snakePos[0][1] < 0 or self.snakePos[0][1] > GRID_SIZE - 1:
            print("Utter noob, you've gone off the screen. Ur trash kid.")
            self.alive = False


    def snakeCollisionCheck(self):
        if len(self.snakePos) > 1: #Ensures that there is more than one bodyPart to the snake, as the snake cannot collide with itself when it is just a head
            for bodyPart in self.snakePos[-len(self.snakePos)+1:]: #This iterates through every position other than the head of the snake
                if bodyPart == self.snakePos[0]: #If the coordinates of the snake head are the same as those of another bodyPart, then we log a collision
                    print("Utter noob, you've collided with yourself. Ur trash kid.")
                    self.alive = False


    def invertDirectionCheck(self, startDirection):
        newDirection = self.direction 
        directionInverted = False

        #This code has been implemented to reset the snake when the snake is turnt back upon itself
        if len(self.snakePos) > 1: #Checks that the snake is larger than one as the snake can go in any direction when it is that small
            if startDirection == 'UP' and newDirection == 'DOWN':
                directionInverted = True
            
            elif startDirection == 'DOWN' and newDirection == 'UP':
                directionInverted = True
            
            elif startDirection == 'RIGHT' and newDirection == 'LEFT':
                 directionInverted = True
            
            elif startDirection == 'LEFT' and newDirection == 'RIGHT':
                directionInverted = True
            
            if directionInverted: #If the user has gone back on themselves, we reset the game
                print('You went back on yourself... What a noob. Get gud kid.')
                self.alive = False


    def blitLength(self, screen):
        highscore = loadHighscore()

        myfont = pygame.font.SysFont("monospace",20)
        text = myfont.render("Length: {0} Highscore: {1}".format(self.length, highscore), 1, (0,0,0))
        screen.blit(text, (10,10))


    def blitDeathText(self, screen):
        if not self.alive:
            myfont = pygame.font.SysFont("monospace", 35, bold = pygame.font.Font.bold)
            text = myfont.render("You died at length {0}".format(self.length), 1, (22,158,74))
            screen.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2))
            text = myfont.render("Press enter to restart", 1, (22,158,74))
            screen.blit(text, (SCREEN_WIDTH/2 - text.get_width()/2, SCREEN_HEIGHT/2 - text.get_height()/2 + 30))


    def snakeDeath(self, screen):
        if not self.alive:
            newHighscoreCheck(self)
        
            if len(self.snakePos) > 0:
                self.snakePos.remove(random.choice(self.snakePos))
            #I have now changed this so that the user can press enter for the game to restart earlier, this is found in the eventManager function
            else:
                main()



        #Don't like this effect as much as it can take too long when the snake is too long
        '''
        Pops each body part from the snake frame by frame
        if len(self.snakePos) > 0:
            self.snakePos.pop()
        else:
            main()   
        '''


class Food(object):
    def __init__(self):
        self.foodPos = [[random.randint(0,GRID_SIZE - 1), random.randint(0,GRID_SIZE - 1)]] #This holds the location of the food object
        self.foodBuffer = 7 #This the amount of pixels that buffer the food from its surrounding cell 
        self.maxFoodAmount = 3 #This is the greatest amount of food that is allowed on the board at any given time


    def addFood(self, snakeObj):
    
        uniquePosition = False

        while not uniquePosition: #Loops until the random position generated is in a unique location(one that is not already occupied)
            newPos = [random.randint(0,GRID_SIZE - 1), random.randint(0,GRID_SIZE - 1)]
            uniquePosition = True

            for bodyPart in snakeObj.snakePos: #Iterates through each position of the snake's body
                if newPos == bodyPart: #Checks if the new position of the food falls within the bounds of the snake's body
                    uniquePosition = False
                
            for food in self.foodPos:
                if newPos == food: #Checks if the new position of the food is the same as any already existing foods
                    uniquePosition = False
                       
        #If the code gets to here, we can safely add the food in the newPos as it has been checked against the snake's body and the positions of already existing foods
        self.foodPos.append(newPos) #Appends the new foodPos to the list of foodPositions


    def drawFood(self, surface):
        for food in self.foodPos:
            foodRect = pygame.Rect((food[0] * CELL_WIDTH + self.foodBuffer, food[1] * CELL_HEIGHT + self.foodBuffer), (CELL_WIDTH - self.foodBuffer * 2, CELL_HEIGHT - self.foodBuffer * 2))
            pygame.draw.rect(surface, (255,0,0), foodRect)


    def removeFood(self, food):
        self.foodPos.remove(food) #Removes the food position from the list of food positions


    def foodAmountCheck(self, snakeObj):
        if len(self.foodPos) < self.maxFoodAmount: #If the amount of food is less than the maxFoodAmount...
            self.addFood(snakeObj) #Add another piece of food to the board



class SnakeAI(object):
    def __init__(self, snakeObj, foodObj, active = True):
        self.snakeObj = snakeObj
        self.foodObj = foodObj
        self.active = active
        self.moves = ['UP','DOWN','LEFT','RIGHT']
        self.allowedMoves = ['UP','DOWN','LEFT','RIGHT']
        self.forbiddenMoves = []
        self.recommendedMoves = []

    def resetMoves(self):
        self.allowedMoves = self.moves.copy() #Have to use .copy() otherwise any changes made to self.allowedMoves also get made to self.moves
        self.forbiddenMoves = []
        self.recommendedMoves = []


    def removeMoves(self):
        for move in self.forbiddenMoves: #Iterating through all the moves that have been deemed forbidden (as they would lead to the snake's death)
            moveCount = self.allowedMoves.count(move) #Checks that the move is still available
            if moveCount == 1:
                self.allowedMoves.remove(move) #Removes the move from allowedMoves


    def selectMove(self):
        print("Allowed moves: ", self.allowedMoves)
        print("Recommended moves: ", self.recommendedMoves)
        chosenMove = ""
        matchedMoves = []

        #Finds the moves that are both allowed and recomended
        for move in self.recommendedMoves:
            if move in self.allowedMoves:
                matchedMoves.append(move)

        #If there are no moves that are both allowed and recomended, then we just choose an allowed move
        if len(matchedMoves) == 0:
            if len(self.allowedMoves) == 0: #If there are no allowed moves, this means that the snake will die whereever it moves
                chosenMove = random.choice(self.moves) #So we just select a random direction and let it die
                print("The snake will die after this move to the: " + chosenMove)

            else: #We choose an allowed move if there are any available
                chosenMove = random.choice(self.allowedMoves)

        #If there are moves that are both allowed and recomended, then we choose one of those
        else:
            chosenMove = random.choice(matchedMoves)
        
        self.snakeObj.direction = chosenMove #We set the direction of the snake to the direction that we have selected
        

    def avoidWalls(self): 
        #Checking if the snake is on the edge of the board, if so we ban the move that would lead to the snake's death

        if self.snakeObj.snakePos[0][0] < 1:
            self.forbiddenMoves.append('LEFT')
            print('On the left wall!')
        elif self.snakeObj.snakePos[0][0] > GRID_SIZE - 2:
            self.forbiddenMoves.append('RIGHT')
            print('On the right wall!')
        elif self.snakeObj.snakePos[0][1] < 1:
            self.forbiddenMoves.append('UP')
            print('On the upper wall!')
        elif self.snakeObj.snakePos[0][1] > GRID_SIZE - 2:
            self.forbiddenMoves.append('DOWN')
            print('On the lower wall!')

    #The error is in here - removing moves when there is nothing there...
    def avoidSnake(self):
        #Checking if any of the possible next moves would lead to the snake colliding with itself, if so we ban the move that would lead to the snake's death
        
        if len(self.snakeObj.snakePos) > 1: #Ensures that there is more than one bodyPart to the snake, as the snake cannot collide with itself when it is just a head
            for bodyPart in self.snakeObj.snakePos[-len(self.snakeObj.snakePos)+1:]:# This iterates through every position other than the first
                
                if bodyPart[1] == self.snakeObj.snakePos[0][1]: #Ensuring the y values are equal before we check either side
                    if bodyPart[0] == self.snakeObj.snakePos[0][0] + 1: 
                        self.forbiddenMoves.append('RIGHT')
                        print('Snake to the right!')
                    elif bodyPart[0] == self.snakeObj.snakePos[0][0] - 1: 
                        self.forbiddenMoves.append('LEFT')
                        print('Snake to the left!')
                
                if bodyPart[0] == self.snakeObj.snakePos[0][0]: #Ensuring the x values are equal before we check above and below
                    if bodyPart[1] == self.snakeObj.snakePos[0][1] + 1: 
                        self.forbiddenMoves.append('DOWN')
                        print('Snake below!')
                    elif bodyPart[1] == self.snakeObj.snakePos[0][1] - 1: 
                        self.forbiddenMoves.append('UP')
                        print('Snake above!')

            
    def runAI(self):
        if self.active:
            self.resetMoves() #Resets the moveset so that all directions are available

            self.avoidWalls() #Removes directions dependent on wall and snake positions
            self.avoidSnake() #Removes directions dependent on snake body and snake head positions

            self.removeMoves() #Actually removes the moves from the moveset

            self.getToFood()

            self.selectMove() #Selects the direction that the snake will move in
            print("Direction chosen: ", self.snakeObj.direction, '\n')

            self.eatFoodCheck() #Checks if the snake has landed on food and if it has, consumes it


    def eatFoodCheck(self):
        self.snakeObj.foodCollisionCheck(self.foodObj)


    def getToFood(self):
        targetFoodPosition = []
        smallestDifference = 100000000
        targetXDifference = 0
        targetYDifference = 0

        for food in self.foodObj.foodPos: #Iterates through each food item position on the board
            xDifference = self.snakeObj.snakePos[0][0] - self.foodObj.foodPos[0][0] #Finding the x difference between the food and the snake head
            yDifference = self.snakeObj.snakePos[0][1] - self.foodObj.foodPos[0][1] #Finding the y difference between the food and the snake head


            xDifferencePos = xDifference
            yDifferencePos = yDifference
            if xDifferencePos < 0: xDifferencePos = xDifference * -1 #Ensuring a positive value for comparision
            if yDifferencePos < 0: yDifferencePos = yDifference * -1 #Ensuring a positive value for comparision

            totalDifference = xDifferencePos + yDifferencePos #Calculates the total range between the snake head and the food

            if totalDifference < smallestDifference: #Checking whether the current difference is the smallest found so far
                smallestDifference = totalDifference 
                targetXDifference = xDifference
                targetYDifference = yDifference
                targetFoodPosition = food 
        
        if yDifference > 0:
            self.recommendedMoves.append('UP')
        else:
            self.recommendedMoves.append('DOWN')

        if xDifference > 0:
            self.recommendedMoves.append('LEFT')
        else:
            self.recommendedMoves.append('RIGHT')



def drawGrid(surface):
    for y in range(0, int(GRID_SIZE)): #Iterates over each y value
        for x in range(0, int(GRID_SIZE)): #Iterates over each x value
            rectangle = pygame.Rect((x*CELL_WIDTH, y*CELL_HEIGHT), (CELL_WIDTH, CELL_HEIGHT)) #Creates the rectangle object
            if (x+y)%2 == 0: #Switches each cell colour by using mod 2 to check for remainder values
                pygame.draw.rect(surface,(193,216,228), rectangle)
            else:
                pygame.draw.rect(surface, (184,194,205), rectangle)


def eventManager(snake, snakeAI):
    for event in pygame.event.get(): #Iterating through all events that pygame has noticed
        if event.type == pygame.QUIT: #If the event is a quit type, we just quit the application
            newHighscoreCheck(snake)
            pygame.quit()
            quit()
        
        elif event.type == pygame.KEYDOWN: #If pygame notices a key down, we check if it is a directional key and assign this direction to the snake
            if not snakeAI.active:
                snake.setDirection(event)
        
            #Handling keydown events that are exclusive for when the snake is in a death state
            if not snake.alive:
                if event.key == 13: #13 is the event key for the 'enter' key on the keyboard
                    main()


def screenManager(snake, food, screen, surface):
    drawGrid(surface) #Draws the grid onto the surface
    food.drawFood(surface) #Draws the food onto the surface
    snake.drawSnake(surface) #Draws the snake onto the surface above the grid
    screen.blit(surface, (0,0)) #Actually putting the surface on the screen by blitting the entire surface
    snake.blitLength(screen) #Blits the length directly onto the screen, above the surface that is blitted on the line prior
    snake.blitDeathText(screen) #Blits death text onto screen when snake is in death state
    pygame.display.update() #Updates the display so that changes are visible

    
def gameManager(snake, food, snakeAI):
    
    #Order: handle events (This is now done outside of this function), move the stuff, collisions and other checks, update the screen. This order maintains a responsive feeling. Always update the screen last.
    
    #snakeAI.active = True ############################### Change to make game playable
    snakeAI.active = False
    snakeAI.runAI() #Runs the snake AI
    
    snake.moveSnake() #Moves the snake across the grid

    snake.foodCollisionCheck(food) #Checks for collisions between the snake head and the food
    snake.wallCollisionCheck() #Checks if the snake has fallen out of the bounds of the screen
    snake.snakeCollisionCheck() #Checks if the snake has collided with itself
    

    food.foodAmountCheck(snake) #Checks that there is enough food on the board at any given time


def nextFrameCheck(currentFrame, frameChangesPerSecond):
    #We want the game(as in each visible change in the snake's position) to run at a slow frame rate, most likely around 5 fps
    #However, the screen should still run at 60 fps so I have implemented this code to achieve this

    displayRate = FRAME_RATE / frameChangesPerSecond #Calculation to find the amount of screen frames to wait before we update the game fram
    displayRate = int(round(displayRate)) #Ensuring that the display rate is a nice integer value
    if displayRate == 0: displayRate = 1 #Ensuring that the display rate is at least one frame per second

    if currentFrame % displayRate == 0: 
        return True

    else:
        return False

    
def loadHighscore():
        try:
            with open(os.path.join(THIS_FOLDER, HIGHSCORES_FILE), 'r+') as file:
                highscore = int(file.read())

        except:
            with open(os.path.join(THIS_FOLDER, HIGHSCORES_FILE), 'w') as file:
                highscore = int(file.read())
                highscore = 0
            
        return highscore


def newHighscoreCheck(snake):
    
    try:
        highscore = loadHighscore()
        if snake.length > highscore:
            highscore = snake.length

            try:
                with open(os.path.join(THIS_FOLDER, HIGHSCORES_FILE), 'w') as file:
                        file.write(str(highscore))
                        
            except Exception as error:
                print(error)
                print('Highscore write error')
            
    except Exception as error:
        print(error)
        print('userHighscore or gameHighscore not defined')


def main():
    pygame.init() #Initialising pygame
    pygame.display.set_caption('Snake')

    currentFrame = 0

    clock = pygame.time.Clock() #Initialising clock object
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32) #Setting the screen size

    surface = pygame.Surface(screen.get_size()) #Creating a pygame surface object
    surface = surface.convert() #Good practice apparently but I don't understand why myself

    snake = Snake()
    food = Food()

    snakeAI = SnakeAI(snake, food, active = False)

    while True:
        clock.tick(FRAME_RATE) #Does not allow the game to go over the frame rate specified
        currentFrame += 1

        eventManager(snake, snakeAI) #Manages the events outside of the game frames for a more responsive feel. If the game frame rate is 1fps, you can only input every second. Now, you can input every 1/60 of a second and the screen frame rate is 60

        if snake.alive: #Called when the snake is alive
            if nextFrameCheck(currentFrame, GAME_FRAME_RATE): #This calls the game code at the correct time, this is so there is a difference between the game frame rate and the display frame rate
                #The order of these are very important. If the screenManager was called before the gameManager, the game feel unresponsive and sluggish as the actions you make update a frame later
                gameManager(snake, food, snakeAI) #Manages all gameplay mechanics
                screenManager(snake, food, screen, surface) #Manages all drawing, blitting, and updating. Basically everything to do with viewing the game
        else: #Called when the snake is in a dying state, this is so we can use the faster frame rate of the screen as opposed to the slow rate we use for the game mechanics, this allows for smoother animations. 
            frameChangesPerSecond = int(round(snake.length/snake.deathAnimationDuration)) #This gets the amount of snake body parts we want to remove per second to ensure that the death animation lasts the correct amount of time
            if frameChangesPerSecond == 0: frameChangesPerSecond = 1 #Ensuring that there is at least one frame change per second
            print(snake.deathAnimationDuration, frameChangesPerSecond)


            if nextFrameCheck(currentFrame, frameChangesPerSecond):
                snake.snakeDeath(screen)
                screenManager(snake, food, screen, surface)



if __name__ == '__main__':
    main()