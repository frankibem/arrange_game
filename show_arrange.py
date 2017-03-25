from graphics import *


class State:

    def __init__(self, init_state):
        self.state = init_state
        self.find_X()
        self.print_state()


    
    def move(self, move):
        X = self.hole_X
        Y = self.hole_Y

        if(move == 'left'):
            tmp = self.state[X][Y+1]
            self.state[X][Y+1] = self.state[X][Y]
            self.state[X][Y] = tmp
            self.hole_Y = Y+1

        elif(move == 'right'):
            tmp = self.state[X][Y-1]
            self.state[X][Y-1] = self.state[X][Y]
            self.state[X][Y] = tmp
            self.hole_Y = Y-1


        elif(move == 'up'):
            tmp = self.state[X+1][Y]
            self.state[X+1][Y] = self.state[X][Y]
            self.state[X][Y] = tmp
            self.hole_X = X+1

        elif(move == 'down'):
            tmp = self.state[X-1][Y]
            self.state[X-1][Y] = self.state[X][Y]
            self.state[X][Y] = tmp
            self.hole_X = X-1
        
        self.print_state()

    def find_X(self):
        state = self.state
        X = 0
        Y = 0
        for i in range(len(state)):
            for j in range(len(state)):
                if(self.state[i][j][0] == 'X'):
                    self.hole_X = i
                    self.hole_Y = j
                    continue
        print('X at: ({}, {})'.format(self.hole_X, self.hole_Y, end=""))


    def print_state(self):
        print('State: ')
        for row in range(len(self.state)):
            print(self.state[row])
        print('\n')



def parse_element(element, State, gui):
    gui.define_state(State.state)
    # gui.draw_board(0)

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
                # print_data(stack, op)
                stack.append(op)
                op = ""

            elif(op == "total_weight("):
                stack.append(op)
                # print_data(stack, op)
                op = ""

        if(ch == ')'):

            # Get Move Data
            if(stack[len(stack)-1] == "move("):
                stack.pop()
                # print_data(stack, op)
                params = op[:len(op)-1].split(",")      #remove last ')' and split into  block and direction
                block = params[0]
                direction = params[1]
                print("Move: " + block + " - " + direction)
                state.move(direction)
                op = ""
                
            # Get occurs data
            elif(stack[len(stack)-1] == "occurs("):
                stack.pop()
                # print_data(stack, op)
                step = op[1:len(op)-1]
                print("Step: " + step)
                op = ""

            # Get Total Weight Data
            elif(stack[len(stack)-1] == "total_weight("):
                stack.pop()
                # print_data(stack, op)
                print("Weight: " + op[0:len(op)-1])
                op = ""


def print_data(stack, op):
        print("Stack: ")
        print(stack)
        print("OP: " + op)


def parseState(file):
    text = file.read().split('\n')
    text = text[:len(text) - 1]

    for elm in range(len(text)):
        text[elm] = text[elm].split(' ')[:len(text)]
    
    print(text)
    return text

class GUI:

    def __init__(self , step):
        self.states = 0
        self.win = GraphWin("Arrange Game", 1240,720)

    def define_state(self,state):
        self.state = state
        # for step in range(step):
        self.draw_board(self.states)
        self.states = self.states+1
        

    def draw_line(self,X1,Y1,X2,Y2):
        line = Line(Point(X1,Y1), Point(X2,Y2))
        line.draw(self.win)

    def draw_text(self,point,text):
        Text(point,text).draw(self.win)


    def draw_border(self,X1,Y1,X2,Y2):
        border = Rectangle(Point(X1,Y1),Point(X2,Y2))
        border.draw(self.win)


    def draw_board(self,steps):
        # Iterate through state steps
        SIZE = len(self.state[0])
        LEVEL = 0

        for step in range(steps + 1):
            board_size = (50 * SIZE)

            if(((board_size + 10) * step) > 1200 * (LEVEL + 1)):
                LEVEL = LEVEL + 1

            top_left_x = (board_size * step + 10) - (1200 * LEVEL)
            top_left_y = 10 + ((board_size + 10) * LEVEL)
            bottom_right_x = board_size + (board_size * step) - (1200 * LEVEL)
            bottom_right_y = (10 + board_size) + ((board_size + 10) * LEVEL)

            for i in range(SIZE):
                #Draw Board Edges
                self.draw_border(top_left_x,top_left_y, bottom_right_x,bottom_right_y)

                #Horizontal Lines
                self.draw_line(top_left_x, top_left_y + (50 * i), bottom_right_x, top_left_y + (50 * i))

                #Vertical Lines
                self.draw_line(top_left_x + (50 * i), 10 + (board_size + 10) * LEVEL,top_left_x + (50 * i),10 + (50 * (SIZE)) + ((board_size + 10) * LEVEL))
            
        for x in range(SIZE):
            for y in range(SIZE):
                self.draw_text(Point((top_left_x+25)+ 50 * x,(top_left_y+25)+50 * y),self.state[y][x])

    
#------- Main --------

file = open('solution.txt','r')

state_file = open('init_state.txt', 'r')

state = State(parseState(state_file))


#Find First Answer Set
lines = file.read().split('\n')

if(lines[3] == "UNSATISFIABLE"):
    print(lines[3])
    exit(-1)

lines = lines[3:len(lines) - 9]          #Remove Generic Clingo Print outs

AS = lines[len(lines)-2:len(lines)-1][0].split(" ")     #Get Last answer set into list['Answer: #', Answer Set, 'Optimization: #']
#print(lines)
#print(AS)

steps = len(AS) -1

gui = GUI(steps)

# Parse each element in the answer set
for element in AS:
    parse_element(element, state, gui)
gui.win.getMouse()






