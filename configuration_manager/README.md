# Configurations Manager

It provides with the basic functionalities including the directory management, log management, XML configurations parsing conversion of XML element tree into Python dictionary object. The features it provides include:

* a centralized management of directories,
* XML parsing and manipulation, and
* a uniform format for the log settings.

## Basic Description

* **global_settings.xml**: XML file which contains the configuration settings.
* **directories_manager.py**: Creates and manages the directories. It also creates the default directories such as results, logs etc.  
* **xml_parser.py**: It provides the functionalities for parsing an xml file and to manipulate it (e.g. converting an xml element tree into dictionary etc.). 
* **config_logger.py**: Creates and configure logger using specified name and configuration settings.
* **configurations_manager.py**: Mediator to communicate with all modules and a central point to manage the configurations.
* **utils/directory_utils.py**: Utility methods for directory management such as to safely creating a directory where there is a race condition i.e. multiple processes try to create the same directory.
* **utils/dictionary_utils.py**: Utility methods to manipulate the nested dictionaries such as to find and set a value in a nested dictionary.

## Example

A minimal working example code is provided in example directory.

The following example illustrates how to:

1. Parse XML configurations with Configurations Manager
1. Setup (default) output directories at default locations (specified in XML configurations)
1. Retrieve path to default directories
1. Setup Log configurations 
   1. set path to logs at default location (e.g. ../Cosimulation_outputs/<username>_output_<timestamp>/logs)
   1. set user specified path to the logs
   
```python
# instantiate configuration manager
configurations_manager = ConfigurationsManager()

# get path to setup output directory from the configuration file
default_dir = configurations_manager.get_configuration_settings('output_directory', 'global_settings.xml')

# make default directories i.e. Output,  Output/Results, Output/Logs, Output/Figures using user id, timestamp to make it unique
configurations_manager.setup_default_directories(default_dir['output_directory'])

# get path to the default output directory
configurations_manager.get_default_directory(DefaultDirectories.OUTPUT)

# load log configurations
logger_settings = configurations_manager.get_configuration_settings('log_configurations', 'global_settings.xml')

# configure logger with default settings
example_logger = configurations_manager.load_log_configurations(name=__name__, log_configurations=logger_settings)

# configure logger with user specified location
dir_path=Path('../my_logs')
example_logger = configurations_manager.load_log_configurations(name=__name__, log_configurations=logger_settings,
                                                         directory='tests', directory_path=dir_path)

# emit logs
example_logger.info("logger is configured!")
example_logger.error("an error message!")
```

## License

Copyright 2020 Forschungszentrum Jülich GmbH  
"Licensed to the Apache Software Foundation (ASF) under one or more contributor
license agreements; and to You under the Apache License, Version 2.0. "