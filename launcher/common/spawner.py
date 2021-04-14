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
import os
import multiprocessing
import time
import traceback
import queue


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
    __stop_action_event = None
    __stopping_event = None  # Additional mechanism to be stopped

    def __init__(self, launcher_PID=None, actions_to_be_carried_out=None,
                 returned_codes=None, logger=None, stopping_event=None):
        multiprocessing.Process.__init__(self)
        self.__actions_to_be_carried_out = actions_to_be_carried_out
        self.__launcher_PID = launcher_PID
        self.__logger = logger
        self.__returned_codes = returned_codes
        self.__stop_action_event = multiprocessing.Event()
        self.__stopping_event = stopping_event

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
            try:
                # TO BE DONE: Configuring the timeout value from XML files
                picked_action = self.__actions_to_be_carried_out.get(timeout=5)
            except queue.Empty:
                self.__logger.info('{}: waiting for a new action (task)'.format(self.__spawner_label))

                os.sched_yield()  # relinquishing for a while

                # after informing it's still alive, goes for an action again
                continue
            except KeyboardInterrupt:
                picked_action = None
                self.__logger.info('KeyboardInterrupt caught by {}'.format(self.__spawner_label))

            # Checking if the Launcher has put the poison pill
            # which is considered the "normal" ending procedure
            if picked_action is None:
                self.__logger.info('{}: finishing, there is no more actions to be spawn'.format(self.__spawner_label))
                self.__actions_to_be_carried_out.task_done()

                # Leaving the processing action loop
                break

            #######################
            # Performing the action
            # NOTE: Spawner (worker) will do the needful by means of the Action class
            #######################
            self.__logger.info('{} has picked the action {}'.format(self.__spawner_label,
                                                                    picked_action.get_action_xml_id()))

            try:
                # Action class (picked_action) will spawn the action by means of Popen
                # NOTE: Actions class will run another infinite loop to get the stdout and stderr from the action
                returned_code = -1
                self.__stop_action_event.clear()
                returned_code = picked_action.spawn_the_action(stop_action_event=self.__stop_action_event)
            except KeyboardInterrupt:
                self.__logger.info('{} caught KeyboardInterrupt'.format(self.__spawner_label))

                # Setting up the peremptory finishing request for the picked Action
                self.__stop_action_event.set()
                # JUST FOR TESTING ->time.sleep(1)
            else:
                self.__logger.info('{}: the <{}> action has finished'.format(self.__spawner_label,
                                                                             picked_action.get_action_xml_id()))
                # setting the action (task) as accomplished
                self.__actions_to_be_carried_out.task_done()

                # reporting the action returned code
                self.__returned_codes.put(returned_code)
