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
# import signal
import subprocess
import time

# Co-Simulator's imports
import common


class Action:
    """
        - Spawns an action by means of subprocess.Popen

    Methods:
    --------
        spawn_the_action: Spawn a action (task) by using subprocess.Popen

    """
    __event_action_xml_id = None
    __logger = None
    __popen_args = None
    __stopping_event = None

    def __init__(self, event_action_xml_id=None, action_xml_id=None,
                 action_popen_args_list=None, logger=None, stopping_event=None):
        self.__event_action_xml_id = event_action_xml_id
        self.__action_xml_id = action_xml_id
        self.__action_popen_args_list = action_popen_args_list
        self.__logger = logger
        self.__stopping_event = stopping_event

    def spawn_the_action(self, stop_action_event=None):
        """
            Implements the main loop to manage a action based on XML configuration files

            NOTE: This method is very linked to the Spawner class since
                    in the Spawner main loop, this method is called.
        :return:

        """
        self.__logger.debug('event {}, spawning {}, {}'.format(self.__event_action_xml_id,
                                                               self.__action_xml_id,
                                                               self.__action_popen_args_list))
        """
        # print('__spawning_troubleshooting__, {},{}'.format(self.__action_xml_id, self.__action_popen_args_list))
        """
        try:
            # Turning off output buffering for the child process
            os.environ['PYTHONUNBUFFERED'] = "1"

            # Spawning the action
            # NOTE: Since the encoding or errors arguments were not specified,
            #       neither universal_newlines was True,
            #       stdout=subprocess.PIPE and stderr=subprocess.PIPE
            #       are READABLE STREAMS and not TEXT STREAMS
            popen_process = subprocess.Popen(self.__action_popen_args_list,
                                             stdin=None,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             shell=False)

        except OSError as os_error_e:
            self.__logger.error('Action {} could not be spawned by Popen'.format(self.__action_xml_id))
            self.__logger.error('OSError: {}'.format(os_error_e.strerror))
            return common.enums.ActionReturnCodes.OS_ERROR_EXCEPTION
        except ValueError:
            self.__logger.error('Action {} reports Popen arguments error'.format(self.__action_xml_id))
            self.__logger.error('ValueError: {}'.format(self.__action_popen_args_list))
            return common.enums.ActionReturnCodes.VALUE_ERROR_EXCEPTION
        else:
            self.__logger.info('Action <{}> was spawned successfully'.format(self.__action_xml_id))

            self.__logger.info('PPID={},PID={} is running action <{}>'.format(os.getpid(),  # Spawner PID
                                                                              popen_process.pid,
                                                                              # The spawned action PID
                                                                              self.__action_xml_id, ))

        #
        poll_rc = None
        stdout_line = None
        stderr_line = None

        # getting outputs until the spawned action has finished
        while True:
            # Checking for peremptory finishing request
            if stop_action_event.is_set():
                self.__logger.info('{} will signal PID={} to be concluded'.format(self.__action_xml_id,
                                                                                  popen_process.pid))
                popen_process.terminate()

                os.sched_yield()
                time.sleep(0.001)  # giving a chance to the POpen process to finish

                try:
                    popen_process.wait(timeout=1)
                except subprocess.TimeoutExpired:
                    self.__logger.info('{} will signal PID={} to be forced to concluded'.format(self.__action_xml_id,
                                                                                                popen_process.pid))
                    popen_process.kill()

                # last checking
                stopping_rc = popen_process.poll()
                if stopping_rc is None:
                    self.__logger.info('{} could not conclude PID={}'.format(self.__action_xml_id,
                                                                             popen_process.pid))
                else:
                    self.__logger.info('{} was able to conclude PID={} which returns rc={}'.format(self.__action_xml_id,
                                                                                                   popen_process.pid,
                                                                                                   stopping_rc))
                # leaving the getting outputs loop
                break

            # Processing the Popen process stdout and stderr outcomes
            try:
                poll_rc = popen_process.poll()
                stdout_line = popen_process.stdout.readline()
                stderr_line = popen_process.stderr.readline()
            except KeyboardInterrupt:
                self.__logger.info('KeyboardInterrupt caught by action <{}>'.format(self.__action_xml_id))
                # setting up the peremptory finishing request
                stop_action_event.set()
                continue
            # TO BE DONE: as a matter of time, more exceptions should be caught here
            # except Exception as ex:
            #    self.__logger.exception('getting stdout and stderr from <{}>'.format(self.__action_xml_id))

            if poll_rc is not None and not stdout_line and not stderr_line:
                # spawned action has finished and there is no more bytes on the stdout stderr to be gathered

                # leaving the getting outputs loop
                break

            if stdout_line:
                # something has been generated by the spawned action
                self.__logger.info('{}: {}'.format(self.__action_xml_id,
                                                   stdout_line.strip().decode('utf-8')))

            if stderr_line:
                # some error has been reported by the spawned action
                self.__logger.error('{}: {}'.format(self.__action_xml_id,
                                                    stderr_line.strip().decode('utf-8')))

            # relinquishing the CPU window time for a while
            os.sched_yield()

        # The spawned action has finished
        return_code = popen_process.poll()

        if not return_code == 0:
            self.__logger.error('Action {} went wrong, finished returning rc={}'.format(self.__action_xml_id,
                                                                                        return_code))
            return common.enums.ActionReturnCodes.NOT_OK

        self.__logger.info('Action <{}> finished properly.'.format(self.__action_xml_id))
        return common.enums.ActionReturnCodes.OK

    def get_action_xml_id(self):
        return self.__action_xml_id
