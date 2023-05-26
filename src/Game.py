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
                            print(piece.get_image_name())
                            on_tile_clicked = True

                            store_tile = tile
                            self.board.draw_board()
                            self.board.clicked_on_tile(tile)
                            possible_moves = self.board.get_all_possible_moves(tile)
                            self.board.draw_move_preview(possible_moves)

                            if possible_moves is None:
                                on_tile_clicked = False

                    # check if clicked on same tile again and remove possible moves
                    elif possible_moves is not None and (tile == store_tile or (
                            tile not in possible_moves and "long_castle" not in possible_moves and "short_castle" not in possible_moves)):
                        on_tile_clicked = False
                        self.board.update_board()
                        possible_moves = None

                    # only really move piece if tile is empty (TODO: or can take) and there are possible moves and
                    #  you are not on an  earlier move
                    elif (piece == "-" or piece.get_image_name() == "wR" or
                          piece.get_image_name() == "bR") and on_tile_clicked and possible_moves is not None and self.board.can_move():

                        if tile in possible_moves:
                            self.board.move_piece(store_tile, tile)
                            if self.board.whites_turn:
                                self.board.whites_turn = False
                            else:
                                self.board.whites_turn = True

                        # handle castling
                        elif self.board.whites_turn and tile == (7, 7) and "short_castle" in possible_moves:
                            print("moin")
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

p.quit()
