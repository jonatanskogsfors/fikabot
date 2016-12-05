import datetime


class Fika:
    def __init__(self, name: str, start: datetime.time, stop: datetime.time):
        self.name = name
        self.start = start
        self.stop = stop
        self.already_announced = False

    def should_be_announced_to_the_world(self):
        return self.is_happening_right_now() and not self.already_announced

    def is_happening_right_now(self):
        now = datetime.datetime.now()
        it_is_a_work_day = now.weekday() < 5
        the_clock_says_its_time = self.start < now.time() < self.stop
        return it_is_a_work_day and the_clock_says_its_time

    def was_announced(self):
        self.already_announced = True
