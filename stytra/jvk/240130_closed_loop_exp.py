# file where Jaap tries to play around and understand stytra
# conda activate stytra_env
# python -m stytra.examples.240130_closed_loop_exp


import numpy as np
import pandas as pd
from pathlib import Path

from stytra import Stytra
from stytra.stimulation import Protocol
from stytra.stimulation.stimuli import Basic_CL_1D, GratingStimulus
from lightparam import Param


class ClosedLoop1DProt(Protocol):
    name = "BabyVR_test"

# JvK added the dir, log format and camera attributes, might be wrong)	
    stytra_config = dict(
        display=dict(min_framerate=50),
        tracking=dict(embedded=True, method="tail", estimator="vigor"),
	dir_save= "H:\stytra_data",
	dir_assets= "H:\stytra_resources",
	log_format= "hdf5",
# JvK: use this to use the camera
#	camera=dict(type="ximea", rotation=-1, roi=[0, 0, 784, 784])
# JvK: use this to troubleshoot using a video file
 	camera=dict(
           min_framerate=60,
           video_file=str(Path(__file__).parent / "assets" / "fish_compressed.h5")	
        ),
    )

    def __init__(self):
        super().__init__()

        self.inter_stim_pause = Param(20.0)
        self.grating_vel = Param(10.0)
        self.grating_duration = Param(10.0)
        self.grating_cycle = Param(10.0)

    def get_stim_sequence(self):
        stimuli = []
        # # gratings
        p = self.inter_stim_pause / 2
        v = self.grating_vel
        d = self.grating_duration

        t_base = [0, p, p, p + d, p + d, 2 * p + d]
        vel_base = [0, 0, -v, -v, 0, 0]
        t = []
        vel = []

        t.extend(t_base)
        vel.extend(vel_base)

        df = pd.DataFrame(dict(t=t, base_vel=vel))

        ClosedLoop1DGratings = type("Stim", (Basic_CL_1D, GratingStimulus), {})

        stimuli.append(
            ClosedLoop1DGratings(
                df_param=df,
                grating_angle=np.pi / 2,
                grating_period=self.grating_cycle,
                grating_col_1=(255,) * 3,
            )
        )
        return stimuli


if __name__ == "__main__":
    s = Stytra(protocol=ClosedLoop1DProt())
