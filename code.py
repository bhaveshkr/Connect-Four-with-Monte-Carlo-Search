"""Connect Four computer game with two modes 
   1.AI versus AI
   2.Human versus AI
   Implemented AI Player using Monte Carlo Search 
"""
__author__ = 'Bhavesh Kumar'

import numpy as np
import copy
import random
import pandas as pd


class ModifiedConnectFour:
    '''  # - unplayable cells
        . (dot) - unoccupied don't-count cells
        X - for yellow disk
        O - for blue disk
        small o and small x - occupied don't-count cells
    '''
    def __init__(self):
        self.game_type = None  # 0 - Computer versus Computer, 1 - Human versus Computer
        self.starts_first = None  # 0 - Computer, 1 - Human
        self.current_player = None
        self.grids = None
        self.rows = None
        self.columns = None
        self.ai = MCTS()
        self.last_item_position = []

        # simulation specific to the player wil be used to experiment
        self.experiment = False
        self.player1_simulation = None
        self.player2_simulation = None
        self.csv_row = {}

    def is_valid_board_config(self, columns_height, do_not_count_cells):
        no_of_columns = [x for x in range(6, 12)]  # 6 - 11
        columns_height = columns_height.strip().split(' ')
        do_not_count_cells = do_not_count_cells.split(' ')
        do_not_count_cells_coordinates = []
        columns = len(columns_height)
        rows = int(max(columns_height))

        if columns not in no_of_columns or len(do_not_count_cells) is not 2:
            return False, columns_height, rows, columns

        for cell in do_not_count_cells:
            column, row = cell[0], int(cell[1])
            column_index = Utils.get_index_alphabets(column)
            do_not_count_cells_coordinates.append((row, column_index))
            if (1 > column_index + 1 > rows) or (1 > row > rows):
                return False, columns_height, rows, columns
        return True, columns_height, rows, columns, do_not_count_cells_coordinates

    def play(self, game_type=None, columns_height=None, do_not_count_cells=None):
        # start of this game
        while True:
            try:
                self.game_type = int(input("Please enter game type \n "
                                       "0 - Computer versus Computer \n "
                                       "1 - Human versus Computer\n")) if game_type is None else game_type
                if self.game_type is 0:
                    self.starts_first = 0
                else:
                    self.starts_first = int(input('Who will start first \n 0 - Computer \n 1 - Human\n'))
                self.current_player = self.starts_first
                if columns_height is None:
                    columns_height = input('Please enter the height for each columns separated by single space.\n')
                if do_not_count_cells is None:
                    do_not_count_cells = input('Please enter don''t count cells separated by single space. \n '
                                           'Ex. A2 B3, for column A and row 2 and column and row 3)\n')
                is_board_valid, columns_height, rows, columns, do_not_count_cells_coordinates = \
                    self.is_valid_board_config(columns_height, do_not_count_cells)

                if is_board_valid is not True:
                    print('Invalid board configuration, please try again!')
                    continue
            except ValueError:
                print('Invalid board configuration, please try again!')
                continue
            break
        self.rows, self.columns = rows, columns
        self.grids = [[''] * columns for _ in range(rows)]
        for column_index, row_count in enumerate(columns_height):
            for row_index in range(rows - int(row_count)):
                self.grids[row_index][column_index] = '#'
        for coordinate in do_not_count_cells_coordinates:
            self.grids[rows - coordinate[0]][coordinate[1]] = '.'
        self.grids = np.array(self.grids, dtype=str)
        print('Initial game board')
        Utils.print_grid(self.grids)

        # start playing now
        self.play_next_move()

    def play_next_move(self):
        if self.is_grid_full() is True:
            print('Game is a draw.')
            return
        if self.game_type is 1:
            if self.current_player is 0:
                self.play_computer()
            else:
                self.play_human()
        else:
            self.play_computer()

    def play_computer(self):
        print('AI player {} played'.format(self.current_player))
        best_move = self.ai.get_best_move(self.grids, self)
        self.place_object(best_move)
        Utils.print_grid(self.grids)
        has_won = self.check_winning()
        if has_won:
            print('AI player {} has won the match'.format(self.current_player))
            self.csv_row['won'] = self.current_player
        else:
            self.current_player = 1 if self.current_player == 0 else 0
            self.play_next_move()

    def play_human(self):
        message = 'Please enter a column in alphabets ex. A or B... to play.\n'
        while True:
            play_in_column = input(message)
            column_index = Utils.get_index_alphabets(play_in_column)
            grid = self.place_object(column_index)
            if grid is None:
                print('Selected column is full or out of the board.')
                continue
            break
        Utils.print_grid(self.grids)
        has_won = self.check_winning()
        if has_won:
            print('Human player has won the match')
        else:
            self.current_player = 0
            self.play_next_move()

    def is_legal_move(self, column):
        if self.columns > column >= 0:
            for i in range(self.rows):
                c_val = self.grids[i][column]
                if c_val is not '#' and c_val is not 'X' and c_val is not 'O':
                    return True
        return False

    def is_grid_full(self):
        for row in self.grids:
            for column in range(self.columns):
                if row[column] == '':
                    return False
        return True

    def place_object(self, column_index, grid_val=None, trial=None):
        self.last_item_position = []
        player = 1 if trial is True else self.current_player
        grid = self.grids if grid_val is None else grid_val
        rows, cols = grid.shape
        if column_index >= cols:
            return None
        row = rows
        for g in grid[::-1]:
            row -= 1
            symbol = ''
            if g[column_index] == '':
                symbol = 'X' if player is 0 else 'O'
            elif g[column_index] == '.':
                symbol = 'x' if player is 0 else 'o'
            elif symbol == '':
                continue
            g[column_index] = symbol
            self.last_item_position = [row, column_index]
            return grid
        return None

    def check_winning(self, grid=None, trial=None):
        player = 1 if trial is True else self.current_player
        symbol = 'X' if player is 0 else 'O'
        grid = self.grids if grid is None else grid
        if self.last_item_position == []:
            return None
        row = self.last_item_position[0]
        col = self.last_item_position[1]
        item = self.grids[row][col]
        rows = len(self.grids)
        cols = len(self.grids[0])
        if item is None:
            return False
        for delta_row, delta_col in [(1, 0), (0, 1), (1, 1), (1, -1)]:
            counter = 1
            for delta in (1, -1):
                delta_row *= delta
                delta_col *= delta
                next_row = row + delta_row
                next_col = col + delta_col
                while 0 <= next_row < rows and 0 <= next_col < cols:
                    if grid[next_row][next_col] == symbol:
                        counter += 1
                    else:
                        break
                    if counter == 4:
                        return True
                    next_row += delta_row
                    next_col += delta_col
        return False

    def run_experiment(self):
        self.experiment = True
        self.csv_row = {}
        column_configs = ["7 8 6 7 8 9 8 6", "7 6 6 5 7 6 7 5 7", "7 6 5 8 6 6 6 7", "5 6 7 8 6 7 8 6"]
        do_not_care_points = ["A3 B1", "B2 C3", "D1 D3", "E1 E2"]
        simulations = [80, 150, 500, 2000]
        for index, column_config in enumerate(column_configs):
                for player1 in simulations:
                    for player2 in simulations:
                        for i in range(10):
                            self.player1_simulation = player1
                            self.player2_simulation = player2
                            self.csv_row = {'column_config': column_config,
                                            'do_not_care_points': do_not_care_points,
                                            'player1_simulation': player1,
                                            'player2_simulation': player2}
                            self.play(game_type=0, columns_height=column_config,
                                      do_not_count_cells=do_not_care_points[index])
                            df = pd.DataFrame(self.csv_row)

                            with open('experiment_result.csv', 'a') as f:
                                df.to_csv(f, index=False, header=False)
                            f.close()


