from time import sleep
from random import random

class Network():
    def __init__(self):
        self.delay = 0
        self.probability_packet_loss = 0

    def simulate_network(self):
        if random() < self.probability_packet_loss:
            return 1
        sleep(self.delay)
        return 0

    def has_delay(self):
        return self.delay > 0
    def has_packet_loss(self):
        return self.probability_packet_loss > 0
