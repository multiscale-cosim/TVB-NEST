from nest_elephant_tvb.launcher.run_exploration import run

if __name__ == "__main__":
    import sys
    print(sys.argv)
    if len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        run("/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/case_up_down/parameter.json")
        # raise Exception('not enough arg')
