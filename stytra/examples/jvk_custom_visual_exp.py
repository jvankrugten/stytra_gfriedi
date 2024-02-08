#python -m stytra.jvk.jvk_custom_visual_exp.py

import socket
import json
from stytra import Stytra, Protocol
from stytra.stimulation.stimuli import VisualStimulus
from PyQt5.QtCore import QRect
from PyQt5.QtGui import QBrush, QColor
from pathlib import Path 

REQUIRES_EXTERNAL_HARDWARE = False

 

class NoStimulusVR(VisualStimulus):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
 
    def update(self):
        fish_vel = self._experiment.estimator.get_velocity()
        self.send_data_over_tcp(fish_vel)

        return fish_vel

    def send_data_over_tcp(self, fish_velocity):
        # Create a TCP/IP socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('f462i-8840e6', 12346)  # Fixed the server address format
        server_socket.bind(server_address)
        server_socket.listen(1)
        print("Waiting for a connection...")
        connection, client_address = server_socket.accept()
        print("Connection established with:", client_address)

        try:
            while True:
                data = {'fish_velocity': fish_velocity}
                serialized_data = json.dumps(data).encode('utf-8')
                connection.sendall(serialized_data)
        finally:
            # Clean up the connection
            connection.close()

 
class CustomProtocol(Protocol):

    name = "custom protocol"  # protocol name
    stytra_config = dict(
        tracking=dict(method="tail", estimator="vigor"),
        camera=dict(
            video_file=str(Path(__file__).parent / "assets" / "fish_compressed.h5")
        ),
    )

 
    def get_stim_sequence(self):
        return [NoStimulusVR(duration=1000)]

  

if __name__ == "__main__":
    Stytra(protocol=CustomProtocol())