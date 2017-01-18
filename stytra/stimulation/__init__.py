from PyQt5.QtCore import pyqtSignal, QTimer, QObject
import datetime
from copy import deepcopy


class Protocol(QObject):
    """ Class that manages the stimulation protocol, includes a timer, updating
        signals etc.

    """

    sig_timestep = pyqtSignal(int)
    sig_stim_change = pyqtSignal(int)
    sig_protocol_finished = pyqtSignal()

    def __init__(self, stimuli, dt):
        super(Protocol, self).__init__()

        self.t_start = None
        self.t = 0
        self.stimuli = stimuli
        self.i_current_stimulus = 0
        self.current_stimulus = stimuli[0]
        self.timer = QTimer()
        self.dt = dt

    def start(self):
        self.t_start = datetime.datetime.now()
        self.timer.timeout.connect(self.timestep)
        self.timer.setSingleShot(False)
        self.timer.start(self.dt)
        self.current_stimulus.started = datetime.datetime.now()
        self.sig_stim_change.emit(0)

    def timestep(self):
        self.current_stimulus.elapsed = (datetime.datetime.now() - \
                                         self.current_stimulus.started).total_seconds()
        if self.current_stimulus.elapsed > self.current_stimulus.duration:
            if self.i_current_stimulus >= len(self.stimuli)-1:
                self.end()
                self.sig_protocol_finished.emit()
            else:
                self.i_current_stimulus += 1
                self.current_stimulus = self.stimuli[self.i_current_stimulus]
                self.current_stimulus.started = datetime.datetime.now()
                self.sig_stim_change.emit(self.i_current_stimulus)
        self.t = (datetime.datetime.now()-self.t_start).total_seconds()
        self.sig_timestep.emit(self.i_current_stimulus)

    def end(self):
        self.timer.timeout.disconnect()
        self.timer.stop()


