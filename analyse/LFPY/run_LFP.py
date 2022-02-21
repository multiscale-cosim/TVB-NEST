#  Copyright 2020 Forschungszentrum Jülich GmbH and Aix-Marseille Université
# "Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements; and to You under the Apache License, Version 2.0. "
from nest_elephant_tvb.analyse.LFPY.LFP import generate_LFP

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 10:
        generate_LFP(sys.argv[1], sys.argv[2], float(sys.argv[3]), float(sys.argv[4]),
                     [int(sys.argv[5]), int(sys.argv[6])], [int(sys.argv[7]), int(sys.argv[8])], name=sys.argv[9])
    else:
        raise Exception('bad number of argument')
