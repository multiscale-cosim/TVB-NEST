from mpi4py import MPI
import pathlib
import os
from nest_elephant_tvb.utils import create_logger

class MPI_communication_extern:

    def __init__(self,name,path,level_log,communication_intern,**karg):
        self.logger = create_logger(path,name, level_log)
        self.name = name
        self.ports = []
        self.path_ports = []
        self.logger.info('end MPI extern init')
        self.communication_internal = communication_intern(self.logger,**karg)

    def run(self,path_connection):
        if path_connection is not None:
            self.logger.info('create connection')
            self.create_connection(path_connection)
        self.simulation_time()
        if path_connection is not None:
            self.close_connection()
        self.finalise()

    def create_connection(self,paths,info=MPI.INFO_NULL,comm=MPI.COMM_SELF):
        '''
        MPI inter communicator to NEST

        '''
        self.logger.info('Translate Receive: before open_port')
        ### Connection to simulation (incoming data)
        port = MPI.Open_port(info)
        self.ports.append(port)
        for path in paths:
            self.logger.info('Translate '+self.name+': after open_port: ' + port)
            # Write file configuration of the port
            fport = open(path, "w+")
            fport.write(port)
            fport.close()
            pathlib.Path(path + '.unlock').touch()
            self.logger.info('Translate '+self.name+': path_file: ' + path)
            self.path_ports.append(path)
            self.logger.info('Wait for Translate : '+port)
        self.port_comm = comm.Accept(port, info, 0)
        self.logger.info('Connection accepted')

    def simulation_time(self,*args):
        raise Exception('not yet implemented')

    def close_connection(self):
        self.logger.info("close connection")
        for port in self.ports:
            MPI.Close_port(port)
        for path in self.path_ports:
            os.remove(path)
        self.logger.info("close connection : delete file ")
        self.port_comm.Disconnect()
        self.logger.info("disconnect connection ")

    def finalise(self):
        self.logger.info("finalise")
        end = self.communication_internal.finalise()
        if end:
            self.logger.info(" real finalise")
            MPI.Finalize()
