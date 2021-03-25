# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
#
# Forschungszentrum Jülich
#  Institute: Institute for Advanced Simulation (IAS)
#    Section: Jülich Supercomputing Centre (JSC)
#   Division: High Performance Computing in Neuroscience
# Laboratory: Simulation Laboratory Neuroscience
#       Team: Multi-scale Simulation and Design
#
# ------------------------------------------------------------------------------
import multiprocessing


class Spawner(multiprocessing.Process):
    """
        Implements the Spawner process which will spawn a picked actions
        from the actions Joinable Queue and set the result into the
        return codes Queue

    Methods:
    --------
        run: Spawn a action by means an Action object

    """
    __actions_to_be_carried_out = None  # Joinable Queue
    __launcher_PID = 0
    __logger = None  # logger object reference
    __returned_codes = None  # Queue
    __spawner_label = ''  # formed in run method PPID+PID+Name

    def __init__(self, launcher_PID=None, actions_to_be_carried_out=None, returned_codes=None, logger=None):
        multiprocessing.Process.__init__(self)
        self.__actions_to_be_carried_out = actions_to_be_carried_out
        self.__launcher_PID = launcher_PID
        self.__logger = logger
        self.__returned_codes = returned_codes

    def run(self) -> None:
        """
            Implements the main loop of a forked process (spawner)

        :return:
             There is no return code since it will taken from
             the code returned by the spawned action and
             placed into the results queue.

             NOTE: the results codes queue will be controlled for the
                    parent process of the spawner(s), commonly the "launcher"
        """
        self.__spawner_label = 'PPID={},PID={},{}'.format(self.__launcher_PID, self.pid, self.name)
        self.__logger.info('{} started'.format(self.__spawner_label))

        while True:
            # getting next action (task) to be spawned
            picked_action = self.__actions_to_be_carried_out.get()

            # should the Spawner stop by itself?
            if picked_action is None:
                # poison pill has been gotten
                # it is taken as the "normal" stopping mechanism
                self.__actions_to_be_carried_out.task_done()

                # ending the spawner process
                break

            self.__logger.info('{} has picked the action {}'.format(self.__spawner_label,
                                                                    picked_action.get_action_xml_id()))

            # Action class will spawn the action by means of Popen
            returned_code = picked_action.spawn_the_action()

            # setting the action (task) as accomplished
            self.__actions_to_be_carried_out.task_done()

            # reporting the action returned code
            self.__returned_codes.put(returned_code)