class Node:
    def __init__(self, grid, root=None):
        self.root = root
        self.grid = grid
        self.win = 0
        self.play = 0

    def update_win(self):
        self.win += 1

    def update_play(self):
        self.play += 1


class MCTS:
    def __init__(self):
        self.children = []
        self.no_of_simulations = 80
        self.columns = None

    def get_best_move(self, grid, game, trial=True):
        '''
        :param grid: game board
        :param game: instance of ModifiedConnectFour class
        :param trial: True if lookup for opposition is required
        :param simulations: optional param for simulation to run
        :return: modified game board
        '''
        if game.experiment is True:
            self.no_of_simulations = game.player1_simulation if game.current_player == 0 else game.player2_simulation

        moves = len(grid[0])
        self.children = []
        for m in range(moves):
            self.children.append(Node(None))

        for i in range(self.no_of_simulations):
            random_move = random.randrange(moves)
            if not game.is_legal_move(random_move):
                continue
            current_child = self.children[random_move]
            current_state = copy.copy(grid)
            modified_current_state = game.place_object(random_move, current_state, trial)
            won = game.check_winning(modified_current_state, trial)
            if won:
                current_child.update_win()
            current_child.update_play()
        win_ratio_arr = [child.win/child.play if child.win and child.play > 0 else 0.0 for child in self.children]
        best_move = win_ratio_arr.index(max(win_ratio_arr))
        invalid_good_best_move = best_move is 0 and all(v == 0.0 for v in win_ratio_arr)
        if invalid_good_best_move and trial is True:
            return self.get_best_move(grid, game, trial=False)
        elif invalid_good_best_move:
            while True:
                random_move = random.randrange(moves)
                if game.is_legal_move(random_move):
                    best_move = random_move
                    break
        return best_move


class Utils:
    @staticmethod
    def get_index_alphabets(alphabet):
        alphabets = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return alphabets.index(str.upper(alphabet))
    @staticmethod
    def print_grid(grid):
        print('\n'.join([''.join(['{:2}|'.format(item) for item in row]) for row in grid]))


if __name__ == '__main__':
    game = ModifiedConnectFour()
    game.play()

    # run experiment
    # game.run_experiment()
