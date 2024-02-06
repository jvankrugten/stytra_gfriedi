import time
import json
import socket
from pathlib import Path
from stytra import Stytra
from stytra.examples.gratings_exp import GratingsProtocol
from stytra.stimulation.estimators import VigorMotionEstimator


class TrackingGratingsProtocol(GratingsProtocol):
    name = "gratings_tail_tracking"

    # To add tracking to a protocol, we simply need to add a tracking
    # argument to the stytra_config:
    stytra_config = dict(
        tracking=dict(embedded=True, method="tail"),
        camera=dict(
            min_framerate=60,
            video_file=str(Path(__file__).parent / "assets" / "fish_compressed.h5")
        ),
    )

    def get_fish_vel(self):
        """Function that updates the estimated fish velocity. Change to add lag or
        shunting.
        """
        self.fish_vel = self._experiment.estimator.get_velocity()

    def send_data(self, data):
        HOST = 'f462i-8840e6'  # The server's hostname or IP address
        PORT = 12345        # The port used by the server

        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(data).encode())

if __name__ == "__main__":
    protocol = TrackingGratingsProtocol()

    # Initialize Stytra and start the protocol
    stytra = Stytra(protocol)
    stytra.start()

    while True:
        # Gather data from your protocol
        protocol.get_fish_vel()  # Update fish velocity
        data = protocol.fish_vel  # Access fish velocity

        # Send data via TCP
        protocol.send_data(data)

        time.sleep(1)  # Adjust the delay as needed
