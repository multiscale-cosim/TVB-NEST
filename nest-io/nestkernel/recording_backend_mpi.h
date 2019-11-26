/*
 *  recording_backend_screen.h
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

#ifndef RECORDING_BACKEND_MPI_H
#define RECORDING_BACKEND_MPI_H

#include "recording_backend.h"
#include <set>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <unistd.h>
#include <mpi.h>

namespace nest
{

/**
 * A simple recording backend implementation that prints all recorded data to
 * screen.
 */
class RecordingBackendMPI : public RecordingBackend
{
public:
  RecordingBackendMPI();
  ~RecordingBackendMPI() throw();

  void initialize() override;
  void finalize() override;

  void enroll( const RecordingDevice& device, const DictionaryDatum& params ) override;

  void disenroll( const RecordingDevice& device ) override;

  void set_value_names( const RecordingDevice& device,
    const std::vector< Name >& double_value_names,
    const std::vector< Name >& long_value_names ) override;

  void cleanup() override;

  void prepare() override;

  void write( const RecordingDevice&, const Event&, const std::vector< double >&, const std::vector< long >& ) override;

  void set_status( const DictionaryDatum& ) override;

  void get_status( DictionaryDatum& ) const override;

  void pre_run_hook() override;

  void post_run_hook() override;

  void post_step_hook() override;

  void check_device_status( const DictionaryDatum& ) const override;
  void get_device_defaults( DictionaryDatum& ) const override;
  void get_device_status( const RecordingDevice& device, DictionaryDatum& params_dictionary ) const override;

private:
  struct Parameters_
  {
    int refresh_rate_;

    Parameters_();

    void get( const RecordingBackendMPI&, DictionaryDatum& ) const;
    void set( const RecordingBackendMPI&, const DictionaryDatum& );
  };

  bool enrolled_;
  bool prepared_;

  Parameters_ P_;
  std::list<index> _list_spike_detector;
  std::vector<std::string> _list_label;
  std::vector<MPI_Comm*> _list_communication;

  typedef std::vector< std::map< index, const RecordingDevice* > > device_map;
  device_map devices_;

  struct DeviceData
  {
    DeviceData() = delete;
    DeviceData( std::string, std::string );
    void set_value_names( const std::vector< Name >&, const std::vector< Name >& );
    void get_status( DictionaryDatum& ) const;
    void set_status( const DictionaryDatum& );

  private:
    long precision_;                         //!< Number of decimal places used when writing decimal values
    bool time_in_steps_;                     //!< Should time be recorded in steps (ms if false)
    std::string modelname_;                  //!< File name up to but not including the "."
    std::string vp_node_id_string_;          //!< The vp and node ID component of the filename
    std::string file_extension_;             //!< File name extension without leading "."
    std::string label_;                      //!< The label of the device.
    std::ofstream file_;                     //!< File stream to use for the device
    std::vector< Name > double_value_names_; //!< names for values of type double
    std::vector< Name > long_value_names_;   //!< names for values of type long

  };

  typedef std::vector< std::map< size_t, DeviceData > > data_map;
  data_map device_data_;

  void prepare_stream_();

  void get_port(const RecordingDevice& device,char* port_name);
  void get_port(const index index_node, const std::string& label,char* port_name);

  std::ios::fmtflags old_fmtflags_;
  long old_precision_;
};

inline void
RecordingBackendMPI::get_status( DictionaryDatum& d ) const
{
  P_.get( *this, d );
}


inline void
RecordingBackendMPI::prepare_stream_()
{
    
}

} // namespace

#endif // RECORDING_BACKEND_MPI_H
