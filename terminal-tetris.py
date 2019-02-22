#!/usr/bin/env python3

# zach bray
# 2018-09-07

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

import curses
import time
import random

def main():
	screen = Screen()
	curses.wrapper(screen.init)

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

class Screen:
	def __init__(self):
		self.screen = None
		self.tetris = None
		self.width = 0
		self.height = 0
		self.k = 0
		self.ticks = 0

	def init(self, screen):
		self.screen = screen
		self.set_width_height()
		self.init_colors()
		self.screen.nodelay(True)
		curses.curs_set(False)

		self.tetris = Tetris(self)

		self.screen.clear()
		self.screen.refresh()

		# start the looop
		self.game_loop()

	def game_loop(self):
		while (self.k != ord('q')):
			self.screen.clear()
			self.set_width_height()

			self.render_title()
			self.tetris.render()
			self.render_test()
			self.screen.addstr(0,0, "k: " + str(self.k))

			self.screen.addstr(0,1, "k: " + str(curses.can_change_color()))

			self.screen.refresh()			
			self.k = self.screen.getch()			
			self.ticks += 1
			time.sleep(1/60)

	def render_title(self):
		self.render_str('╔═════════════╗', self.tetris.screen_y - 4)
		self.render_str('║ T E T R I S ║', self.tetris.screen_y - 3)
		self.render_str('╚═══╤═════╤═══╝', self.tetris.screen_y - 2)
		self.render_str('╔═╦═══════╧═════╧═══════╦═╗', self.tetris.screen_y - 1)

	def render_test(self):
		y = self.tetris.screen_y + self.tetris.rows - 7
		x = self.tetris.screen_x - 26
		self.addstr(y    , x, '        ╭───╮')
		self.addstr(y + 1, x, '        │ W │─ drop')
		self.addstr(y + 2, x, 'left ┐  ╰───╯  ┌ right')
		self.addstr(y + 3, x, '   ╭───╮╭───╮╭───╮')
		self.addstr(y + 4, x, '   │ A ││ S ││ D │')
		self.addstr(y + 5, x, '   ╰───╯╰───╯╰───╯')
		self.addstr(y + 6, x, '          └ rotate')

	def init_colors(self):
		curses.init_pair(1, curses.COLOR_GREEN, curses.COLOR_BLACK)
		curses.init_pair(2, curses.COLOR_RED, curses.COLOR_BLACK)
		curses.init_pair(3, curses.COLOR_YELLOW, curses.COLOR_BLACK)
		curses.init_pair(4, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
		curses.init_pair(5, curses.COLOR_CYAN, curses.COLOR_BLACK)
		curses.init_pair(6, curses.COLOR_WHITE, curses.COLOR_BLACK)
		curses.init_pair(7, curses.COLOR_BLUE, curses.COLOR_BLACK)

	def addstr(self, y, x, string):
		self.screen.addstr(y, x, string)

	def color(self, on, index):
		if (on == "on"):
			self.screen.attron(curses.color_pair(index))
		else:
			self.screen.attroff(curses.color_pair(index))

	# renders a string center on row y
	def render_str(self, s, y):
		l = len(s)
		x = self.width // 2 - l // 2 - 1
		self.screen.addstr(y, x, s)

	# updates the width and height variables, keeps things center
	def set_width_height(self):
		self.height, self.width  = self.screen.getmaxyx()

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

class Tetris:

	# initialize game vars
	def __init__(self, screen):
		self.screen = screen
		
		self.columns = 10
		self.rows = 20

		self.set_screen_xy()

		self.matrix = [0] * (self.rows * self.columns)

		self.block = Block(self.columns)


	# render the block and matrix
	def render(self):
		self.set_screen_xy()
		self.input()

		if (self.screen.ticks % 40 == 0):
			self.decrease_block()

		for y in range(0, self.rows):
			yp = self.screen_y + y
			
			self.screen.addstr(yp, self.screen_x - 4, '╟╳╢');
			
			for x in range(0, self.columns):
				xp = self.screen_x + x * 2
				
				if (self.block.is_block(x, y)):
					self.screen.color("on", self.block.index)
					self.screen.addstr(yp, xp, "█▋")
					self.screen.color("off", self.block.index)

				m = self.get_matrix(x, y)
				if (m > 0):
					self.screen.color("on", m)
					self.screen.addstr(yp, xp, "█▋")
					self.screen.color("off", m)					

				
			self.screen.addstr(yp, self.screen_x + self.columns * 2, '╟╳╢');

	# process input
	def input(self):
		k = self.screen.k

		if (k == ord('a')):
			self.move(-1)
		elif (k == ord('d')):
			self.move(1)
		elif (k == ord('s')):
			self.block.rotate()
		elif (k == ord('w')):
			self.drop_block()

	# tries to move the blocks left or right
	def move(self, i):
		self.block.x += i

		if (not self.valid_block()):
			self.block.x -= i


	# moves the block down one, returns true if collision
	def decrease_block(self):
		self.block.y += 1
		
		if (self.valid_block()):
			return False
		else:
			self.block.y -= 1
			self.new_block()
			return True


	# checks if current block position collides with matrix and is in bounds
	def valid_block(self):
		for y in range(0, self.block.h):
			for x in range(0, self.block.w):
				xp = x + self.block.x
				yp = y + self.block.y

				# no block, no collision
				if (not self.block.is_block(xp, yp)):
					continue

				# out of bounds
				if (xp < 0 or xp >= self.columns or yp >= self.rows):
					return False

				# collides with block
				if (self.get_matrix(xp, yp)):
					return False
		return True


	# instantly drop block to bottom
	def drop_block(self):
		for y in range(0, self.rows - self.block.y):
			if (self.decrease_block()):
				return


	# add the current block to the matrix and create a new block
	def new_block(self):
		for y in range(0, self.block.h):
			for x in range(0, self.block.w):
				xp = x + self.block.x
				yp = y + self.block.y
				if (self.block.is_block(xp, yp)):
					self.set_matrix(xp, yp, self.block.index)
		self.check_row_complete()
		self.block = Block(self.columns)

	# checks if any rows are full
	def check_row_complete(self):
		y = self.rows - 1
		while (y >= 0):
			for x in range(self.columns):
				if (self.get_matrix(x, y) == 0):
					break
				if (x == self.columns - 1):
					self.delete_row(y)
					y += 1
			y -= 1

	# moves rows up start_y down one
	def delete_row(self, start_y):
		for y in range(start_y, 0, -1):
			for x in range(0, self.columns):
				self.set_matrix(x, y, self.get_matrix(x, y - 1))

	# shortcut 
	def set_matrix(self, x, y, i):
		self.matrix[x + y * self.columns] = i

	# shortcut
	def get_matrix(self, x, y):
		return self.matrix[x + y * self.columns]

	# update coordinates from screen size
	def set_screen_xy(self):
		self.screen_x = self.screen.width // 2 - self.columns
		self.screen_y = self.screen.height - self.rows - 2

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

class Block:
	
	# indexed with curses.init_pair - 1
	types = [
		[[0,1,1],
		 [1,1,0]],

		[[1,1,0],
		 [0,1,1]],

		[[1,1],
		 [1,1]],

		[[0,1,0],
		 [1,1,1],
		 [0,0,0]],

		[[0,0,0,0],
		 [1,1,1,1],
		 [0,0,0,0],
		 [0,0,0,0]],

		[[0,0,1],
		 [1,1,1],
		 [0,0,0]],

		[[1,0,0],
		 [1,1,1],
		 [0,0,0]]
	]

	# randomly pick a new block and set variables
	def __init__(self, columns):
		self.index = random.randint(0, len(self.types) - 1)
		self.type = self.types[self.index]
		self.columns = columns
		self.set_width_height()

		# add one because this is just used to index
		#	 colors which have to start at index 1
		self.index += 1
		
		self.x = self.columns // 2 - self.w // 2
		self.y = 0

	# update width and height
	def set_width_height(self):
		self.w = len(self.type[0])
		self.h = len(self.type)

	# sometimes block is not block
	def is_block(self, x, y):
		return (x >= self.x and x < self.x + self.w and
				y >= self.y and y < self.y + self.h and
				self.type[y - self.y][x - self.x] == 1)

	# somehow that rotates a matrix so neat
	def rotate(self):
		self.type = list(zip(*self.type[::-1]))
		self.set_width_height()

# ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- ---- #

if (__name__) == '__main__':
	main()
