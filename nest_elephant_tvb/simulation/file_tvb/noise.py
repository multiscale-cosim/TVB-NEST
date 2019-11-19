from tvb.simulator.noise import Additive
from tvb.datatypes import arrays
import numpy
from tvb.basic.traits import types_basic as basic

class  Ornstein_Ulhenbeck_process (Additive):

    _noise= numpy.nan

    def generate(self, shape, lo=-1.0, hi=1.0):
        self._noise = super(Ornstein_Ulhenbeck_process,self).generate(shape, lo=-1.0, hi=1.0)
        return self._noise

    def gfun(self, state_variables):
        """
            Drop noise in order to avoid negative frequency

        """
        noise_add = numpy.sqrt(2.0 * self.nsig)
        check = self._noise*noise_add*1.5 + state_variables
        # drop value for negative noise
        g_x = numpy.squeeze(numpy.swapaxes(numpy.repeat([noise_add],state_variables.shape[1],axis=0),0,1),3)
        g_x[:,numpy.where(check[0,:,:] <= 0.0)] = 0.0
        g_x[:,numpy.where(check[1,:,:] <= 0.0)] = 0.0
        return g_x
