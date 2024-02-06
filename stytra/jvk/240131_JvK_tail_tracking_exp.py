from pathlib import Path
from stytra import Stytra
from stytra.examples.gratings_exp import GratingsProtocol


class TrackingGratingsProtocol(GratingsProtocol):
    name = "gratings_tail_tracking"

    # To add tracking to a protocol, we simply need to add a tracking
    # argument to the stytra_config:
    stytra_config = dict(
        tracking=dict(embedded=True, method="tail"),
# JvK: use this to use the camera
#	camera=dict(type="ximea", rotation=-1, roi=[0, 0, 784, 784])
# JvK: use this to troubleshoot using a video file
 	camera=dict(
           min_framerate=60,
           video_file=str(Path(__file__).parent / "assets" / "fish_compressed.h5")	
        ),
    )


if __name__ == "__main__":
    s = Stytra(protocol=TrackingGratingsProtocol())
