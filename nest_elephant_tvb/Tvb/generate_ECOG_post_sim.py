from nest_elephant_tvb.Tvb.helper_function_zerlaut import ECOG, findVec
from tvb.simulator.common import iround, numpy_add_at
from example.analyse.get_data import get_rate
import numpy as np
import tvb.simulator.lab as lab
import matplotlib.pyplot as plt

class wapper_ECOG(ECOG):
    def config_for_sim(self, fake_simulator):
        """Configure monitor for given simulator.

        Grab the Simulator's integration step size. Set the monitor's variables
        of interest based on the Monitor's 'variables_of_interest' attribute, if
        it was specified, otherwise use the 'variables_of_interest' specified
        for the Model. Calculate the number of integration steps (isteps)
        between returns by the record method. This method is called from within
        the the Simulator's configure() method.

        """
        ####  Ecog
        self.volume_cortical = self.volume[fake_simulator['cortical']]
        non_cortical_indices, = np.where(~fake_simulator['cortical'])
        self.volume_non_cortical = self.volume[non_cortical_indices]

        ####  general
        self.dt = fake_simulator['dt']
        self.istep = iround(self.period / self.dt)
        self.voi = self.variables_of_interest
        if self.voi is None or self.voi.size == 0:
            self.voi = np.r_[:len(fake_simulator['variables_of_interest'])]

        ####  projection
        if hasattr(self, 'sensors'):
            self.sensors.configure()

        # handle observation noise and configure white/coloured noise
        # pass in access to the: i) dt and ii) sample shape
        if self.obsnoise is not None:
            # configure the noise level
            if self.obsnoise.ntau > 0.0:
                noiseshape = self.sensors.labels[:,np.newaxis].shape
                self.obsnoise.configure_coloured(dt=self.dt, shape=noiseshape)
            else:
                self.obsnoise.configure_white(dt=self.dt)

        # handle region vs simulation, analytic vs numerical proj, cortical vs subcortical.
        # setup convenient locals
        surf = fake_simulator['surface']
        conn = fake_simulator['connectivity']
        using_cortical_surface = surf is not None
        if using_cortical_surface:
            non_cortical_indices, = np.where(np.bincount(surf.region_mapping) == 1)
            self.rmap = surf.region_mapping
        else:
            # assume all cortical if no info
            if conn.cortical.size == 0:
                conn.cortical = np.array([True] * conn.weights.shape[0])
            non_cortical_indices, = np.where(~conn.cortical)
            if self.region_mapping is None:
                raise Exception("Please specify a region mapping on the EEG/MEG/iEEG monitor when "
                                "performing a region simulation.")
            else:
                self.rmap = self.region_mapping

            self.log.debug('Projection used in region sim has %d non-cortical regions', non_cortical_indices.size)

        have_subcortical = len(non_cortical_indices) > 0

        # determine source space
        if using_cortical_surface:
            sources = {'loc': surf.vertices, 'ori': surf.vertex_normals}
        else:
            sources = {'loc': conn.centres[conn.cortical], 'ori': conn.orientations[conn.cortical]}

        # compute analytic if not provided
        if not hasattr(self, 'projection'):
            self.log.debug('Precomputed projection not unavailable using analytic approximation.')
            self.gain = self.analytic(**sources)

        # reduce to region lead field if region sim
        if not using_cortical_surface and self.gain.shape[1] == self.rmap.size:
            gain = np.zeros((self.gain.shape[0], conn.number_of_regions))
            numpy_add_at(gain.T, self.rmap, self.gain.T)
            self.log.debug('Region mapping gain shape %s to %s', self.gain.shape, gain.shape)
            self.gain = gain

        # append analytic sub-cortical to lead field
        if have_subcortical:
            # need matrix of shape (proj.shape[0], len(sc_ind))
            src = conn.centres[non_cortical_indices], conn.orientations[non_cortical_indices]
            self.gain = np.hstack((self.gain, self.analytic(*src)))
            self.log.debug('Added subcortical analytic gain, for final shape %s', self.gain.shape)

        if self.sensors.usable is not None and not self.sensors.usable.all():
            mask_unusable = ~self.sensors.usable
            self.gain[mask_unusable] = 0.0
            self.log.debug('Zeroed gain coefficients for %d unusable sensors', mask_unusable.sum())

        # unconditionally zero NaN elements; framework not prepared for NaNs.
        nan_mask = np.isfinite(self.gain).all(axis=1)
        self.gain[~nan_mask] = 0.0
        self.log.debug('Zeroed %d NaN gain coefficients', nan_mask.sum())

        # attrs used for recording
        self._state = np.zeros((self.gain.shape[0], len(self.voi)))
        self._period_in_steps = int(self.period / self.dt)
        self.log.debug('State shape %s, period in steps %s', self._state.shape, self._period_in_steps)

        self.log.info('Projection configured gain shape %s', self.gain.shape)


