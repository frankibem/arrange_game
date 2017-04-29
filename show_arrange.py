from graphics import *
import time


class State:

    def __init__(self):
        self.state = []  # init_state
        self.hole_X = None
        self.hole_Y = None
        self.weight = 0

    def load(self, file):
        text = file.read().split('\n')
        text = text[:len(text) - 1]

        for elm in range(len(text)):
            text[elm] = text[elm].split(' ')[:len(text)]

        print(text)
        self.state.append(text)
        self.find_X()
        self.print_state()
        return text

    def move(self, move):
        X = self.hole_X
        Y = self.hole_Y
        
        loc_N = self.find_N(move[0])        #Find number to move to hole


        # Make the move
        tmp = self.state[len(self.state) - 1][X][Y]
        self.state[len(self.state) - 1][X][Y] = self.state[len(self.state) - 1][loc_N[0]][loc_N[1]]
        self.state[len(self.state) - 1][loc_N[0]][loc_N[1]] = tmp
        self.hole_X = loc_N[0]
        self.hole_Y = loc_N[1]  


        self.weight = self.weight + int(self.state[len(self.state) - 1][X][Y][-2])

        self.print_state()


    def find_X(self):
        state = self.state[len(self.state) - 1]
        X = 0
        Y = 0
        for i in range(len(state)):
            for j in range(len(state)):
                if(self.state[len(self.state) - 1][i][j][0] == 'X'):
                    self.hole_X = i
                    self.hole_Y = j
                    continue
        print('X at: ({}, {})'.format(self.hole_X, self.hole_Y, end=""))


    def find_N(self, N):
        state = self.state[len(self.state) - 1]
        X = 0
        Y = 0
        for i in range(len(state)):
            for j in range(len(state)):
                if(self.state[len(self.state) - 1][i][j][0] == N):
                    X = i
                    Y = j
                    continue
        # print('X at: ({}, {})'.format(self.hole_X, self.hole_Y, end=""))
        return (X,Y)


    def print_state(self):
        print('State: ')
        for row in range(len(self.state[len(self.state) - 1])):
            print(self.state[len(self.state) - 1][row])
        print('\n')


def parse_element(element, State):

    print("Parsing Atom: " + element)
    stack = []
    op = ""
    for ch in element:
        op = op + ch
        if(ch == '('):
            if(op == "occurs("):
                # print_data(stack, op)
                stack.append(op)
                op = ""

            elif(op == "move("):
                stack.append(op)
                stack.append("loc(")
                op = ""

            elif(op == "total_weight("):
                stack.append(op)
                # print_data(stack, op)
                op = ""

        if(ch == ')'):

            # Get Move Data
            if(stack[len(stack) - 1] == "loc("):
                stack.pop()
                # print_data(stack, op)
                # remove last ')' and split into  block and location
                params = op[:len(op) - 1].split(",")
                block = params[0]
                location = (params[1],params[2])
                print("Move: " + block + " - " + location[0]+','+location[1]+ ')')
                State.move(block +','+location[0]+','+location[1]+ ')')     #loc(X,Y)
                op = ""

            # Get occurs data
            elif(stack[len(stack) - 1] == "occurs("):
                stack.pop()
                # print_data(stack, op)
                print("operation: ", op)
                step = len(State.state)
                print("Step: " + str(step))
                op = ""

            # Get Total Weight Data
            elif(stack[len(stack) - 1] == "total_weight("):
                stack.pop()
                # print_data(stack, op)
                print("Weight: " + op[0:len(op) - 1])
                op = ""


class GUI:

    def __init__(self, step):
        self.states = 0
        self.win = GraphWin("Arrange Game", 1240, 720)

    # Set State and Print
    def define_state(self, state):
        self.state = state
        self.draw_board(self.states)
        self.states = self.states + 1

    def draw_line(self, X1, Y1, X2, Y2):
        line = Line(Point(X1, Y1), Point(X2, Y2))
        line.draw(self.win)

    def draw_text(self, point, text):
        block = Text(point, text)
        if(text[0] == 'X'):
            block.setTextColor("red")
        block.draw(self.win)

    def draw_border(self, X1, Y1, X2, Y2):
        border = Rectangle(Point(X1, Y1), Point(X2, Y2))
        border.setWidth(3)
        border.draw(self.win)


    def draw_total_weight(self,weight):
        text = Text(Point(620,20), "Total Weight: " + weight)
        text.setSize(24)
        text.draw(self.win)

    def draw_board(self, steps):
        # Constants
        SIZE = len(self.state[0])
        LEVEL = 0
        edge = 10
        cell_size = 50
        board_size = (cell_size * SIZE)

        # animate
        time.sleep(.5)

        # Iterate through state steps
        for step in range(steps + 1):
            # Move down one Board Size when no more step boards fit on screen
            if(((board_size + edge) * step) > 1200 * (LEVEL + 1)):
                LEVEL = LEVEL + 1

            # Point References
            top_left_x = (board_size * step + edge) - (1200 * LEVEL)
            top_left_y = edge + ((board_size + edge) * LEVEL)
            bottom_right_x = board_size + (board_size * step) - (1200 * LEVEL)
            bottom_right_y = (edge + board_size) + \
                ((board_size + edge) * LEVEL)

            #Upper bound for weight
            top_left_y = top_left_y + 50
            bottom_right_y = bottom_right_y + 50

            for i in range(SIZE):
                # Draw Board Edges
                self.draw_border(top_left_x, top_left_y,
                                 bottom_right_x, bottom_right_y)

                # Horizontal Lines
                self.draw_line(top_left_x, top_left_y + (cell_size * i),
                               bottom_right_x, top_left_y + (cell_size * i))

                # Vertical Lines
                self.draw_line(top_left_x + (cell_size * i), edge + (board_size + edge) * LEVEL + 50, top_left_x + (
                    cell_size * i), edge + (cell_size * (SIZE)) + ((board_size + edge) * LEVEL) + 50)

        # Print Text
        for x in range(SIZE):
            for y in range(SIZE):
                self.draw_text(Point((top_left_x + 25) + cell_size * x,
                                     (top_left_y + 25) + cell_size * y), self.state[y][x])


def main():
    with open('out/solution.txt', 'r') as sol:
        with open('out/initial_state.txt', 'r') as init_state:
            state = State()
            state.load(init_state)

            # Find First Answer Set
            lines = sol.read().split('\n')

            if(lines[3] == "UNSATISFIABLE"):
                print(lines[3])
                exit(-1)

            lines = lines[3:len(lines) - 9]  # Remove Generic Clingo Print outs

            # Get Last answer set into list['Answer: #', Answer Set,
            # 'Optimization: #']
            AS = lines[len(lines) - 2:len(lines) - 1][0].split(" ")

            # Number of Steps to Solution
            steps = len(AS) - 1

            # Initialize GUI
            gui = GUI(steps)

            # Parse each element in the answer set
            for element in range(len(AS)):
                # Feed state to GUI
                gui.define_state(state.state[len(state.state) - 1])

                # Parse Actions
                parse_element(AS[element], state)

            #Draw total weight
            gui.draw_total_weight(str(state.weight))

            # Handle Closing
            try:
                gui.win.getMouse()
            except KeyboardInterrupt as err:
                sys.exit(0)


main()
