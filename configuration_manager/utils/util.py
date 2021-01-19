import os
import errno


def safe_makedir(target_directory):
    """Creates a directory.

    Safely creates a directory where there is a race condition i.e.
    multiple processes try to create the same directory.

    Parameters
    ----------
    target_directory : string
        The Name for the target directory

    Returns
    -------
    target_directory: str
        Target directory
    """
    try:
        os.makedirs(target_directory)
    except OSError as e:
        if e.errno == errno.EEXIST and os.path.isdir(target_directory):
            # The directory already exists.
            pass
        else:
            # Either there exists some file with the same name as the
            # target directory, or there is some different error.
            # Just re-raise the error!
            raise e
    finally:
        return target_directory
