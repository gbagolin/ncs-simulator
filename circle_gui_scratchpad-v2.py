#!/usr/bin/python3

__author__ = 'Michele Penzo'

from tkinter import *
import Point
import Angle
from time import sleep
import math


def is_round_corner_done(angle_steps):
    for bool in angle_steps:
        if bool == False:
            return False
    return True


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
    circle_center = Point(1300,500)
    x, y = 1300, 500
    radius = 300 - default_pen_size

    error_start_counter = False
    is_first_point = True

    # coordinates of rectangle
    x1, y1, x2, y2 = 100, y - 400, 800, y + 400
    left_down_rectangle_point = Point(100,circle_center.y - 400)

    first_point_drawn = Point(None, None)
    fx, fy = None, None
    # right shift, from scratchpad to circle
    right_shift = 800
                            #90   #180   #270   #360
    angle_steps_passed = [False, False, False, False]

    done = False

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

        if is_round_corner_done(self.angle_steps_passed):
            print("Hai finitooo")
        else:
            if self.old_x and self.old_y:
                # test angle
                if self.fy and self.fx :
                    p1 = (event.x + self.right_shift, event.y)
                    p2 = (self.x, self.y)
                    p3 = (self.fx,self.fy)
                    angle = getAngle(p3,p2,p1)

                    if angle > 0 and angle < 90 :
                        self.angle_steps_passed[0] = True
                    elif angle > 90 and angle < 180:
                        self.angle_steps_passed[1] = True
                    elif angle > 270 and angle < 360:
                        self.angle_steps_passed[2] = True
                    if angle > 359 and self.angle_steps_passed[2]:
                        self.angle_steps_passed[3] = True

                    print(self.angle_steps_passed)

                sleep(self.DELAY)  # DELAY in seconds
                if not (event.x < self.x1 or event.x > self.x2 or event.y < self.y1 or event.y > self.y2):
                    self.line_points_id.append(self.c.create_line(self.old_x + self.right_shift, self.old_y, event.x + self.right_shift, event.y,
                                       width=self.line_width, fill=self.default_color, capstyle=ROUND, smooth=TRUE,
                                       splinesteps=36))

                    if self.error_start_counter:
                        if self.is_first_point:
                            self.is_first_point = False
                            self.line_points_id.append(self.c.create_line(event.x + self.right_shift, event.y, self.x , self.y,width=3))
                            self.fx = event.x + self.right_shift
                            self.fy = event.y

                        # calculating distance from center
                        distance_circle = abs(
                            math.sqrt((event.x - self.x + self.right_shift) ** 2 + (event.y - self.y) ** 2) - self.radius)

                        distance = round(distance_circle, 2)

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
        self.is_first_point = True
        self.angle_steps_passed = [False, False, False, False]

if __name__ == '__main__':
    Paint()