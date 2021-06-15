#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from nest_elephant_tvb.Tvb.simulation_Zerlaut import run_normal
import sys

if __name__ == "__main__":
    if len(sys.argv) == 2:
        run_normal(sys.argv[1])
    else:
        raise Exception('not good number of argument ')