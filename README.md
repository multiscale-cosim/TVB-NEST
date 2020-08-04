# TVB-NEST
EBRAINS The Virtual Brain - NEST cosimulation

## Concept 
This is a proof of concept for the co-simulation between TVB and NEST.
It should be flexible and scalable to adapt to any networks simulation and run in supercomputers.

## Table of Contents
1. [Installation and update](#installation)
    1. [Advice for using the repository](#advice)
    2. [Different Installation](#diff_install)
2. [Dependencies](#dependencies)
    1. [Nest](#dependencies_nest)
    2. [MPI](#dependencies_mpi)
    3. [Python library](#dependencies_py)
3. [Adaptation to your own usage](#usages)
    1. [The management of parameters or change parameters](#usages_1)
    2. [The modification of translation](#usages_2) 
    3. [The modification of Nest configuration](#usages_3)
    4. [The modification of TVB configuration](#usages_4)
4. [Tests](#tests)
    1. [How to test the installation](#test_1)
5. [Cluster](#cluster)
    1. [Deepest](#deepest)
6. [Future implementation](#future)
7. [Extension](#extension)
8. [Files](#files)

## Installation and update :<a name="installalation"></a>
### Advice for using the repertory :<a name="advice"></a>
For cloning the project, you also need to clone the submodule ([git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules)). \
I advise you to clone the repertory with the following command :  git clone --recurse-submodules 

For updating the folder, you also need to update the submodule by the following command: git submodule update.

### Different Installation :<a name="diff_install"></a>
In the folder installation, you have three possibilities : 
- docker :
    The script '/install/deep/create_container_X.sh' is  for creating a docker image from the configuration file '/install/deep/Nest_TVB_config_X.dockerfile'. The configuration 1 use is based on alpine distribution (1) and the configuration 2 is based on debian distribution (2).\
    The script '/install/deep/run_image.sh' uses the test 'tests/run_co-sim_test_docker.py'.
- singularity : 
    The folder contains the same file as docker except for testing the image.\
    The configuration full (3) is to create an image for running the example from jupyter notebook.([example](#example))
- virtual environment :
    The script 'create_virtual_python.sh' creates a virtual environment in the current path with all the python library for running the script.
    WARNING : the library for PyNest is not available in this environment. You should compile Nest and add the path of the library in the PYTHONPATH before to use it.
- installation on DEEP-EST :
    The script 'install/deep/install.sh' is for the installation in the cluster Deepest. (see the section [cluster](#cluster))
- local installation : the script is only an example of local installation in an environment where you don't have super user right. 
WARNING : It should not be used in your computer.

If you install in your computer, you should look at the configuration file of the deepest installation, the local installation or the singularity configuration.\
The installation is not for the moment standardize.\
For testing your installation, you should look at the section [Test](#tests) or the folder tests.

## Dependencies<a name="dependencies"></a>
#### Nest<a name="dependencies_nest"></a>
the version of Nest is base of Nest 3 is already included in the repertory\
For the dependency of Nest, you should look at this page : https://nest-simulator.readthedocs.io/en/stable/installation/linux_install.html \
For having the correct configuration parameters of Nest, you should look at this page : https://nest-simulator.readthedocs.io/en/stable/installation/install_options.html \
I use the next commands for compiling nest : \
   * mkdir ./lib/nest_run \
   * mkdir ./lib/nest_build \
   * cd  ./lib/nest_build \
   * cmake ..nest-io-dev/ -DCMAKE_INSTALL_PREFIX:PATH='../lib/nest_run/' -Dwith-python=3 -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-debug=ON \
   * make
   
#### MPI<a name="dependencies_mpi"></a>
MPI need to be MPI-3 ( I use the following implementation : http://www.mpich.org/static/downloads/3.1.4/mpich-3.1.4.tar.gz)

#### Python library<a name="dependencies_py"></a>
The script 'install/py_venv/create_virtual_python.sh' is to install all python dependency in a virtual environment in the current folder. (see [installation section](#installation))

Python library :
1. nose
2. numpy 
3. cython
4. Pillow
5. scipy
6. elephant
7. mpi4py
8. tvb-library version >=2.0
9. tvb-data version >=2.0
10. tvb-gdist version >=2.0

## Adaptation to your own usage<a name="usages"></a>
### The management of parameters or change parameters:<a name="usages_1"></a>
 The file 'nest_elephant_nest/orchestrator/parameters_managers.py' which manages the modification of parameters of the exploration and links parameters.
 If you change a parameter, you should be careful of the dependency between parameters ( see the file 'example/parameter/test_nest.py' ).
 If you explore a particular parameter, you should be careful of the name of parameters and the real modification of it.
 
### If you modify the translation part :<a name="usages_2"></a>
 The translation function is simple to change the function.
 In the files, 'nest_elephant_nest/translation/science_tvb_to_nest.py' or 'science_nest_to_tvb.py' contains all the functions for exploring different solution of translations.
 The translation tvb to nest is composed of one function :
 - generate_spike :
 This function takes in input the rates of TVB and generates an array with all the input spike for each neuron.
 Actually, the function is a generation of spike with a generator of inhomogeneous Poisson (implemented in elephant).
 The parameter is the percentage of rates shared between all neurons. (It's a very simple translation.) 
 
 The translation nest to TV bis composed of two functions : (see the folder documentation)
 - add_spikes : 
    This function takes an array of spike and store it in a buffer.
    The actual function store the spike in a histogram
 - analyse:
    This function takes the buffer and transforms in rates.
    Actually, the model is based on a sliding window of the histogram. The analyse generate rate with a sliding window.
 
### If you modify the Nest configuration:<a name="usages_3"></a>
You should create a new file in 'nest_elephant_nest/Nest/ ' and modify the orchestrator and the script 'nest_elephant_nest/Nest/run_mpi_nest.sh'. 
The orchestrator needs to have access to 2 files for the co-simulation : spike_generators.txt and spikes_detectors.txt . These files contain the ids of devices for the connection with Nest and there are generate by the configuration of Nest.
If you need an example, you can look 'nest_elephant_nest/Nest/simulation_Zerlaut.py'.
The example is composed of functions for the configuration of the simulator and the running functions at the end.

There are 5 steps : 
- Configure kernel of Nest 
- Create the population of neurons
- Create the connection between and inside population 
- Create the device (WARNING: this function need to send the ids of device using MPI. These ids are used for the configuration of the translators.)
- Simulate

The first 4 steps are the initialization of Nest.\
If you include or remove the parameters of Nest, you need to change 'nest_elephant_nest/simulation/parameters_managers.py' to include or remove the link between parameters.
Moreover, the name of the section of parameters need to begin by 'param'.

### If you modify TVB configuration:<a name="usages_4"></a>
You should change the beginning of the file nest_elephant_nest/TVB/simulation_Zerlaut.py .
This file contains the initialization and configuration of TVB in the function init. All the parameters are used in this file.
The other function is the wrapper for I/O communication with MPI and the launcher of the simulator TVB.
The dependency with the parameter of Nest is defined in 'nest_elephant_nest/orchestrator/parameters_managers.py'.
There exist two types of monitors depending on your use of the model TVB. Interface_co_simulation.py is to include a measure from Nest inside the model. Interface_co_simulation_parallel.py is to replace the coupling variable by a measure from Nest. 

## Tests<a name="tests"></a>
### How to test the installation (they don't check the correctness of the simulation)<a name="tests_1"></a>

1. Test the Nest I/O :
    1. 'tests/test_input_nest_current.sh'\
     The test is for the step current generator with mpi communication. The array at this end of the output is the event record by a spike detector.
     If there is an event from the neurons 1, this meaning the device impact the dynamic of the neuron.
    2. 'tests/test_input_nest_current_multiple.sh'\
     The test is for the step current generator with mpi communication in different parameterization of Nest. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
     The checking is the same then previously for each test. The time of each spike events between runs need to be different. 
    3. 'tests/test_input_nest_spike.sh'\
     The test is for the device spike generator with mpi communication. The two arrays at this end of the output is the event record by a spike detector.
     The first array is a recording of the neurons 1. If there are events, this means the spike generator doesn't have an impact on the neurons.
     The second array is a recording of the two spike generator itself. If there is no event from the id 7, this mean there will be a problem. We can compare the value of the array with the data send previously.  
    4. 'tests/test_record_nest_spike.sh'\
     The test is for testing the spike detector and the spike generator with mpi communication. It's just to test it's possible to run it.
    5. 'tests/test_record_nest_spike_multiple.sh' (also test the multithreading) 
     The test is for testing the spike detector and the spike generator with mpi communication in different parameterization of Nest. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
      It's just to test it's possible to run it.
2. Translation:
    1. 'tests/test_translator_tvb_to_nest.sh'\
        This test is for the module translation between Tvb to Nest.
        You can check if it succeeds to exist without error (exit of Nest Input and TVB output and the end of the processes).
        You can check if they receive size and the array are different to zero for Nest INPUT. Nest Input (x) needs to be different. 
    2. 'tests/test_translator_nest_to_tvb.sh'\
        This test is for the module translation between Nest to TVB.
        You can check if it succeeds to exist without error (exit of Nest Output and TVB input and the end of the processes).
        The second evaluation is by looking at the alternation between TVB INPUT and NEST OUTPUT.
        The third check is the right value of Nest Output need to be different to zeros (number of spikes receive * 3) 
    3. 'tests/test_nest_save.sh'\
       This test is for the module translation between Nest save. The implementation of this translator reuse the interface with Nest from Nest to TVB.
       You can check if it succeeds to exist without error (exit of Nest Output and the end of the processes).
3. Orchestrator:
    1. 'tests/run_tvb_one.py' : run exploration 2D of TVB only with one region
    2. 'tests/run_tvb.py' : run exploration 2D of TVB only with the test parameter
    3. 'tests/run_nest_one.py' : run exploration 2D of Nest only with one region 
    4. 'tests/run_nest.py' :  run exploration 2D of Nest only with the test parameter
    5. 'tests/run_nest.py' : run exploration 2D of Nest with translator for saving the mean firing rate
    6. 'tests/run_nest_co-sim.py' : run exploration 2D co-simulation with test parameter
    7. 'tests/run_nest_co-sim_test.py' : file using by test_co-sim.sh
4. Test the co-simulation:
    1. 'tests/test_co-sim.sh'\
        This test is for the application. It tests the co-simulation in different parameterization of Nest. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
        The success of these tests is to arrive at the end without any errors. 
    
5. For testing the co-simulation in a container : (see [installation](#installation) for the creation of image)
   * 'install/docker/test_image.sh'
   * 'install/singularity/test_image.sh'

    These tests are based on the script 'tests/run_nest_co-sim_test.py'. They need a parameter to choose the image to test.\
    For docker, 0 is for alpine distribution (local:NEST_TVB_IO) and 1 is for the debian distribution  (local:NEST_TVB_IO_2).\
    For singularity, 0 is for the full image (Nest_TVB_full.simg), 1 is for alpine distribution (Nest_TVB_1.simg) and 2 is for debian distribution (Nest_TVB_2.simg).

## Cluster <a name="cluster"></a>
The option for using the project in a cluster is based on the system manager slum. If you have another system manager, you need to modify all 'nest_elephant/orchestrator/run_exploration.py'.
For the moment, it's impossible to add options to slim but it's easy to add this feature.
WARNING: this project is only tested on DEEPEST.
### DEEPEST : <a name="deepest"></a>
The installation and the option for the cluster are built for DEEPEST (https://www.deep-projects.eu/).
The file 'install/deep/install.sh' is to compile and install all the python library in the folder lib for the usage in the cluster.
For testing the installation, you need to change the file /tests/init.sh. The paraemter CLUSTER and DEEPEST need be change from 'false' to 'true'.

## Future implementation :<a name="future"></a>
1. Improve the communication pattern for the input of Nest
2. Add a second function to transform rate to spike based on Multiple Interaction Process Model
3. Add test for the input and output of interface TVB.
4. Add test for validating values of a simulation
5. Add some functions of the simulation Nest to include multimeter recorder and other stimuli.
6. Refractor the code to avoid the same piece of code in different file ( example :  the creation of a logger, ...)

## Extension :<a name="extension"></a>
1. Replace the device in Nest by included the input directly in the neurons 
2. Improve the orchestrator for managing communication of MPI and the synchronization between all processes

## Files<a name="files"></a>
* doc : Documentation of the project
    * UML : UML of communication and state of modules
* example : an example of the usage of  the proof of concept
    * analyse : the function for analysis of the output of examples
    * parameter : parameter for the simulation and the data
        * data_mouse : data from Allen Institute of mouse connectome is composed of the file of the distance between each region and the weight of the connections
        * test_nest.py : parameter for testing the installation 
    * test_1 : folder for running example
        * parameter : parameters of example_1
    * example_1.ipynb : jupyter notebook for running an example of co-simulation
* [install](#installation)
    * [deep](#deepest)
        install.sh : installation on deepest cluster
		Should be installed in /p/project/type1_1/[personaldir]
    * docker
        create_docker.sh, create_docker_2.sh : create the docker image for the project
        Nest_TVB.dockerfile, Nest_TVB_2.dockerfile : file of configurations for docker
        run_images : example of running co-simulation with the image 
    * py_venv
        create_virtual_python.sh : create the virtual environment
    * singularity
        create_container.sh, create_container_2.sh : create the singularity image for the project
        Nest_TVB_config.singularity, Nest_TVB_config_2.singularity : file of configurations for singularity
        create_container_full.sh, Nest_TVB_config_full.singularity : file for the creation of the image for running a jupyter server with the co-simulation
        run_images : example of running co-simulation with the image 
* nest-io-dev : the branch of Nest with IO using MPI
* nest_elephant_nest: file which contains all the kernel of the simulation
    * Nest : folder contains all the file to configure and launch Nest
        * run_mpi_nest.sh : run the simulation Zerlaut with MPI ( use by the orchestrator for launch Nest)
        * simulation_Zerlaut.py : run the Nest part of the application
    * orchestrator:
        * parameters_manager.py : script which manages the parameters ( saving, modify parameters of exploration and link between parameters. )
        * run_exploration.py : main script of the simulation for the exploration of 1 or 2 parameters with 1 or 2 simulators
    * translation: folder contains the translator between TVB and Nest
        * run_... : for running the different component
        * nest_to_tvb : for communication between Nest to TVB
        * tvb_to_nest : for communication between TVB to Nest
        * science_... : files contain the function to transform spike to rate and opposite
        * rate_spike : special function use in science based on elephant applications
        * test_file : all the tests of translators and Nest I/O
    * TVB
        *  modify TVB : folder contains file for the interface and the extensions of TVB
            * Zerlaut.py : model of the Mean Field
            * noise.py : specific noise for this model
            * Interface_co_simulation.py : interface can be used only in sequential but allow using intermediate result for the firing rate. (Need to compute Nest before TVB.)
            * Interface_co_simulation_parallel.py : can be used to compute TVB and Nest in same time
            * test_interface... : test for the interface with the model of Wong Wang
        * simulation_Zerlaut.py : the script for the configure and the running of the simulator of TVB
        * run_mpi_tvb.sh : run the simulation Zerlaut with MPI ( use by the orchestrator for launch TVB )
* test_nest: contains all the [test](#tests)   
