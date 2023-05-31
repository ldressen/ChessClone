import os

import numpy as np
import pygame as p
from Piece import Piece


class Board:
    DIMENSION = 8
    square_size = 0

    def __init__(self, size, screen):
        self.screen = screen
        self.checks = []
        self.square_size = size / self.DIMENSION
        self.moveLog = []
        self.current_move = 0
        self.undo_idx = 0
        self.is_log = False
        self.move_log_index = 0
        self.whites_turn = True
        self.images = {}
        self.in_check = False
        self.sound_on = True
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
        p.init()
        self.check_sound = p.mixer.Sound("../res/sounds/laser1.wav")
        self.take_sound = p.mixer.Sound("../res/sounds/big-impact-7054.wav")
        self.move_sound = p.mixer.Sound("../res/sounds/jumpland.wav")
        self.checkmate_sound = p.mixer.Sound("../res/sounds/SUIII.wav")
        self.check_sound.set_volume(0.25)
        self.take_sound.set_volume(0.25)
        self.move_sound.set_volume(0.25)
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
        if self.in_check:
            self.draw_capture_rect(self.checks[0][1], color=p.Color("red"))

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
        if isinstance(self.board[tile2[1], tile2[0]], Piece) and self.sound_on:
            p.mixer.Sound.play(self.take_sound)
        elif self.sound_on:
            p.mixer.Sound.play(self.move_sound)
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

        if piece.typ == "P":
            return self.check_pawn_moves(tile)

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

    def draw_capture_rect(self, tile, color=p.Color((211, 211, 211))):
        p.draw.rect(self.screen, color=color,
                    rect=p.Rect(tile[0] * self.square_size + 0.1 * self.square_size,
                                tile[1] * self.square_size + 0.1 * self.square_size,
                                self.square_size * 0.8,
                                self.square_size * 0.8), width=3,
                    border_radius=1)

    def draw_move_preview(self, tile_list):
        """
        Draws the circles to indicate possible moves.
        :param tile_list: tuple
        """
        if tile_list is None or len(tile_list) == 0:
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
        og_piece: Piece = self.board[tile[1], tile[0]]
        for y_up in range(tile[1] - 1, -1, -1):  # all moves above the rook
            piece = self.board[y_up, tile[0]]
            if piece == "-":
                moves.append((tile[0], y_up))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (tile[0], y_up)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((tile[0], y_up))
                break
            else:
                break
        return moves

    def check_below_line(self, tile):
        moves = []
        og_piece: Piece = self.board[tile[1], tile[0]]
        for y_down in range(tile[1] + 1, 8, 1):  # all moves below the rook
            piece = self.board[y_down, tile[0]]
            if piece == "-":
                moves.append((tile[0], y_down))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (tile[0], y_down)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((tile[0], y_down))
                break
            else:
                break
        return moves

    def check_right_line(self, tile):
        moves = []
        og_piece: Piece = self.board[tile[1], tile[0]]
        for x_right in range(tile[0] + 1, 8, 1):  # all moves to the right of the rook
            piece = self.board[tile[1], x_right]
            if piece == "-":
                moves.append((x_right, tile[1]))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x_right, tile[1])))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x_right, tile[1]))
                break
            else:
                break
        return moves

    def check_left_line(self, tile):
        moves = []
        og_piece: Piece = self.board[tile[1], tile[0]]
        for x_left in range(tile[0] - 1, -1, -1):  # all moves to the right of the rook
            piece = self.board[tile[1], x_left]
            if piece == "-":
                moves.append((x_left, tile[1]))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x_left, tile[1])))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x_left, tile[1]))
                break
            else:
                break
        return moves

    def check_upper_left_right_diagonal(self, tile):
        moves = []
        x, y = tile[0] - 1, tile[1] - 1
        og_piece = self.board[tile[1], tile[0]]
        while x >= 0 and y >= 0:
            piece = self.board[y, x]
            if piece == "-":
                moves.append((x, y))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x, y)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x, y))
                break
            x -= 1
            y -= 1

        return moves

    def check_lower_left_right_diagonal(self, tile):
        moves = []
        x, y = tile[0] + 1, tile[1] + 1
        og_piece = self.board[tile[1], tile[0]]
        while x <= 7 and y <= 7:
            piece = self.board[y, x]
            if piece == "-":
                moves.append((x, y))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x, y)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x, y))
                break
            x += 1
            y += 1

        return moves

    def check_upper_right_left_diagonal(self, tile):
        moves = []
        x, y = tile[0] + 1, tile[1] - 1
        og_piece = self.board[tile[1], tile[0]]
        while x <= 7 and y >= 0:
            piece = self.board[y, x]
            if piece == "-":
                moves.append((x, y))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x, y)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x, y))
                break
            x += 1
            y -= 1

        return moves

    def check_lower_right_left_diagonal(self, tile):
        moves = []
        x, y = tile[0] - 1, tile[1] + 1
        og_piece = self.board[tile[1], tile[0]]
        while x >= 0 and y <= 7:
            piece = self.board[y, x]
            if piece == "-":
                moves.append((x, y))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x, y)))
                    break
                elif (not piece.is_white() and og_piece.is_white()) or (piece.is_white() and not og_piece.is_white()):
                    moves.append((x, y))
                break
            x -= 1
            y += 1

        return moves

    def check_king_moves(self, tile):
        moves = []
        x_start = tile[0]
        y_start = tile[1]
        og_piece = self.board[tile[1], tile[0]]
        for x in range(x_start - 1, x_start + 2):
            for y in range(y_start - 1, y_start + 2):
                if 0 <= x < 8 and 0 <= y < 8:
                    piece = self.board[y, x]
                    if piece == "-":
                        moves.append((x, y))
                    elif isinstance(piece, Piece):
                        if piece.typ == "K" and piece.color != og_piece.color:
                            pass
                        elif (not piece.is_white() and og_piece.is_white()) or (
                                piece.is_white() and not og_piece.is_white()):
                            moves.append((x, y))

        if self.check_short_castle():
            moves.append("short_castle")

        if self.check_long_castle():
            moves.append("long_castle")

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
            7, 2] == "-" and self.board[7, 1] == "-" and isinstance(self.board[7, 0], Piece) and self.board[
            7, 0].get_image_name() == "wR":
            return True
        elif not black_king_moved and self.board[0, 3] == "-" and self.board[
            0, 2] == "-" and self.board[0, 1] == "-" and isinstance(self.board[0, 0], Piece) and self.board[
            0, 0].get_image_name() == "bR":
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
        og_piece = self.board[tile[1], tile[0]]
        # above right
        if 0 <= x + 1 < 8 and 0 <= y - 2 < 8:
            piece = self.board[y - 2, x + 1]
            if piece == "-":
                moves.append((x + 1, y - 2))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x + 1, y - 2)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x+1, y-2))

        # above left
        if 0 <= x - 1 < 8 and 0 <= y - 2 < 8:
            piece = self.board[y - 2, x - 1]
            if piece == "-":
                moves.append((x - 1, y - 2))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x - 1, y - 2)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x-1, y-2))

        # below right
        if 0 <= x + 1 < 8 and 0 <= y + 2 < 8:
            piece = self.board[y + 2, x + 1]
            if piece == "-":
                moves.append((x + 1, y + 2))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x + 1, y + 2)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x+1, y+2))
        # below left
        if 0 <= x - 1 < 8 and 0 <= y + 2 < 8:
            piece = self.board[y + 2, x - 1]
            if piece == "-":
                moves.append((x - 1, y + 2))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x - 1, y + 2)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x-1, y+2))
        # right above
        if 0 <= x + 2 < 8 and 0 <= y - 1 < 8:
            piece = self.board[y - 1, x + 2]
            if piece == "-":
                moves.append((x + 2, y - 1))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x + 2, y - 1)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x + 2, y - 1))
        # right below
        if 0 <= x + 2 < 8 and 0 <= y + 1 < 8:
            piece = self.board[y + 1, x + 2]
            if piece == "-":
                moves.append((x + 2, y + 1))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x + 2, y + 1)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x + 2, y + 1))
        # left above
        if 0 <= x - 2 < 8 and 0 <= y - 1 < 8:
            piece = self.board[y - 1, x - 2]
            if piece == "-":
                moves.append((x - 2, y - 1))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x - 2, y - 1)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x - 2, y - 1))
        # left below
        if 0 <= x - 2 < 8 and 0 <= y + 1 < 8:
            piece = self.board[y + 1, x - 2]
            if piece == "-":
                moves.append((x - 2, y + 1))
            elif isinstance(piece, Piece):
                if piece.typ == "K" and piece.color != og_piece.color:
                    self.checks.append((tile, (x - 2, y + 1)))
                    pass
                elif (not piece.is_white() and og_piece.is_white()) or (
                        piece.is_white() and not og_piece.is_white()):
                    moves.append((x - 2, y + 1))
        return moves

    def check_pawn_moves(self, tile):
        piece: Piece = self.board[tile[1], tile[0]]
        piece_u_l, piece_u_r, piece_l_l, piece_l_r, piece_u, piece_l = None, None, None, None, None, None
        # check if out of bounds
        if 0 <= tile[1] - 1 < 8 and 0 <= tile[0] - 1 < 8:
            piece_u_l = self.board[tile[1] - 1, tile[0] - 1]
        if 0 <= tile[1] - 1 < 8 and 0 <= tile[0] + 1 < 8:
            piece_u_r = self.board[tile[1] - 1, tile[0] + 1]
        if 0 <= tile[1] + 1 < 8 and 0 <= tile[0] - 1 < 8:
            piece_l_l = self.board[tile[1] + 1, tile[0] - 1]
        if 0 <= tile[1] + 1 < 8 and 0 <= tile[0] + 1 < 8:
            piece_l_r = self.board[tile[1] + 1, tile[0] + 1]

        if 0 <= tile[1] - 1 < 8:
            piece_u = self.board[tile[1] - 1, tile[0]]
        if 0 <= tile[1] + 1 < 8:
            piece_l = self.board[tile[1] + 1, tile[0]]

        moves = []
        # white pawns
        if piece.color == "w":
            # check free space
            if piece_u == "-":
                moves.append((tile[0], tile[1] - 1))
                # move 2 when on 6th rank
                if tile[1] == 6 and self.board[tile[1] - 2, tile[0]] == "-":
                    moves.append((tile[0], tile[1] - 2))
            # check captures
            if piece_u_l is not None and isinstance(piece_u_l, Piece):
                if piece_u_l.typ == "K" and piece_u_l.color != piece.color:
                    self.checks.append((tile, (tile[0]-1, tile[1]-1)))
                elif not piece_u_l.is_white():
                    moves.append((tile[0] - 1, tile[1] - 1))
            if piece_u_r is not None and isinstance(piece_u_r, Piece):
                if piece_u_r.typ == "K" and piece_u_r.color != piece.color:
                    self.checks.append((tile, (tile[0] + 1, tile[1] - 1)))
                elif not piece_u_r.is_white():
                    moves.append((tile[0] + 1, tile[1] - 1))

            # TODO: check en passant

        # black pawns
        elif piece.color == "b":
            # check free space
            if piece_l == "-":
                moves.append((tile[0], tile[1] + 1))
                # move 2 when on 1st rank
                if tile[1] == 1 and self.board[tile[1] + 2, tile[0]] == "-":
                    moves.append((tile[0], tile[1] + 2))
            # check captures
            if piece_l_l is not None and isinstance(piece_l_l, Piece):
                if piece_l_l.typ == "K" and piece_l_l.color != piece.color:
                    self.checks.append((tile, (tile[0] - 1, tile[1] + 1)))
                elif piece_l_l.is_white():
                    moves.append((tile[0] - 1, tile[1] + 1))
            if piece_l_r is not None and isinstance(piece_l_r, Piece):
                if piece_l_r.typ == "K" and piece_l_r.color != piece.color:
                    self.checks.append((tile, (tile[0] + 1, tile[1] + 1)))
                elif piece_l_r.is_white():
                    moves.append((tile[0] + 1, tile[1] + 1))
            # TODO: check en passant

        return moves

    def check_for_checks(self):
        self.checks = []
        for i in range(self.board.shape[0]):
            for j in range(self.board.shape[1]):
                if self.board[j, i] == "-":
                    pass
                else:
                    self.get_all_possible_moves((i, j))
        if len(self.checks) > 0:
            print("moin")
            self.check()
            print(self.checks)

    def check(self):
        self.draw_capture_rect(self.checks[0][1], color=p.Color("Red"))
        if self.sound_on:
            p.mixer.Sound.play(self.check_sound)
        self.in_check = True

    def handle_check(self, tile, possible_moves):
        moves = []
        checks_tmp = self.checks
        board_tmp = self.board.copy()
        self.sound_on = False
        for move in possible_moves:
            board_tmp = self.board.copy()
            self.move_piece(tile, move)
            self.check_for_checks()
            if len(self.checks) == 0:
                moves.append(move)
            self.checks = checks_tmp
            self.board = board_tmp.copy()
            self.update_board()
        self.sound_on = True
        print(moves)
        return moves

    def check_checkmate(self):
        moves = []
        self.sound_on = False
        for x in range(self.board.shape[0]):
            for y in range(self.board.shape[1]):
                tile = (x, y)
                piece = self.board[y, x]
                if piece == "-":
                    pass
                elif (piece.is_white() and not self.whites_turn) or (not piece.is_white() and self.whites_turn):
                    possible_moves = self.get_all_possible_moves(tile)
                    possible_moves = self.handle_check(tile, possible_moves)
                    if len(possible_moves) > 0:
                        moves.append(possible_moves)
        self.sound_on = True
        if len(moves) == 0:
            p.mixer.Sound.play(self.checkmate_sound)
            return True
        return False
