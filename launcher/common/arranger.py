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

# Co-Simulator imports
import common


class Arranger(object):
    """
        Arranges the run time environment
    """

    # general members
    __configuration_manager = None
    __variables_manager = None
    __logger = None

    def __init__(self, configuration_manager=None, logger=None, variables_manager=None, items_to_be_arranged_dict=None):
        # getting objects referenced provided when the instance object is created
        self.__configuration_manager = configuration_manager
        self.__logger = logger
        self.__variables_manager = variables_manager
        self.__items_to_be_arranged_dict = items_to_be_arranged_dict

    def __dir_creation(self, dir_to_be_created=None):

        try:
            # NOTE: It's OK if the directory already exists
            os.makedirs(dir_to_be_created, exist_ok=True)
            #
            # _just_for_debugging_ print(dir_to_be_created)
            #
        except OSError:
            self.__logger.error('{} making dir(s) went wrong'.format(dir_to_be_created))
            return common.enums.ArrangerReturnCodes.MKDIR_ERROR

        return common.enums.ArrangerReturnCodes.OK

    def arrange(self):

        for key, value in self.__items_to_be_arranged_dict.items():
            # key = Arrangement XML id, e.g. arr_01
            arrangement_duty = value[common.xml_tags.CO_SIM_XML_ARRANGEMENT_DUTY]
            raw_arrange_what = value[common.xml_tags.CO_SIM_XML_ARRANGEMENT_WHAT]
            transformed_arrange_what = \
                common.utils.transform_co_simulation_variables_into_values(variables_manager=self.__variables_manager,
                                                                           functional_variable_value=raw_arrange_what)

            if arrangement_duty == common.constants.CO_SIM_ARRANGEMENT_DIR_CREATION:

                if not self.__dir_creation(dir_to_be_created=transformed_arrange_what) == \
                       common.enums.ArrangerReturnCodes.OK:
                    return common.enums.ArrangerReturnCodes.MKDIR_ERROR

        return common.enums.ArrangerReturnCodes.OK
