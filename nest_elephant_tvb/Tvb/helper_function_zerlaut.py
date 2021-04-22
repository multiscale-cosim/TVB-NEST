# https://stackoverflow.com/questions/51272288/how-to-calculate-the-vector-from-two-points-in-3d-with-python
def multiDimenDist(point1,point2):
   #find the difference between the two points, its really the same as below
   deltaVals = [point2[dimension]-point1[dimension] for dimension in range(len(point1))]
   runningSquared = 0
   #because the pythagarom theorm works for any dimension we can just use that
   for coOrd in deltaVals:
       runningSquared += coOrd**2
   return runningSquared**(1/2)
def findVec(point1,point2,unitSphere = False):
  #setting unitSphere to True will make the vector scaled down to a sphere with a radius one, instead of it's orginal length
  finalVector = [0 for coOrd in point1]
  for dimension, coOrd in enumerate(point1):
      #finding total differnce for that co-ordinate(x,y,z...)
      deltaCoOrd = point2[dimension]-coOrd
      #adding total difference
      finalVector[dimension] = deltaCoOrd
  if unitSphere:
      totalDist = multiDimenDist(point1,point2)
      unitVector =[]
      for dimen in finalVector:
          unitVector.append( dimen/totalDist)
      return unitVector
  else:
      return finalVector

from tvb.simulator.monitors import Projection,Attr, Float
from tvb.datatypes.sensors import SensorsEEG
from tvb.datatypes.time_series import TimeSeriesEEG, List
from tvb.datatypes.region_mapping import RegionMapping
import numpy as np


class SensorsECOG(SensorsEEG):
    pass


class TimeSeriesECOG(TimeSeriesEEG):
    sensors = Attr(field_type=SensorsECOG)
    labels_ordering = List(of=str, default=("Time", "1", "ECOG Sensor", "1"))


class ECOG(Projection):
    sensors = Attr(SensorsECOG, required=True, label="ECOG Sensors",
                   doc='Sensors to use for this ECOG monitor')
    scaling = Float(field_type=float,label="scaling factor",
                            doc="""Scaling the signal""")

    def analytic(self, loc, ori):
        # localisation => source positions
        # orientation => source orientation
        gain = self.scaling / np.array(
            [np.linalg.norm(np.expand_dims(i, 0) - loc, axis=1) for i in self.sensors.locations])
        return gain

    def create_time_series(self, connectivity=None, surface=None,
                           region_map=None, region_volume_map=None):
        return TimeSeriesECOG(sensors=self.sensors,
                             sample_period=self.period,
                             title=' ' + self.__class__.__name__)

    @classmethod
    def from_file(cls, sensors_fname, scaling, rm_f_name="regionMapping_16k_76.txt",
                  period=1e3/1024.0, **kwds):
        """
        Build Projection-based monitor from sensors and projection files, and
        any extra keyword arguments are passed to the monitor class constructor.

        """
        result = cls(scaling=scaling, period=period, **kwds)
        result.sensors = cls.sensors.field_type.from_file(sensors_fname)
        result.region_mapping = RegionMapping.from_file(rm_f_name)
        return result