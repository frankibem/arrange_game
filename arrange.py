import os
import random
import subprocess
import argparse

TEMPLATE_FILE = "template.txt"  # contains non dynamic parts of problem (in ASP)
GEN_FILE = 'generated.lp'  # Generated ASP program goes here
SOLN_FILE = 'solution.txt'  # Clingo solution to logic program in GEN_FILE goes here
STATE_FILE = "initial_state.txt"  # Initial configuration is stored here
OUT_DIR = "out"  # Output files go here

# Placeholder for empty cell
HOLE = -1

# Directions of motion (of the hole)
LEFT = 'left'
RIGHT = 'right'
UP = 'up'
DOWN = 'down'
MOVES = [LEFT, RIGHT, UP, DOWN]

# Arrange Game Settings
STEPS = 15
SIZE = 4
MIN_MOVE = 15
MAX_MOVE = 25


class Arrange:
    """
    Environment that represents the 'Arrange Game'
    """

    def __init__(self, size=2, min_weight=1, max_weight=5, steps=STEPS):
        """
        Creates a new game\n
        :param size: Dimension of game will be (size x size). Must be >= 2\n
        :param min_weight: The minimum weight of a cell\n
        :param max_weight: The maximum weight of a cell
        """

        if size < 2:
            raise ValueError('The size of the board cannot be less than 2')

        self.size = size
        self.min_weight = min_weight
        self.max_weight = max_weight
        self.steps = steps
        self.cells = []
        self.weights = dict()
        self.hole_index = -1

        # Create initial configuration
        self.reset()
        self.__setup()

    def __valid_moves(self):
        """
        :return: A list of moves that can be taken in the current configuration
        """
        result = []

        # 0-based coordinates of hole
        y = self.hole_index // self.size
        x = self.hole_index - (y * self.size)

        if x > 0:
            result.append(LEFT)
        if x < (self.size - 1):
            result.append(RIGHT)
        if y > 0:
            result.append(UP)
        if y < (self.size - 1):
            result.append(DOWN)

        return result

    def reset(self):
        """
        Generates a new configuration of the arrange game with randomly
        assigned cells and weights
        """

        # End configuration of board
        self.cells = [x for x in range(1, self.size * self.size)]
        self.cells.append(HOLE)
        self.hole_index = (self.size * self.size) - 1

        self.weights = dict()
        for c in self.cells:
            if c == HOLE:
                self.weights[HOLE] = 0
                continue
            self.weights[c] = random.randint(self.min_weight, self.max_weight)

        # Shuffle board by taking random initial moves
        move_count = random.randint(MIN_MOVE, MAX_MOVE)
        for i in range(move_count):
            valid_moves = self.__valid_moves()
            direction = random.choice(valid_moves)
            self.move(direction)

    def move(self, direction):
        """
        Moves the hole in the given direction
        :param direction: The direction to move the hole in
        """

        if direction not in MOVES:
            raise ValueError("{} is not a valid direction".format(direction))
        if direction not in self.__valid_moves():
            raise ValueError("Moving {} is not possible in the current configuration".format(direction))

        if direction == LEFT:
            new_loc = self.hole_index - 1
        elif direction == RIGHT:
            new_loc = self.hole_index + 1
        elif direction == UP:
            new_loc = self.hole_index - self.size
        else:
            new_loc = self.hole_index + self.size

        # Swap hole and block
        self.cells[new_loc], self.cells[self.hole_index] = HOLE, self.cells[new_loc]

        # Update hole location
        self.hole_index = new_loc

    def pretty_print(self):
        """
        Display the current configuration for debugging
        """

        for i in range(self.size):
            for j in range(self.size):
                c = self.cells[i * self.size + j]
                print('{}({})   '.format(('X' if c == HOLE else c), self.weights[c]), end='')
            print()
        print('\n')

    def write_state(self):
        with open(os.path.join(OUT_DIR, STATE_FILE), 'w') as ofile:
            for i in range(self.size):
                for j in range(self.size):
                    c = self.cells[i * self.size + j]
                    ofile.write('{}({}) '.format(('X' if c == HOLE else c), self.weights[c]))
                ofile.write('\n')

    def write_asp(self):
        """
        Writes the rules to solve the current game using ASP (clingo)
        :param fname: The name of the output file
        """
        file_path = os.path.join(OUT_DIR, GEN_FILE)
        print('Writing ASP program to {}...'.format(file_path))

        with open(file_path, 'w') as ofile:
            # Write constants
            ofile.write('#const n = {}.\n'.format(self.steps))
            ofile.write('#const board_size = {}.\n\n'.format(self.size))

            # Write assigned weights
            ofile.write('% Assigned weights\n')
            for c in self.cells:
                if c == HOLE:
                    continue

                weight = self.weights[c]
                item = str(c)
                ofile.write('weight({}, {}). '.format(item, weight))
            ofile.write('\n\n')

            # Write initial block configuration
            ofile.write('% Initial cell configuration\n')
            for y in range(self.size):
                for x in range(self.size):
                    c = self.cells[y * self.size + x]
                    item = 'hole' if c == HOLE else str(c)
                    ofile.write('holds(on({}, loc({},{})), 0).\n'.format(item, x, y))

            # Write goal
            last = (self.size * self.size) - 1
            ofile.write('\n% Desired goal\n')
            ofile.write('goal(I) :- ')
            for y in range(self.size):
                for x in range(self.size):
                    c = y * self.size + x
                    if c == last:
                        break

                    item = str(c + 1)
                    ofile.write('holds(on({}, loc({}, {})), I), '.format(item, x, y))
            ofile.write('holds(on(hole, loc({}, {})), I).\n\n'.format(self.size - 1, self.size - 1))

            # Write cell adjacency information
            for y in range(0, self.size):
                for x in range(0, self.size):
                    if (x + 1) < self.size:
                        ofile.write(
                            'adjacent(loc({}, {}), loc({}, {})).\n'.format(x, y, x + 1, y))
                    if (y + 1) < self.size:
                        ofile.write(
                            'adjacent(loc({}, {}), loc({}, {})).\n'.format(x, y, x, y + 1))
            ofile.write('\n')

            # Write out rest of program logic
            with open(TEMPLATE_FILE, 'r') as ifile:
                for line in ifile:
                    ofile.write(line)
        print('Done.')

    def solve(self, clingo_path):
        in_fname = os.path.join(OUT_DIR, GEN_FILE)
        soln_fname = os.path.join(OUT_DIR, SOLN_FILE)
        print("Solving ASP program in {} and writing to {}...".format(in_fname, soln_fname))

        commands = [clingo_path, in_fname]
        with open(soln_fname, 'w') as ofile:
            subprocess.run(commands, stdout=ofile)

        print('Done.')

    def __setup(self):
        """
        Creates and cleans the output directory (if necessary)
        """
        os.makedirs(OUT_DIR, exist_ok=True)
        [os.remove(os.path.join(OUT_DIR, f)) for f in os.listdir(OUT_DIR)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('clingo_path', help='The path to the clingo solver')
    parser.add_argument('-s', '--size', type=int, default=SIZE, help='The board dimensions will be (size x size)')
    parser.add_argument('-n', '--time_steps', type=int, default=STEPS,
                        help='The max number of steps for the clingo to solve it in')
    parser.add_argument('--min', type=int, default=MIN_MOVE, help='Minimum number of initial random moves')
    parser.add_argument('--max', type=int, default=MAX_MOVE, help='Maximum number of initial random moves')
    args = parser.parse_args()

    clingo = args.clingo_path
    STEPS = args.time_steps
    SIZE = args.size
    MIN_MOVE = args.min
    MAX_MOVE = args.max

    game = Arrange(SIZE)
    game.write_state()
    game.write_asp()
    game.solve(clingo)
