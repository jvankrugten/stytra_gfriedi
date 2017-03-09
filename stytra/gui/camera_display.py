from PyQt5.QtCore import QTimer, Qt, QRectF, QObject
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QPushButton
import pyqtgraph as pg
from queue import Empty
import numpy as np
from paramqt import ParameterGui
from stytra.metadata import MetadataCamera
from stytra.tracking.diagnostics import draw_tail


class CameraViewWidget(QWidget):
    def __init__(self, camera_queue, control_queue=None, camera_rotation=0,
                 camera_parameters=None):
        """
        A widget to show the camera and display the controls
        :param camera_queue: queue dispatching frames to display
        :param control_queue: queue with controls for the camera
        :param camera_rotation:
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
            self.camera_parameters = camera_parameters
            self.control_widget = ParameterGui(self.camera_parameters)
            self.layout.addWidget(self.control_widget)
            for control in self.control_widget.parameter_controls:
                control.control_widget.valueChanged.connect(self.update_controls)
            self.control_queue = control_queue
            self.control_queue.put(self.camera_parameters.get_param_dict())

        self.captureButton = QPushButton('Capture frame')
        self.captureButton.clicked.connect(self.save_image)
        self.layout.addWidget(self.captureButton)

        self.setLayout(self.layout)

    def update_controls(self):
        self.control_widget.save_meta()
        self.control_queue.put(self.camera_parameters.get_param_dict())

    def update_image(self):
        try:
            time, im_in = self.camera_queue.get(timeout=0.001)
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
    def __init__(self, tail_start_points_queue, tail_position_data, *args, **kwargs):
        """
        Widget for select tail points and monitoring tracking in embedded animal.
        :param tail_start_points_queue: queue where to dispatch tail points
        :param tail_position_data: DataAccumulator object with tail tracking data.
        """
        self.tail_position_data = tail_position_data
        super().__init__(*args, **kwargs)

        self.label = pg.TextItem('Select tail of the fish:')

        self.roi_tail = pg.LineSegmentROI(((320, 480), (320, 0)),
                                          pen=dict(color=(250, 10, 10),
                                                   width=4))
        self.display_area.addItem(self.roi_tail)

        self.tail_start_points_queue = tail_start_points_queue

        self.tail_start_points_queue.put(self.get_tail_coords())
        self.roi_tail.sigRegionChanged.connect(self.send_roi_to_queue)

    def send_roi_to_queue(self):
        self.tail_start_points_queue.put(self.get_tail_coords())

    def get_tail_coords(self):
        # Invert x and y:
        start_y = self.roi_tail.listPoints()[0].x()  # start y
        start_x = self.roi_tail.listPoints()[0].y()  # start x
        length_y = self.roi_tail.listPoints()[1].x() - start_y  # delta y
        length_x = self.roi_tail.listPoints()[1].y() - start_x  # delta x
        return {'start_x': start_x, 'start_y': start_y,
                'tail_len_x': length_x, 'tail_len_y': length_y,
                'n_segments': 30, 'window_size': 30}

    def update_image(self):
        position_data = None
        # Try to retrieve data about tail position of available:
        try:
            # Try to get time and frames from the camera queue (cut and paste
            # from CameraViewWidget):
            time, im_in = self.camera_queue.get(timeout=0.0001)

            try:
                if self.tail_position_data:
                    position_data = self.tail_position_data.stored_data[-1][1]
            except IndexError:
                pass



            if self.camera_rotation >= 1:
                im_in = np.rot90(im_in, k=self.camera_rotation)
            self.centre = np.array(im_in.shape[::-1])/2
            if position_data:  # draw the tail before displaying the frame:
                im_in = draw_tail(im_in, position_data)
            self.image_item.setImage(im_in)
        except Empty:
            pass


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


if __name__ == '__main__':
    from multiprocessing import Queue
    from PyQt5.QtWidgets import QApplication
    app = QApplication([])
    q = Queue()
    for i in range(100):
        q.put(np.random.randint(0, 255, (640, 480), dtype=np.uint8))

    w = CameraTailSelection(q, 'b')
    w.show()
    app.exec_()
