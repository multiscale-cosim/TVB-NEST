/*
 *  recording_device.h
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

#ifndef INPUT_DEVICE_H
#define INPUT_DEVICE_H

// C++ includes:
#include <fstream>
#include <vector>

// Includes from libnestutil:
#include "lockptr.h"

// Includes from nestkernel:
#include "node.h"
#include "device.h"
#include "device_node.h"
#include "input_backend.h"
#include "nest_types.h"
#include "kernel_manager.h"

// Includes from sli:
#include "dictdatum.h"
#include "dictutils.h"

namespace nest
{

class InputDevice :  public DeviceNode, public Device
{
public:

  InputDevice();
  InputDevice( const InputDevice& );

  void calibrate( const std::vector< Name >&, const std::vector< Name >& );

  bool is_active( Time const& T ) const;

  bool get_time_in_steps() const;

  /**
   * Device type.
   */
  enum Type
  {
    CURRENT_GENERATOR,
    SPIKE_GENERATOR
  };

  virtual Type get_type() const = 0;

  void set_status( const DictionaryDatum& );
  void get_status( DictionaryDatum& ) const;
  
  
protected:
  std::vector <double> read();
  void set_initialized_() override;


private:
  struct Parameters_
  {
    std::string label_;    //!< A user-defined label for symbolic device names.
    bool time_in_steps_;   //!< Flag indicating if time is recorded in steps or ms
    Name input_from_; //!< Array of input backends to use

    Parameters_();
    void get( const InputDevice&, DictionaryDatum& ) const;
    void set( const InputDevice&, const DictionaryDatum&, long );
  } P_;

  struct State_
  {
    size_t n_events_;

    State_();
    void get( DictionaryDatum& ) const;
    void set( const DictionaryDatum&, const InputDevice& );
  } S_;

  DictionaryDatum backend_params_;
};

inline void
InputDevice::get_status( DictionaryDatum& d ) const
{
  P_.get( *this, d );
  S_.get( d );

  Device::get_status( d );

  ( *d )[ names::element_type ] = LiteralDatum( names::recorder );

  kernel().io_manager.get_input_backend_device_status(P_.input_from_, *this, d );
}

inline bool
InputDevice::is_active( Time const& T ) const
{
  const long stamp = T.get_steps();

  return get_t_min_() < stamp && stamp <= get_t_max_();
}

inline bool
InputDevice::get_time_in_steps() const
{
  return P_.time_in_steps_;
}

inline std::vector <double>
InputDevice::read()
{
  ++S_.n_events_;
  return kernel().io_manager.read( *this );
}

} // namespace

#endif // RECORDING_DEVICE_H
