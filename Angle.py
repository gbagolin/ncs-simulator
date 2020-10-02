import math
class Angle:
    def __init__(self, p1, p2, p3):
        self.p1 = p1
        self.p2 = p2
        self.p3 = p3
        self.angle = self.get_angle()

    def get_angle(self):
        ang = math.degrees(math.atan2(self.p3.y - self.p2.y, self.p3.x - self.p2.x) - math.atan2(self.p1.y - self.p2.y, self.p1.x - self.p2.x))
        return ang + 360 if ang < 0 else ang
