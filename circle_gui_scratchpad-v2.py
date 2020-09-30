#!/usr/bin/python3

__author__ = 'Michele Penzo'

from tkinter import *
from tkinter.colorchooser import askcolor
import pyautogui
import numpy as np

from time import sleep

class Paint(object):
    # default parameters
    default_pen_size = 4.0
    default_color = 'black'

    # ------------------------------
    # ---- max delay in seconds ----
    DELAY = 0
    total_error = 0

    line_points_id = []

    # starting coordinate of circle --> not the center of monitor
    x, y = 1300, 500
    radius = 300 - default_pen_size

    error_start_counter = False

    # coordinates of rectangle
    x1, y1, x2, y2 = 100, y - 400, 800, y + 400

    # right shift, from scratchpad to circle
    right_shift = 800

    # whiteboard
    def __init__(self):
        self.root = Tk()
        self.root.title('NCS Server')

        # the new cursor
        self.root.config(cursor='arrow red')

        # get width and height
        _width = self.root.winfo_screenwidth()
        _height = self.root.winfo_screenheight()

        # canvas
        self.c = Canvas(self.root, bg='white', width=_width, height=_height)
        self.c.grid(row=1, columnspan=50)

        # distance labele
        self.label = Label(self.root, text='Errore --->   ', font=("Helvetica", 16))
        self.label.grid(sticky=E, row=0, column=0)

        # correction error printed here
        self.label_error = Label(self.root, text='', font=("Helvetica", 16))
        self.label_error.grid(sticky=W, row=0, column=1)

        self.label = Label(self.root, text='Errore complessivo --->   ', font=("Helvetica", 16))
        self.label.grid(sticky=E, row=0, column=2)

        # correction error printed here
        self.label_total_error = Label(self.root, text='', font=("Helvetica", 16))
        self.label_total_error.grid(sticky=W, row=0, column=3)

        # start button
        self.start_button = Button(self.root, text='Inizia', font=("Helvetica", 16), command=self.start)
        self.start_button.grid(sticky=W, row=0, column=4)

        # getting the coordinates 
        xr1, yr1, xr2, yr2 = self.x - self.radius, self.y - self.radius, self.x + self.radius, self.y + self.radius
        self.c.create_oval(xr1, yr1, xr2, yr2, outline="#ff0000", fill="#add4d9", width=self.default_pen_size)

        self.c.create_line(self.x, self.y - self.radius - 10, self.x, self.y - self.radius + 10, width=3)

        self.c.create_rectangle(self.x1, self.y1, self.x2, self.y2, outline="#000000", fill="#bfbfbf",
                                width=self.default_pen_size)

        center_x = self.x1 + ((self.x2 - self.x1) / 2)
        mylabel = self.c.create_text((center_x, self.y1 - 20), text="Disegna qui sotto!", font=("Helvetica", 16))

        self.setup()

        self.root.mainloop()

    # set base values
    def setup(self):
        self.old_x = None
        self.old_y = None

        self.line_width = self.default_pen_size
        self.color = self.default_color

        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    # method for writing on whiteboard
    def paint(self, event):

        if self.old_x and self.old_y:
            sleep(self.DELAY)  # DELAY in seconds
            if not (event.x < self.x1 or event.x > self.x2 or event.y < self.y1 or event.y > self.y2):
                self.line_points_id.append(self.c.create_line(self.old_x + self.right_shift, self.old_y, event.x + self.right_shift, event.y,
                                   width=self.line_width, fill=self.default_color, capstyle=ROUND, smooth=TRUE,
                                   splinesteps=36))

                if self.error_start_counter:
                    # calculating distance from center4
                    distance_rectangle = abs(
                        np.sqrt(min(event.x - self.x1 + self.right_shift, event.x - self.x2 + self.right_shift) ** 2 + min(
                            event.y - self.y1, event.y - self.y2) ** 2) - self.radius)

                    distance_circle = abs(
                        np.sqrt((event.x - self.x + self.right_shift) ** 2 + (event.y - self.y) ** 2) - self.radius)

                    distance = round(distance_circle / distance_rectangle, 2)

                    self.total_error += abs(distance)
                    self.label_error['text'] = round(distance, 2)
                    self.label_total_error['text'] = round(self.total_error, 2)

        self.old_x = event.x
        self.old_y = event.y

    # reset value
    def reset(self, event):
        self.old_x = None
        self.old_y = None


    def start(self):
        self.error_start_counter = True
        #reset counters
        self.total_error = 0
        self.label_error['text'] = 0
        self.label_total_error['text'] = 0
        #delete lines on canvas
        for point in self.line_points_id:
            self.c.delete(point)

if __name__ == '__main__':
    Paint()
