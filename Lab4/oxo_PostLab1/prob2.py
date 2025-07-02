import tkinter as tk 
from tkinter import filedialog 

def select_file():
	root = tk.Tk()
	root.withdraw()  # Hide the root window
	file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
	return file_path

if __name__ == "__main__": 
	selected_file = select_file()
	print(f"Selected file: {selected_file}") 