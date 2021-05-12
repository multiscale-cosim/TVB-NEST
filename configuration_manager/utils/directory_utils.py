# ------------------------------------------------------------------------------
#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor
#  license agreements; and to You under the Apache License, Version 2.0. "
# ------------------------------------------------------------------------------

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
            # Just re-raise the error for now.
            raise e
        return target_directory