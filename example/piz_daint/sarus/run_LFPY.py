from analyse.LFPY.LFP import generate_LFP

if __name__ == '__main__':
    import sys

    if len(sys.argv) == 8:
        generate_LFP(sys.argv[1], sys.argv[2], [int(sys.argv[3]), int(sys.argv[4])],
                     [int(sys.argv[5]), int(sys.argv[6])], [int(sys.argv[7]), int(sys.argv[8])], name=sys.argv[9])
    else:
        raise Exception('bad number of argument')
