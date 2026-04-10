# Group#: B21
# Student Names: Anna Bartl and Conor O'Neill

"""
    This program implements a variety of the snake 
    game (https://en.wikipedia.org/wiki/Snake_(video_game_genre))
"""

import threading
import queue        #the thread-safe queue from Python standard library

from tkinter import Tk, Canvas, Button
import random, time

class Gui():
    """
        This class takes care of the game's graphic user interface (gui)
        creation and termination.
    """
    def __init__(self):
        """        
            The initializer instantiates the main window and 
            creates the starting icons for the snake and the prey,
            and displays the initial gamer score.
        """
        #some GUI constants
        scoreTextXLocation = 60
        scoreTextYLocation = 15
        textColour = "white"
        #instantiate and create gui
        self.root = Tk()
        self.canvas = Canvas(self.root, width = WINDOW_WIDTH, 
            height = WINDOW_HEIGHT, bg = BACKGROUND_COLOUR)
        self.canvas.pack()
        #create starting game icons for snake and the prey
        self.snakeIcon = self.canvas.create_line(
            (0, 0), (0, 0), fill=ICON_COLOUR, width=SNAKE_ICON_WIDTH)
        self.preyIcon = self.canvas.create_rectangle(
            0, 0, 0, 0, fill=ICON_COLOUR, outline=ICON_COLOUR)
        #display starting score of 0
        self.score = self.canvas.create_text(
            scoreTextXLocation, scoreTextYLocation, fill=textColour, 
            text='Your Score: 0', font=("Helvetica","11","bold"))
        #binding the arrow keys to be able to control the snake
        for key in ("Left", "Right", "Up", "Down"):
            self.root.bind(f"<Key-{key}>", game.whenAnArrowKeyIsPressed)

    def gameOver(self):
        """
            This method is used at the end to display a
            game over button.
        """
        gameOverButton = Button(self.canvas, text="Game Over!", 
            height = 3, width = 10, font=("Helvetica","14","bold"), 
            command=self.root.destroy)
        self.canvas.create_window(200, 100, anchor="nw", window=gameOverButton)
    

class QueueHandler():
    """
        This class implements the queue handler for the game.
    """
    def __init__(self):
        self.queue = gameQueue
        self.gui = gui
        self.queueHandler()
    
    def queueHandler(self):
        '''
            This method handles the queue by constantly retrieving
            tasks from it and accordingly taking the corresponding
            action.
            A task could be: game_over, move, prey, score.
            Each item in the queue is a dictionary whose key is
            the task type (for example, "move") and its value is
            the corresponding task value.
            If the queue.empty exception happens, it schedules 
            to call itself after a short delay.
        '''
        try:
            while True:
                task = self.queue.get_nowait()
                if "game_over" in task:
                    gui.gameOver()
                elif "move" in task:
                    points = [x for point in task["move"] for x in point]
                    gui.canvas.coords(gui.snakeIcon, *points)
                elif "prey" in task:
                    gui.canvas.coords(gui.preyIcon, *task["prey"])
                elif "score" in task:
                    gui.canvas.itemconfigure(
                        gui.score, text=f"Your Score: {task['score']}")
                self.queue.task_done()
        except queue.Empty:
            gui.root.after(100, self.queueHandler)


