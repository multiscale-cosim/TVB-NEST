from .run_exploration import run

print(__name__)
if __name__ == "__main__":
    print(__name__)
    import sys
    print(sys.argv)
    if len(sys.argv) == 2:
        run(sys.argv[1])
    else:
        raise Exception('not enough arg')
