from scipy.fftpack import basic
from tvb.simulator.monitors import Raw, basic, arrays
from tvb.simulator.history import BaseHistory, Dim, NDArray
from types import MethodType
import numpy


class Model_with_proxy():
    '''
    Minimum variables and functions for creating a model with proxy
    '''
    _id_proxy = [] # identifier of the proxy node
    _update = False # if the proxy node have define by the integrator
    _proxy_value = None # the value of the proxy node for current computation

    def copy_inst(self, model_without_proxy):
        '''
        Copy the value of an instance without proxy
        :param model_without_proxy: model without proxy
        '''
        for key, value in vars(model_without_proxy).items():
            setattr(self, key, value)
        self.configure()

    def set_id_proxy(self, id_proxy):
        '''
        define the list of the different proxy
        :param id_proxy: list with the identifier of the proxy node
        '''
        self._id_proxy = id_proxy

    def update_proxy(self, data):
        '''
        the new data for the next computation
        :param data: valeu for the proxy node
        '''
        self._update = True
        self._proxy_value = data

    def firing_rate(self):
        '''
        function in order to have access to the firing rate
        :return: firing rate of the model
        '''
        return self._firing_rate

class HistoryProxy(BaseHistory):
    "History implementation for saving proxy data."

    nb_proxy = Dim()  # number of proxy
    dim_1 = Dim()  # dmension one
    dt = NDArray((dim_1, dim_1), 'f')  # integration time of the simulator
    current_step = NDArray((dim_1, dim_1), 'f', read_only=False)  # the current time step of the simulation
    id_proxy = NDArray((nb_proxy,), 'i')  # the identification of proxy node
    buffer = NDArray(('n_time', 'n_cvar', 'n_node', 'n_mode'), 'f8', read_only=False)  # the buffer of value of th proxy

    def __init__(self, time_synchronize, dt, id_proxy, cvars, n_mode):
        '''
        initialisation of the history for saving proxy value
        :param time_synchronize: time between two receiving value
        :param dt: time of integration
        :param id_proxy: list of the proxy node
        :param cvars: the number of coupling variable
        :param n_mode: the number of mode
        '''
        #TODO send warning for bad size delay
        dim = max(1, (len(id_proxy)))
        size_history = numpy.zeros((dim, dim), dtype=numpy.int)  # size of number of node
        size_history[0, 0] = int(time_synchronize / dt) + 1  # size of the number of saving step
        super(HistoryProxy, self).__init__(None, size_history, cvars, n_mode)
        self.dim_1 = 1
        self.dt = numpy.array([dt])
        self.nb_proxy = id_proxy.shape[0]
        self.id_proxy = id_proxy

    def update(self, step, data):
        '''
        update the history with new value
        :param step: the step of the update value
        :param data: the data for the proxy node
        '''
        if self.id_proxy.size != 0:
            step_n = data[0] / self.dt[0] - step  # the indexe of the buffer
            if any(step_n > self.n_time):  # check if there are not too much data
                raise Exception('ERROR too early')
            if any(numpy.rint(step_n).astype(int) < 0.0):  # check if it's not missing value
                raise Exception('ERROR too late')
            indice = numpy.expand_dims(numpy.rint(step_n + step).astype(int) % self.n_time, 1)
            if indice.size != numpy.unique(indice).size:  # check if the index is correct
                raise Exception('ERRROR two times are the same')
            self.buffer[indice, 0, :, 0] = data[1]

    def next_step(self):
        '''
        :return: return the next step
        '''
        return self.buffer[(int(self.current_step)) % self.n_time]

    def update_current_step(self, step):
        '''
        update the curretn step of the simulator
        :param step: current step
        :return:
        '''
        self.current_step = numpy.array([step])

############################################ Modify Zerlaut #############################################
from Zerlaut import Zerlaut_adaptation_first_order,Zerlaut_adaptation_second_order

class Zerlaut_adaptation_first_order_proxy(Zerlaut_adaptation_first_order,Model_with_proxy):
    '''
    modify class in order to take in count proxy firing rate and to monitor the firing rate
    '''
    def __init__(self):
        super(Zerlaut_adaptation_first_order,self).__init__()

    def dfun(self, x, c, local_coupling=0.0):
        if self._update and self._id_proxy.size != 0:
            x[0,self._id_proxy]=self._proxy_value
            self._firing_rate=x[0, :]
            self._update=False
        deriv = super(Zerlaut_adaptation_first_order,self).dfun(x, c, local_coupling)
        return deriv

