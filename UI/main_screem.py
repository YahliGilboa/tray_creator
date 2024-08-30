from tkinter import *
from tkinter.ttk import *

# Constants for window size
WINDOW_WIDTH = 700
WINDOW_HEIGHT = 500

# Create the main Tkinter window
master = Tk()
master.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

# Configure the grid layout to expand properly
master.grid_columnconfigure(0, weight=1)
master.grid_columnconfigure(1, weight=1)

# Create and place the header label
main_header = Label(
    master,
    text="Please enter the desired height\nand width of your tray",
    font=("Sans", 22, "bold"),
    justify="center",
    anchor="center"
)
main_header.grid(row=0, column=0, columnspan=2, sticky="nsew")

# Create and place the Entry widgets for height and width
width_prompt = Entry(master)
width_prompt.insert(0,"enter width in mm")
height_prompt = Entry(master)
height_prompt.insert(0,"enter height in mm")

width_prompt.grid(row=1, column=0, padx=10, pady=10, sticky="e")
height_prompt.grid(row=1, column=1, padx=10, pady=10, sticky="w")

# master.grid_columnconfigure(0, weight=1)
# master.grid_columnconfigure(1, weight=1)
# width_prompt.grid(row=1,column=0)
# height_prompt.grid(row=1,column=1)


#
# # this will create a label widget
# b1 = Button(text="bruh")
# b2 = Button(text="bruh")
# b3 = Button(text="bruh")
# b4 = Button(text="bruh")
#
# b1.grid(row=0,column=0)
# b2.grid(row=0,column=1)
# b3.grid(row=1,column=0)
# b4.grid(row=1,column=1)



# infinite loop which can be terminated by keyboard
# or mouse interrupt
master.mainloop()
