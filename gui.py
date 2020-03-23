import time
import curses


class GUI:
    def __init__(self):
        self.results = {}
        self.scr = None
        self.frame = 0

    def run(self):
        curses.wrapper(self.loop)

    def update(self, results):
        self.results = results
        self.render()

    def render(self):
        if self.scr == None:
            return
        self.scr.clear()
        self.render_results(1, 3)
        self.scr.addstr(1, 1, str(self.frame))
        self.scr.refresh()
        self.frame += 1

    def loop(self, scr):
        self.scr = scr
        while True:
            time.sleep(1)

    def render_results(self, x, y):
        y_offset = 0
        for register, value in self.results.items():
            self.scr.addstr(y + y_offset, x, f"{register.name}={value}")
            y_offset += 1
