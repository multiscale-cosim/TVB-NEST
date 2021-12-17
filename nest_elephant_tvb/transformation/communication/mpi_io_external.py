#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "

from mpi4py import MPI
import pathlib
import os
from nest_elephant_tvb.utils import create_logger
from timer.Timer import Timer


class MPICommunicationExtern:
    """
    Abstract class for MPI communication with a simulator.
    Management of MPI communication for exchange of data with simulator.
    """

    def __init__(self, name, path, level_log, communication_intern, **karg):
        """
        Initialisation of the MPI communication
        :param name: name of the module
        :param path: path of the port
        :param level_log: level of the logger
        :param communication_intern: internal communication
        :param karg: other parameter
        """
        self.logger = create_logger(path, name, level_log)
        self.name = name  # name of module
        self.ports = []  # array to save the MPI port
        self.path_ports = []  # path for sharing the connection ports
        self.port_comms = []  # communication
        self.timer = Timer(19, 100000)
        self.communication_internal = communication_intern(self.logger, timer=self.timer,
                                                           **karg)  # connection between function
        self.logger.info('MPI IO ext : end MPI extern init')
        self.path = path

    def run(self, path_connection):
        """
        running time of the function, it's the main function
        :param path_connection: path for the simulation
        """
        self.timer.start(0)
        # Step 1 : creation of the connection
        if path_connection is not None:
            self.logger.info('MPI IO ext : run : create connection')
            self.create_connection(path_connection)
        self.timer.change(0, 0)
        # Step 2 : simulation time / communication with the simulator during the simulation
        self.simulation_time()
        self.timer.change(0, 0)
        # Step 3 : close the connection
        if path_connection is not None:
            self.close_connection()
        self.timer.change(0, 0)
        # Finalise the MPI communication
        self.finalise()
        self.timer.stop(0)
        self.timer.save(self.path + "/timer_" + self.logger.name + '.npy')

    def create_connection(self, paths, info=MPI.INFO_NULL, comm=MPI.COMM_SELF, root_node=0):
        """
        Create the port the get external connection
        :param paths: Paths for the file to create with the port
        :param info: MPI info object
        :param comm: MPI communicator
        :param root_node: the root node of the communication
        """
        self.logger.info('MPI IO ext : create connection : Translate Receive: before open_port')
        # Creation of MPI port
        port = MPI.Open_port(info)
        self.ports.append(port)
        # Create the files for simulator to connect
        self.logger.info('MPI IO ext : create connection : Translate ' + self.name + ': after open_port: ' + port)
        for path in paths:
            # Write file configuration of the port
            fport = open(path, "w+")
            fport.write(port)
            fport.close()
            pathlib.Path(path + '.unlock').touch()
            self.path_ports.append(path)
        self.timer.change(0, 0)
        self.logger.info('MPI IO ext : create connection : Translate ' + self.name + ': path_file: ' + paths[-1])
        self.logger.info('MPI IO ext : create connection : Wait for Translate : ' + port)
        self.port_comms.append(comm.Accept(port, info, root_node))
        self.logger.info('MPI IO ext : create connection : Connection accepted')

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
        self.logger.info("MPI IO ext : close connection")
        # TODO : Need to check if the close of the port can be before or not?
        for port in self.ports:
            MPI.Close_port(port)
        self.logger.info("MPI IO ext : close connection : delete file ")
        for path in self.path_ports:
            os.remove(path)
        self.logger.info("MPI IO ext : close connection : disconnect connection ")
        for port_comm in self.port_comms:
            port_comm.Disconnect()
        self.logger.info("MPI IO ext : close connection : end close connection")

    def finalise(self):
        """
        Finalise of MPI
        """
        self.logger.info("MPI IO ext : finalise")
        end = self.communication_internal.finalise()
        # Only one process need to finalise MPI
        if end:
            self.logger.info("MPI IO ext : real finalise")
