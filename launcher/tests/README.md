## **Integration Tests**

### Prerequisite:
#### On Super-Computers:
`module load GCC ParaStationMPI mpi4py SciPy-Stack/2020-Python-3.8.5`

#### Setting-Up Environment Variables
`export MULTISCALETVBNEST=/path/to/TVB-NEST`

`export PYTHONPATH=/path/to/TVB-NEST/configuration_manager:/path/to/TVB-NEST/launcher`

e.g.
`export MULTISCALETVBNEST=/home/user/TVB-NEST/`

`export PYTHONPATH=${PYTHONPATH}:/home/user/TVB-NEST/configuration_manager/:/home/user/TVB-NEST/`

Using the MULTISCALETVBNEST environment variable:
`export PYTHONPATH=${PYTHONPATH}:${MULTISCALETVBNEST}/configuration_manager/:${MULTISCALETVBNEST}`

NOTE: Be aware that the MULTISCALETVBNEST environment variable name is referenced in the XML configuration files.

### Simple Integration Test:
`python3 /path/to/launcher/main.py --action-plan /path/to/tests/plans/simple_plan_on_local.xml --parameters /path/to/tests/parameters/simple_parameters.xml`

e.g.
`python3 /home/user/TVB-NEST/launcher/main.py --global-settings /home/user/TVB-NEST/configuration_manager/global_settings.xml --action-plan /home/user/TVB-NEST/launcher/tests/plans/simple_plan_on_local.xml --parameters /home/user/TVB-NEST/launcher/tests/parameters/simple_parameters.xml`

Using the environment variable defined above:
`python3 ${MULTISCALETVBNEST}/launcher/main.py --global-settings ${MULTISCALETVBNEST}/configuration_manager/global_settings.xml --action-plan ${MULTISCALETVBNEST}/launcher/tests/plans/simple_plan_on_local.xml --parameters ${MULTISCALETVBNEST}/launcher/tests/parameters/simple_parameters.xml`

```python3 ${MULTISCALETVBNEST}/launcher/main.py --global-settings ${MULTISCALETVBNEST}/configuration_manager/global_settings.xml --action-plan ${MULTISCALETVBNEST}/launcher/tests/plans/simple_plan_on_cluster.xml --parameters ${MULTISCALETVBNEST}/launcher/tests/parameters/simple_parameters.xml```

### Client/Server MPI Inter-Communication
`python3 /home/user/TVB-NEST/launcher/main.py --action-plan /path/to/tests/plans/mpi_intercommunicator_plan_on_local.xml --parameters /path/to/tests/parameters/empty_parameters.xml`

e.g.
`python3 /home/user/TVB-NEST/launcher/main.py --action-plan /home/user/TVB-NEST/launcher/tests/plans/mpi_intercommunicator_plan_on_local.xml --parameters /home/user/TVB-NEST/launcher/tests/parameters/empty_parameters.xml`

Using the environment variable defined above:
```python3 ${MULTISCALETVBNEST}/launcher/main.py --global-settings ${MULTISCALETVBNEST}/configuration_manager/global_settings.xml --action-plan ${MULTISCALETVBNEST}/launcher/tests/plans/mpi_intercommunicator_plan_on_cluster.xml --parameters ${MULTISCALETVBNEST}/launcher/tests/parameters/empty_parameters.xml```
