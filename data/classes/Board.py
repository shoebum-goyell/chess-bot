import pygame
import random
from data.classes.Square import Square
from data.classes.pieces.Rook import Rook
from data.classes.pieces.Bishop import Bishop
from data.classes.pieces.Knight import Knight
from data.classes.pieces.Queen import Queen
from data.classes.pieces.King import King
from data.classes.pieces.Pawn import Pawn
import subprocess
import copy


# Game state checker
class Board:
	def __init__(self, width, height):
		self.width = width
		self.height = height
		self.tile_width = width // 8
		self.tile_height = height // 8
		self.selected_piece = None
		self.turn = 'white'

		# try making it chess.board.fen()
		self.config = []

		self.squares = self.generate_squares()

		self.setup_board()

	# def copy(self):
	# 	return copy.deepcopy(self.squares)
	
	def to_fen(self):
		# Initialize an empty FEN string
		fen = ''
		# Iterate over each rank
		for y in range(0, 8):
			empty = 0
			# Iterate over each file
			for x in range(8):
				piece = self.get_piece_from_pos((x, y))
				# If the square is empty
				if piece is None:
					empty += 1
				else:
					# If the previous squares were empty, add the count to the FEN string
					if empty > 0:
						fen += str(empty)
						empty = 0
					# Add the piece to the FEN string
					if(piece.color == 'white'):
						fen += piece.notation
					else:
						fen += piece.notation.lower()
			# If the last squares were empty, add the count to the FEN string
			if empty > 0:
				fen += str(empty)
			# Separate ranks with a slash
			if y < 7:
				fen += '/'
		# Add the current player
		fen += ' ' + ('w' if self.turn == 'white' else 'b')
		# TODO: Add castling availability, en passant target square, halfmove clock, and fullmove number
		return fen + " KQkq - 0 1"

	def loadFromFen(self, fen):
		# Split the FEN string into main parts
		parts = fen.split(" ")
		# Split the first part into rows
		rows = parts[0].split("/")
		# Initialize an empty config
		config = []
		# For each row
		for row in rows:
			# Initialize an empty row
			r = []
			# For each character in the row
			for c in row:
				# If the character is a digit
				if c.isdigit():
					# Add that many empty strings to the row
					r += [''] * int(c)
				else:
					# Otherwise, add the character to the row
					if(c.islower()):
						r.append('b'+c.upper())
					else:
						r.append('w'+c)
			# Add the row to the config
			config.append(r)
		return config


	def generate_squares(self):
		output = []
		for y in range(8):
			for x in range(8):
				output.append(
					Square(x,  y, self.tile_width, self.tile_height)
				)
		return output
	

	
	def play_random_move(self):
		possible_moves = []
		for piece in [i.occupying_piece for i in self.squares if i.occupying_piece is not None and i.occupying_piece.color == 'black']:
			a = [piece, piece.get_valid_moves(self)]
			if(len(piece.get_valid_moves(self)) != 0):
				possible_moves.append(a)
		self.make_move(possible_moves)

	def ai_move(self, oldpos, newpos):
		pi = self.get_piece_from_pos(oldpos)
		self.selected_piece = pi
		self.selected_piece.move(self, self.get_square_from_pos(newpos))
		self.turn = 'white' if self.turn == 'black' else 'black'

	def make_move(self, possible_moves):
		move = random.choice(possible_moves)
		self.selected_piece = move[0]
		self.selected_piece.move(self, random.choice(move[1]))
		self.turn = 'white' if self.turn == 'black' else 'black'


	def get_square_from_pos(self, pos):
		for square in self.squares:
			if (square.x, square.y) == (pos[0], pos[1]):
				return square


	def get_piece_from_pos(self, pos):
		return self.get_square_from_pos(pos).occupying_piece


	def setup_board(self):
		# iterating 2d list
		self.config = self.loadFromFen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
		print(self.config)
		for y, row in enumerate(self.config):
			for x, piece in enumerate(row):
				if piece != '':
					square = self.get_square_from_pos((x, y))

					# looking inside contents, what piece does it have
					if piece[1] == 'R':
						square.occupying_piece = Rook(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)
					# as you notice above, we put `self` as argument, or means our class Board

					elif piece[1] == 'N':
						square.occupying_piece = Knight(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)

					elif piece[1] == 'B':
						square.occupying_piece = Bishop(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)

					elif piece[1] == 'Q':
						square.occupying_piece = Queen(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)

					elif piece[1] == 'K':
						square.occupying_piece = King(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)

					elif piece[1] == 'P':
						square.occupying_piece = Pawn(
							(x, y), 'white' if piece[0] == 'w' else 'black', self
						)


	def handle_click(self, mx, my):
		x = mx // self.tile_width
		y = my // self.tile_height
		clicked_square = self.get_square_from_pos((x, y))

		if self.selected_piece is None:
			if clicked_square.occupying_piece is not None:
				if clicked_square.occupying_piece.color == self.turn:
					self.selected_piece = clicked_square.occupying_piece

		elif self.selected_piece.move(self, clicked_square):
			self.turn = 'white' if self.turn == 'black' else 'black'
			fen = self.to_fen()
			print(self.to_fen())
			result = subprocess.run(["./main", "8", fen], capture_output = True, text = True)
			s = 'abcdefgh'
			x1 = s.index(result.stdout[0])
			y1 = 8 - int(result.stdout[1])
			pos = [x1, y1]
			x2 = s.index(result.stdout[2])
			y2 = 8 - int(result.stdout[3])
			pos2 = [x2, y2]
			print(result.stdout)
			self.ai_move(pos, pos2)
			# self.play_random_move()
			# print(self.squares)


		elif clicked_square.occupying_piece is not None:
			if clicked_square.occupying_piece.color == self.turn:
				self.selected_piece = clicked_square.occupying_piece


	def is_in_check(self, color, board_change=None): # board_change = [(x1, y1), (x2, y2)]
		output = False
		king_pos = None

		changing_piece = None
		old_square = None
		new_square = None
		new_square_old_piece = None

		if board_change is not None:
			for square in self.squares:
				if square.pos == board_change[0]:
					changing_piece = square.occupying_piece
					old_square = square
					old_square.occupying_piece = None
			for square in self.squares:
				if square.pos == board_change[1]:
					new_square = square
					new_square_old_piece = new_square.occupying_piece
					new_square.occupying_piece = changing_piece

		pieces = [
			i.occupying_piece for i in self.squares if i.occupying_piece is not None
		]

		if changing_piece is not None:
			if changing_piece.notation == 'K':
				king_pos = new_square.pos
		if king_pos == None:
			for piece in pieces:
				if piece.notation == 'K' and piece.color == color:
						king_pos = piece.pos
		for piece in pieces:
			if piece.color != color:
				for square in piece.attacking_squares(self):
					if square.pos == king_pos:
						output = True

		if board_change is not None:
			old_square.occupying_piece = changing_piece
			new_square.occupying_piece = new_square_old_piece
						
		return output


	# def is_in_checkmate(self, color):
	# 	output = False

	# 	for piece in [i.occupying_piece for i in self.squares]:
	# 		if piece != None:
	# 			if piece.notation == 'K' and piece.color == color:
	# 				king = piece

	# 	if king.get_valid_moves(self) == []:
	# 		if self.is_in_check(color):
	# 			output = True

	# 	return output
	
	def is_in_checkmate(self, color):
		output = False
		validmoves = []
		for piece in [i.occupying_piece for i in self.squares if i.occupying_piece is not None and i.occupying_piece.color == color]:
			validmoves.extend(piece.get_valid_moves(self))
		if validmoves == []:
			if self.is_in_check(color):
				output = True
		return output


	def draw(self, display):
		if self.selected_piece is not None:
			self.get_square_from_pos(self.selected_piece.pos).highlight = True
			for square in self.selected_piece.get_valid_moves(self):
				square.highlight = True

		for square in self.squares:
			square.draw(display)