def compute_ecog(parameters):
    nb_region = int(parameters['param_tvb_connection']['nb_region'])
    tract_lengths = np.load(parameters['param_tvb_connection']['path_distance'])
    weights = np.load(parameters['param_tvb_connection']['path_weight'])
    if 'path_region_labels' in parameters['param_tvb_connection'].keys():
        region_labels = np.loadtxt(parameters['param_tvb_connection']['path_region_labels'], dtype=str)
    else:
        region_labels = np.array([], dtype=np.dtype('<U128'))
    if 'path_centers' in parameters['param_tvb_connection'].keys():
        centers = np.loadtxt(parameters['param_tvb_connection']['path_centers'])
    else:
        centers = np.array([])
    if 'orientation' in parameters['param_tvb_connection'].keys() and parameters['param_tvb_connection']['orientation']:
        orientation = []
        for i in np.transpose(centers):
            orientation.append(findVec(i, np.mean(centers, axis=1)))
        orientation = np.array(orientation)
    else:
        orientation = None
    if 'path_cortical' in parameters['param_tvb_connection'].keys():
        cortical = np.load(parameters['param_tvb_connection']['path_cortical'])
    else:
        cortical = None
    connection = lab.connectivity.Connectivity(number_of_regions=nb_region,
                                               tract_lengths=tract_lengths[:nb_region, :nb_region],
                                               weights=weights[:nb_region, :nb_region],
                                               region_labels=region_labels,
                                               centres=centers.T,
                                               cortical=cortical,
                                               orientations=orientation)
    connection.configure()
    volume = np.loadtxt(parameters['param_tvb_monitor']['parameter_ECOG']['path_volume'])[:nb_region]  # volume of the regions
    monitor = wapper_ECOG().from_file(parameters['param_tvb_monitor']['parameter_ECOG']['path'],
                     parameters['param_tvb_monitor']['parameter_ECOG']['scaling'],
                     volume=volume
                     )
    fake_simulator = {'dt': 0.1, 'variables_of_interest': ("E",),
                      'cortical': np.load(parameters['param_tvb_connection']["path_cortical"]),
                      'connectivity':connection,
                      'surface':None}
    monitor.config_for_sim(fake_simulator)
    rates = get_rate(parameters['result_path'] + '/tvb/')
    monitor_value = []
    monitor_time = []
    for i in range(rates[0][1].shape[0]):
        print(i)
        value = monitor.sample(i + 1, rates[0][1][i])
        if value is not None:
            monitor_time.append(value[0])
            monitor_value.append(value[1])
    plt.plot(monitor_time,np.concatenate(monitor_value)[:,0])
    plt.xlim(xmin=42500.0, xmax=53500.0)
    plt.show()
    np.save(parameters['result_path']+'/tvb/ECOG.npy',[monitor_time,monitor_value])

if __name__ == '__main__':
    path_parameter = '/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/local_cluster/case_up_down/'
    # path_parameter = '/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/local_cluster/case_asynchronous/'
    # path_parameter = '/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/local_cluster/case_regular_burst/'
    import json
    with open(path_parameter + '/parameter.json') as f:
        parameters = json.load(f)
    parameters['param_tvb_monitor']['parameter_ECOG']['path'] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/sensor_hypocampus.txt"
    parameters['param_tvb_monitor']['parameter_ECOG']['path_volume'] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/region_volume.txt"
    parameters['param_tvb_monitor']['parameter_ECOG']['scaling'] = 1.0
    parameters['param_tvb_connection']["path_region_labels"] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/region_labels.txt"
    parameters['param_tvb_connection']["path_centers"] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/centres.txt"
    parameters['param_tvb_connection']["path_cortical"] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/cortical.npy"
    parameters['param_tvb_connection']["path_distance"] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/distance.npy"
    parameters['param_tvb_connection']["path_weight"] = "/home/kusch/Documents/project/co_simulation/TVB-NEST-nest_PR/example/parameter/data_mouse/weights.npy"

    parameters['result_path'] = path_parameter
    compute_ecog(parameters)
