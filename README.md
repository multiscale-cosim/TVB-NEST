#Co-simulation Between TVb and NEST
## Concept 
This is a prof of concept for the co-simulation between TVB and NEST.
It should be flexible and scalable to adapt to any networks simulation and run in supercomputers.

WARNING : this code has some bugs and missing elements.
WARNING : All the script needs to be launch in the repertory where there are.


## Table of Contents
1. [Installation and update](#installalation)
    1. [Advice for using the repertory](#advice)
    2. [Different Installation](#diff_install)
2. [Dependencies](#dependencies)
3. [Adaption to your own usage](#usages)
    1. [The management of parameters or change parameters](#usages_1)
    2. [The modification of the translation](#usages_2) 
    2. [If you want to modify the Nest configuration](#usages_3)
    3. [If you want to modify TVB configuration](#usages_4)
4. [Tests](#tests)
    1. [How to test the installation](#test_1)
5. [Future implementation](#future)
6. [Extension](#extension)
7. [Files](#files)

## Installation and update :<a name="installalation"></a>
### Advice for using the repertory :<a name="advice"></a>
For cloning the project, you need also to clone the submodule.
I advice you to clone the repertory with the following command :  git clone --recurse-submodules 

For updating the folder, you need also to update the submodule by the following command: git submodule update

### Different Installation :<a name="diff_install"></a>
In the folder installation, you have three possibilities : 
- docker :
    There are one script for creating a docker image and one script for running a example of usage of this image.
    There are the possibility of two different OS : alpine (1) and debian (2)
- singularity : 
    The same function for docker are available for singularity
- virtual environment :
    There are one script for create a virtual environment with all the python library for running the script.
    WARNING : the library for PyNest are not available in this environment. You should compile Nest and add the path of the library in the PYTHONPATH before to use it.

If you want to install in your computer, you should look the configuration file of singularity.
This are only possibility and not a formal way to install and to use this git repository.
To test your installation, you should look the section Test or the folder test_nest

## Dependencies<a name="dependencies"></a>
Nest : the version of Nest is base of Nest 3 is already included in the repertory
        For the dependency of nest, you should look this page : https://nest-simulator.readthedocs.io/en/stable/installation/linux_install.html
        For having the good configuration parameters of Nest, you should look this page : https://nest-simulator.readthedocs.io/en/stable/installation/install_options.html
        I use the next commands for compiling nest :
        mkdir ./lib/nest_run
        mkdir ./lib/nest_build
        cd  ./lib/nest_build
        cmake ../../nest-io-dev/ -DCMAKE_INSTALL_PREFIX:PATH='../lib/nest_run/' -Dwith-python=3 -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-debug=ON
        make 
MPI : MPI need to be MPI-3 ( I use the following implementation : http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz)

Python library :
1. TVB version >=2.0
2. numpy
3. mpi4py
5. threading
6. scipy
7. json
9. numba
10. quantities
11. elephant
12. neo

## Adaption to your own usage<a name="usages"></a>
### The management of parameters or change parameters:<a name="usages_1"></a>
 The file nest_elephant_nest/simulation/parameters_managers.py which manage the modification of parameters of the exploration and the link between parameters.
 If you want to change a parameters, you should be careful of the dependency between parameters ( see the file test_parameters ).
 If you want to explore a particular parameters, you should be careful of the name of parameters and the real modification of it.
 
### The modification of the translation :<a name="usages_2"></a>
 The translation function is simple to change the function.
 In the files nest_elephant_nest/simulation/files_translation/science_tvb_to_nest.py or science_nest_to_tvb.py contains all the functions for exploring different solution of translations.
 The translation tvb to nest is composed of one function :
 - generate_spike :
 This function take in input the rates of TVB and generate an array with all the input spike for each neurons.
 Actually, the function is a generation of spike with a generator of inhomogeneous poisson (implemented in elephant).
 The parameter is the percentage of rate shared between all neurons. (it's a very simple translation) 
 
 The translation nest to tvb is composed of two functions :
 - add_spikes : 
    This function takes an array of spike and store it in a buffer.
    The actual function store the spike in an histogram
 - analyse:
    This function take the buffer and transform in rates.
    Actually, the model is based on a sliding window of the histogram. The analyse generate rate with a sliding window.
 
### If you want to modify the Nest configuration:<a name="usages_3"></a>
You should change the file nest_elephant_nest/simulation/simulation_nest.py
The most important of this file is the the function at the end call for the run exploration.
There are 5 step : 
- Configure Nest
- Create the population of neurons
- Create the connection between population 
- Create the device (WARNING: this function need to send the ID's of device using MPI. This ids are used for the configuration of the translators)
- Simulate

The 4 first step are the initialisation of Nest.
If you include or remove the parameters of Nest, you need to change nest_elephant_nest/simulation/parameters_managers.py for remove the link between parameters.
Moreover, the name of the parameters need to begin by 'param'.  

### If you want to modify TVB configuration:<a name="usages_4"></a>
You should change the beginning of the file nest_elephant_nest/simulation/simulation_zerlaut.py
The function init create the simulator for running TVB. All the parameters are use in this file.
The dependency with the parameter of Nest are define in nest_elephant_nest/simulation/parameters_managers.py. 

## Tests<a name="tests"></a>
### How to test the installation (don't the correctness of the simulation)<a name="tests_1"></a>
Before every test include in your python path the folder and the installation of Nest

Example/test of the different modules
1. Nest :
    1. test_nest/test_input_nest_current.sh
    2. test_nest/test_input_nest_current_multiple.sh (test also the multi-threading)
    3. test_nest/test_input_nest_spike.sh 
    4. test_nest/test_record_nest_spike.sh
    5. test_nest/test_record_nest_spike_multiple.sh (test also the multi-threading) 
2. test_nest/test_translator_nest_to_tvb.sh
3. test_nest/test_translator_tvb_to_nest.sh
4. test_nest/test_nest_save.sh

Test only nest : run_nest_one.py (for 1 region in Nest but it can be easily extend to 112 regions)
Test only tvb : run_tvb_one.py (for 1 region in TVB but it can be easily extend to 112 regions)

For testing the co-simulation, you can check : 
    - test_nest/test_co-sim.sh
    - install/docker/run_image.sh
    - install/singularity/run_image.sh

## Future implementation :<a name="future"></a>
1. Improve the communication pattern for the input of Nest
2. Install on cluster
3. Add a second function to transform rate to spike based on Multiple Interaction Process Model
4. Improve synchronisation between modules (actually file synchronization).
5. Add test for the input an output of interface TVB.
6. Add test for valid the value a simulation
7. Add some functions of the simulation Nest to include multimeter recorder and other stimuli. 

## Extension :<a name="extension"></a>
1. Replace the output of simulator by a streaming output function.
2. Replace the device in Nest by include the input direct in the neurons 
3. Create an orchestrator for managing communication of MPI and the synchronisation between all the elements

## Files<a name="files"></a>
* doc : Documention of the project
    * UML : UML of communication and state of modules
* [install](#installalation)
    * docker
        create_docker.sh, create_docker_1.sh : create the docker image for the project
        Nest_TVB.dockerfile, Nest_TVB_1.dockerfile : file of configuration for docker
        run_images : example of running co-simulation with the image 
    * py_venv
        create_virtual_python.sh : create the virtual environment
    * singularity
        create_container.sh, create_container_1.sh : create the singularity image for the project
        Nest_TVB_config.singularity, Nest_TVB_config_1.singularity : file of configuration for singularity
        run_images : example of running co-simulation with the image 
* nest-io : new version of Nest (old repertory will disappear)
* nest-io-dev : the branch of Nest with IO using MPI
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
        * parameters_manager.py : script which manage the parameters ( saving, modify parameters of exploration and link between parameters.
        * run_exploration.py : main script of the simulation for the exploration of 1 parameters with one or 2 simulators
        * simulation_nest.py : the script the configuration and the running of the simulation of Nest
        * simulation_zerlaut.py : the script for the configure and the running of the simulator of TVB
* test_nest: contains all the [test](#tests)   
