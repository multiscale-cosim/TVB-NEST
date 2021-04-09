#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import pathlib
import os
from nest_elephant_tvb.utils import create_logger


class MPI_communication_extern:
    """
    Abstract class for MPI communication with a simulator.
    Management of MPI communication for exchange of data with simulator.
    """
    def __init__(self, name, path, level_log, communication_intern, **karg):
        self.logger = create_logger(path, name, level_log)
        self.name = name  # name of module
        self.ports = []  # array to save the MPI port
        self.path_ports = []  # path for sharing the connection ports
        self.port_comms = []  # communication
        self.communication_internal = communication_intern(self.logger, **karg)  # connection between function
        self.logger.info('end MPI extern init')

    def run(self, path_connection):
        """
        running time of the function, it's the main function
        :param path_connection: path for the simulation
        """
        # Step 1 : creation of the connection
        if path_connection is not None:
            self.logger.info('create connection')
            self.create_connection(path_connection)
        # Step 2 : simulation time / communication with the simulator during the simulation
        self.simulation_time()
        # Step 3 : close the connection
        if path_connection is not None:
            self.close_connection()
        # Finalise the MPI communication
        self.finalise()

    def create_connection(self, paths, info=MPI.INFO_NULL, comm=MPI.COMM_SELF, root_node=0):
        """
        Create the port the get external connection
        :param paths: Paths for the file to create with the port
        :param info: MPI info object
        :param comm: MPI communicator
        :param root_node: the root node of the communication
        """
        self.logger.info('Translate Receive: before open_port')
        # Creation of MPI port
        port = MPI.Open_port(info)
        self.ports.append(port)
        # Create the files for simulator to connect
        self.logger.info('Translate ' + self.name + ': after open_port: ' + port)
        for path in paths:
            # Write file configuration of the port
            fport = open(path, "w+")
            fport.write(port)
            fport.close()
            pathlib.Path(path + '.unlock').touch()
            self.path_ports.append(path)
        self.logger.info('Translate '+self.name+': path_file: ' + paths[-1])
        self.logger.info('Wait for Translate : '+port)
        self.port_comms.append(comm.Accept(port, info, root_node))
        self.logger.info('Connection accepted')

    def simulation_time(self, *args):
        """
        Connection with the simulator
        :param args: parameter for the simulation
        """
        raise Exception('not yet implemented')

    def close_connection(self):
        """
        Close the port of connection
        """
        self.logger.info("close connection")
        # TODO : Need to check if the close of the port can be before or not?
        for port in self.ports:
            MPI.Close_port(port)
        self.logger.info("close connection : delete file ")
        for path in self.path_ports:
            os.remove(path)
        self.logger.info("disconnect connection ")
        for port_comm in self.port_comms:
            port_comm.Disconnect()
        self.logger.info("end close connection")

    def finalise(self):
        """
        Finalise of MPI
        """
        self.logger.info("finalise")
        end = self.communication_internal.finalise()
        # Only one process need to finalise MPI
        if end:
            self.logger.info(" real finalise")
            MPI.Finalize()