class Zeralut_adaptation_second_order_proxy(Zerlaut_adaptation_second_order,Model_with_proxy):
    '''
    modify class in order to take in count proxy firing rate and to monitor the firing rate
    '''
    def __init__(self):
        super(Zerlaut_adaptation_second_order,self).__init__()

    def dfun(self, x, c, local_coupling=0.0):
        if self._update and self._id_proxy.size != 0:
            x[0,self._id_proxy]=self._proxy_value
            self._firing_rate=x[0, :]
            self._update=False
        deriv = super(Zerlaut_adaptation_second_order,self).dfun(x, c, local_coupling)
        return deriv


#######################################################################################

class Interface_co_simulation(Raw):
    id_proxy = arrays.IntegerArray(
        label = "Identifier of proxys",
        order = -1)
    time_synchronize = basic.Float(
        label="simulated time between receiving the value of the proxy",
        order=-1)

    _model_with_proxy=None

    def __init__(self,model_with_proxy,**kwargs):
        super(Interface_co_simulation, self).__init__(**kwargs)
        self._model_with_proxy=model_with_proxy

    def config_for_sim(self,simulator):
        #configuration of all monitor
        super(Interface_co_simulation, self).config_for_sim(simulator)

        # create the model with proxy
        if not hasattr(self._model_with_proxy(), '_id_proxy'):
            raise Exception("ERROR type of model doesn't accept proxy")  #avoid bad type of class
        new_model = self._model_with_proxy()
        new_model.copy_inst(simulator.model)
        simulator.model = new_model
        self.model = simulator.model
        self.model.set_id_proxy(self.id_proxy)

        ######## WARNING:Change the instance simulator for taking in count the proxy ########
        # overwrite of the simulator for update the proxy value
        class Simulator_proxy (type(simulator)):
            #Modify the call method of the simulator in order to update the proxy value
            def __call__(self, simulation_length=None, random_state=None, proxy_data=None):
                if hasattr(self.integrator, 'history_proxy') and proxy_data is not None:
                    self.integrator.update_proxy_history(self.current_step + 1, proxy_data)
                return super(type(simulator),self).__call__(simulation_length=simulation_length, random_state=random_state)

        #change the class of the simulator
        simulator.__class__ = Simulator_proxy

        # overwrite of the method _loop_compute_node_coupling of the simulator :
        # this method is the first method call in the integration loop.
        # This overwriting add the update of the current step for the integrator
        original_method = simulator._loop_compute_node_coupling
        def _loop_compute_node_coupling(self,step):
            ''''
            see the simulator for this method
            '''
            self.integrator.history_proxy.update_current_step(step)
            return original_method(step)
        simulator._loop_compute_node_coupling = MethodType(_loop_compute_node_coupling,simulator)

        ######## WARNING:Change the instance of integrator for taking in count the proxy ########
        # Modify the Integrator for manage the proxy node :

        ## Add an history for saving the value from external input
        simulator.integrator.history_proxy = HistoryProxy(self.time_synchronize,simulator.integrator.dt,self.id_proxy,simulator.model.cvar,simulator.model.number_of_modes)
        def update_proxy_history(self, step, proxy_data ):
            '''
            update the history with the new value
            :param step: the current step
            :param proxy_data: the value of proxy node
            '''
            self.history_proxy.update(step,proxy_data)
        # add a method for update the history of the integrator
        simulator.integrator.update_proxy_history = MethodType(update_proxy_history, simulator.integrator)

        ## use the data in history to compute next step (overwrite of the method scheme)
        simulator.integrator._scheme_original_ = simulator.integrator.scheme
        simulator.integrator.interface_co_simulation = self # access to the model method (I am not sure to be the best way)
        def scheme(self, X, dfun, coupling, local_coupling, stimulus):
            self.interface_co_simulation.model.update_proxy(self.history_proxy.next_step())
            return self._scheme_original_(X, dfun, coupling, local_coupling, stimulus)
        simulator.integrator.scheme = MethodType(scheme,simulator.integrator)

    def sample(self, step, state):
        '''
        record fo the monitor in order to send result of TVB
        :param step: current step
        :param state: the state of all the node and also the value of the proxy
        :return:
        '''
        self.step = step
        time = step * self.dt
        return [time, numpy.expand_dims(self.model.firing_rate(),0)]