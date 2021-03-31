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

# Co-Simulator's imports
import common


class Launcher(object):
    """
        Implements the Co-Simulation launcher component

    Methods:
    --------
        carry_out_action_plan: Launches the sub-processes based on the action-plan dictionary

    """
    __actions_to_be_carried_out_jq = None  # Joinable queue to trigger spawning actions processes
    __action_plan_dict = {}  # The action plan to be carried out
    __actions_popen_args_dict = {}  # Popen arguments keyed by action XML IDs
    __actions_return_codes_q = None  # Queue where the actions return codes will be placed
    __actions_xml_filenames_dict = {}  # XML filenames from the <action_xml> element of the action plan XML file
    __configuration_manager = {}  # Object reference to a ConfigurationManager class instance
    __launching_strategy_dict = {}  # Mapped action plan, actions grouped by events
    __launcher_PID = 0  # The PID where the object of this class is being executed
    __logger = None
    __maximum_number_actions_found = 0  # It will be the number of spawner to be started
    __stopping_event = None  # Event to be used as alternative mechanism to stop Spawner children processes

    def __init__(self, action_plan_dict=None, actions_popen_args_dict=None, configuration_manager=None, logger=None):
        """
        :param action_plan_dict:
            Contains the sketch about what action must be spawn and the expected events during
            the execution of the spawned sub-processes
        :param logger:
            references to the logger manager where the log messages will be sent
        """
        self.__action_plan_dict = action_plan_dict
        self.__actions_popen_args_dict = actions_popen_args_dict
        self.__configuration_manager = configuration_manager
        self.__logger = logger

        self.__actions_to_be_carried_out_jq = multiprocessing.JoinableQueue()
        self.__actions_return_codes_q = multiprocessing.Queue()

        self.__launcher_PID = os.getpid()

        self.__stopping_event = multiprocessing.Event()

    def __map_out_launching_strategy(self):
        """
            Goes through the action plan dictionary and find the CO_SIM_EVENT entries
            in order to establish the converging points where the launcher should
            perform a wait for the actions previously launched.

        :return:
            LAUNCHER_OK: The launching strategy was built out properly
            MAPPING_OUT_ERROR: The action plan contain some unlogical sequence of actions
            XML_ERROR: The <action_plan> section contains some erroneous entries
        """
        self.__launching_strategy_dict = {}
        actions_list = []
        self.__maximum_number_actions_found = 0
        actions_counter = 0

        # looking for the events and grouping the actions based on them.
        # i.e. based on {'action_type': 'CO_SIM_EVENT', 'action_event': 'CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS'}
        #
        # the {'action_type': 'CO_SIM_ACTION_SCRIPT', 'action_script': 'initial_spikes_generator.xml',
        #      'action_launch_method': 'CO_SIM_SEQUENTIAL_ACTION'}
        # will be grouped
        for key, value in self.__action_plan_dict.items():
            # checking again the <action_type> value, just in case...
            if value['action_type'] == common.constants.CO_SIM_ACTION:
                # accumulating the actions before finding an event action type
                actions_list.append(key)

                # counting the number the actions associated to the event
                # to establish the number of spawner processes
                # to be created later
                actions_counter += 1
            elif value['action_type'] == common.constants.CO_SIM_EVENT:
                # an event has been found (meaning, a graph node)
                # related to actions (task to be spawned),
                # it must be SEQUENTIAL or CONCURRENT
                self.__launching_strategy_dict[key] = {'action_event': value['action_event'],
                                                       'actions_list': actions_list, }
                actions_list = []
                actions_counter = 0
            else:
                self.__logger.error('wrong <action_type> found: {}'.format(value['action_type']))
                return common.enums.LauncherReturnCodes.XML_ERROR

            if actions_counter > self.__maximum_number_actions_found:
                # keeping the maximum number of actions associated to one event
                # in order to use it as number of spawner process to be initiated
                self.__maximum_number_actions_found = actions_counter

            self.__logger.debug(
                f'-> {self.__maximum_number_actions_found} <- is the maximum number of actions associated to a event')

        if self.__launching_strategy_dict and actions_list:
            self.__logger.error('<action_plan> must be ended with a CO_SIM_EVENT element')
            return common.enums.LauncherReturnCodes.MAPPING_OUT_ERROR

        # in this point
        # __launching_strategy_dict contains the actions grouped by events
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __check_actions_grouping(self):
        """
            Goes through the launching strategy dictionary in order to check
            whether the actions associated to the waiting events have the proper
            action type, i.e. SEQUENTIAL or CONCURRENT

        :return:
            LAUNCHER_OK: The actions' launching methods concord with the waiting event
            ACTIONS_GROUPING_ERROR: The launcher strategy is inconsistent due to wrong grouping association
            XML_ERROR: The <action_plan> section contains some erroneous entries
        """

        for key, value in self.__launching_strategy_dict.items():
            action_xml_id = key  # e.g. action_010 taken from XML <action_010>
            action_event = value['action_event']  # SEQUENTIAL or CONCURRENT
            actions_list = value['actions_list']  # e.g. [action_006, action_008, ]
            expected_action_launch_method = ''

            if action_event == common.constants.CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS:
                expected_action_launch_method = common.constants.CO_SIM_SEQUENTIAL_ACTION
            elif action_event == common.constants.CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS:
                expected_action_launch_method = common.constants.CO_SIM_CONCURRENT_ACTION
            else:
                self.__logger.error('wrong <action_event> entry found: {}'.format(action_event))
                return common.enums.LauncherReturnCodes.XML_ERROR

            for current_action in actions_list:
                if self.__action_plan_dict[current_action]['action_launch_method'] == expected_action_launch_method:
                    # the action has the expected launching method
                    # NOTE: here could be placed additional code to grab information associated to the current_action
                    #       notwithstanding, it has been preferred to keep each method performing one particular task
                    pass
                else:
                    self.__logger.error('<{}> method {} expects <{}> having the {} launching method'.
                                        format(action_xml_id, action_event, current_action,
                                               expected_action_launch_method))
                    return common.enums.LauncherReturnCodes.ACTIONS_GROUPING_ERROR

        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __gather_action_xml_filenames(self):
        """
            - Goes through the launching strategy dictionary in order to gather the XML filenames
                from the action plan XML file.

        :return:
            LAUNCHER_OK: All the XML filenames were gathered from the action plan XML file
            GATHERING_XML_FILENAMES_ERROR: Error by gathering the XML filename from the section <action_xml>
        """

        self.__actions_xml_filenames_dict = {}

        try:
            for key, value in self.__launching_strategy_dict.items():
                actions_list = value['actions_list']  # e.g. [action_006, action_008, ]

                for current_action in actions_list:
                    self.__actions_xml_filenames_dict[current_action] = \
                        {'action_xml': self.__action_plan_dict[current_action]['action_xml']}

        except KeyError:
            return common.enums.LauncherReturnCodes.GATHERING_XML_FILENAMES_ERROR

        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __start_spawner_processes(self):
        """

        :return:
            LAUNCHER_OK:

        """
        # TO BE DONE: checking the proper number of child processes to be created
        #                based on the number of CPU on the system
        #                   when __maximum_number_actions_found is greater than it
        #
        self.__spawners = [common.Spawner(self.__launcher_PID,  # PPID for the Spawner
                                          actions_to_be_carried_out=self.__actions_to_be_carried_out_jq,
                                          returned_codes=self.__actions_return_codes_q,
                                          logger=self.__logger,
                                          stopping_event=self.__stopping_event)
                           for n_spawners in range(self.__maximum_number_actions_found)]

        for current_spawner in self.__spawners:
            current_spawner.start()

        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __perform_spawning_strategy(self):
        """
            Spawns the actions and manage the outcomes based on the found events.

        :return:
            LAUNCHER_OK: all the action finished as expected
            XML_ERROR: The <action_event> element contains a erroneous entry
        """

        try:

            # going through the launching strategy dictionary
            # in order to get the events and the actions
            # that belongs to such event
            for key, value in self.__launching_strategy_dict.items():
                event_action_xml_id = key  # the event
                action_event = value['action_event']  # the event defining the spawning strategy
                actions_list = value['actions_list']  # list of actions owned by the event

                if action_event == common.constants.CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS:
                    # Sequential actions management
                    self.__logger.info('Sequentially processing of actions owned by the event <{}>'.format(event_action_xml_id))
                    for action_xml_id in actions_list:
                        action_popen_args_list = []
                        try:
                            action_popen_args_list = self.__actions_popen_args_dict[action_xml_id]
                        except KeyError:
                            self.__logger.error('There are no Popen args to spawn the action {}'.format(action_xml_id))
                        self.__actions_to_be_carried_out_jq.put(common.Action(event_action_xml_id=event_action_xml_id,
                                                                              action_xml_id=action_xml_id,
                                                                              action_popen_args_list=action_popen_args_list,
                                                                              logger=self.__logger,
                                                                              ))
                        # SEQUENTIAL effect
                        # waiting until the Task has finished (task by task)
                        self.__actions_to_be_carried_out_jq.join()

                elif action_event == common.constants.CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS:
                    # Concurrent actions management
                    self.__logger.info('Concurrently Processing of actions owned by the event <{}>'.format(event_action_xml_id))
                    for action_xml_id in actions_list:
                        action_popen_args_list = []
                        try:
                            action_popen_args_list = self.__actions_popen_args_dict[action_xml_id]
                        except KeyError:
                            self.__logger.error('There are no Popen args to spawn the action <{}>'.format(action_xml_id))
                        self.__actions_to_be_carried_out_jq.put(common.Action(event_action_xml_id=event_action_xml_id,
                                                                              action_xml_id=action_xml_id,
                                                                              action_popen_args_list=action_popen_args_list,
                                                                              logger=self.__logger))
                    # CONCURRENT effect
                    # waiting until ALL the tasks have finished (task grouped by the event)
                    self.__actions_to_be_carried_out_jq.join()
                else:
                    # wrong entry found
                    self.__logger.error('wrong <action_event>: {}'.format(action_event))
                    return common.enums.LauncherReturnCodes.XML_ERROR

        except KeyboardInterrupt:
            self.__logger.info("Caught KeyboardInterrupt! Setting stop event...")
        finally:
            self.__stopping_event.set()

        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def carry_out_action_plan(self):
        """
            Goes through the action-plan dictionary and spawn the required actions
            and waits for and manages  the happened events

        :return:
            LAUNCHER_OK: All the action were spawned according to the action-plan
                        and the actions did not report any issue (return code != 0)

            MAPPING_OUT_ERROR: The action plan has not proper logic to be mapped out into
                                the launching strategy dictionary

            PERFORMING_STRATEGY_ERROR: Some of the action ended with error
        """

        ########
        # STEP 1 - Grouping actions by events
        ########
        if not self.__map_out_launching_strategy() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('something went wrong by mapping out the action plan')
            return common.enums.LauncherReturnCodes.MAPPING_OUT_ERROR

        ########
        # STEP 2 - Checking the actions grouping, i.e. SEQUENTIAL or CONCURRENT
        ########
        if not self.__check_actions_grouping() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('an action inconsistently associated to a waiting event was found')
            return common.enums.LauncherReturnCodes.ACTIONS_GROUPING_ERROR

        ########
        # STEP 3 - Gathering the XML filenames from the <action_xml> element of each action
        ########
        if not self.__gather_action_xml_filenames() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('error by gathering XML filenames from the action plan')
            return common.enums.LauncherReturnCodes.GATHERING_XML_FILENAMES_ERROR

        ########
        # STEP 4 - Starting the child processes which will spawn the actions
        ########
        if not self.__start_spawner_processes() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('something went wrong by starting spawners processes')
            return common.enums.LauncherReturnCodes.STARTING_SPAWNERS_ERROR

        ########
        # STEP 5 - Carrying out the action plan, based on events and their associated actions
        ########
        if not self.__perform_spawning_strategy() == common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('something went wrong by executing the action plan')
            return common.enums.LauncherReturnCodes.PERFORMING_STRATEGY_ERROR

        ########
        # STEP 6 - Stopping the spawner processes by poison pilling them
        ########
        for current_spawner in self.__spawners:
            self.__actions_to_be_carried_out_jq.put(None)  # the poison pill

        # Waiting until all the spawner processes have taken their pill
        self.__actions_to_be_carried_out_jq.join()

        ########
        # STEP 7 - getting results
        ########
        there_was_an_error = False
        while not self.__actions_return_codes_q.empty():
            current_action_result = self.__actions_return_codes_q.get()
            if current_action_result == 0:
                continue
            else:
                there_was_an_error = True
                break

        #########
        # STEP 8 - Joining spawner processes (just in case)
        #########
        for current_spawner in self.__spawners:
            current_spawner.join()

        if there_was_an_error:
            return common.enums.LauncherReturnCodes.ACTIONS_FINISHED_WITH_ERROR

        # no errors! (all actions returned Popen rc=0)
        return common.enums.LauncherReturnCodes.LAUNCHER_OK
