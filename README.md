#Co-simulation Between TVb and NEST
#READ IT before to use this :
## Concept 
This is a prof of concept for the co-simulation between TVB and NEST.
It should be flexible and scalable to adapt to any applications and run on supercomputers.

WARNING : this code has some bugs and missing elements.

##Future implementation :
1. **FOR DEBUGGING** : Create a debugger of all the components 
2. Reproducibility : 
    1. Add seed in the science module for TVB to Nest
    2. Solve the issue of Nest (https://github.com/nest/nest-simulator/issues/1409)
3.  Add test for the input an output of interface TVB
4.  Miss a mechanism to synchronise all the components at the begging system at the begging.
5.  It is missing the initialisation for the Communication
6.  Manage the MPI/Threading of Nest (Actual give a segmentation error. For avoiding it, put the same number of MPI process than virtual process)
7.  Finish to change the noise in TVB
8.  Modify the function generates parameters in run_explorations parameters for all parameters.
9.  Add some functions of the simulation Nest to include multimeter recorder and other stimuli. 

##Test
### The Missing Tests
1.  The ending of the simulation is not ready to use. They’re not test for check if the application finish correctly.
2.  The saving of histogram is not testing.
3.  Miss control over the time of all the simulator during the simulation
### How to test the application
Before every test include in your python path the folder and the installation of Nest

Example/test of the different components
1. test_nest/test_input_nest_current.sh
2. test_nest/test_input_nest_spike.sh 
3. test_nest/test_record_nest_spike.sh
4. test_nest/test_translator_nest_to_tvb.sh
5. test_nest/test_translator_tvb_to_nest.sh

Test only nest : run_nest_one.py,run_nest_two.py,run_nest_three.py (test with 1, 2 ou 3 regions)
Test only tvb : run_tvb_one.py,run_tvb_two.py,run_tvb_three.py (test with 1, 2 ou 3 regions)
Test co-simulation : 
    mpirun -n X python test_nest/run_co-sim.py 

## Future ideas
1. Need to create an orchestrator for managing communication of MPI and the synchronisation between all the elements
2. The implementation of any translator can be done by replacing the function in the file science
3. Increase the Configuration file for a generalisation of the configuration of Nest and TVB.
    For the moment the configuration is based on region connected. Each region has 2 populations of excitatory and inhibitory neurons.
    The type of the neurons is the same everywhere.
    TVB is based on a model based on the model of adaptive exponential integrate and fire neurons. The most of the configuration is coming from the configuration of Nest.
4. Improvement of the MPI protocol between all the components
5. Improve the different I/O interface for all the components

## Dependencies
Nest : the version  of Nest is base of Nest 3 is already included in the repertory

MPI :

Python library :
1. TVB version >=2.0
2. numpy
3. mpi4py
5. threading
6. scipy
7. json
8. subprocess
9. numba
10. quantities
11. elephant
12. neo

## Files
* nest-io : new version of Nest (need to be compiled with MPI option)
* nest_elephant_nest: file which contains all the kernel of the simulation
    * parameter : parameter for the simulation and the data
        * data_mouse : data from Allen Institute of mouse connectome is composed of the file of the distance between each region and the weight of the connections
    * simulation : folder contains every file for the simulation
        * file_translation: folder contains the translator between TVB and Nest
            * run_... : for running the different component
            * nest_to_tvb : for the communication between Nest to TVB
            * tvb_to_nest : for the communication between TVB to Nest
            * science_... : files contain the function to transform spike to rate and opposite
            * rate_spike : special function use in science based on elephant applications
            * test_file : all the tests of translators and Nest I/O
        *  file TVB : folder contains file for the interface of TVB 
            * Zerlaut.py : model of the Mean Field
            * noise.py : specific noise for this model
            * Interface_co_simulation.py : interface can be used only in sequential but allow using intermediate result for the firing rate. (Need to compute Nest before TVB)
            * Interface_co_simulation_parallel.py : can be used to compute TVB and Nest in same time
            * test_interface... : test for the interface with the model of Wong Wang
        * correct_parameters.sh : script for modifying the parameters after to save in json (allow to use like python package)
        * run_exploration.py : main script of the simulation for the exploration of 2 parameters with one or 2 simulators
        * simulation_nest.py : the script the configuration and the running of the simulation of Nest
        * simulation_zerlaut.py : the script for the configure and the running of the simulator of TVB
* test_nest: contains all the test (see the section test)   
