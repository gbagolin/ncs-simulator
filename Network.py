from time import sleep
from random import random

class Network():
    def __init__(self, delay, probability_packet_loss):
        self.delay = delay
        self.probability_packet_loss = probability_packet_loss

    def simulate_network(self):
        sleep(self.delay)
        return random() < self.probability_packet_loss

    def has_delay(self):
        return self.delay > 0

