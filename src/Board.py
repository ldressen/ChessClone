import os

import numpy as np
import pygame as p


class Board:
    DIMENSION = 8
    square_size = 0

    def __init__(self, size, screen):
        self.screen = screen
        self.square_size = size / self.DIMENSION
        self.moveLog = []
        self.current_move = 0
        self.undo_idx = 0
        self.is_log = False
        self.move_log_index = 0
        self.whites_turn = True
        self.images = {}
        self.board = np.array([
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ])
        self.load_images()
        self.draw_board()
        self.draw_pieces()

    def load_images(self):
        """
        Loads the images for the pieces and stores it in dictionairy.
        """
        path = "../res/pieces/"
        for piece in sorted(os.listdir(path)):
            self.images[piece.replace(".png", "")] = p.image.load(path + piece)

    def draw_board(self):
        """
        Draws the basic 8x8 chessboard layout.
        """
        colors = [p.Color("White"), p.Color("gray")]
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                color = colors[(row + col) % 2]
                p.draw.rect(self.screen, color,
                            p.Rect(col * self.square_size, row * self.square_size, self.square_size, self.square_size))

    def draw_pieces(self):
        """
        Draws the pieces on their current position.
        """
        for row in range(self.DIMENSION):
            for col in range(self.DIMENSION):
                piece = self.board[row, col]
                if piece != "-":
                    self.screen.blit(self.images[piece],
                                     p.Rect(col * self.square_size, row * self.square_size, self.square_size,
                                            self.square_size))

    def get_tile_from_pixel_coords(self, pos: tuple):
        """
        Convert pixel coordinates into corresponding tile that was clicked on.
        :param pos: tuple
        :return: x_tile, ytile: tuple
        """
        x_tile: int = int(pos[0] // self.square_size)
        y_tile: int = int(pos[1] // self.square_size)

        return x_tile, y_tile

    def clicked_on_tile(self, tile: tuple):
        """
        Highlights the tile the player clicked on when a piece is there.
        :param tile: tuple
        """
        p.draw.rect(self.screen, p.Color(211, 211, 211),
                    p.Rect(tile[0] * self.square_size, tile[1] * self.square_size, self.square_size,
                           self.square_size))
        self.draw_pieces()

    def update_board(self):
        """
        Updates the board and the pieces.
        """
        self.draw_board()
        self.draw_pieces()

    def move_piece(self, tile1, tile2):
        """
        Moves piece from one tile to another.
        :param tile1: tuple
        :param tile2: tuple
        """
        piece = self.board[tile1[1], tile1[0]]
        self.board[tile2[1], tile2[0]] = piece
        self.board[tile1[1], tile1[0]] = "-"
        self.update_board()
        self.moveLog.append((tile1, tile2))
        self.current_move += 1
        self.undo_idx += 1
        print(self.current_move)
        print(self.moveLog)

    def move_piece_index_back(self, idx):
        """
        Makes the move of a piece backwards.
        :param idx: int
        """
        move = self.moveLog[idx]
        tile1 = move[0]
        tile2 = move[1]
        piece = self.board[tile2[1], tile2[0]]
        self.board[tile1[1], tile1[0]] = piece
        self.board[tile2[1], tile2[0]] = "-"
        self.undo_idx -= 1
        print(self.undo_idx)
        self.update_board()

    def move_piece_index_forward(self, idx):
        """
        Makes the move of a piece forward.
        :param idx: int
        """
        move = self.moveLog[idx - 1]
        tile1 = move[0]
        tile2 = move[1]
        piece = self.board[tile1[1], tile1[0]]
        self.board[tile2[1], tile2[0]] = piece
        self.board[tile1[1], tile1[0]] = "-"
        self.undo_idx += 1
        self.update_board()

    def can_move(self):
        if self.current_move == self.undo_idx:
            return True
        return False

    def undo_move(self):
        """
        Undos move and displays the move before.
        """
        if len(self.moveLog) > 0 and self.undo_idx > 0:
            self.move_piece_index_back(self.undo_idx - 1)

    def move_forward(self):
        """
        Displays next move that was played.
        """
        if len(self.moveLog) > 0 and self.undo_idx < self.current_move:
            self.move_piece_index_forward(self.undo_idx + 1)

    def get_all_possible_moves(self, tile):
        """
        Returns all move a particular piece can perform on a certain tile.
        :param tile: tuple
        :return: list(tuple)
        """
        if self.board[tile[1], tile[0]] == "-":
            return 0

        # white pawns
        if self.board[tile[1], tile[0]] == "wP" and self.board[tile[1] - 1, tile[0]] == "-":
            if tile[1] == 6 and self.board[tile[1] - 2, tile[0]] == "-":
                return [(tile[0], tile[1] - 1), (tile[0], tile[1] - 2)]
            else:
                return [(tile[0], tile[1] - 1)]

        # black pawns
        if self.board[tile[1], tile[0]] == "bP" and self.board[tile[1] + 1, tile[0]] == "-":
            if tile[1] == 1 and self.board[tile[1] + 2, tile[0]] == "-":
                return [(tile[0], tile[1] + 1), (tile[0], tile[1] + 2)]
            else:
                return [(tile[0], tile[1] + 1)]

        # rooks
        if self.board[tile[1], tile[0]] == "wR" or self.board[tile[1], tile[0]] == "bR":
            moves = []
            # upwards
            moves.extend(self.check_above_line(tile))
            # downwards
            moves.extend(self.check_below_line(tile))
            # right
            moves.extend(self.check_right_line(tile))
            # left
            moves.extend(self.check_left_line(tile))

            return moves

    def draw_move_preview(self, tile_list):
        """
        Draws the circles to indicate possible moves.
        :param tile: tuple
        """
        for tile in tile_list:
            p.draw.circle(self.screen, p.Color((211, 211, 211)), (
                tile[0] * self.square_size + self.square_size / 2, tile[1] * self.square_size + self.square_size / 2),
                          self.square_size / 3)

    # all methods that check possible moves in a particular shape
    def check_above_line(self, tile):
        moves = []
        for y_up in range(tile[1] - 1, -1, -1):  # all moves above the rook
            if self.board[y_up, tile[0]] == "-":
                moves.append((tile[0], y_up))
            else:
                break
        return moves

    def check_below_line(self, tile):
        moves = []
        for y_down in range(tile[1] + 1, 8, 1):  # all moves below the rook
            if self.board[y_down, tile[0]] == "-":
                moves.append((tile[0], y_down))
            else:
                break
        return moves

    def check_right_line(self, tile):
        moves = []
        for x_right in range(tile[0] + 1, 8, 1):  # all moves to the right of the rook
            if self.board[tile[1], x_right] == "-":
                moves.append((x_right, tile[1]))
            else:
                break
        return moves

    def check_left_line(self, tile):
        moves = []
        for x_left in range(tile[0] - 1, -1, -1):  # all moves to the right of the rook
            if self.board[tile[1], x_left] == "-":
                moves.append((x_left, tile[1]))
            else:
                break
        return moves
