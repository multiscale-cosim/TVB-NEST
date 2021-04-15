# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
# ------------------------------------------------------------------------------
from pathlib import Path
from configurations_manager import ConfigurationsManager
from default_directories_enum import DefaultDirectories

if __name__ == '__main__':
    ''' 
        This is a minimal working example illustrating how configurations manager
        can be used to:

         i.   parse XML configurations, 
         ii.  setup default output directories, and
         iii. create a logger with user specified configuration settings
    '''

    # instantiate configuration manager
    configurations_manager = ConfigurationsManager()

    # get path to setup output directory from the XML configuration file
    default_dir = configurations_manager.get_configuration_settings(
        'output_directory', 'example_settings.xml')

    # setup default directories (Output, Output/Results, Output/Logs,
    # Output/Figures, Output/Monitoring_DATA)
    configurations_manager.setup_default_directories(default_dir['output_directory'])

    # get path to the default output directory
    print('path to outputs: ', configurations_manager.get_directory(DefaultDirectories.OUTPUT))

    # load log configurations from XML file
    logger_settings = configurations_manager.get_configuration_settings(
        'log_configurations', 'example_settings.xml')

    # configure logger with the default settings
    example_logger = configurations_manager.load_log_configurations(name=__name__,
                                                                    log_configurations=logger_settings)

    # emit logs
    example_logger.info("default: logger is configured!")
    example_logger.error("default: an error message!")

    # configure logger with user specified location for log emissions
    dir_path=Path('Example_customized_location_for_logs')
    example_logger = configurations_manager.load_log_configurations(name='example_logger',
                                                                    log_configurations=logger_settings,
                                                                    directory='example_logs_directory',
                                                                    directory_path=dir_path)

    # emit logs
    example_logger.info("customized location: logger is configured!")
    example_logger.error("customized location: an error message!")