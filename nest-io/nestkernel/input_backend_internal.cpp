/*
 *  input_backend_internal.cpp
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
#include "input_backend_internal.h"
#include "input_device.h"

void
nest::InputBackendInternal::enroll( const InputDevice& device,
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
nest::InputBackendInternal::disenroll( const InputDevice& device )
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
nest::InputBackendInternal::initialize()
{
  auto nthreads = kernel().vp_manager.get_num_threads();
  device_map devices( nthreads );
  devices_.swap( devices );
  
}

void
nest::InputBackendInternal::prepare()
{
  if ( not enrolled_ )
  {
    return;
  }

  if ( prepared_ )
  {
    throw BackendPrepared( "InputBackendInternal" );
  }
  prepared_ = true;
}

void
nest::InputBackendInternal::cleanup()
{
}


void
nest::InputBackendInternal::finalize()
{
    printf("Closing\n\n" );
}

std::vector <double>
nest::InputBackendInternal::read( InputDevice& device )
{
  std::vector< double > result;
  return result;
}


void
nest::InputBackendInternal::set_value_names( const InputDevice& device,
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
nest::InputBackendInternal::check_device_status( const DictionaryDatum& params ) const
{
  // nothing to do
}

/* ----------------------------------------------------------------
 * Parameter extraction and manipulation functions
 * ---------------------------------------------------------------- */
nest::InputBackendInternal::Parameters_::Parameters_()
{
}

void
nest::InputBackendInternal::Parameters_::get( const InputBackendInternal&,
  DictionaryDatum& d ) const
{
  //( *d )[ names::precision ] = precision_;
}

void
nest::InputBackendInternal::Parameters_::set( const InputBackendInternal&,
  const DictionaryDatum& d )
{
  /*if (  ) )
  {
    std::cout << std::fixed;
    std::cout << std::setprecision( precision_ );
  }*/
}

void
nest::InputBackendInternal::set_status( const DictionaryDatum& d )
{
  Parameters_ ptmp = P_; // temporary copy in case of errors
  ptmp.set( *this, d );  // throws if BadProperty
  // if we get here, temporaries contain consistent set of properties
  P_ = ptmp;
}

void
nest::InputBackendInternal::pre_run_hook()
{
  // nothing to do
}

void
nest::InputBackendInternal::post_run_hook()
{
  // nothing to do
}

void
nest::InputBackendInternal::post_step_hook()
{
  // nothing to do
}

void
nest::InputBackendInternal::get_device_defaults( DictionaryDatum& params ) const
{
  // nothing to do
}

void
nest::InputBackendInternal::get_device_status( const nest::InputDevice& device,
  DictionaryDatum& params_dictionary ) const
{
  // nothing to do
}


