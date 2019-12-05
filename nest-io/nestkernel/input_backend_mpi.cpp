/*
 *  recording_backend_screen.cpp
 *
 *  This file is part of NEST.
 *
 *  Copyright (C) 2004 The NEST Initiative
 *
 *  NEST is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  NEST is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with NEST.  If not, see <http://www.gnu.org/licenses/>.
 *
 */

// C++ includes:
#include <iostream>


// Includes from nestkernel:
#include "input_backend_mpi.h"
#include "input_device.h"
#include <fstream>


void
nest::InputBackendMPI::initialize()
{
  auto nthreads = kernel().vp_manager.get_num_threads();
  device_map devices( nthreads );
  devices_.swap( devices );
}

void
nest::InputBackendMPI::finalize()
{
  printf("Closing\n\n" );
}

void
nest::InputBackendMPI::enroll( const InputDevice& device,
  const DictionaryDatum& params )
{
  if ( device.get_type() == InputDevice::SPIKE_GENERATOR ){
	  thread tid = device.get_thread();
	  index node_id = device.get_node_id();

	  device_map::value_type::iterator device_it = devices_[ tid ].find( node_id );
	  if ( device_it != devices_[ tid ].end() )
	  {
	    devices_[ tid ].erase( device_it );
	  }
	  devices_[ tid ].insert( std::make_pair( node_id, &device ) );
  }
  else
  {
    throw BadProperty( "Only spike generators can have input backend 'mpi'." );
  }
}

void
nest::InputBackendMPI::disenroll( const InputDevice& device )
{
  thread tid = device.get_thread();
  index node_id = device.get_node_id();

  device_map::value_type::iterator device_it = devices_[ tid ].find( node_id );
  if ( device_it != devices_[ tid ].end() )
  {
    devices_[ tid ].erase( device_it );
  }
}

void
nest::InputBackendMPI::set_value_names( const InputDevice& device,
                                        const std::vector< Name >& double_value_names,
                                        const std::vector< Name >& long_value_names)
{
  // nothing to do
}


void
nest::InputBackendMPI::pre_run_hook()
{
  // nothing to do
}


void
nest::InputBackendMPI::cleanup()
{
  // nothing to do
}

std::vector <double>
nest::InputBackendMPI::read( InputDevice& device )
{
  std::vector< double > result;
  const thread t = device.get_thread();
  const index gid = device.get_node_id();

  if ( devices_[ t ].find( gid ) == devices_[ t ].end() )
  {
    return result;
  }

#pragma omp critical
  {
    bool ending = false;
    int index_list = 0 ;
    for (index it : _list_spike_detector){
      if (it == device.get_node_id()){
        MPI_Comm* newcomm = _list_communication[index_list];
        if(newcomm == NULL) {
          printf("Error %x\n", newcomm);
          break;
        }
        receive_spike_train(kernel().simulation_manager.get_clock(),result,newcomm);
        ending=true;
      }
      index_list++;
    }
    if (not ending) {
      _list_spike_detector.push_back(device.get_node_id());
      _list_label.push_back(device.get_label());
      MPI_Comm* newcomm = new MPI_Comm; //TODO need to free memory after
      _list_communication.push_back(newcomm);
      char port_name[MPI_MAX_PORT_NAME];
      get_port(device,port_name);
      fflush(stdout);
      printf("ID to %d\n", int(device.get_node_id()));
      printf("Connect to %s\n", port_name);
      fflush(stdout);
      int status = MPI_Comm_connect(port_name, MPI_INFO_NULL, 0, MPI_COMM_WORLD, newcomm);
      printf("Connect MPI Output Comm 3 status: %d\n",status);
      fflush(stdout);
      receive_spike_train(kernel().simulation_manager.get_clock(),result,newcomm);
    }
  }
  return result;
}

void
nest::InputBackendMPI::check_device_status( const DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::InputBackendMPI::get_device_defaults( DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::InputBackendMPI::get_device_status( const nest::InputDevice& device,
                                          DictionaryDatum& params_dictionary ) const
{
  // nothing to do
}

void
nest::InputBackendMPI::post_run_hook()
{
  // nothing to do
}

void
nest::InputBackendMPI::post_step_hook()
{
  // nothing to do
}

void
nest::InputBackendMPI::get_status( lockPTRDatum< Dictionary, &SLIInterpreter::Dictionarytype >& ) const
{
  // nothing to do
}

void
nest::InputBackendMPI::set_status( const DictionaryDatum& d )
{
  // nothing to do
}

void
nest::InputBackendMPI::prepare()
{
  // nothing to do
}
void
nest::InputBackendMPI::get_port(const InputDevice& device, char* port_name) {
  get_port(device.get_node_id(),device.get_label(),port_name);
}

void
nest::InputBackendMPI::get_port(const index index_node, const std::string& label, char* port_name){
  std::ostringstream basename;
  const std::string& path = kernel().io_manager.get_data_path();
  if ( not path.empty() )
  {
    basename << path << '/';
  }
  basename << kernel().io_manager.get_data_prefix();

  if ( not label.empty() )
  {
    basename << label;
  }
  else {
     //TODO take in count this case
  }
  char add_path[150];
  sprintf(add_path, "/%zu.txt", index_node);
  basename << add_path;
  std::cout << basename.rdbuf() << std::endl;
  std::ifstream file(basename.str());
  if (file.is_open()) {
    file.getline(port_name, 256);
  }
  file.close();
}

void
nest::InputBackendMPI::receive_spike_train(Time clock,std::vector<double>& result,MPI_Comm* newcomm){
  double time_currrent =clock.get_ms() ;
  MPI_Send(&time_currrent, 1, MPI_DOUBLE, 0, 0, *newcomm);
  MPI_Status status_mpi;
  double receive_num[1];
  MPI_Recv(&receive_num, 1, MPI_DOUBLE,0 ,MPI_ANY_TAG ,*newcomm ,&status_mpi);
  if(status_mpi.MPI_TAG == 1){
    return;
  }
  while (status_mpi.MPI_TAG == 0 or status_mpi.MPI_TAG == -1){
    if (status_mpi.MPI_TAG == 0) {
      result.push_back(receive_num[0]);
    }
    printf("Message Received %.6f\n", receive_num[0]);
    MPI_Recv(&receive_num, 1, MPI_DOUBLE,0 ,MPI_ANY_TAG ,*newcomm ,&status_mpi);
  }
  fflush(stdout);
  //restore_cout_();
}