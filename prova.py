#!/usr/bin/python3

__author__ = 'Michele Penzo'

from tkinter import *
from Point import Point
from Angle import Angle
from time import sleep
import math


def round_corner(angle_steps):
    return all(angle_steps)


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
    circle_center = Point(1300, 500)
    radius = 300 - default_pen_size

    error_start_counter = False
    is_first_point = True

    # coordinates of rectangle
    left_down_rectangle_point = Point(100, circle_center.y - 400)
    right_up_rectangle_point = Point(800, circle_center.y + 400)

    first_point_drawn = Point(None, None)
    # right shift, from scratchpad to circle
    right_shift = 800
    # 90   #180   #270   #360
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
        left_circle_point = Point(self.circle_center.x - self.radius, self.circle_center.y - self.radius)
        right_circle_point = Point(self.circle_center.x + self.radius, self.circle_center.y + self.radius)

        self.c.create_oval(left_circle_point.x, left_circle_point.y, right_circle_point.x, right_circle_point.y,
                           outline="#ff0000", fill="#add4d9", width=self.default_pen_size)

        self.c.create_line(self.circle_center.x, self.circle_center.y - self.radius - 10, self.circle_center.x,
                           self.circle_center.y - self.radius + 10, width=3)

        self.c.create_rectangle(self.left_down_rectangle_point.x, self.left_down_rectangle_point.y,
                                self.right_up_rectangle_point.x, self.right_up_rectangle_point.y, outline="#000000",
                                fill="#bfbfbf",
                                width=self.default_pen_size)

        center_x = self.left_down_rectangle_point.x + (
                (self.right_up_rectangle_point.x - self.left_down_rectangle_point.x) / 2)
        mylabel = self.c.create_text((center_x, self.left_down_rectangle_point.y - 20), text="Disegna qui sotto!",
                                     font=("Helvetica", 16))

        self.setup()

        self.root.mainloop()

    # set base values
    def setup(self):
        self.old_point = Point(None, None)

        self.line_width = self.default_pen_size
        self.color = self.default_color

        self.c.bind('<B1-Motion>', self.paint)
        self.c.bind('<ButtonRelease-1>', self.reset)

    # method for writing on whiteboard
    def paint(self, event):

        if round_corner(self.angle_steps_passed):
            print("Hai finitooo")
        else:
            if self.old_point.x and self.old_point.y:
                # test angle
                if self.first_point_drawn.x and self.first_point_drawn.y:

                    p1 = Point(event.x + self.right_shift, event.y)

                    angle = Angle(self.first_point_drawn, self.circle_center, p1).angle

                    if angle > 0 and angle < 90:
                        self.angle_steps_passed[0] = True
                    elif angle > 90 and angle < 180:
                        self.angle_steps_passed[1] = True
                    elif angle > 270 and angle < 360:
                        self.angle_steps_passed[2] = True
                    if angle > 359 and self.angle_steps_passed[2]:
                        self.angle_steps_passed[3] = True

                    print(self.angle_steps_passed)

                sleep(self.DELAY)  # DELAY in seconds

                if not (event.x < self.left_down_rectangle_point.x or event.x > self.right_up_rectangle_point.x
                        or event.y < self.left_down_rectangle_point.y or event.y > self.right_up_rectangle_point.y):
                    self.line_points_id.append(
                        self.c.create_line(self.old_point.x + self.right_shift, self.old_point.y,
                                           event.x + self.right_shift, event.y,
                                           width=self.line_width, fill=self.default_color, capstyle=ROUND, smooth=TRUE,
                                           splinesteps=36))

                    if self.error_start_counter:
                        if self.is_first_point:
                            self.is_first_point = False
                            self.line_points_id.append(
                                self.c.create_line(event.x + self.right_shift, event.y, self.circle_center.x, self.circle_center.y, width=3))
                            self.first_point_drawn.x = event.x + self.right_shift
                            self.first_point_drawn.y = event.y

                        # calculating distance from center
                        distance_circle = abs(
                            math.sqrt(
                                (event.x - self.circle_center.x + self.right_shift) ** 2 + (event.y - self.circle_center.y) ** 2) - self.radius)

                        distance = round(distance_circle, 2)

                        self.total_error += abs(distance)
                        self.label_error['text'] = round(distance, 2)
                        self.label_total_error['text'] = round(self.total_error, 2)

            self.old_point.x = event.x
            self.old_point.y = event.y

    # reset value
    def reset(self, event):
        self.old_point.x = None
        self.old_point.y = None

    def start(self):
        self.error_start_counter = True
        # reset counters
        self.total_error = 0
        self.label_error['text'] = 0
        self.label_total_error['text'] = 0
        # delete lines on canvas
        for point in self.line_points_id:
            self.c.delete(point)

        self.is_first_point = True
        self.angle_steps_passed = [False, False, False, False]

if __name__ == '__main__':
    Paint()
