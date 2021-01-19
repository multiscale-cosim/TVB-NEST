from definitions import CONFIG_FILE
from xml_parser import Parser
from config_logger import ConfigLogger
from directories_manager import DirectoriesManager


class ConfigurationsManager(object):
    """Manages all the configuration settings."""
    # create output directories
    dm = DirectoriesManager()
    __directories = {'output': DirectoriesManager.get_output_directory(),
                     'logs': DirectoriesManager.get_logs_directory(),
                     'results': DirectoriesManager.get_results_directory()}

    @classmethod
    # retrieves directory
    def get_directory(cls, key):
        value = cls.__directories.get(key)
        if value:
            return cls.__directories.get(key)
        else:
            exit(1)  # TODO: better exception handling

    @classmethod
    def __load_configurations(cls, configuration_file):
        return Parser.load_xml(configuration_file)

    @classmethod
    def load_log_configurations(cls, name, target_directory=None,
                                configuration_file=CONFIG_FILE):
        """Creates a logger with the specified name and configuration settings.

        Parameters
        ----------
        name : str
            Logger name

        target_directory: str
            target directory to emit the logs

        configuration_file: str
            File name of the configuration settings

        Returns
        ------
        Return a logger
        """
        if target_directory is None:
            # default name for the logs directory
            target_directory = cls.get_directory('logs')
            # print(target_directory)
        configurations = cls.__load_configurations(configuration_file)
        root = configurations.getroot().find('log_configurations')
        log_config_settings = Parser.convert_xml2dict(root)
        logger = ConfigLogger()
        return logger.initialize_logger(name, target_directory, 
                                        xml_configurations=log_config_settings)

if __name__ == '__main__':
    myLogger = ConfigurationsManager().load_log_configurations(__name__)
    myLogger.info("configured")