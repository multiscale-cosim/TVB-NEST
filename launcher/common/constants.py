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

"""
Environment Variables Dictionaries KEYS
"""
CO_SIM_VARIABLE_DESCRIPTION = 'description'
CO_SIM_VARIABLE_VALUE = 'value'

"""
CO_SIM_ACTION_TYPES_TUPLE:
    Represents the different kinds of Co-Simulation actions
    that could be used as part of the <action_type> XML element,
    e.g.
    <action_plan>
        <action_NNN>
            <action_type>
                --> here shall be used a value from CO_SIM_ACTION_TYPES_TUPLE
            </action_type>
        </action_NNN>
    </action_plan>

Meanings:
   CO_SIM_ACTION: The action is a  program/script that will be launched based on the
                        definition of the Co-Simulation Action XML file which is specified
                        in the <action_script></action_script> element

   CO_SIM_EVENT:        The action is a event that the launcher shall be aware of, the kind of event must
                        be specified in the <action_event></action_event> element
"""
CO_SIM_ACTION = 'CO_SIM_ACTION'
CO_SIM_EVENT = 'CO_SIM_EVENT'
CO_SIM_ACTION_TYPES_TUPLE = (
    CO_SIM_ACTION,
    CO_SIM_EVENT,
)

"""
CO_SIM_ACTION_LAUNCH_METHODS_TUPLE:
    Represents the different methods how Co-Simulation actions
    could be launched
    e.g.
    <action_plan>
        <action_NNN>
            <action_type>
                CO_SIM_ACTION_SCRIPT            
            </action_type>
            <action_launch_method>
                --> here shall be used a value from CO_SIM_ACTION_LAUNCH_METHODS_TUPLE
            </action_launch_method>
        </action_NNN>
    </action_plan>
Meanings:
    CO_SIM_SEQUENTIAL_ACTION: The action will be launched synchronously, which means that the
                                launcher shall wait until the action finishes in order to
                                continue with the defined action plan.
    CO_SIM_CONCURRENT_ACTION: The action will be launched asynchronously, which means that the
                                launcher will continue launching other actions or managing a particular
                                event. As a rule of thumb, if the action plan contains asynchronous actions,
                                a CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS must be specified.                                       
"""
CO_SIM_SEQUENTIAL_ACTION = 'CO_SIM_SEQUENTIAL_ACTION'
CO_SIM_CONCURRENT_ACTION = 'CO_SIM_CONCURRENT_ACTION'
CO_SIM_ACTION_LAUNCH_METHODS_TUPLE = (
    CO_SIM_SEQUENTIAL_ACTION,
    CO_SIM_CONCURRENT_ACTION,
)

"""
CO_SIM_ACTION_EVENTS_TUPLE:
    Represents the different events that the launcher could wait for 
    e.g.
    <action_plan>
        <action_NNN>
            <action_type>
                CO_SIM_ACTION_EVENT            
            </action_type>
            <action_event>
                --> here shall be used a value from CO_SIM_ACTION_EVENTS_TUPLE
            </action_event>
        </action_NNN>
    </action_plan>
Meanings:
    CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS: The launcher shall wait for the ending of all the actions launched synchronously. 
                                        The launcher will not perform any further processing until
                                        the synchronous action(s) defined previously to the event is/are accomplished.
                                         
    CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS: The launcher shall wait for the ending of all the actions launched asynchronously.
                                        The launcher will not perform any further processing until
                                        the asynchronous action(s) defined previously to the event is/are accomplished.
                                        As a rule of thumb, an action plan must contains as a last action this kind
                                        of event.                                        
"""
CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS = 'CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS'
CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS = 'CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS'

CO_SIM_ACTION_EVENTS_TUPLE = (
    CO_SIM_WAIT_FOR_SEQUENTIAL_ACTIONS,
    CO_SIM_WAIT_FOR_CONCURRENT_ACTIONS,
)

"""
CO_SIM_REGEX_ENVIRONMENT_VARIABLE:
    Regular expression to find references to environment variables in the 
    Co-Simulation XML configuration files 
"""
CO_SIM_REGEX_ENVIRONMENT_VARIABLE: str = r'(\$\{|\})'
CO_SIM_REGEX_CO_SIM_VARIABLE: str = r'(\{CO_SIM_|\})'

