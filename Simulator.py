#!/usr/bin/python3

__author__ = 'Michele Penzo'

from tkinter import *
from Point import Point
from Angle import Angle
import numpy as np
from Network import Network
import math


class Paint(object):
    # default parameters
    default_pen_size = 4.0
    default_color = 'black'

    line_points_id = []

    # starting coordinate of circle --> not the center of monitor
    circle_center = Point(1300, 500)
    radius = 300 - default_pen_size

    error_start_counter = False
    is_first_point = True

    max_drawable_x = 300

    # coordinates of rectangle
    left_down_rectangle_point = Point(100, circle_center.y - 400)
    right_up_rectangle_point = Point(800, circle_center.y + 400)

    left_down_rectangle_point_green_area_1 = Point(100 + 100, circle_center.y - 400)
    right_up_rectangle_point_green_area_1 = Point(800 - 100, max_drawable_x)

    left_down_rectangle_point_green_area_2 = Point(100 + 100, circle_center.y + 400)
    right_up_rectangle_point_green_area_2 = Point(800 - 100, 700)

    first_point_drawn = Point(None, None)
    # right shift, from scratchpad to circle
    right_shift = 800

    first_quadrant = False
    fourth_quadrant = False
    mouse_event_stopped = False
    is_second_point_drawn = True

    button_released = False
    first_quadrant_second_step = False
    fourth_quadrant_second_step = False
    step_passed = False

    distance = 0

    done = False

    rec_pressed = False

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
        self.label_total_error.grid_propagate(False)

        # start button
        self.start_button = Button(self.root, text='Inizia', font=("Helvetica", 16), command=self.start)
        self.start_button.grid(sticky=W, row=0, column=4)
        self.start_button.grid_propagate(False)

        # what_to_do_label
        self.label_state = Label(self.root, text='Stato', font=("Helvetica", 16))
        self.label_state.grid(sticky=W, row=0, column=5, padx=100)

        # getting the coordinates
        left_circle_point = Point(self.circle_center.x - self.radius, self.circle_center.y - self.radius)
        right_circle_point = Point(self.circle_center.x + self.radius, self.circle_center.y + self.radius)

        self.c.create_oval(left_circle_point.x, left_circle_point.y, right_circle_point.x, right_circle_point.y,
                           outline="#ff0000", fill="#add4d9", width=self.default_pen_size)

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
        self.network = Network()

        self.label_state['text'] = 'Prova a disegnare e quando sei pronto premi inizia'

    # method for writing on whiteboard
    def paint(self, event):
        # instant error
        # check if 360 degrees have been drawn
        if self.done and not self.button_released:
            self.label_state['text'] = "Hai fatto un angolo giro, ora confronta l'errore con le prove precedenti"
            self.label_total_error['text'] = round(self.total_error - abs(self.distance), 2)

        elif self.done and self.button_released:
            self.label_state['text'] = "Hai fatto un angolo giro, ma hai rilasciato il mouse, esperimento non valido"
            self.label_total_error['text'] = round(self.total_error - abs(self.distance), 2)
        else:
            if self.old_point.x and self.old_point.y:

                # object network simulates the network, simulate a packet loss.
                if self.network.simulate_network():
                    return

                # check point is drawn inside the rectangle.
                if not (event.x < self.left_down_rectangle_point.x or event.x > self.right_up_rectangle_point.x
                        or event.y < self.left_down_rectangle_point.y or event.y > self.right_up_rectangle_point.y):

                    # button "INIZIA" has been pressed"
                    if self.error_start_counter:

                        # First point drawn
                        if self.is_first_point:
                            print(self.rec_pressed)
                            if self.rec_pressed:
                                self.label_state['text'] = 'Ricalca la circonferenza facendo un angolo giro'
                                self.is_first_point = False
                                # CALCULATE STRAIGHT LINE PASSING FROM POINTS (CENTER.X, CENTER.Y) AND (EVENT.X + RIGHT_SHIFT, EVENT.Y)
                                x = [event.x + self.right_shift, self.circle_center.x]
                                y = [event.y, self.circle_center.y]
                                coefficients = np.polyfit(x, y, 1)

                                point_x1 = ((self.right_up_rectangle_point.y - coefficients[1]) / coefficients[0])
                                point_y1 = self.right_up_rectangle_point.y

                                point_x2 = ((self.left_down_rectangle_point.y - coefficients[1]) / coefficients[0])
                                point_y2 = self.left_down_rectangle_point.y

                                # print(coefficients)

                                line_id = self.c.create_line(point_x1, point_y1, point_x2, point_y2, width=7,
                                                             fill='orange')

                                self.line_points_id.append(line_id)

                                self.first_point_drawn.x = event.x + self.right_shift
                                self.first_point_drawn.y = event.y
                                self.c.delete(self.rectangle_up_id)
                                self.c.delete(self.rectangle_down_id)
                        else:
                            if self.first_point_drawn.x and self.first_point_drawn.y:
                                line_id = self.c.create_line(self.old_point.x + self.right_shift, self.old_point.y,
                                                             event.x + self.right_shift, event.y,
                                                             width=self.line_width, fill=self.default_color,
                                                             capstyle=ROUND,
                                                             smooth=TRUE,
                                                             splinesteps=36)

                                self.line_points_id.append(line_id)

                                # calculating distance from center
                                distance_circle = abs(
                                    math.sqrt(
                                        (event.x - self.circle_center.x + self.right_shift) ** 2 + (
                                                event.y - self.circle_center.y) ** 2) - self.radius)

                                distance_between_old_evn_new_evn = 0
                                old_error = self.distance
                                if self.network.has_delay() and self.old_point.x and self.old_point.y:
                                    distance_between_old_evn_new_evn = abs(
                                        math.sqrt(
                                            (event.x - self.old_point.x + self.right_shift) ** 2 + (
                                                    event.y - self.old_point.y) ** 2) - self.radius)

                                self.distance = round(distance_circle, 2)
                                self.total_error += abs(self.distance) + round(distance_between_old_evn_new_evn,
                                                                               2) * old_error
                                self.label_error['text'] = round(self.distance, 2)
                                self.label_total_error['text'] = round(self.total_error, 2)

                                # point drawn
                                p1 = Point(event.x + self.right_shift, event.y)
                                # angle between the center of the cirle, the point drawn and the first point drawn.
                                angle = Angle(self.first_point_drawn, self.circle_center, p1).angle
                                # check where the angle stays.
                                # print(angle)

                                if angle > 0 and angle < 90 and self.is_second_point_drawn:
                                    self.is_second_point_drawn = False
                                    self.first_quadrant = True
                                    self.label_state[
                                        'text'] = 'Ricalca la circonferenza facendo un angolo giro in senso ORARIO'
                                elif angle > 90 and self.first_quadrant:
                                    self.step_passed = True
                                elif self.first_quadrant and self.step_passed and angle > 0 and angle < 90 and not self.is_second_point_drawn:
                                    self.done = True

                                if angle > 270 and angle < 360 and self.is_second_point_drawn:
                                    self.is_second_point_drawn = False
                                    self.fourth_quadrant = True
                                    self.label_state[
                                        'text'] = 'Ricalca la circonferenza facendo un angolo giro in senso ANTI-ORARIO'
                                elif angle < 270 and self.fourth_quadrant:
                                    self.step_passed = True
                                elif self.fourth_quadrant and self.step_passed and angle > 270 and angle < 360 and not self.is_second_point_drawn:
                                    self.done = True



            self.old_point.x = event.x
            self.old_point.y = event.y

    # reset value
    def reset(self, event):
        self.old_point.x = None
        self.old_point.y = None
        self.button_released = True

    def rec_event(self, event):
        self.rec_pressed = True

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
        self.is_second_point_drawn = True
        self.step_passed = False
        self.done = False
        self.button_released = False
        self.first_quadrant = False
        self.fourth_quadrant = False
        self.first_point_drawn.x = None
        self.first_point_drawn.y = None

        self.rectangle_up_id = self.c.create_rectangle(self.left_down_rectangle_point_green_area_1.x,
                                                       self.left_down_rectangle_point_green_area_1.y,
                                                       self.right_up_rectangle_point_green_area_1.x,
                                                       self.right_up_rectangle_point_green_area_1.y,
                                                       outline="#000000",
                                                       fill="green",
                                                       width=self.default_pen_size
                                                       )

        self.rectangle_down_id = self.c.create_rectangle(self.left_down_rectangle_point_green_area_2.x,
                                                         self.left_down_rectangle_point_green_area_2.y,
                                                         self.right_up_rectangle_point_green_area_2.x,
                                                         self.right_up_rectangle_point_green_area_2.y,
                                                         outline="#000000",
                                                         fill="green",
                                                         width=self.default_pen_size
                                                         )
        self.c.tag_bind(self.rectangle_up_id, "<Button-1>", self.rec_event)
        self.c.tag_bind(self.rectangle_down_id, "<Button-1>", self.rec_event)
        self.rec_pressed = False


if __name__ == '__main__':
    Paint()
