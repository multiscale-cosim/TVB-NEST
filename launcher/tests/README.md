## **Integration Tests**

### Prerequisite:

`export PYTHONPATH=/path/to/TVB-NEST/configuration_manager:/path/to/TVB-NEST/launcher`

e.g.

`export PYTHONPATH=/home/user/TVB-NEST/configuration_manager/:/home/user/TVB-NEST/`

### Simple Integration Test:

`python3 /path/to/launcher/main.py --action-plan /path/to/tests/plans/simple_plan_on_local.xml --parameters /path/to/tests/parameters/simple_parameters.xml`

e.g.

`python3 /home/user/TVB-NEST/launcher/main.py --action-plan /home/user/TVB-NEST/launcher/tests/plans/simple_plan_on_local.xml --parameters /home/user/TVB-NEST/launcher/tests/parameters/simple_parameters.xml`

### Client/Server MPI Inter-Communication

`python3 /home/user/TVB-NEST/launcher/main.py --action-plan /path/to/tests/plans/mpi_intercommunicator_plan_on_local.xml --parameters /path/to/tests/parameters/empty_parameters.xml`

e.g.
`python3 /home/user/TVB-NEST/launcher/main.py --action-plan /home/user/TVB-NEST/launcher/tests/plans/mpi_intercommunicator_plan_on_local.xml --parameters /home/user/TVB-NEST/launcher/tests/parameters/empty_parameters.xml`
