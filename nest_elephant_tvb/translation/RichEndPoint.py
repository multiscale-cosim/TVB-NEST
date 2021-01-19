# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from mpi4py import MPI
import pathlib

def make_connections(path_to_files_receive, path_to_files_send, logger_master):
    '''
    Rich End Point. Still a first draft, will be changed to a proper interface.
    This function establishes two MPI intercommunicators. One to NEST and one to TVB.
    :param path_to_files_receive: path to file, store information about receiving MPI connection
    :param path_to_files_send: path to file, store information about sending MPI connection
    :param logger_master: main logger for the connections
    '''
    use_mpi = True
    # init MPI
    if use_mpi:
        comm = MPI.COMM_WORLD  # INTRA communicator
        info = MPI.INFO_NULL
        root=0
    else:
        comm = None
    ### nest connection
    comm_receiver, port_receive = nest_connection(comm, root, info, logger_master, path_to_files_receive)
    ### tvb connecction
    comm_sender, port_send = tvb_connection(comm, root, info, logger_master, path_to_files_send)
    logger_master.info('Connections made, starting translation...')
    
    return comm, comm_receiver, port_receive, comm_sender, port_send


def nest_connection(comm, root, info, logger_master, path_to_files_receive):
    '''
    MPI inter communicator to NEST
    
    '''
    logger_master.info('Translate Receive: before open_port')
    if comm.Get_rank() == 0:
        ### Connection to simulation (incoming data)
        port_receive = MPI.Open_port(info)
        logger_master.info('Translate Receive: after open_port: '+port_receive)
        # Write file configuration of the port
        fport = open(path_to_files_receive, "w+")
        fport.write(port_receive)
        fport.close()
        pathlib.Path(path_to_files_receive+'.unlock').touch()
        logger_master.info('Translate Receive: path_file: ' + path_to_files_receive)
    else:
        port_receive = None
    
    # broadcast port info, accept connection on all ranks!
    # necessary to avoid problems with information about the mpi rank in open port file.
    port_receive = comm.bcast(port_receive,root) # TODO: ask Lena if this is needed/correct.
    logger_master.info('Translate Receive: Rank ' + str(comm.Get_rank()) + ' accepting connection on: ' + port_receive)
    comm_receiver = comm.Accept(port_receive, info, root) 
    logger_master.info('Translate Receive: Simulation client connected to' + str(comm_receiver.Get_rank()))
    
    return comm_receiver, port_receive


def tvb_connection(comm, root, info, logger_master, path_to_files_send):
    '''
    MPI inter communicator to TVB
    
    '''
    logger_master.info('Translate SEND: before open_port')
    if comm.Get_rank() == 0:
        ### Connection to simulation (incoming data)
        port_send = MPI.Open_port(info)
        logger_master.info('Translate SEND: after open_port : '+port_send)
        # Write file configuration of the port
        fport = open(path_to_files_send, "w+")
        fport.write(port_send)
        fport.close()
        pathlib.Path(path_to_files_send+'.unlock').touch()
        logger_master.info('Translate SEND: path_file: ' + path_to_files_send)
    else:
        port_send = None
    
    # broadcast port info, accept connection on all ranks!
    # necessary to avoid problems with information about the mpi rank in open port file.
    port_send = comm.bcast(port_send,root)
    logger_master.info('Translate SEND: Rank ' + str(comm.Get_rank()) + 'accepting connection on: ' + port_send)
    comm_sender = comm.Accept(port_send, info, root) 
    logger_master.info('Translate SEND: Simulation client connected to' + str(comm_sender.Get_rank()))
    
    return comm_sender, port_send


def close_and_finalize(port_send, port_receive, logger_master):
    # close port
    MPI.Close_port(port_send)
    MPI.Close_port(port_receive)
    logger_master.info('close communicator')
    # finalise MPI
    MPI.Finalize()




