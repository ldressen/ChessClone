import os

import numpy as np
import pygame as p
from Piece import Piece


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
            [Piece("b", "R"), Piece("b", "N"), Piece("b", "B"), Piece("b", "Q"), Piece("b", "K"), Piece("b", "B"),
             Piece("b", "N"), Piece("b", "R")],
            [Piece("b", "P"), Piece("b", "P"), Piece("b", "P"), Piece("b", "P"), Piece("b", "P"), Piece("b", "P"),
             Piece("b", "P"), Piece("b", "P")],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            ["-", "-", "-", "-", "-", "-", "-", "-"],
            [Piece("w", "P"), Piece("w", "P"), Piece("w", "P"), Piece("w", "P"), Piece("w", "P"), Piece("w", "P"),
             Piece("w", "P"), Piece("w", "P")],
            [Piece("w", "R"), Piece("w", "N"), Piece("w", "B"), Piece("w", "Q"), Piece("w", "K"), Piece("w", "B"),
             Piece("w", "N"), Piece("w", "R")]
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
                if piece != "-" and isinstance(piece, Piece):
                    self.screen.blit(self.images[piece.get_image_name()],
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
        if tile2 == "short_castle":
            self.short_castle(tile1)
            return
        if tile2 == "long_castle":
            self.long_castle(tile1)
            return

        piece = self.board[tile1[1], tile1[0]]
        self.board[tile2[1], tile2[0]] = piece
        self.board[tile1[1], tile1[0]] = "-"
        self.update_board()
        self.moveLog.append((tile1, tile2))
        self.current_move += 1
        self.undo_idx += 1
        # print(self.current_move)
        # print(self.moveLog)

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
        piece: Piece = self.board[tile[1], tile[0]]

        # white pawns
        if piece.get_image_name() == "wP" and self.board[tile[1] - 1, tile[0]] == "-":
            if tile[1] == 6 and self.board[tile[1] - 2, tile[0]] == "-":
                return [(tile[0], tile[1] - 1), (tile[0], tile[1] - 2)]
            else:
                return [(tile[0], tile[1] - 1)]

        # black pawns
        if piece.get_image_name() == "bP" and self.board[tile[1] + 1, tile[0]] == "-":
            if tile[1] == 1 and self.board[tile[1] + 2, tile[0]] == "-":
                return [(tile[0], tile[1] + 1), (tile[0], tile[1] + 2)]
            else:
                return [(tile[0], tile[1] + 1)]

        # rooks
        if piece.typ == "R":
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

        # bishops
        if piece.typ == "B":
            moves = []
            # check left right diagonal
            moves.extend(self.check_upper_left_right_diagonal(tile))
            moves.extend(self.check_lower_left_right_diagonal(tile))
            # check right left diagonal
            moves.extend(self.check_upper_right_left_diagonal(tile))
            moves.extend(self.check_lower_right_left_diagonal(tile))

            return moves

        # queens
        if piece.typ == "Q":
            moves = []
            # check left right diagonal
            moves.extend(self.check_upper_left_right_diagonal(tile))
            moves.extend(self.check_lower_left_right_diagonal(tile))
            # check right left diagonal
            moves.extend(self.check_upper_right_left_diagonal(tile))
            moves.extend(self.check_lower_right_left_diagonal(tile))
            # upwards
            moves.extend(self.check_above_line(tile))
            # downwards
            moves.extend(self.check_below_line(tile))
            # right
            moves.extend(self.check_right_line(tile))
            # left
            moves.extend(self.check_left_line(tile))
            return moves

        # kings
        if piece.typ == "K":
            return self.check_king_moves(tile)

        # knights
        if piece.typ == "N":
            return self.check_knight_moves(tile)

    def draw_capture_rect(self, tile):
        p.draw.rect(self.screen, color=p.Color((211, 211, 211)), rect=p.Rect(tile[0] * self.square_size + 0.1 * self.square_size,
                                                                             tile[1] * self.square_size + 0.1 * self.square_size,
                                                                             self.square_size * 0.8,
                                                                             self.square_size * 0.8), width=3,
                    border_radius=1)

    def draw_move_preview(self, tile_list):
        """
        Draws the circles to indicate possible moves.
        :param tile_list: tuple
        """
        if tile_list is None:
            return
        for tile in tile_list:

            if tile != "short_castle" and tile != "long_castle":
                if self.board[tile[1], tile[0]] == "-":
                    p.draw.circle(self.screen, p.Color((211, 211, 211)), (
                        tile[0] * self.square_size + self.square_size / 2,
                        tile[1] * self.square_size + self.square_size / 2),
                                  self.square_size / 3)
                else:
                    self.draw_capture_rect(tile)
            elif tile == "short_castle":
                if self.whites_turn:
                    self.draw_capture_rect((7, 7))
                else:
                    self.draw_capture_rect((7, 0))

            elif tile == "long_castle":
                if self.whites_turn:
                    self.draw_capture_rect((0, 7))
                else:
                    self.draw_capture_rect((0, 0))

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

    def check_upper_left_right_diagonal(self, tile):
        moves = []
        x, y = tile[0] - 1, tile[1] - 1
        while x >= 0 and y >= 0 and self.board[y, x] == "-":
            moves.append((x, y))
            x -= 1
            y -= 1

        return moves

    def check_lower_left_right_diagonal(self, tile):
        moves = []
        x, y = tile[0] + 1, tile[1] + 1
        while x <= 7 and y <= 7 and self.board[y, x] == "-":
            moves.append((x, y))
            x += 1
            y += 1

        return moves

    def check_upper_right_left_diagonal(self, tile):
        moves = []
        x, y = tile[0] + 1, tile[1] - 1
        while x <= 7 and y >= 0 and self.board[y, x] == "-":
            moves.append((x, y))
            x += 1
            y -= 1

        return moves

    def check_lower_right_left_diagonal(self, tile):
        moves = []
        x, y = tile[0] - 1, tile[1] + 1
        while x >= 0 and y <= 7 and self.board[y, x] == "-":
            moves.append((x, y))
            x -= 1
            y += 1

        return moves

    def check_king_moves(self, tile):
        moves = []
        x_start = tile[0]
        y_start = tile[1]

        for x in range(x_start - 1, x_start + 2):
            for y in range(y_start - 1, y_start + 2):
                if 0 <= x < 8 and 0 <= y < 8 and self.board[y, x] == "-":
                    moves.append((x, y))

        if self.check_short_castle():
            moves.append("short_castle")

        if self.check_long_castle():
            moves.append("long_castle")

        print(moves)

        return moves

    def check_short_castle(self):
        white_king_moved = False
        black_king_moved = False
        for move in self.moveLog:
            if (4, 7) == move[0]:
                white_king_moved = True
            elif (4, 0) == move[0]:
                black_king_moved = True
        if not white_king_moved and self.board[7, 5] == "-" and self.board[
            7, 6] == "-" and isinstance(self.board[7, 7], Piece) and self.board[7, 7].get_image_name() == "wR":
            return True
        elif not black_king_moved and self.board[0, 5] == "-" and self.board[
            0, 6] == "-" and isinstance(self.board[0, 7], Piece) and self.board[0, 7].get_image_name() == "bR":
            return True

        return False

    def check_long_castle(self):

        white_king_moved = False
        black_king_moved = False
        for move in self.moveLog:
            if (4, 7) == move[0]:
                white_king_moved = True
            elif (4, 0) == move[0]:
                black_king_moved = True
        if not white_king_moved and self.board[7, 3] == "-" and self.board[
            7, 2] == "-" and self.board[7, 1] == "-" and isinstance(self.board[7, 0], Piece) and self.board[7, 0].get_image_name() == "wR":
            return True
        elif not black_king_moved and self.board[0, 3] == "-" and self.board[
            0, 2] == "-" and self.board[0, 1] == "-" and isinstance(self.board[0, 0], Piece) and self.board[0, 0].get_image_name() == "bR":
            return True

        return False

    def short_castle(self, tile):
        x_start = tile[0]
        y_start = tile[1]
        if self.whites_turn:
            self.move_piece(tile, (tile[0] + 2, tile[1]))
            self.move_piece((tile[0] + 3, tile[1]), (tile[0] + 1, tile[1]))
            self.update_board()
        else:
            self.move_piece(tile, (tile[0] + 2, tile[1]))
            self.move_piece((tile[0] + 3, tile[1]), (tile[0] + 1, tile[1]))
            self.update_board()

    def long_castle(self, tile):
        x_start = tile[0]
        y_start = tile[1]
        if self.whites_turn:
            self.move_piece(tile, (tile[0] - 2, tile[1]))
            self.move_piece((tile[0] - 4, tile[1]), (tile[0] - 1, tile[1]))
            self.update_board()
        else:
            self.move_piece(tile, (tile[0] - 2, tile[1]))
            self.move_piece((tile[0] - 4, tile[1]), (tile[0] - 1, tile[1]))
            self.update_board()

    def check_knight_moves(self, tile):
        moves = []
        x = tile[0]
        y = tile[1]
        # above right
        if 0 <= x + 1 < 8 and 0 <= y - 2 < 8 and self.board[y - 2, x + 1] == "-":
            moves.append((x + 1, y - 2))
        # above left
        if 0 <= x - 1 < 8 and 0 <= y - 2 < 8 and self.board[y - 2, x - 1] == "-":
            moves.append((x - 1, y - 2))
        # below right
        if 0 <= x + 1 < 8 and 0 <= y + 2 < 8 and self.board[y + 2, x + 1] == "-":
            moves.append((x + 1, y + 2))
        # below left
        if 0 <= x - 1 < 8 and 0 <= y + 2 < 8 and self.board[y + 2, x - 1] == "-":
            moves.append((x - 1, y + 2))
        # right above
        if 0 <= x + 2 < 8 and 0 <= y - 1 < 8 and self.board[y - 1, x + 2] == "-":
            moves.append((x + 2, y - 1))
        # right below
        if 0 <= x + 2 < 8 and 0 <= y + 1 < 8 and self.board[y + 1, x + 2] == "-":
            moves.append((x + 2, y + 1))
        # left above
        if 0 <= x - 2 < 8 and 0 <= y - 1 < 8 and self.board[y - 1, x - 2] == "-":
            moves.append((x - 2, y - 1))
        # left below
        if 0 <= x - 2 < 8 and 0 <= y + 1 < 8 and self.board[y + 1, x - 2] == "-":
            moves.append((x - 2, y + 1))

        return moves
