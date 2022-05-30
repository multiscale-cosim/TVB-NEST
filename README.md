# TVB-NEST PAPER TIMER
EBRAINS The Virtual Brain - NEST co-simulation with timer 

## Concept 
This is the co-simulation between TVB and NEST with timer.
It should be flexible and scalable to adapt to any networks simulation and run in supercomputers.
You can find some results and singularity image of the project in this Zenedo depot : http://dx.doi.org/10.5281/zenodo.6370058 

## Table of Contents
1. [Installation and update](#installation)
    1. [Advice for using the repository](#advice)
    2. [Different Installation](#diff_install)
2. [Example](#example)
    1. [Mouse Brain](#mouse_brain)
3. [Dependencies](#dependencies)
    1. [NEST](#dependencies_nest)
    2. [MPI](#dependencies_mpi)
    3. [Python library](#dependencies_py)
4. [Adaptation to your own usage](#usages)
    1. [The management of parameters or change parameters](#usages_1)
    2. [The modification of transformers](#usages_2) 
    3. [The modification of NEST configuration](#usages_3)
    4. [The modification of TVB configuration](#usages_4)
5. [Tests](#tests)
    1. [How to test the installation](#test_1)
6. [Cluster](#cluster)
    1. [Deepest](#deepest)
7. [Future implementation](#future)
8. [Extension](#extension)
9. [Files](#files)

## Installation and update :<a name="installalation"></a>
### Advice for using the repertory :<a name="advice"></a>
For cloning the project, you also need to clone the submodule ([git submodule](https://git-scm.com/book/en/v2/Git-Tools-Submodules)). \
I advise you to clone the repertory with the following command :  git clone --recurse-submodules 

For updating the folder, you also need to update the submodule by the following command: git submodule update.

### Different Installation :<a name="diff_install"></a>
WARNING: all the installation can run the co-simulation but some of them doesn't included Neuron which is necessary 
for the simualtion of LFP or they doesn't include VTK whihc is necessay for some image of the paper.
In the folder installation, you have multiple possibilities (personal computer, cluster, container):
- container :
    - docker :\
        The script 'install/docker/create_container.sh' is  for creating a docker image from the configuration file
        'install/docker/NEST_TVB_paper.dockerfile'.\
        For saving the docker image in file, the script save_docker_paper.sh, create tar file with the docker image 
        which can be load by [docker]() or [sarus]().
        The script 'install/docker/run_image.sh' uses the test 'tests/run_co-sim_test_docker.py'.
    - singularity : \
        The script 'install/docker/create_container_paper.sh' is  for creating a singularity image from the configuration file
        'install/docker/NEST_TVB_paper.dockerfile'. The default configuration is based on debian distribution.
        Another possibility is the script 'install/docker/create_container_paper_alpine.sh' which use alpine os (light os).
- personal computer :      
    - virtual environment :
        The script 'create_virtual_python.sh' creates a virtual environment in the current path with all the python library for running the script.
        WARNING : the library for PyNEST is not available in this environment. You should compile NEST and add the path of the library in the PYTHONPATH before to use it.
    - empty environment where you don't have the root access:
        WARNING : You should not use this script for your personal computer.
        If you do it, you need to check careful of the software already install on your computer for not install them two times. \
        the script is only an example of local installation in an environment where you don't have super user right.
        For running a simulation, you need to be careful of the path for include the software install.
- clusters:      
    - installation on DEEP-EST :
        The script 'install/deep/install.sh' is for the installation in the cluster Deepest. (see the section [cluster](#cluster))
    - installation on JUSUF :
        The script 'install/jusuf/install.sh' is for the installation in the cluster JUSUF. (see the section [cluster](#cluster))
    - installation on Piz Daint :
        The script 'install/piz-daint/install.sh' is for the installation in the cluster Piz Daint. (see the section [cluster](#cluster))
    - installation on INS cluster :
        The script 'install/local_cluster/install.sh' is for the installation in the INS cluster. (see the section [cluster](#cluster))

If you install in your computer, you should look at the configuration file of the singularity configuration or the local installation.\
The installation is not for the moment standardize. \
For testing your installation, you should look at the section [Test](#tests) or the folder tests.

## Example<a name="example"></a>
In the folder example, you can find jupyter notebook for having a demonstration of this project and some result of the simulation.
The [result of the simulation](#short_sim) can help you to understand the structure of folders for saving the output of simulation and to prepare your visualization.
The structure of the result is defined in the launcher file, it can be modified but this organization helps to separate the different modules of the simulation and the logs. 

The example is based on the application of the framework. For the moment, there is only one application.

#### Mouse Brain<a name="mouse_brain"></a>
This example is a demonstration of the full-mouse brain with 2 regions simulate with NEST.\
For running this example, you need to create the full image of singularity which contains all the modules for the jupyter notebook.
Once you have this image, you should launch the next command of the folder example:
> singularity run --app jupyter-notebook ../install/singularity/NEST_TVB_full.simg

The jupyter home page will start in your browser and you can launch the jupyter notebook.

This example is composed of 4 parts:
   1. The explanation of all the parameters of the application
   2. The running part of the application
   3. The display of the result of the simulation (short simulation)
   4. The display of the result of a long simulation
   
## Dependencies<a name="dependencies"></a>
#### NEST<a name="dependencies_nest"></a>
The version of NEST is base of NEST 3 is already included in the repertory\
For the dependency of NEST, you should look at this page : https://nest-simulator.readthedocs.io/en/v3.0/installation/linux_install.html . \
For having the correct configuration parameters of NEST, you should look at this page : https://nest-simulator.readthedocs.io/en/v3.0/installation/install_options.html \
I use the next commands for compiling NEST : 
   * mkdir ./lib/nest_run 
   * mkdir ./lib/nest_build 
   * cd  ./lib/nest_build 
   * cmake ../../nest-io-dev/ -DCMAKE_INSTALL_PREFIX:PATH='../lib/nest_run/' -Dwith-python=3 -Dwith-mpi=ON -Dwith-openmp=ON -Dwith-debug=ON \
   * make -j
   * make install
   
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
11. neuron
12. hybrid-LFP
13. vtk

## Adaptation to your own usage<a name="usages"></a>
### The management of parameters or change parameters:<a name="usages_1"></a>
 The function 'generate_parameter' in the file 'nest_elephant_nest/launcher/run_exploration.py' which manages the modification of parameters of the exploration and links parameters.
 If you want to change a parameter, you should be careful of the dependency between parameters ( see the file 'analyse/parameter/test_nest.py' ).
 If you want to run an exploration along a particular parameter, you should be careful of the name of parameters, the link the others and the real modification of it. (Some parameters can't be changed with the actual interface.)
 
### If you modify the transformation part :<a name="usages_2"></a>
 The transformation function is simple to change the function.
 In the files, 'nest_elephant_nest/transformation/transformation/transformation_function.py' contains all the functions for exploring different solution of transformations.
 The transformation TVB to NEST is composed of one function :
 - generate_spike :
    This function takes in input the rates of TVB and generates an array with all the input spike for each neuron.
    There is actually two option : Single Interaction Process Model and Multiple Interaction Process Model based on the paper Kuhn, Alexandre, Ad Aertsen, and Stefan Rotter. “Higher-Order Statistics of Input Ensembles and the Response of Simple Model Neurons.” Neural Computation 15, no. 1 (January 2003): 67–101. https://doi.org/10.1162/089976603321043702.
    You should use the second function because the first option is very slow. 
    Actually, the functions use the generation of spike from a generator of inhomogeneous Poisson (implemented by the package Elephant).
    The main parameter of these function is the percentage of rates shared between all neurons. 
 
 The transformer NEST to TVB is composed of two functions :
 - add_spikes : 
    This function takes an array of spike and store it in a buffer.
    The actual function store the spike in a histogram
 - analyse:
    This function takes the buffer and transforms in rates.
    Actually, the model is based on a sliding window of the histogram. The analyse generate rate with a sliding window.
   
You can put your own transformation function, if you follow the description of the simulation_time function. 
The synchronization of the modules of the co-simulation is based on the different step of these classes.

### If you modify the NEST configuration:<a name="usages_3"></a>
You should create a new file in 'nest_elephant_nest/Nest/ ' and modify the launcher (run_exploration.py) for the usage of your new script. 
The launcher needs to have access to 2 files for the co-simulation : 'spike_generators.txt' and 'spikes_detectors.txt'. \
These files contain the ids of devices for the connection with NEST and there are generated by the configuration of NEST.
If you need an example, you can look 'nest_elephant_nest/Nest/simulation_Zerlaut.py'.
The example is composed of functions for the configuration of the simulator and the running functions at the end.

There are 5 steps : 
- Configure kernel of NEST 
- Create the population of neurons
- Create the connection between and inside population 
- Create the device (WARNING: this function need to send the ids of device using MPI. These ids are used for the configuration of the transformer.)
- Simulate

The first 4 steps are the initialization of NEST.\
If you include or remove the parameters of NEST, you need to change the function 'create_linked_parameters' in 'nest_elephant_nest/launcher/run_exploration.py' to include or remove the link between parameters.
Moreover, the name of the section of parameters needs to begin by 'param'.

### If you modify TVB configuration:<a name="usages_4"></a>
You should change the beginning of the file 'nest_elephant_nest/TVB/simulation_Zerlaut.py'.
This file contains the initialization and configuration of TVB in the function init. All the parameters are used in this file.
The other function is the wrapper for I/O communication with MPI and the launcher of the simulator TVB.
The dependency with the parameter of NEST is defined in the function 'create_linked_parameters' in 'nest_elephant_nest/launcher/run_exploration.py'.
There exist two types of monitors depending on your use of the model TVB. Interface_co_simulation.py is to include a measure from NEST inside the model. Interface_co_simulation_parallel.py is to replace the coupling variable by a measure from NEST. 

## Tests<a name="tests"></a>
### How to test the installation (they don't check the correctness of the simulation)<a name="tests_1"></a>

1. Test the NEST I/O :
    1. 'tests/test_input_nest_current.sh'\
     The test is for the step current generator with mpi communication. The array at this end of the output is the event record by a spike detector.
     If there is an event from the neurons 1, this meaning the device impact the dynamic of the neuron.
    2. 'tests/test_input_nest_current_multiple.sh'\
     The test is for the step current generator with mpi communication in different parameterization of NEST. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
     The checking is the same then previously for each test. The time of each spike events between runs need to be different. 
    3. 'tests/test_input_nest_spike.sh'\
     The test is for the device spike generator with mpi communication. The two arrays at this end of the output is the event record by a spike detector.
     The first array is a recording of the neurons 1. If there are events, this means the spike generator doesn't have an impact on the neurons.
     The second array is a recording of the two spike generator itself. If there is no event from the id 7, this mean there will be a problem. We can compare the value of the array with the data send previously.  
    4. 'tests/test_input_nest_spike_dict.sh'\
     It's the same test as previously, except the definition of the parameters is done before the creation of the device.  
    5. 'tests/test_input_nest_spike_multi.sh'\
     It's the same test as previously, except that NEST use multithreading.  
    6. 'tests/test_input_nest_spike_dict.sh'\
     It's the same test as previously, except that NEST use multithreading.  
    7. 'tests/test_record_nest_spike.sh'\
     The test is for testing the spike detector and the spike generator with mpi communication. It's just to test it's possible to run it.
    8. 'tests/test_record_nest_spike_multiple.sh' (also test the multithreading) 
     The test is for testing the spike detector and the spike generator with mpi communication in different parameterization of NEST. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
     It's just to test it's possible to run it.
    9. 'tests/test_nest_MPI_threading/run_test.sh'\
     This script is based on a generic test for testing the multithreading of NEST. However it's too complex but it seems to test correctly NEST.
2. Transformation:
    1. 'tests/test_transformer_tvb_to_nest.sh'\
        This test is for the module transformation between TVB to NEST.
        You can check if it succeeds to exist without error (exit of NEST Input and TVB output and the end of the processes).
        You can check if they receive size and the array are different to zero for NEST INPUT. NEST Input (x) needs to be different. 
    2. 'tests/test_transformer_nest_to_tvb.sh'\
        This test is for the module transformer between NEST to TVB.
        You can check if it succeeds to exist without error (exit of NEST Output and TVB input and the end of the processes).
        The second evaluation is by looking at the alternation between TVB INPUT and NEST OUTPUT.
        The third check is the right value of NEST OUTPUT need to be different to zeros (number of spikes receive * 3) 
    3. 'tests/test_nest_save.sh'\
       This test is for the module transformer between NEST save. The implementation of this transformer reuse the interface with NEST from NEST to TVB.
       You can check if it succeeds to exist without error (exit of NEST OUTPUT and the end of the processes).
3. Launcher:
    1. 'tests/run_tvb_one.py' : run exploration 2D of TVB only with one region
    2. 'tests/run_tvb.py' : run exploration 2D of TVB only with the test parameter
    3. 'tests/run_nest_one.py' : run exploration 2D of NEST only with one region 
    4. 'tests/run_nest.py' :  run exploration 2D of NEST only with the test parameter
    5. 'tests/run_nest.py' : run exploration 2D of NEST with transformer for saving the mean firing rate
    6. 'tests/run_nest_co-sim.py' : run exploration 2D co-simulation with test parameter
    7. 'tests/run_nest_co-sim_test.py' : file using by test_co-sim.sh
4. Test the co-simulation:
    1. 'tests/test_co-sim.sh'\
        This test is for the application. It tests the co-simulation in different parameterization of NEST. The parameter testing is for testing the case of use only threading, use only MPI process or a mix of the two.
        The success of these tests is to arrive at the end without any errors. 
    
5. For testing the co-simulation in a container : (see [installation](#installation) for the creation of image)
   * 'install/docker/test_image.sh'
   * 'install/singularity/test_image.sh'

    These tests are based on the script 'tests/run_nest_co-sim_test.py'. They need a parameter to choose the image to test.\
    For docker, only one image 0 is for the debian distribution  (local:NEST_TVB_IO_PAPER_TIMER).\
    For singularity, 0 is for the debian distribution (NEST_TVB_paper_timer.simg), 1 is for alpine distribution (NEST_TVB_paper_alpine_timer.simg).

## Cluster <a name="cluster"></a>
For running the co-simulation on a cluster, all the test was done with [slurm](https://slurm.schedmd.com/). The option to slurm is pass in the parameters 'mpirun'. (see [example](https://slurm.schedmd.com/mpi_guide.html))
WARNING: this project is tested on DEEPEST, Piz Daint and JUSUF. Each configuration is dependant of the cluster setting.
### DEEPEST : <a name="deepest"></a>
The installation and the option for the cluster are built for [DEEPEST](https://www.deep-projects.eu/).
The file 'install/deep/install.sh' is to compile and install all the python library in the folder lib for the usage in the cluster.
For testing the installation, you need to change the file /tests/init.sh. The parameter CLUSTER and DEEPEST need be change from 'false' to 'true'.
Limited to co-simulation without visualization and plotting parts and LFP generation.
### JUSUF : <a name="jusuf"></a>
The installation and the option for the cluster are built for [JUSUSF](https://fz-juelich.de/ias/jsc/EN/Expertise/Supercomputers/JUSUF/JUSUF_node.html).
The file 'install/jusuf/install.sh' is to compile and install all the python library in the folder lib for the usage in the cluster.
For testing the installation, you need to change the file /tests/init.sh.\
Limited to co-simulation without visualization and plotting parts and LFP generation.
### PIZ DAINT : <a name="piz_daint"></a>
The installation and the option for the cluster are built for [Piz Daint](https://www.cscs.ch/computers/piz-daint/).
The file 'install/piz-daint/install.sh' is to compile and install all the python library in the folder lib for the usage in the cluster.
For testing the installation, you need to change the file /tests/init.sh.\
Piz Daint has the software [sarus](https://user.cscs.ch/tools/containers/sarus/) for running docker image on the cluster.
The folder 'install/piz-daint/install.sh' contains the script of loading the image a tar docker image for the user.
This image is used for running the simulation as the example (example/piz_daint/sarus/run_cluster)
### INS cluster : <a name="ins_cluster"></a>
The installation and the option for the cluster are built for INS cluster which is a small cluster for a laboratory ([INS](https://ins-amu.fr/)).
The file 'install/local_cluster/install.sh' is to compile and install all the python library in the folder lib for the usage in the cluster. 


## Missing implementation :<a name="future"></a>
1. Add test for the input and output of interface TVB.
2. Add test for validating values of a simulation
3. Add some functions of the simulation NEST to include multimeter recorder. (limitation the recording part is only for spike time)
4. Debug the problems of the usage of vtk in the containers.

## Files<a name="files"></a>
* analyse: the function for analysis of the output of examples
    * image_3d: folder which contains the script for plotting figure in 3D
        * logo_Nest.png: logo of NEST
        * logo_TVB.png: logo of TVB
        * mouse_sphere.py: print the mouse brain with or without the logo of TVB and NEST
    * LFPY: folder contains the function for creating LFP from the spike trains using HYBRIDLFPY
        * example_plotting.py: file for plotting the result for the HybridLFPy example
        * expsuni.mod: exponential synapse for NEURON simulator
        * LFP.py: file for creating LFP from a simulation
        * run_LFP.py: file for running LFP from a docker or singularity image
        * select_spikes.py: select the spike which is necessary for the generation of LFP.
    * parameter: parameter for the simulation and the data
      * data_mouse: data from Allen Institute of mouse connectome is composed of the file of the distance between each region and the weight of the connections
      * test_nest.py: parameter for testing the installation 
    * create_figure_title.py: create the figure for the example
    * get_data.py: function for getting data from the simulation
    * min_delay.py: get the minimum of delay from a connectome
    * neuron_widget.py: notebook widget for see the dynamic of an individual neurons
    * plot_electrode_morphologie.py: plot the electrode with neurons
    * print_connectome.py: plot the connectome (weights and track length)
    * print_electrode.py: plot the electrode alone
    * print_figure_2_big_image.py: plot one part of the figure 2 of the paper
    * print_figure_2_composite_image.py: plot the other part of the figure 2 of the paper
    * print_figure_macro.py: plot the figure 4 of the paper
    * print_figure_micro.py: plot the figure 3 of the paper
    * print_figure_overview.py: plot the 4 figures of the first figure of the paper 
    * trial_print_figure_macro_more.py: extra function plotting macro result
    * trial_print_figure_micro.py: extra function for plotting micro result
    * trial_print_figure_micro_0.py: extra function for plotting micro result
* doc: Documentation of the project
    * UML: UML of communication and state of modules ( the file .uxl is the file for [UMLET](https://www.umlet.com/))
        * class_heritage.pdf/.uxf: Internal communication classes of the transformer and the link with the others classes.
        * communication_Nest.pdf/.uxf: protocol of communication with NEST
        * communication_TVB.pdf/.uxf: protocol of communication with the wrapper of TVB
        * High_level.pdf/.uxf: details of the communication between the different modules and components of the simulations.
        * initialisation.pdf/.uxf: details of the different step for the initialisation.
        * instance_of_object.pdf/.uxf: the different instance fo object in the transformation modules.
        * loop_end.pdf/.uxf: details step for the end of the simulations
        * MPI_internal.pdd/.uxf: details of internal communication using MPI in the transformation modules.
        * Nest_IO.pdf/.uxf: state diagram of the different state of NEST simulator for the exchange of the data.
        * organisation.pdf/.uxf: overview of the file organisation of the repository
        * overview.pdf/.uxf: simplified overview of the communication between the different modules and components of the simulations.
        * state_Nest.pdf/.uxf: state diagram of NEST for the simulation part.
        * state_TVB.pdf/.uxf: state diagram of the wrapper TVB for the simulation part.
        * Thread_internal.pdf/.uxf: details of internal communication using MPI in the transformation modules.
        * transformation.pdf/.uxf: schematic of the transformation function
        * transformation_spike_rate.pdf/.uxf: state diagram of the transformation component
        * TVB_IO.pdf/.uxf: state diagram of communication of the wrapper of TVB
* [example](#example): examples of the usage of the proof of concept
    * docker: (example using the docker image)
        * run_docker.sh: example how to run the docker image for a co-simulation
    * singularity: (example using the singularity image)
        * run_singularty.sh: example how to run the singularity image for a co-simulation
    * local: (example for running the example with local installation)
        * run_local.sh: run the co-simulation example
    * local_cluster: (example for running example on INS cluster)
        * run_local.sh: run the co-simulation example
        * run_job.sh: summit a job for co-simulation on the cluster
    * jusuf: (example for running simulation on jusuf)
        * run_cluster.sh: summit a job for co-simulation on the cluster
        * run_example.sh: run the co-simulation after loading and prepare the environment for the co-simulation.
    * piz-daint: (example ofr running co-simulation on piz-daint)
        * LFP:
            * run_cluster_LFP.sh: push a job for generate LFP on the cluster.
            * run_LFPY.py: function for calling the generator with the good parameters
            * run_LFPY.sh: function for run the python script and loading the dependency
        * sarus: (example for using sarus for running co-simulation)
            * run_cluster.sh: push a job for co-simulation on the cluster.
            * run_cluster_LFP.sh: push a job for generate LFP on the cluster. 
            * run_LFPY.py: function for calling the generator with the good parameters 
            * run_LFPY.sh: function for run the python script and loading the dependency
            * run_sarus.sh: function for running the co-simulation

    * <a name="short_sim">short_simulation</a>: folder of the result of the short simulation
        * log: folder contains all the log of the simulation
        * nest: generated files by the NEST module
            * labels.csv: the label of the recorder and the type of recording
            * population_GIDs.dat: the id of the neurons and the type of neurons
            * spike_detector.txt: the id of spike detector
            * spike_generator.txt: the id of spike generator
            * other files : the output of the spike detectors and multimeters
        * transformer: 
            * receive_from_tvb: contains the MPI port for the connection of TVB to the transformer during the simulation
            * send_to_tvb: contains the MPI port for the connection of TVB to the transformer during the simulation
            * spike_detector: contains the MPI port for the connection of NEST to the transformer during the simulation
            * spike_generator: contains the MPI port for the connection of NEST to the transformer during the simulation
        * tvb: generated files by TVB modules
            * step_*.npy : the output of the monitor of TVB
            * step_init.npy: the initialisation value of the node in TVB
        * init_rates.npy: initialisation of the rate from NEST to TVB
        * init_spikes.npy: initialisation of spikes from TVB to NEST
        * parameters: parameters for the simulation
    * long_simulation: same result but for a longer simulation
    * [demonstration_mouse_brain.ipynb](#mouse_brain): jupyter notebook for running an example of the application
* [install](#installation)
    * [deep](#deepest)
        install.sh: installation on deepest cluster
    * docker
        create_docker_paper.sh: create the docker image for the paper.
        Nest_TVB_paper.dockerfile: file of configurations for docker.
        save_docker_paper.sh: save the docker image in tar image.
        test_image.sh: test the docker image .
    * jusuf
        install.sh: install on jusuf
    * local
        install_ubuntu.sh: install on ubuntu system.
    * local_cluster
        install.sh: install on INS cluster
    * piz-daint
        * sarus
            load_image.sh: load docker image on the Piz Daint cluster
        install.sh: local install of the project
        run.sh: submit a job for launching the co-simulation
        trial_install_nest.sh: installation of NEST only
        trial_install_LFPy.sh: installation of LFPy only
    * py_venv
        create_virtual_python.sh: create the virtual environment
    * singularity
        create_container_paper.sh, create_container_paper_alpine.sh: create the singularity image for the paper with different operative system.
        Nest_TVB_paper.singularity, Nest_TVB_paper_alpine.singularity: file of configurations for singularity.
        log_package.txt: list of ubuntu package for the simulation of the paper.
        log_pip.txt: list of the python package for the simulation of the paper.
        test_images.sh: example of running co-simulation with the image.
    * install_local.sh: installation in empty environment without root access
* nest-io-dev: the branch of NEST with IO using MPI
* nest_elephant_nest: file which contains all the kernel of the simulation
    * launcher:
        * run_exploration.py: main script of the simulation for the exploration of 1 or 2 parameters with 1 or 2 simulators and management of the parameters.
        * run_nest_only.py: run only NEST simulation
        * run_tvb_only.py: run only TVB simulation
    * Nest: folder contains all the file to configure and launch NEST
        * simulation_Zerlaut.py: run the NEST part of the application
    * transformation: folder contains the transformer between TVB and NEST
        * communication:
            * internal.py: abstract of the internal communication
            * internal_mpi.py: implementation of internal communication using MPI.
            * internal_thread.py: implementation of internal communication using thread of python.
            * mpi_io_external.py: management of external communication with simulator.
        * simulator_IO:
            * Nest_IO.py: communication with NEST (send and receive data)
            * TVB_IO.py: communication with TVB (send and receive data)
        * transformation_function:
            * rate_spike.py: function using elephant for changing rates to spikes and opposite.
            * transformation_function.py: object which transform data from one simulator to the second
        nest_to_tvb.py: module for receiving, transforming and sending the data from NEST to TVB.
        tvb_to_nest.py: module for receiving, transforming and sending the data from TVB to NEST.     
    * TVB
        *  modify TVB: folder contains file for the interface and the extensions of TVB
            * Zerlaut.py: model of the Mean Field (modification of the official model where the noise is part of the model)
            * Interface_co_simulation.py: interface can be used only in sequential but allow using intermediate result for the firing rate. (Need to compute NEST before TVB.)
            * Interface_co_simulation_parallel.py: can be used to compute TVB and NEST in same time
            * test_interface...: test for the interface with the model of Wong Wang
        * simulation_Zerlaut.py: the script for the configure and the running of the simulator of TVB
        * generate_ECOG_post_sim.py: generation of ECOG a simulation
        * helper_function_zerlaut.py: function for ECOG sensors and for finding the normal of a face
        * wrapper_TVB.py: wrapper of TVB without MPI (use for launching TVB alone)
        * wrapper_TVB_mpi.py: wrapper of TVB using MPI for communication with the transformer
    * utils.py: files for creating loggers for the different modules
* tests: contains all the [test](#tests)  
    * test_nest_file: (file for testing different configuration of NEST)
        * spike_detector_mpi.py: test spike detector with only MPI
        * spikedetector_mpi_thread.py: test spike detector with MPI and thread
        * spikegenerator_mpi.py: test spike generator with only MPI
        * spikegenerator_mpi_dict.py: test spike generator with only MPI with parameters in dictionary
        * step_current_generator_mpi.py: test current generator with only MPI
        * step_current_generator_mpi_thread.py: test current generator with MPI and thread 
    * test_nest_MPI_threading: (file for testing NEST in different configuration)
        * check_result.py: check the output of the simulation between MPI communication and the simulator
        * helper.py: function create logger and NEST devices
        * input_current_region_activity_multiple.py: generate current for NEST using MPI communication
        * input_region_activity_multiple.py: generate spikes for NEST using MPI communication
        * nest_config.py: configure NEST for the tests
        * record_region_activity_multiple.py: receive spikes from NEST
        * run_test.sh: run multiple test for testing different configuration of NEST, MPI and thread.
    * test_transformation: (test transformation function and NEST device)
        * input_nest_current: file for sending current  
            * input_current.py: generate currents with 1 MPI rank
            * input_current_multiple.py: generate currents with multi MPI rank
        * record_nest_activity.py:
            * record_region_activity.py: record spikes with 1 MPI rank
            * record_region_activity_multi.py: record spikes with multi MPI rank
        * spike_nest_input.py:
            * input_region_activity.py: generate spikes with 1 MPI rank
            * input_region_activity_multi.py: generate spikes with multi MPi rank
        * test_input_nest_to_tvb.py: mock up for replacing NEST for sending data
        * test_input_tvb_to_nest.py: mock up for replacing TVB for sending data
        * test_receive_nest_to_tvb.py: mock up for replacing NEST for receiving data
        * test_receive_tvb_to_nest.py: mock up for replacing TVB for receiving data
    * init.sh: initialise the environment for the test or the simulation
    * init_rates.npy: initialization of the rate for the first communication
    * init_spikes.npy: initialization of the spikes for the first communication
    * run_co_sim.py: a simple co-simulation
    * run_co-sim_test.py: test of the co-simulation
    * run_co-sim_test_docker.py: test of the co-simulation with docker
    * run_nest.py: simulation of nest only
    * test_co_sim.sh: run of co-simulation with multiple simulation
    * test_input_nest_current.sh: test current devices with MPI backend of NEST
    * test_input_nest_current_multi.sh: test current devices with MPI backend of NEST with multiple MPI configuration 
    * test_input_nest_spike.sh: test spike generator with MPI backend of NEST 
    * test_input_nest_spike_dict.sh: test spike generator with MPI backend of NEST with dictionary backend 
    * test_input_nest_spike_multi_dict.sh: test spike generator with MPI backend of NEST with dictionary backend with multiple MPI configuration 
    * test_record_nest_spike.sh: test spike recorder with MPI backend of NEST 
    * test_record_nest_spike_multi.sh: test spike recorder with MPI backend of NEST with multiple MPI configuration  
    * test_transformer_nest_to_tvb.sh: test transformer spikes to rates   
    * test_transformer_tvb_to_nest.sh: test transformer rates to spikes
* timer: File for timer recording and plotting
    * plot_result: plot result timer
        * analyse_timer.py: plot details result of 
        * compare_time_paper.py: plot time of the result local run
        * compare_time_paper_2.py: plot time of the result with comparison of NEST configuration
        * compare_time_paper_jusuf.py: plot time for the running on jusuf
        * get_time_data.py: get data of timer 
        * pot_figure_comparison.py: plot details comparison 
        * trial_compare_time.py: file for testing the printing results
    * parameters.py: default parameters for timer
    * run_co-sim_mpi.py: run co-simulation with timer and 1 thread by rank for NEST
    * run_co-sim_mpi_vp_2.py: run co-simulation with timer and 2 thread by rank for NEST
    * run_co-sim_mpi_vp_4.py: run co-simulation with timer and 4 thread by rank for NEST
    * run_co-sim_neuron.py: run co-simulation with number of neurons 
    * run_co-sim_thread.py: run co-simulation with different number of threads for NEST 
    * run_co-sim_time.py: run co-simulation with different synchronize time between simulator 
    * run_co-sim_TVB_ebrains.py: run tests for different configuration
    * run_timer_mpi.sh: run all the co-simulation for different number of MPI and 1 thread by rank for NEST 
    * run_timer_mpi_vp_2.sh: run all the co-simulation for different number of MPI and 2 thread by rank for NEST 
    * run_timer_mpi_vp_4.sh: run all the co-simulation for different number of MPI and 4 thread by rank for NEST
    * run_timer_neuron.sh: run all the co-simulation for different number of neurons
    * run_timer_run_all.sh: run all the co-simulation with timer  
    * run_time_thread.sh: run all the co-simulation for one MPI rank and different number of thread for NEST  
    * run_timer_timer.sh: run all the co-simulation for different time of synchronization between  
    * Timer.py: class of timer for record time in python
* LICENSE: License of the project
* NOTICE: notice for the License
