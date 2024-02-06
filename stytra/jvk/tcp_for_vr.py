
""" 
This is where JvK tries to put together a tcp protocol that will send relevant information to the VR python.
""" 

""" 
Look in stytra.estimators for usefull information that is obtained by the tracking, caculated online and used in 
example scripts (like combined_conditional_exp), and the closed loop stimulus (stimulation/stimuli/closed_loop), 
estimators that seem to be updated online are found in the script: stytra/stimulation/estimators
"""

""" 
To think about:
Stytra will not tell the VR the exact same thing as LabVIEW did (forward, yaw, self.globalFrameIdentifier, self.labviewState, self.twoPfram), 
so we have to change something on whatever end of the tcp/ip

Make sure (check other closed loop protocols) that it is send online
""" 

""" 
We have to:
initiate the port, 
provide it with an adress to send stuff to,
get together the data we want to send (from stytra tracking to VR),
package it in tcp format,
send it.
"""

import socket

if __name__ == "__main__":
    address = "tcp://{}:5555".format(socket.gethostbyname(socket.gethostname())) #this ine is from the ymq_trigger stytra script, the tcp/ip lines below are copied from the VR code
    
    # set up Transmission Control Protocol
    self.tcp_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)  # instantiate TCP/IP socket for communication
    self.tcp_socket.connect(("localhost", 6341))  # open socket on 127.0.0.1 with specified port 6341

    # set up data to send, something like: 
    fish_vel = self._experiment.estimator.get_velocity()
    fish_vel_insta = self._experiment.estimator.get_istantaneous_velocity()
    fish_bouts = self._experiment.estimator.get_bout_occured()

    # make datagram from tcp/ip
    sData = struct.pack('>ddddi', fish_vel,fish_vel_insta,fish_bouts) #change the '>ddddi' to the data types and byte order of the data
    # tcp/ip connection: send datagram
    self.tcp_socket.sendall(sData)
    # 
    # 