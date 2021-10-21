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
from python.launcher import Launcher
from python.Application_Companion.common_enums import Response


class LaunchingManager(object):
    """
    1. Groups the actions and their launching methods based on events
    such as SEQUENTIAL or CONCURRENT
    2. Performs SEQUENTIAL actions
    3. Performs CONCURRENT actions
    """

    def __init__(self, action_plan_dict, actions_popen_args_dict,
                 log_settings, configurations_manager):
        # initialize logger with uniform settings
        self._logger_settings = log_settings
        self._configurations_manager = configurations_manager
        self.__logger = self._configurations_manager.load_log_configurations(
                                    name=__name__,
                                    log_configurations=self._logger_settings)
        # The action plan to be carried out
        self.__action_plan_dict = action_plan_dict
        # Popen arguments keyed by action XML IDs
        self.__actions_popen_args_dict = actions_popen_args_dict
        # XML filenames from <action_xml> element of the action plan XML file
        self.__actions_xml_filenames_dict = {}
        # Mapped action plan, actions grouped by events
        self.__launching_strategy_dict = {}
        # the number of spawner to be started
        self.__maximum_number_actions_found = 0
        # Joinable queue to trigger spawning actions processes
        self.__actions_to_be_carried_out_jq = multiprocessing.JoinableQueue()
        # Queue where the actions return codes will be placed
        self.__actions_return_codes_q = multiprocessing.Queue()
        self.__launching_manager_PID = os.getpid()
        self.__stopping_event = multiprocessing.Event()
        self.__logger.debug('Launching Manager is initialized.')

    def __get_expected_action_launch_method(self, action_event):
        '''
        helper function which returns the relative launching mehtod
        based on the action-event type.
        '''
        # Case 1: SEQUENTIAL_ACTIONS
        if action_event == common.constants.CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS:
            return common.constants.CO_SIM_SEQUENTIAL_ACTION
        # Case 2: CONCURRENT_ACTIONS
        if action_event == common.constants.CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS:
            return common.constants.CO_SIM_CONCURRENT_ACTION

        # Otherwise, the <action_event> element contains an erroneous entry
        self.__logger.error(f'wrong <action_event> entry found:{action_event}')
        return common.enums.LauncherReturnCodes.XML_ERROR

    def __check_actions_grouping(self):
        """
            Goes through the launching strategy dictionary in order to check
            whether the actions associated to the waiting events have the
            proper action type, i.e. SEQUENTIAL or CONCURRENT

        :return:
            LAUNCHER_OK: The actions' launching methods concord with the
            waiting event

            ACTIONS_GROUPING_ERROR: The launcher strategy is inconsistent due
            to wrong grouping association

            XML_ERROR: The <action_plan> section contains some erroneous
            entries
        """
        self.__logger.debug('Validating the grouping of action and launching'
                            'methods')
        for key, value in self.__launching_strategy_dict.items():
            action_xml_id = key  # e.g. action_010 taken from XML <action_010>
            action_event = value['action_event']  # SEQUENTIAL or CONCURRENT
            actions_list = value['actions_list']  # e.g.[action_006,action_008]
            expected_action_launch_method = ''

            # get action event launching method type
            expected_action_launch_method =\
                self.__get_expected_action_launch_method(action_event)
            # validate action event launching method type
            if expected_action_launch_method ==\
                    common.enums.LauncherReturnCodes.XML_ERROR:
                # an error is already logged for wrong action_event entry
                return common.enums.LauncherReturnCodes.XML_ERROR

            # validate the grouping of actions and their launching method types
            for current_action in actions_list:
                if self.__action_plan_dict[current_action]['action_launch_method']\
                     == expected_action_launch_method:
                    # NOTE: here could be placed additional code to grab
                    # information associated to the current_action
                    # notwithstanding, it has been preferred to keep each
                    # method performing one particular task
                    pass
                else:
                    # action is associated with a wrong launching method type
                    self.__logger.error(
                        f'<{action_xml_id}> method {action_event} '
                        f'expects <{current_action}> having the '
                        f'{expected_action_launch_method} launching method.')
                    return common.enums.LauncherReturnCodes.ACTIONS_GROUPING_ERROR

        # otherwise, action and launching methods grouping is validated
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __gather_action_xml_filenames(self):
        """
        Goes through the launching strategy dictionary in order to gather the
        XML filenames from the action plan XML file.

        :return:
            LAUNCHER_OK: All the XML filenames were gathered from the action
            plan XML file

            GATHERING_XML_FILENAMES_ERROR: Error by gathering the XML filename
            from the section <action_xml>
        """
        self.__logger.debug('Gathering action XML file names.')
        try:
            for _, value in self.__launching_strategy_dict.items():
                actions_list = value['actions_list']  # e.g. [action_006,...]

                for current_action in actions_list:
                    self.__actions_xml_filenames_dict[current_action] = \
                        {'action_xml':
                         self.__action_plan_dict[current_action]['action_xml']}
        except KeyError:
            # XML file name is not found in action_plan_dict
            self.__logger.error('Error in gathering action XML file names.')
            return common.enums.LauncherReturnCodes.GATHERING_XML_FILENAMES_ERROR

        # otherwise, XML file names are gatheres from the action plan XML file
        self.__logger.debug('action XML file names are gathered.')
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __map_out_launching_strategy(self):
        """
            Goes through the action plan dictionary and find the CO_SIM_EVENT
            entries in order to establish the converging points where the
            launcher should perform a wait for the actions previously launched.

        :return:
            LAUNCHER_OK: The launching strategy was built out properly

            MAPPING_OUT_ERROR: The action plan contain some unlogical sequence
            of actions XML_ERROR: The <action_plan> section contains some
            erroneous entries.
        """
        actions_list = []
        actions_counter = 0

        # looking for the events and grouping the actions based on them.
        # e.g. {'action_type': 'CO_SIM_EVENT',
        #       'action_event': 'CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS'}
        # and
        # {'action_type': 'CO_SIM_ACTION_SCRIPT',
        #  'action_script': 'initial_spikes_generator.xml',
        #  'action_launch_method': 'CO_SIM_SEQUENTIAL_ACTION'}
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
                self.__launching_strategy_dict[key] =\
                     {'action_event': value['action_event'],
                      'actions_list': actions_list, }
                actions_list = []
                actions_counter = 0
            else:
                self.__logger.error(f"wrong <action_type> found:"
                                    f"{value['action_type']}")
                return common.enums.LauncherReturnCodes.XML_ERROR

            if actions_counter > self.__maximum_number_actions_found:
                # keeping the maximum number of actions associated to one event
                # in order to use it as number of spawner process to be
                # initiated
                self.__maximum_number_actions_found = actions_counter

            self.__logger.debug(f'Maximum number of actions: '
                                f'{self.__maximum_number_actions_found}')

        if self.__launching_strategy_dict and actions_list:
            self.__logger.error('<action_plan> must be ended with a'
                                ' CO_SIM_EVENT element')
            return common.enums.LauncherReturnCodes.MAPPING_OUT_ERROR

        # at this point __launching_strategy_dict contains the actions
        # grouped by events
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __perform_sequential_actions(self, actions_list, event_action_xml_id):
        '''
        helper function for performing the SEQUENTIAL actions

        Parameters
        ----------

        actions_list : list
            list of (SEQUENTIAL) actions to be performed

        event_action_xml_id: str
            XML tag of the action event

        Returns
        ------
           LAUNCHER_OK: All the SEQUENTIAL actions are performed successfully

           LAUNCHER_NOT_OK: Something went wrong such as no Popen args are
           found to spawn the process
        '''
        self.__logger.info(f'Sequentially processing of actions owned by the '
                           f'event <{event_action_xml_id}>')
        # start spawner proccesses to perform SEQUENTIAL actions
        if self.__start_spawner_processes() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK:
            # processes could not be started,
            # a more specific error is already logged
            return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

        # processes are started, now perform SEQUENTIAL actions
        for action_xml_id in actions_list:
            action_popen_args_list = []
            try:
                # get action (Popen args) to be performed
                action_popen_args_list =\
                     self.__actions_popen_args_dict[action_xml_id]
            except KeyError:
                self.__logger.error(f'There are no Popen args to spawn'
                                    f'<{action_xml_id}>')
                return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

            # Popen args are found
            try:
                # sending action to spawner process to perform it
                self.__actions_to_be_carried_out_jq.put(common.Action(
                        event_action_xml_id=event_action_xml_id,
                        action_xml_id=action_xml_id,
                        action_popen_args_list=action_popen_args_list,
                        logger=self.__logger))
                # SEQUENTIAL effect
                # waiting until the Task has finished (task by task)
                self.__actions_to_be_carried_out_jq.join()
            except KeyboardInterrupt:
                self.__logger.critical('Caught KeyboardInterrupt! '
                                       'Setting stop event')
                # TODO: rather handle it with signal manager
                self.__stopping_event.set()

        # All sequential actions have been performed,
        # stop the spawner processes
        if self.__stop_spawner_processes() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK:
            # processes could not be stopped,
            # a more specific error is already logged
            return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

        # The processes are stopped after performing all SEQUENTIAL actions
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __perform_concurrent_actions(self, actions_list, event_action_xml_id):
        '''
        helper function for performing the CONCURRENT actions

        Parameters
        ----------

        actions_list : list
            list of (CONCURRENT) actions to be performed

        event_action_xml_id: str
            XML tag of the action event e.g. action_004, etc

        Returns
        ------

           LAUNCHER_OK: All the SEQUENTIAL actions are performed successfully

           LAUNCHER_NOT_OK: Something went wrong such as no Popen args are
           found to spawn the process
        '''
        concurrent_actions_list = []
        # gather all concurrent actions to be performed
        self.__logger.debug('populating the list of CONCURRENT actions to be'
                            ' performed')
        for action_xml_id in actions_list:
            action_popen_args_list = []
            try:
                # get action (Popen args) to be performed
                action_popen_args_list =\
                     self.__actions_popen_args_dict[action_xml_id]
            except KeyError:
                self.__logger.error(f'There are no Popen args to spawn'
                                    f'<{action_xml_id}>')
                return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

            # actions (Popen args) are found
            self.__logger.debug(f'appending action: {action_popen_args_list}')
            concurrent_actions_list.append(
                {'action': action_popen_args_list, 'action-id': action_xml_id})

        # initialize launcher to perform concurrent actions
        concurrent_actions_launcher =\
            Launcher(self._logger_settings, self._configurations_manager)
        # perform concurrent actions
        self.__logger.debug(f'performing CONCURRENT actions: '
                            f'{concurrent_actions_list}')
        if concurrent_actions_launcher.launch(concurrent_actions_list) ==\
                Response.OK:
            return common.enums.LauncherReturnCodes.LAUNCHER_OK
        else:
            return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

    def __start_spawner_processes(self):
        """
        helper function to start the spawner processes for performing
        SEQUENTIAL actions.
        """
        self.__spawners = [common.Spawner(
                self.__launching_manager_PID,  # PPID for the Spawner
                actions_to_be_carried_out=self.__actions_to_be_carried_out_jq,
                returned_codes=self.__actions_return_codes_q,
                logger=self.__logger,
                stopping_event=self.__stopping_event)
            for _ in range(self.__maximum_number_actions_found)]

        # start spawner processes
        self.__logger.debug('starting the spawners.')
        for current_spawner in self.__spawners:
            if current_spawner.start() is not None:
                self.__logger.error(f'{current_spawner} could not be started')
                # TODO terminate loudly with error
                return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

        # spawner processes are started
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __stop_spawner_processes(self):
        """
        helper function to stop the spawner processes after performing
        SEQUENTIAL actions.
        """
        # poisen pill to all spawner processes
        self.__logger.debug('Poisen pilling to spawners.')
        try:
            for _ in self.__spawners:
                self.__actions_to_be_carried_out_jq.put(None)

            # Waiting until all the spawner processes have taken their pill
            self.__actions_to_be_carried_out_jq.join()
            self.__logger.debug('All spawners have taken their pill.')
        except KeyboardInterrupt:
            # TODO handle with signal manager
            self.__logger.info("Caught KeyboardInterrupt! Setting stop event")
            self.__stopping_event.set()
            return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

        # all spawner processes have taken their pill
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def __perform_spawning_strategy(self):
        """
        Performs the (SEQUENTIAL and CONCURRENT) actions as per launching
        strategy

        :return:
            LAUNCHER_OK: all the action finished as expected
        """
        # switcher to invoke relevant function to perform specific action types
        action_execution_choices = {
                    # case 1
                    common.constants.CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS:\
                    self.__perform_sequential_actions,
                    # case 2
                    common.constants.CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS:\
                    self.__perform_concurrent_actions}

        # retrieve the actions from launching_strategy_dict to perform them
        for key, value in self.__launching_strategy_dict.items():
            # i. get the event
            event_action_xml_id = key
            # ii. get the event defining the spawning strategy
            action_event = value['action_event']
            # iii. get the list of actions owned by the event
            actions_list = value['actions_list']
            # iv. perform the actions
            if not action_execution_choices[action_event](
                                                    actions_list,
                                                    event_action_xml_id) ==\
                    common.enums.LauncherReturnCodes.LAUNCHER_OK:
                # something went wrong while performing actions,
                # more specific errors are already logged
                return common.enums.LauncherReturnCodes.LAUNCHER_NOT_OK

        # otherwise, all actions are performed successfully
        return common.enums.LauncherReturnCodes.LAUNCHER_OK

    def carry_out_action_plan(self):
        """
        Goes through the action-plan dictionary and spawn the required actions
        and waits for and manages  the happened events

        :return:
            LAUNCHER_OK: All the action are spawned successfully according to
            the action-plan

            MAPPING_OUT_ERROR: The action-plan has not proper logic to be
            mapped out into the launching strategy dictionary

            PERFORMING_STRATEGY_ERROR: Some of the action ended with error
        """

        ########
        # STEP 1 - Grouping actions by events
        ########
        if not self.__map_out_launching_strategy() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('something went wrong by mapping out the'
                                ' action-plan')
            return common.enums.LauncherReturnCodes.MAPPING_OUT_ERROR

        ########
        # STEP 2 - Checking the actions grouping, i.e. SEQUENTIAL or CONCURRENT
        ########
        if not self.__check_actions_grouping() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('an action inconsistently associated to a'
                                ' waiting event was found')
            return common.enums.LauncherReturnCodes.ACTIONS_GROUPING_ERROR

        ########
        # STEP 3 - Gathering the XML filenames from the <action_xml> element of
        # each action
        ########
        if not self.__gather_action_xml_filenames() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('error by gathering XML filenames from the'
                                ' action plan')
            return common.enums.LauncherReturnCodes.GATHERING_XML_FILENAMES_ERROR

        ########
        # STEP 4 - Carrying out the action plan, based on events and their
        # associated actions
        ########
        if not self.__perform_spawning_strategy() ==\
                common.enums.LauncherReturnCodes.LAUNCHER_OK:
            self.__logger.debug('something went wrong by executing the '
                                'action-plan')
            return common.enums.LauncherReturnCodes.PERFORMING_STRATEGY_ERROR

        # Check if all actions are performed without error
        there_was_an_error = False
        while not self.__actions_return_codes_q.empty():
            current_action_result = self.__actions_return_codes_q.get()
            if current_action_result == common.enums.ActionReturnCodes.OK:
                continue
            else:
                there_was_an_error = True
                break
        # some actions finsishes with error
        if there_was_an_error:
            return common.enums.LauncherReturnCodes.ACTIONS_FINISHED_WITH_ERROR

        # no errors! (all actions returned Popen rc=0)
        return common.enums.LauncherReturnCodes.LAUNCHER_OK
