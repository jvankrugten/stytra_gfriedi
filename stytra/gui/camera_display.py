from PyQt5.QtCore import QTimer, Qt, QRectF
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg
from queue import Empty
import numpy as np
from stytra.paramqt import ParameterGui
from stytra.metadata import MetadataCamera
from PIL import Image

class CameraViewWidget(QWidget):
    def __init__(self, camera_queue, control_queue=None, camera_rotation=0):
        """ A widget to show the camera and display the controls

        """

        super().__init__()
        self.camera_display_widget = pg.GraphicsLayoutWidget()

        self.display_area = pg.ViewBox(lockAspect=1, invertY=False)
        self.camera_display_widget.addItem(self.display_area)
        self.display_area.setRange(QRectF(0, 0, 640, 640), update=True,
                                   disableAutoRange=True)
        self.image_item = pg.ImageItem()
        self.display_area.addItem(self.image_item)
        self.timer = QTimer()
        self.timer.start(0)
        self.timer.setSingleShot(False)
        self.timer.timeout.connect(self.update_image)
        self.camera_queue = camera_queue
        self.control_queue = control_queue
        self.camera_rotation = camera_rotation
        self.update_image()
        self.centre = np.array([0, 0])

        self.layout = QVBoxLayout()

        self.layout.addWidget(self.camera_display_widget)
        if control_queue is not None:
            self.metadata = MetadataCamera()
            self.control_widget = ParameterGui(self.metadata)
            self.layout.addWidget(self.control_widget)
            for control in self.control_widget.parameter_controls:
                control.control_widget.valueChanged.connect(self.update_controls)
            self.control_queue = control_queue

        self.captureButton = QPushButton('Catpure frame')
        self.captureButton.clicked.connect(self.save_image)
        self.layout.addWidget(self.captureButton)

        self.setLayout(self.layout)

    def update_controls(self):
        self.control_widget.save_meta()
        self.control_queue.put(self.metadata.get_param_dict())

    def update_image(self):
        try:
            im_in = self.camera_queue.get(timeout=0.001)
            if self.camera_rotation >= 1:
                im_in = np.rot90(im_in, k=self.camera_rotation)

            self.centre = np.array(im_in.shape[::-1])/2
            self.image_item.setImage(im_in)
        except Empty:
            pass

    def save_image(self):
        pass
        # TODO write saving


class CameraTailSelection(CameraViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = pg.TextItem('Select tail of the fish:\n' +
                                 'left click start, right click end')
        self.roi_tail = pg.LineSegmentROI(((320, 480), (320, 0)),
                                          pen=dict(color=(250, 10, 10),
                                                   width=4))
        self.display_area.addItem(self.roi_tail)

    def get_tail_coords(self):
        return self.roi_tail.listPoints()


class CameraViewCalib(CameraViewWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.points_calib = pg.ScatterPlotItem()
        self.display_area.addItem(self.points_calib)

    def show_calibration(self, calibrator):
        if calibrator.proj_to_cam is not None:
            camera_points = np.pad(calibrator.points, ((0, 0), (0, 1)),
                                   mode='constant', constant_values=1) @ calibrator.proj_to_cam.T

            points_dicts = []
            for point in camera_points:
                xn, yn = point[::-1]
                points_dicts.append(dict(x=xn, y=yn, size=8, brush=(210, 10, 10)))

            self.points_calib.setData(points_dicts)


if __name__=='__main__':
    from multiprocessing import Queue
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    q = Queue()
    for i in range(100):
        q.put(np.random.randint(0, 255, (640, 480), dtype=np.uint8))

    w = CameraTailSelection(q, 'b')
    w.show()
    app.exec_()
