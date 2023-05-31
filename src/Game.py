import pygame as p
from Board import Board
from Piece import Piece

WIDTH, HEIGHT = 512, 512
MAX_FPS = 60


class Game:
    run = True

    def __init__(self):
        self.WIN = p.display.set_mode((WIDTH, HEIGHT))
        self.board = Board(WIDTH, self.WIN)
        self.clock = p.time.Clock()

    def main_loop(self):

        on_tile_clicked = False
        store_tile = None
        possible_moves = None
        while 1:
            for event in p.event.get():
                if event.type == p.QUIT:
                    exit(0)
            while self.run:
                for event in p.event.get():
                    if event.type == p.QUIT:
                        self.run = False

                    if event.type == p.MOUSEBUTTONUP:

                        pos = p.mouse.get_pos()
                        tile = self.board.get_tile_from_pixel_coords(pos)
                        board_tile = (tile[1], tile[0])
                        piece = self.board.board[board_tile]

                        # make sure only white can move when it's whites  turn and viceversa
                        if isinstance(piece, Piece) and not on_tile_clicked and self.board.can_move():
                            if (self.board.whites_turn and piece.is_white()) or (
                                    not self.board.whites_turn and not piece.is_white()):
                                on_tile_clicked = True
                                store_tile = tile
                                self.board.update_board()
                                self.board.clicked_on_tile(tile)
                                possible_moves = self.board.get_all_possible_moves(tile)
                                if self.board.in_check:
                                    possible_moves = self.board.handle_check(tile, possible_moves)
                                self.board.draw_move_preview(possible_moves)
                                if possible_moves is None:
                                    on_tile_clicked = False

                        # check if clicked on same tile again and remove possible moves
                        elif possible_moves is not None and (tile == store_tile or (
                                tile not in possible_moves and "long_castle" not in possible_moves and "short_castle" not in possible_moves)):
                            on_tile_clicked = False
                            self.board.update_board()
                            possible_moves = None

                        # only really move piece if there are possible moves and
                        #  you are not on an  earlier move
                        elif on_tile_clicked and possible_moves is not None and self.board.can_move():

                            if tile in possible_moves:
                                self.board.checks = []
                                if self.board.in_check:
                                    self.board.in_check = False
                                self.board.move_piece(store_tile, tile)
                                self.board.check_for_checks()
                                if self.board.in_check:
                                    if self.board.check_checkmate():
                                        self.run = False
                                        break

                                    self.board.handle_check(tile, possible_moves)
                                if self.board.whites_turn:
                                    self.board.whites_turn = False
                                else:
                                    self.board.whites_turn = True

                            # handle castling
                            elif self.board.whites_turn and tile == (7, 7) and "short_castle" in possible_moves:
                                self.board.move_piece(store_tile, "short_castle")
                                self.board.whites_turn = False
                            elif not self.board.whites_turn and tile == (7, 0) and "short_castle" in possible_moves:
                                self.board.move_piece(store_tile, "short_castle")
                                self.board.whites_turn = True
                            elif self.board.whites_turn and tile == (0, 7) and "long_castle" in possible_moves:
                                self.board.move_piece(store_tile, "long_castle")
                                self.board.whites_turn = False
                            elif not self.board.whites_turn and tile == (0, 0) and "long_castle" in possible_moves:
                                self.board.move_piece(store_tile, "long_castle")
                                self.board.whites_turn = True

                            on_tile_clicked = False

                    if event.type == p.KEYDOWN:
                        if event.key == p.K_LEFT:
                            self.board.undo_move()
                        elif event.key == p.K_RIGHT:
                            self.board.move_forward()

                self.clock.tick(MAX_FPS)
                p.display.flip()