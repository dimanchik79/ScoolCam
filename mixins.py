import time


class SetMessage:
    def __init__(self, time_label: object, messsage: str, color_style: str):
        time_label.setText(messsage)
        time_label.setStyleSheet(color_style)


class TimeRuner:
    def __init__(self, time_show: object):
        self.second = None
        self.minute = None
        self.hour = None
        self.time_show = time_show
        
    def timer_set_zero(self):
        self.hour = 0
        self.minute = 0
        self.second = 0

    def run_time(self):
        self.time_show.setText(f'[{self.hour:02d}:{self.minute:02d}:{self.second:02d}]')
        if self.second != 59:
            self.second += 1
        else:
            self.second = 0
            if self.minute != 59:
                self.minute += 1
            else:
                self.minute = 0
                self.hour += 1
        time.sleep(1)
