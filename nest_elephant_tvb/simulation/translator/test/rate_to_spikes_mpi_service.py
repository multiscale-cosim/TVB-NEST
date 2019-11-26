from translator.rate_spike import rates_to_spikes
from quantities import s, kHz
import numpy as np
import numpy.random as rgn
from mpi4py import MPI
import os.path

#Start communication channels
comm = MPI.COMM_WORLD
path_to_files = "/home/sandra/Documents/Cosim/"

#For TVB
# Init connection
tvb_port = MPI.Open_port(MPI.INFO_NULL)
print("Writing port details")
fport_path = path_to_files + "trans_tvb_port.txt"
fport = open(fport_path, "w")
fport.write(tvb_port)
fport.close()
print ("Accepting from: " + tvb_port +"\n")
tvb_comm = comm.Accept(tvb_port, MPI.INFO_NULL, root = 0)
rank_tvb = tvb_comm.Get_rank()
print ("Connected, I'm rank: "+str(rank_tvb)+"\n")
print ("Connected to TVB\n")

#For NEST
# Init connection
print("Waiting for port details")
nest_port_path = path_to_files + "nest_port.txt"
while not os.path.exists(nest_port_path):
  pass
fport = open(nest_port_path, "r")
nest_port = fport.read()
fport.close()
print ("Connecting to: " + nest_port +"\n")
nest_comm = comm.Connect(nest_port, MPI.INFO_NULL)
print ("Connected to NEST\n")

#test one rate
i = 0
while(True):
    rate = tvb_comm.recv(source=0)
    print(rate)
    spike = rates_to_spikes(rate*kHz,t_start=(1.0*i)*s,t_stop=(1.0*(i+1))*s)
    print(spike)
    i = i +1
    for n in range(spike.shape[1]):
      print("What I am sending: "+str(np.array([int(spike[0][n]*1000.0)], dtype=np.int32))+"\n")
      nest_comm.Send([np.array([int(spike[0][n]*1000.0)], dtype=np.int32), MPI.INT], dest=0)
    
    


