from example.parameter import test_nest as parameter_test
from nest_elephant_tvb.orchestrator.run_exploration import run_exploration_2D


def run_exploration(path, begin, end, nb_VP, nb_mpi, cluster):
    parameter_test.param_co_simulation['co-simulation'] = True
    parameter_test.param_co_simulation['cluster'] = cluster
    parameter_test.param_co_simulation['nb_MPI_nest'] = nb_mpi
    parameter_test.param_nest['total_num_virtual_procs'] = nb_VP
    parameter_test.param_nest_topology['nb_neuron_by_region'] = 100
    parameter_test.param_co_simulation['id_region_nest'] = [1, 2]
    parameter_test.param_co_simulation['synchronization'] = 3.5
    parameter_test.param_nest_background['multimeter'] = False
    parameter_test.param_nest_background['record_spike'] = False
    run_exploration_2D(path, parameter_test, {'g': [1.0], 'mean_I_ext': [0.0]}, begin, end)


def test_cosim():
    run_exploration('./tests/test_docker/', 0.0, 21.0, 4, 4, False)
