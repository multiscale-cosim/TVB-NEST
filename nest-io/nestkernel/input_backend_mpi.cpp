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
nest::InputBackendMPI::enroll( const InputDevice& device,
  const DictionaryDatum& params )
{
  if ( device.get_type() == InputDevice::SPIKE_GENERATOR ){
	  const auto tid = device.get_thread();
	  const auto node_id = device.get_node_id();

	  auto device_it = devices_[ tid ].find( node_id );
	  if ( device_it != devices_[ tid ].end() )
	  {
	    devices_[ tid ].erase( device_it );
	  }
	  devices_[ tid ].insert( std::make_pair( node_id, &device ) );

	  enrolled_ = true;
  }
}

void
nest::InputBackendMPI::disenroll( const InputDevice& device )
{
  const auto tid = device.get_thread();
  const auto node_id = device.get_node_id();

  auto device_it = devices_[ tid ].find( node_id );
  if ( device_it != devices_[ tid ].end() )
  {
    devices_[ tid ].erase( device_it );
  }
  enrolled_ = false;
}


void
nest::InputBackendMPI::initialize()
{
  auto nthreads = kernel().vp_manager.get_num_threads();
  device_map devices( nthreads );
  devices_.swap( devices );
  
}

void
nest::InputBackendMPI::prepare()
{
  if ( not enrolled_ )
  {
    return;
  }

  if ( prepared_ )
  {
    throw BackendPrepared( "InputBackendMPI" );
  }
  prepared_ = true;
}

void
nest::InputBackendMPI::cleanup()
{
}


void
nest::InputBackendMPI::finalize()
{
    printf("Closing\n\n" );
    //MPI_Close_port(port_name);
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

    if(!connected_input){
      MPI_Info_create(&info);
      MPI_Info_set(info,"ip_port","8082");
      MPI_Info_set(info,"ip_address", "127.0.0.1");
      MPI_Open_port(info, port_name);
      printf("%s\n\n", port_name); 
      std::ofstream file;
      file.open ("./nest_port.txt");
      //char buff[100];
      //snprintf(buff, sizeof(buff), "%s", port_name);
      file.write(port_name,strlen(port_name));
      //file.write(buff,sizeof(buff));
      file.close();
      fflush(stdout);
      int status = MPI_Comm_accept(port_name, MPI_INFO_NULL, 0, MPI_COMM_WORLD, &newcomm_input);
      printf("Accepted MPI Input Comm backend: %d\n", status); 
      fflush(stdout);
      connected_input = 1;
    }
    int passed_num= 10;
    if(newcomm_input == NULL){
        throw IllegalConnection("Communicator for MPI input failed\n");
    }
    MPI_Recv(&passed_num, 1, MPI_INT, 0, 0, newcomm_input, MPI_STATUS_IGNORE);
    printf("Message Received %d\n", passed_num); 
    result.push_back(double(passed_num));
    fflush(stdout);
    
  }
  return result;
}

/* ----------------------------------------------------------------
 * Parameter extraction and manipulation functions
 * ---------------------------------------------------------------- */

nest::InputBackendMPI::Parameters_::Parameters_()
  //: precision_( 3 )
{

}

void
nest::InputBackendMPI::set_value_names( const InputDevice& device,
  const std::vector< Name >& double_value_names,
  const std::vector< Name >& long_value_names)
{
  const thread t = device.get_thread();
  const thread node_id = device.get_node_id();

  //data_map::value_type::iterator device_data = device_data_[ t ].find( node_id );
  //assert( device_data != device_data_[ t ].end() );
  //device_data->second.set_value_names( double_value_names, long_value_names );
}

void
nest::InputBackendMPI::check_device_status( const DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::InputBackendMPI::Parameters_::get( const InputBackendMPI&,
  DictionaryDatum& d ) const
{
  //( *d )[ names::precision ] = precision_;
}

void
nest::InputBackendMPI::Parameters_::set( const InputBackendMPI&,
  const DictionaryDatum& d )
{
  /*if ( updateValue< long >( d, names::precision, precision_ ) )
  {
    std::cout << std::fixed;
    std::cout << std::setprecision( precision_ );
  }*/
}

void
nest::InputBackendMPI::set_status( const DictionaryDatum& d )
{
  Parameters_ ptmp = P_; // temporary copy in case of errors
  ptmp.set( *this, d );  // throws if BadProperty

  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
}

void
nest::InputBackendMPI::pre_run_hook()
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


