from nest_elephant_tvb.Tvb.simulation_Zerlaut import run_normal
import sys

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        run_normal(sys.argv[1])
    else:
        raise Exception('not good number of argument ')