class Game():
    '''
        This class implements most of the game functionalities.
    '''
    def __init__(self):
        """
           This initializer sets the initial snake coordinate list, movement
           direction, and arranges for the first prey to be created.
        """
        self.queue = gameQueue
        self.score = 0
        #starting length and location of the snake
        #note that it is a list of tuples, each being an
        # (x, y) tuple. Initially its size is 5 tuples.       
        self.snakeCoordinates = [(495, 55), (485, 55), (475, 55),
                                 (465, 55), (455, 55)]
        #initial direction of the snake
        self.direction = "Left"
        self.gameNotOver = True
        self.createNewPrey()

    def superloop(self) -> None:
        """
            This method implements a main loop
            of the game. It constantly generates "move" 
            tasks to cause the constant movement of the snake.
            Use the SPEED constant to set how often the move tasks
            are generated.
        """
        SPEED = 0.15     #speed of snake updates (sec)
        while self.gameNotOver:
            #start a new move (calculate next position and check game status)
            self.move()
            #add the move task to the queue
            self.queue.put_nowait({"move": self.snakeCoordinates})
            time.sleep(SPEED) #add pauses to control speed


    def whenAnArrowKeyIsPressed(self, e) -> None:
        """ 
            This method is bound to the arrow keys
            and is called when one of those is clicked.
            It sets the movement direction based on 
            the key that was pressed by the gamer.
            Use as is.
        """
        currentDirection = self.direction
        #ignore invalid keys
        if (currentDirection == "Left" and e.keysym == "Right" or 
            currentDirection == "Right" and e.keysym == "Left" or
            currentDirection == "Up" and e.keysym == "Down" or
            currentDirection == "Down" and e.keysym == "Up"):
            return
        self.direction = e.keysym

    def move(self) -> None:
        """ 
            This method implements what is needed to be done
            for the movement of the snake.
            It generates a new snake coordinate. 
            If based on this new movement, the prey has been 
            captured, it adds a task to the queue for the updated
            score and also creates a new prey.
            It also calls a corresponding method to check if 
            the game should be over. 
            The snake coordinates list (representing its length 
            and position) should be correctly updated.
        """
        NewSnakeCoordinates = self.calculateNewCoordinates()
        self.snakeCoordinates.append(NewSnakeCoordinates) #add the new coordinates to the snake coordinates list

        self.isGameOver(NewSnakeCoordinates) #check if the game is over based on the new coordinates
        if not self.gameNotOver:
            return

        prey_x, prey_y = self.preyCoordinates   #get the prey coordinates to check if the prey has been captured
        head_x, head_y = NewSnakeCoordinates

        #check if the head of the snake is within the prey's area (considering the prey's width) to determine if the prey has been captured 
        #(mostly done for fist sponned in prey as grid matchup cannot be guaranteed)
        if (prey_x - PREY_ICON_HALF_WIDTH <= head_x <= prey_x + PREY_ICON_HALF_WIDTH and
            prey_y - PREY_ICON_HALF_WIDTH <= head_y <= prey_y + PREY_ICON_HALF_WIDTH):
            #is captured add score and create new prey
            self.score += 1
            self.queue.put_nowait({"score": self.score})
            self.createNewPrey()
        else:
            #if not captured, remove the tail of the snake to keep the same length
            self.snakeCoordinates.pop(0)



    def calculateNewCoordinates(self) -> tuple:
        """
            This method calculates and returns the new 
            coordinates to be added to the snake
            coordinates list based on the movement
            direction and the current coordinate of 
            head of the snake.
            It is used by the move() method.    
        """
        lastX, lastY = self.snakeCoordinates[-1]
        #calculate the new coordinates based on the current direction of movement
        if self.direction == "Left":
            return (lastX - SNAKE_ICON_WIDTH, lastY)
        elif self.direction == "Right":
            return (lastX + SNAKE_ICON_WIDTH, lastY)
        elif self.direction == "Up":
            return (lastX, lastY - SNAKE_ICON_WIDTH)
        elif self.direction == "Down":
            return (lastX, lastY + SNAKE_ICON_WIDTH)
        else:
            #this will only happen if there is a bug, shouldnt happen in normal execution
            raise ValueError(f"Invalid direction: {self.direction}")


    def isGameOver(self, snakeCoordinates) -> None:
        """
            This method checks if the game is over by 
            checking if now the snake has passed any wall
            or if it has bit itself.
            If that is the case, it updates the gameNotOver 
            field and also adds a "game_over" task to the queue. 
        """
        x, y = snakeCoordinates
        # check wall collision: head has moved outside canvas bounds
        # check self-collision: head matches any body segment except the last one (which is the head's previous position and will be vacated after the move)
        if (x < 0 or x >= WINDOW_WIDTH or y < 0 or y >= WINDOW_HEIGHT or 
            snakeCoordinates in self.snakeCoordinates[:-1]):
            self.gameNotOver = False
            self.queue.put_nowait({"game_over": True})
        

    def createNewPrey(self) -> None:
        """ 
            This methods picks an x and a y randomly as the coordinate 
            of the new prey and uses that to calculate the 
            coordinates (x - 5, y - 5, x + 5, y + 5). [you need to replace 5 with a constant]
            It then adds a "prey" task to the queue with the calculated
            rectangle coordinates as its value. This is used by the 
            queue handler to represent the new prey.                    
            To make playing the game easier, set the x and y to be THRESHOLD
            away from the walls. 
        """
        THRESHOLD = 15   #sets how close prey can be to borders
        SCORE_TEXT_X_MAX = 120  # score text occupies roughly x: 0-120, y: 0-30
        SCORE_TEXT_Y_MAX = 30
        #to make the prey alligned with the snakes movement grid
        x_offset = self.snakeCoordinates[0][0] % SNAKE_ICON_WIDTH
        y_offset = self.snakeCoordinates[0][1] % SNAKE_ICON_WIDTH

        #generate possible x and y coordinates for the prey that are aligned with the snake's movement grid and are at least THRESHOLD away from the walls, and not under text
        possible_x = [x for x in range(x_offset, WINDOW_WIDTH, SNAKE_ICON_WIDTH) if THRESHOLD <= x <= WINDOW_WIDTH - THRESHOLD]
        possible_y = [y for y in range(y_offset, WINDOW_HEIGHT, SNAKE_ICON_WIDTH) if THRESHOLD <= y <= WINDOW_HEIGHT - THRESHOLD]
        # a position is excluded only if BOTH x and y are within the score text region
        possible_positions = [
            (x, y) for x in possible_x for y in possible_y
            if not (x <= SCORE_TEXT_X_MAX and y <= SCORE_TEXT_Y_MAX)
        ]
        # select from filtered positions
        available_positions = [(x, y) for (x, y) in possible_positions if (x, y) not in self.snakeCoordinates]
        x, y = random.choice(available_positions)

        #store the prey coordinates
        self.preyCoordinates = (x, y)
        preyCoordinates = (
            x - PREY_ICON_HALF_WIDTH,
            y - PREY_ICON_HALF_WIDTH,
            x + PREY_ICON_HALF_WIDTH,
            y + PREY_ICON_HALF_WIDTH
        )
        self.queue.put_nowait({"prey": preyCoordinates})
        

if __name__ == "__main__":
    #some constants for our GUI
    WINDOW_WIDTH = 500           
    WINDOW_HEIGHT = 300 
    SNAKE_ICON_WIDTH = 15
    PREY_ICON_WIDTH = SNAKE_ICON_WIDTH   #width of the prey matches that of snake
    PREY_ICON_HALF_WIDTH = PREY_ICON_WIDTH // 2 #offset from center to use when drawing prey
    
    BACKGROUND_COLOUR = "green"   #you may change this colour if you wish
    ICON_COLOUR = "yellow"        #you may change this colour if you wish

    gameQueue = queue.Queue()     #instantiate a queue object using python's queue class

    game = Game()        #instantiate the game object

    gui = Gui()    #instantiate the game user interface
    
    QueueHandler()  #instantiate the queue handler    
    
    #start a thread with the main loop of the game
    threading.Thread(target = game.superloop, daemon=True).start()

    #start the GUI's own event loop
    gui.root.mainloop()