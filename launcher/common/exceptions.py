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

class EnvironmentVariableNotSet(Exception):
    """ Exception raised when a referenced environment variable has not been found

    Attributes:
        environment_variable_name -- the referenced variable causing the error
        message -- error message
    """

    def __init__(self, environment_variable_name, message="Environment variable has not been set"):
        self.environment_variable_name = environment_variable_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.environment_variable_name} -> {self.message}'


class CoSimVariableNotFound(Exception):
    """ Exception raised when a referenced CO_SIM_* variable has not been found

    Attributes:
        co_sim_variable_name -- the referenced Co-Simulator variable causing the error
        message -- error message
    """

    def __init__(self, co_sim_variable_name, message="Co-Simulation variable has not been found"):
        self.co_sim_variable_name = co_sim_variable_name
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f'{self.co_sim_variable_name} -> {self.message}'
