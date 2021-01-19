import os
from utils.util import safe_makedir
from datetime import datetime
from definitions import OUTPUT_DIR


class MetaDirectoriesManager(type):
    """This class implements singleton for DirectoriesManager class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(MetaDirectoriesManager, 
                                                cls).__call__(*args, **kwargs)
            cls.__output_directory = cls.__setup_output_directory(OUTPUT_DIR)
            cls.get_results_directory()
            cls.get_logs_directory()
        return cls._instances[cls]

    @staticmethod
    def __setup_output_directory(name):
        """Creates output directory for results, logs etc.

        Parameters
        ----------
        name : str
            Name for the Output directory

        Returns
        ------
        target_directory: str
            Output directory path
        """
        target_directory = os.path.join(OUTPUT_DIR, name)
        target_directory += datetime.strftime(datetime.now(), 
                                                    '_%Y-%m-%d_%H-%M')
        safe_makedir(target_directory)
        return target_directory

    def get_output_directory(cls):
        return cls.__output_directory

    def get_results_directory(cls):
        res_directory = os.path.join(cls.__output_directory, "results")
        safe_makedir(res_directory)
        return res_directory

    def get_logs_directory(cls):
        log_directory = os.path.join(cls.__output_directory, "logs")
        safe_makedir(log_directory)
        return log_directory


class DirectoriesManager(metaclass=MetaDirectoriesManager):
    pass
