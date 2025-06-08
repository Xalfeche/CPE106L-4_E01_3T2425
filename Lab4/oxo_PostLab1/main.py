import tkinter as tk
from tkinter import messagebox, Frame, Button, Label, Entry
from game import Game
from oxo_data import saveGame, restoreGame

class OXOApp:
    def __init__(self, master):
        self.master = master
        self.master.title("OXO Game")
        self.master.geometry("300x400") # Set a default window size

        self._frame = None
        self.switch_frame(LoginFrame) # Start with the login frame

    def switch_frame(self, frame_class, **kwargs):
        """Destroys current frame and creates a new one."""
        new_frame = frame_class(self.master, self, **kwargs) # Pass kwargs to the new frame
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack(fill="both", expand=True)

class LoginFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        Label(self, text="OXO Game Login").pack(pady=10)

        Label(self, text="Username:").pack()
        self.username_entry = Entry(self)
        self.username_entry.pack()

        Label(self, text="Password:").pack()
        self.password_entry = Entry(self, show="*")
        self.password_entry.pack()

        Button(self, text="Login", command=self.login).pack(pady=10)

    def login(self):
        # Basic login simulation - replace with actual authentication if needed
        username = self.username_entry.get()
        password = self.password_entry.get()

        if username and password: # Simple check for non-empty fields
             messagebox.showinfo("Login Successful", f"Welcome, {username}!")
             self.controller.switch_frame(MainMenuFrame)
        else:
             messagebox.showwarning("Login Failed", "Please enter username and password.")


class MainMenuFrame(Frame):
    def __init__(self, master, controller):
        Frame.__init__(self, master)
        self.controller = controller

        Label(self, text="Main Menu").pack(pady=20)

        Button(self, text="New Game", command=self.new_game).pack(pady=5)
        Button(self, text="Continue Game", command=self.continue_game).pack(pady=5)
        Button(self, text="Help", command=self.show_help).pack(pady=5)
        Button(self, text="Exit", command=master.quit).pack(pady=20)

    def new_game(self):
        game = Game()
        self.controller.switch_frame(GameFrame, game=game)

    def continue_game(self):
        saved_board = restoreGame()
        if saved_board:
            game = Game()
            game.board = saved_board
            self.controller.switch_frame(GameFrame, game=game)
        else:
            messagebox.showinfo("Continue Game", "No saved game found.")

    def show_help(self):
        messagebox.showinfo("Help", "OXO Game Rules:\n\nTwo players take turns marking the spaces in a 3x3 grid. The player who succeeds in placing three of their marks in a horizontal, vertical, or diagonal row wins the game.")

class GameFrame(Frame):
    def __init__(self, master, controller, game):
        Frame.__init__(self, master)
        self.controller = controller
        self.game = game
        self.buttons = []

        Label(self, text="OXO Game").pack(pady=10)

        game_board_frame = Frame(self)
        game_board_frame.pack()

        for i in range(9):
            button = Button(game_board_frame, text=self.game.board[i], font=('Arial', 24), width=5, height=2,
                            command=lambda i=i: self.user_move(i))
            button.grid(row=i // 3, column=i % 3)
            self.buttons.append(button)

        Button(self, text="Save Game", command=self.save_game).pack(pady=10)
        Button(self, text="Main Menu", command=lambda: self.controller.switch_frame(MainMenuFrame)).pack(pady=5)


    def user_move(self, cell):
        try:
            result = self.game.userMove(cell)
            self.buttons[cell].config(text='X')
            if result == 'X':
                messagebox.showinfo("Game Over", "You win!")
                self.reset_game()
            else:
                self.computer_move()
        except ValueError:
            messagebox.showwarning("Invalid Move", "Cell is already occupied!")

    def computer_move(self):
        result, cell = self.game.computerMove()
        if cell != -1:
             self.buttons[cell].config(text='O')

        if result == 'O':
            messagebox.showinfo("Game Over", "Computer wins!")
            self.reset_game()
        elif result == 'D':
            messagebox.showinfo("Game Over", "It's a draw!")
            self.reset_game()

    def save_game(self):
        saveGame(self.game.board)
        messagebox.showinfo("Save Game", "Game saved successfully!")

    def reset_game(self):
        self.game = Game()
        for button in self.buttons:
            button.config(text=" ")


if __name__ == "__main__":
    root = tk.Tk()
    app = OXOApp(root)
    root.mainloop()