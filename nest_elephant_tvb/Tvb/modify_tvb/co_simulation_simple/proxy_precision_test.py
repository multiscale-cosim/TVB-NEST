# -*- coding: utf-8 -*-
#
#
#  TheVirtualBrain-Scientific Package. This package holds all simulators, and
# analysers necessary to run brain-simulations. You can use it stand alone or
# in conjunction with TheVirtualBrain-Framework Package. See content of the
# documentation-folder for more details. See also http://www.thevirtualbrain.org
#
# (c) 2012-2020, Baycrest Centre for Geriatric Care ("Baycrest") and others
#
# This program is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software Foundation,
# either version 3 of the License, or (at your option) any later version.
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
# You should have received a copy of the GNU General Public License along with this
# program.  If not, see <http://www.gnu.org/licenses/>.
#
#
#   CITATION:
# When using The Virtual Brain for scientific publications, please cite it as follows:
#
#   Paula Sanz Leon, Stuart A. Knock, M. Marmaduke Woodman, Lia Domide,
#   Jochen Mersmann, Anthony R. McIntosh, Viktor Jirsa (2013)
#       The Virtual Brain: a simulator of primate brain network dynamics.
#   Frontiers in Neuroinformatics (7:10. doi: 10.3389/fninf.2013.00010)
from nest_elephant_tvb.Tvb.modify_tvb.co_simulation_simple.function_tvb import TvbSim
from tvb.tests.library.base_testcase import BaseTestCase
import numpy as np
import numpy.random as rgn


class TestProxyPrecision(BaseTestCase):
    def test_precision(self):
        weight = np.array([[2, 8], [3, 5]])
        delay = 100.0
        delays = np.array([[delay, delay], [delay, delay]])
        init_value = [[0.9], [0.9]]
        resolution_simulation = 0.1
        resolution_monitor = resolution_simulation * 10.0
        time_synchronize = resolution_simulation * 10.0
        nb_init = (int(delay / resolution_simulation)) + 1
        initial_condition = np.array(init_value * nb_init).reshape((nb_init, 1, weight.shape[0], 1))
        proxy_id = [0]

        # full simulation
        rgn.seed(42)
        sim_ref = TvbSim(weight, delays, [], resolution_simulation, resolution_monitor, time_synchronize,
                         initial_condition=initial_condition)
        time, result_ref, s_ref = sim_ref(resolution_monitor, s=True)

        # simulation with one proxy
        rgn.seed(42)
        sim = TvbSim(weight, delays, proxy_id, resolution_simulation, resolution_monitor, time_synchronize,
                     initial_condition=initial_condition)
        time, result, s = sim(resolution_monitor, [time, result_ref[:, proxy_id][:, :, 0]], s=True)

        diff = np.where(result_ref != result)
        diff_s = np.where(s_ref != s)
        assert diff[0].size == 0
        assert diff_s[0].size == 0

        for i in range(0, 10000):
            time, result_ref, s_ref = sim_ref(time_synchronize, s=True)
            time, result, s = sim(time_synchronize, [time, result_ref[:, proxy_id][:, :, 0]], s=True)

            diff = np.where(result_ref != result)
            diff_s = np.where(s_ref != s)
            assert diff[0].size == 0
            assert diff_s[0].size == 0
