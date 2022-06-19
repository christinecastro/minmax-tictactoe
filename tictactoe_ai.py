import tkinter.font as font
import tkinter as tk
import numpy as np
import copy,random,time
from tkinter import *
from tkinter import (ttk, messagebox)

#
#	CastroCMR
#	CMSC 170 X-1L
#	Lab10: Minmax Algorithm
#


class State():
	def __init__(self, array, action, node_type):
		self.array = copy.deepcopy(array)
		self.action = action
		self.type = node_type


class Game():
	def __init__(self, window):
		self.window = window
		self.b= {}  #for grid of buttons      
		self.a =np.array([[None,None,None],
						[None,None,None],
						[None,None,None]])
		self.win = None #flag for winning condition
		self.m = 0 #number of moves made
		
	#Reinitialize for the next game
	def nextGame(self):
		#reinitialize attributes
		self.win = None
		self.m = 0
		self.userturn=False
		self.a =np.array([[None,None,None],
						[None,None,None],
						[None,None,None]])
		#remove grid
		self.frame.place_forget()
		for widget in self.frame.winfo_children():
			widget.destroy()
		self.frame.destroy()
		self.b={}
		#unhide main menu widgets
		self.label1.place(relx=0.5, rely=0.15, anchor=tk.CENTER)
		self.label2.place(relx=0.5, rely=0.45, anchor=tk.CENTER)
		self.x_btn.place(relx=0.35, rely=0.6, anchor=tk.CENTER)
		self.o_btn.place(relx=0.5, rely=0.6, anchor=tk.CENTER)
		self.exit_btn.place(relx=0.65, rely=0.6, anchor=tk.CENTER)

	#Check if agent or user wins (updates self.win)
	def isWin(self): 
		array = self.a
		#check win at rows and columns
		for i in range(3):
			for j  in range(3):
				if(np.all(array[0:,i]==array[0:,i][0])): #column
					if(array[0:,i][0]!=None):
						self.winner = array[0:,i][0]
						self.win = 1
						break
				elif(np.all(array[i,0:]==array[i,0:][0])): #row
					if(array[i,0:][0]!=None):
						self.winner = array[i,0:][0]
						self.win = 1
						break
		#check win at diagonal and antidiagonal
		diagonal = np.array([array[0][0],array[1][1],array[2][2]])
		a_diagonal = np.array([array[0][2], array[1][1], array[2][0]])

		if (np.all(diagonal==diagonal[0])):
			if(diagonal[0]!=None):
				self.winner = diagonal[0]
				self.win = 1

		elif (np.all(a_diagonal==a_diagonal[0])):
			if(a_diagonal[0]!=None):
				self.winner = a_diagonal[0]
				self.win = 1

		#check if draw
		elif( self.m==9 and self.win == None):
			self.win  = -1
			self.winner = None

		#IF GAME OVER------------
		if self.win != None:
			#show message box
			if self.winner == self.agent:
				tk.messagebox.showinfo("Game Over", " You Lose!")
			elif self.winner == self.user:
				tk.messagebox.showinfo("Game Over", "Congrats! You Win!")
			elif self.winner == None:
				tk.messagebox.showinfo("Game Over", "It's a Draw!")
			self.nextGame()
			
	#Check if winning condition is by user or agent
	def checkPlayer(self,block):
		u = None #if blank blocks
		if block==self.agent:
				u = 1 #AI agent wins
		elif block==self.user:
				u = -1 #user wins
		return u

	#Randomize first move of AI agent
	def firstMove(self):
		if self.b!={}:
			i = random.randint(0,2)
			j = random.randint(0,2)
			#update board, array value, and attributes
			self.b[(i,j)].config(text = self.agent)
			self.a[i][j]= self.agent
			self.userturn = True
			self.m +=1
			#check if win
			self.isWin()

	#Makes the AI agent move given the possible moves
	def makeMove(self,moves):
		if len(moves) >0:
			moves = np.array(moves)
			max_val = np.max(moves[:,1]) 
			moves = moves[np.where(moves[:,1] == max_val)] #filter array to ones that have max value
			if len(moves)>1: #more than 1 moves
				#randomize
				n = random.randint(0,len(moves)-1)
				i,j = moves[n][0].action

			else:
				i,j = moves[0][0].action
		#update board, array value, and attributes
		self.b[(i,j)].config(text = self.agent)
		self.a[i][j]= self.agent
		self.userturn = True
		self.m +=1
		#check if win
		self.isWin()

	#Returns the utility value if terminal node
	def utility(self, state):
		array = state.array
		u = None #returned if not a terminal node
		#check win at rows and columns
		for i in range(3):
			for j  in range(3):
				if(np.all(array[0:,i]==array[0:,i][0])): #column
					u = self.checkPlayer(array[0:,i][0])
					break
				elif(np.all(array[i,0:]==array[i,0:][0])): #row
					u = self.checkPlayer(array[i,0:][0])
					break
		#check win at diagonal and antidiagonal
		diagonal = np.array([array[0][0],array[1][1],array[2][2]])
		a_diagonal = np.array([array[0][2], array[1][1], array[2][0]])

		if (np.all(diagonal==diagonal[0])):
			u = self.checkPlayer(diagonal[0])

		elif (np.all(a_diagonal==a_diagonal[0])):
			u = self.checkPlayer(a_diagonal[0])

		#return u if terminal (not draw)
		if (u==1 or u==-1):
			return u

		#check if draw
		if ( np.all( state.array!= None)):
			u  = 0

		return u

	#Maximizes node values
	def max_value(self, state,alpha,beta):
		m = -np.inf
		for i in range(3):
			for j in range(3):
				if state.array[i][j] == None:
					s = copy.deepcopy(state) #copy state
					s.array[i][j] = self.agent #update copied array 
					new_state = State(s.array, (i,j), "min") #next state
					v = self.value(new_state,alpha,beta)
					m = max(m,v)
					if v>= beta:
						return m
					alpha = max(alpha,m)
		return m

	#Minimizes node values
	def min_value(self, state, alpha, beta):
		m = np.inf
		for i in range(3):
			for j in range(3):
				if state.array[i][j] == None:
					s = copy.deepcopy(state) #copy state
					s.array[i][j] = self.user #update copied array 
					new_state = State(s.array, (i,j), "max") #next state
					v = self.value(new_state,alpha,beta)
					m = min(m,v)
					if v<= alpha:
						return m
					beta = min(beta,m)	
		return m	

	#Check if terminal, max node, or min node
	def value(self,state,alpha,beta):
		state = copy.deepcopy(state) #copy state

		if self.utility(state)!=None:
			return self.utility(state)
		elif state.type == "max":
			return self.max_value(state,alpha,beta)
		elif state.type == "min":
			return self.min_value(state,alpha,beta) 

	#Makes AI agent move
	def agentMove(self, array):
		if self.m==0: #if first to make a move
			self.firstMove();

		else: #not the first to make a move
			moves = list()
			for i in range(3):
				for j in range(3):
					if array[i][j] == None:
						arr = copy.deepcopy(array)
						arr[i][j] = self.agent
						new_state = State(arr, (i,j), "min")
						m = self.value(new_state, -np.inf, np.inf)
						moves.append([new_state,m])
			self.makeMove(moves)

	#If user clicks a block on their turn
	def click(self, i,j):
		if self.userturn == True: #must be user's turn to move
			if self.b[(i,j)]["text"]=="":
				##update board, array value, and attributes
				self.b[(i,j)].config(text=self.user)
				self.a[i][j] = self.user
				self.userturn=False
				self.m +=1 #update moves
				self.isWin() #check if win
				self.agentMove(self.a) #AI agent's turn

	#Create and place the grid of buttons on window
	def drawBoard(self):
		#Hide widgets for the main menu
		self.label1.place_forget()
		self.label2.place_forget()
		self.x_btn.place_forget()
		self.o_btn.place_forget()
		self.exit_btn.place_forget()

		#Initialize the frame
		self.frame = tk.Frame(width = 400, height=400)
		self.frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)
		myFont = font.Font(family='Helvetica',size=50)
		self.frame.configure(background="black")

		#create grid of buttons
		for i in range(3):
		   for j in range(3):
	   		self.b[(i,j)] = tk.Button(master=self.frame,borderwidth=1, width=3,height=1,relief=SUNKEN, 
	   			command=lambda row=i, col=j: self.click(row,col ))
	   		self.b[(i,j)].grid(row=i,column=j, padx=2, pady=2,)
	   		self.b[(i,j)]['font'] = myFont
		   	self.b[(i,j)].grid_propagate(0)

	#If user pick X button in main menu
	def userpickX(self):
		self.user = "X"
		self.agent = "O"
		self.userturn = True
		self.drawBoard()

	#If user pick O button in main menu
	def userpickO(self):
		self.user = "X"
		self.agent = "O"
		self.userturn = False
		self.drawBoard()
		self.agentMove(self.a) #AI agent makes a move

	#If user clicks exit button in main menu
	def exit(self):
		quit()

	def mainMenu(self):
		#create and place widgets
		self.label1 = tk.Label(self.window,text ="Tic-Tac-Toe", font=("Century Gothic",30))
		self.label1.place(relx=0.5, rely=0.15, anchor=tk.CENTER)

		self.label2 = tk.Label(self.window,text ="What do you want to play?", font=("Century Gothic",18))
		self.label2.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

		self.x_btn = ttk.Button(text=" X ",width=5, style="my.TButton", command=self.userpickX)
		self.x_btn.place(relx=0.35, rely=0.6, anchor=tk.CENTER)

		self.o_btn = ttk.Button(text=" O ",width=5, style="my.TButton", command= self.userpickO)
		self.o_btn.place(relx=0.5, rely=0.6, anchor=tk.CENTER)

		self.exit_btn = ttk.Button(text=" Exit ",width=5, style="my.TButton",command=self.exit)
		self.exit_btn.place(relx=0.65, rely=0.6, anchor=tk.CENTER)

	
def newWindow():
	# initialize window
	window = tk.Tk() #frame
	s = ttk.Style()
	s.theme_use('vista') #theme used for button
	s.configure("TMenubutton", background="light gray")
	s.configure("my.TButton", background="light gray", font=("Century Gothic", 15))
	window.title("Tic-Tac-Toe") #title
	window.geometry("500x500") #window size
	window.minsize(500,500)
	window.maxsize(500,500)
	return window

def main():

	program = Game(newWindow())
	program.mainMenu()
	running = True
	while running:
		program.window.mainloop()
		break

	return 0

if __name__ == '__main__':
    main()