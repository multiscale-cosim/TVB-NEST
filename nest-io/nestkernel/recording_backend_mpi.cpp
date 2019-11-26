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
#include "recording_device.h"
#include "recording_backend_mpi.h"

nest::RecordingBackendMPI::RecordingBackendMPI()
  : enrolled_( false )
  , prepared_( false )
{
}

nest::RecordingBackendMPI::~RecordingBackendMPI() throw()
{
}


void
nest::RecordingBackendMPI::enroll( const RecordingDevice& device,
  const DictionaryDatum& params )
{
  if ( device.get_type() == RecordingDevice::SPIKE_DETECTOR )
  {
    const auto tid = device.get_thread();
    const auto node_id = device.get_node_id();

    auto device_it = devices_[ tid ].find( node_id );
    if ( device_it != devices_[ tid ].end() )
    {
      devices_[ tid ].erase( device_it );
    }

    devices_[ tid ].insert( std::make_pair( node_id, &device ) );
  }
  else
  {
    throw BadProperty( "Only spike detectors can record to recording backend 'arbor'." );
  }
  enrolled_ = true;
}

void
nest::RecordingBackendMPI::disenroll( const RecordingDevice& device )
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
nest::RecordingBackendMPI::set_value_names( const RecordingDevice& device,
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
nest::RecordingBackendMPI::pre_run_hook()
{
  // nothing to do
}

void
nest::RecordingBackendMPI::post_run_hook()
{
#pragma omp single
  {

  }
}

void
nest::RecordingBackendMPI::post_step_hook()
{
  // nothing to do
}

void
nest::RecordingBackendMPI::check_device_status( const DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::RecordingBackendMPI::get_device_defaults( DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::RecordingBackendMPI::get_device_status( const nest::RecordingDevice& device,
  DictionaryDatum& params_dictionary ) const
{
  // nothing to do
}

void
nest::RecordingBackendMPI::prepare()
{
  if ( not enrolled_ )
  {
    return;
  }

  if ( prepared_ )
  {
    throw BackendPrepared( "RecordingBackendMPI" );
  }
  prepared_ = true;
  // Can we prepare the MPI communicators here?
}

void
nest::RecordingBackendMPI::cleanup()
{
  if ( prepared_ )
  {
    if ( not enrolled_ )
    {
      return;
    }

    if ( not prepared_ )
    {
      throw BackendNotPrepared( "RecordingBackendMPI" );
    }
    prepared_ = false;

    int index_sp=0;
    for (index it : _list_spike_detector){
      char  port_name[MPI_MAX_PORT_NAME];
      get_port(it,_list_label[index_sp],port_name);
      printf("disconnect port %s\n",port_name);
      MPI_Send(0, 0, MPI_INT, 0, 1, *_list_communication[index_sp]);
      MPI_Comm_disconnect(_list_communication[index_sp]);
      printf("disconnect port %s\n",port_name);
      delete _list_communication[index_sp];
      index_sp++;
    }
    _list_spike_detector.clear();
    _list_communication.clear();
    _list_label.clear();
    printf("Closing\n" );
  }
}


void
nest::RecordingBackendMPI::initialize()
{
  auto nthreads = kernel().vp_manager.get_num_threads();
  device_map devices( nthreads );
  devices_.swap( devices );  
}

void
nest::RecordingBackendMPI::finalize()
{
}


void
nest::RecordingBackendMPI::write( const RecordingDevice& device,
  const Event& event,
  const std::vector< double >&,
  const std::vector< long >& )
{
  const thread t = device.get_thread();
  const index gid = device.get_node_id();

  if ( ! enrolled_ )
  {
    return;
  }

  const index sender = event.get_sender_node_id();
  const Time stamp = event.get_stamp();
  const double offset = event.get_offset();

    bool ending = false;
    int index_list = 0 ;
    for (index it : _list_spike_detector){
      if (it == device.get_node_id()){
        MPI_Comm newcomm = *_list_communication[index_list];
        int passed_num[2]= {int(sender), int(stamp.get_ms() - offset)};
        if(newcomm == NULL) {
          printf("Error %x\n", newcomm);
          break;
        }
        MPI_Send(&passed_num, 2, MPI_INT, 0, 0, newcomm);
        fflush(stdout);
        //restore_cout_();
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
      printf("ID to %d\n", device.get_node_id());
      printf("Connect to %s\n", port_name);
      fflush(stdout);
      int status = MPI_Comm_connect(port_name, MPI_INFO_NULL, 0, MPI_COMM_WORLD, newcomm);
      printf("Connect MPI Output Comm 3 status: %d\n",status);
      fflush(stdout);
      int passed_num[2]= {int(sender), int(stamp.get_ms() - offset)};
      MPI_Send(&passed_num, 2, MPI_INT, 0, 0, *newcomm);
    }
}

/* ----------------------------------------------------------------
 * Parameter extraction and manipulation functions
 * ---------------------------------------------------------------- */

nest::RecordingBackendMPI::Parameters_::Parameters_()
  //: precision_( 3 )
{
}

void
nest::RecordingBackendMPI::Parameters_::get( const RecordingBackendMPI&,
  DictionaryDatum& d ) const
{
  //( *d )[ names::precision ] = precision_;
}

void
nest::RecordingBackendMPI::Parameters_::set( const RecordingBackendMPI&,
  const DictionaryDatum& d )
{
  /*if ( updateValue< long >( d, names::precision, precision_ ) )
  {
    std::cout << std::fixed;
    std::cout << std::setprecision( precision_ );
  }*/
}

void
nest::RecordingBackendMPI::set_status( const DictionaryDatum& d )
{
  Parameters_ ptmp = P_; // temporary copy in case of errors
  ptmp.set( *this, d );  // throws if BadProperty

  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
}

void
nest::RecordingBackendMPI::get_port(const RecordingDevice& device, char* port_name) {
  get_port(device.get_node_id(),device.get_label(),port_name);
}

void
nest::RecordingBackendMPI::get_port(const index index_node, const std::string& label, char* port_name){
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
