# Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from mpi4py import MPI
import pathlib

def make_connections(path_to_files_receive, path_to_files_send, logger_master):
    '''
    Rich End Point, first draft, to be changed soon.
    This function establishes two MPI intercommunicators, e.g. one to NEST and one to TVB.
    Currently:
        - either as a 'nest_to_tvb' server, with sender 'nest' and receiver 'tvb'
        - or vice versa
    The goal is to have a 'transformer' (one for each direction) which CONTAINS a RichEndPoint
    
    :param path_to_files_receive: path to file, store information about receiving MPI connection
    :param path_to_files_send: path to file, store information about sending MPI connection
    :param logger_master: main logger for the connections
    '''
    # NOTE: this is a placeholder. The whole RichEndPoint will be implemented properly soon.
    use_mpi = True 
    # init MPI
    if use_mpi:
        comm = MPI.COMM_WORLD  # INTRA communicator
        info = MPI.INFO_NULL
        root=0
    else:
        comm = None
    
    ### receiver connection
    comm_receiver, port_receive = _open_port_accept_connection(comm, root, info, logger_master, path_to_files_receive)
    ### sender connection
    comm_sender, port_send = _open_port_accept_connection(comm, root, info, logger_master, path_to_files_send)
    logger_master.info('Connections made, starting translation...')
    
    return comm, comm_receiver, port_receive, comm_sender, port_send


def _open_port_accept_connection(comm, root, info, logger_master, path_to_files):
    '''
    General MPI Server-Client connection.
    Opens a port and writes the details to file. Then accepts an incoming connection
    from another application on this port. The resulting INTER communicator is returned.
    
    In some MPI implementations, information about the rank is encoded in the port infos.
    Therefore only rank 0 opens the port and broadcasts the relevant info to all other ranks.
    So a M:N connection between two MPI applications is possible.
    
    TODO: better documentation.
    
    :param comm: the INTRA communicator of the calling application ('server') which opens and accepts the connection
    :param root: the root rank on which the 'main' connection before broadcast in done
    :param info: MPI info object
    :param logger_master: the master logger of this cosim run
    :param path_to_files: location of the files 
    
    :return intra_comm: the newly created intra communicator between the two applications
    :return port: the port information, needed to properly close the connection after the job
    '''
    logger_master.info('Transformer: before open port')
    if comm.Get_rank() == root:
        ### Connection to simulation (incoming data)
        port = MPI.Open_port(info)
        logger_master.info('Transformer: after open port, port details:'+port)
        # Write file configuration of the port
        fport = open(path_to_files, "w+")
        fport.write(port)
        fport.close()
        pathlib.Path(path_to_files+'.unlock').touch()
        logger_master.info('Transformer: path to file with port info:' + path_to_files)
    else:
        port = None
    
    # broadcast port info, accept connection on all ranks!
    # necessary to avoid problems with information about the mpi rank in open port file.
    port = comm.bcast(port,root) # TODO: ask Lena if this is needed/correct.
    logger_master.info('Transformer: Rank ' + str(comm.Get_rank()) + ' accepting connection on: ' + port)
    intra_comm = comm.Accept(port, info, root) 
    logger_master.info('Transformer: Simulation client connected to' + str(intra_comm.Get_rank()))
    
    return intra_comm, port


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