'''
# TODO: use this code from Wouter for proper FAT END POINTS
# taken from second refactor at: 
# https://gitlab.version.fz-juelich.de/klijn1/co-simulation-tvb-nest/-/blob/refactor/nest_elephant_tvb/simulation/file_translation/nest_to_tvb.py


class FatEndPoint():
    #TODO: Class still contains MPI, should be refactored to have a generic connection
    # TODO: Composition version inheritance: 
    def __init__(self, path, logger=None, server = False):
        self._path = path
        self._logger = logger      
        self._mpi_info = MPI.INFO_NULL
        self._status = MPI.Status()  
        self._init = False
      
        if server:
            self._set_port()
            #TODO: root = 0 Fix when multi processing translator         
            self._comm = MPI.COMM_WORLD.Accept(self._port, self._mpi_info, 0) 
        else:
            self._get_port()       
            #TODO: root = 0 Fix when multi processing translator         
            self._comm = MPI.COMM_WORLD.Connect(self._port)

    def _get_port(self):
        self._wait_for_unlock_of_port_file()

        with open(self._path, "r") as fport:
            self._port = fport.readline()

    def _wait_for_unlock_of_port_file(self):
        # Wait for the port file to become available
        max_mpi_connection_attempts = 50
        file_unlock=False
        for attempt in range(max_mpi_connection_attempts):
            if os.path.exists(self._path+".unlock"):
                print ("simulated_nest_generator: MPI connection file available after t={0} seconds".format(attempt));sys.stdout.flush()
                file_unlock=True
                break

            time.sleep(1)

        if file_unlock is False:
            print("simulated_nest_generator: Could file not unlocked after t={0} attempts, exit".format(max_mpi_connection_attempts));sys.stdout.flush()
            sys.exit (1)

    def _set_port(self):   
        self._port = MPI.Open_port(self._mpi_info)

        # Write file configuration of the port  
        with  open(self._path, "w+") as file:
            file.write(self._port)

        # Write the unlock file
        Path(self._path + ".unlock").touch()  

    def finalize(self):  
        # TODO: there should also be an open_connection
        # TODO: There should also be a finalize on the subclass?        
        self._comm.Disconnect()
        MPI.Close_port(self._port)

    def receive_status(self, source = 0):
        # TODO: rename to get_status_other_side
        # TODO: This status feels more like something one level higher on the protocol
        # Challenge, currently tightly coupled to  MPI
        # TODO: Maybe there should be two statusses? status endpoint and status com channel?
        check = np.empty(1,dtype="b")
        self._comm.Recv([check, 1, MPI.CXX_BOOL], source=source, tag=MPI.ANY_TAG, status=self._status)
        #TODO tag = self._status.Get_tag() 
        if self._status.Get_tag() == 0:
            return FatEndpointState.READY_FOR_SEND

        elif self._status.Get_tag() == 1:
            return FatEndpointState.END_EPOCH

        elif self._status.Get_tag() == 2:
            return FatEndpointState.END_APPLICATION

        elif self._status.Get_tag() == 3:
            return FatEndpointState.READY_FOR_RECEIVE

        else:
            # TODO: fix exception handling
            raise Exception("encountered unknown receive status")

    def send_status(self, com_state):
        # TODO: refactor out all the tag magic
        # call the underlaying functions pending the status type
        if com_state is FatEndpointState.READY_FOR_SEND:
            self._comm.Send([np.array([True],dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=0)

        elif com_state is FatEndpointState.END_EPOCH: 
           self._comm.Send([np.array([True],dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=1)

        elif com_state is FatEndpointState.END_APPLICATION:
            time.sleep(.05)  # TODO: I don't like these grace period sleeps. Find out root cause
            self._comm.Send([np.array([True], dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=2)

        elif com_state is FatEndpointState.READY_FOR_RECEIVE:
            self._comm.Send([np.array([True],dtype='b'), 1, MPI.CXX_BOOL], dest=0, tag=3)
'''
