import ROOT
from ROOT import pythonization
import numpy as np
import math

@pythonization('TH1', is_prefix=True)
@pythonization('TH2', is_prefix=True)
@pythonization('TH3', is_prefix=True)
def numpy_pythonizer_roothistograms(klass, name):
    if name in ["TH1D", "TH2D", "TH3D"]:
        # klass.np_bytes = 8
        klass.np_type = np.float64
    if name in ["TH1F", "TH2F", "TH3F"]:
        # klass.np_bytes = 4
        klass.np_type = np.float32
    if name in ["TH1I", "TH2I", "TH3I"]:
        # klass.np_bytes = 4
        klass.np_type = np.int32
    if name in ["TH1S", "TH2S", "TH3S"]:
        # klass.np_bytes = 2
        klass.np_type = np.int16
    # Not supported - GetArray returns a TArrayC, but numpy sees this as an empty string, so it would take more work to get there...
    # if name in ["TH1C", "TH2C", "TH3C"]:
    #     klass.np_bytes = 1
    #     klass.np_type = np.int8
    def _get_shape(self):
        n = self.GetDimension()
        shape = []
        shape.append(self.GetNbinsX()+2)
        if n > 1:
            shape.append(self.GetNbinsY()+2)
        if n > 2:
            shape.append(self.GetNbinsZ()+2)
        return tuple(shape)

    def _get_shape_inverted(self):
        return tuple([x for x in self._get_shape()][::-1])

    def _remove_flow(self, arr):
        n = self.GetDimension()
        # slicer = [slice(1:-1)]*self.GetDimension()
        # return arr[*slicer]
        if n == 3:
            return arr[1:-1, 1:-1, 1:-1]
        if n == 2:
            return arr[1:-1, 1:-1]
        if n == 1:
            return arr[1:-1]
            
    def _safe_cast(self, arr):
        if arr.dtype == self.np_type:
            return arr
        else:
            try:
                return arr.astype(self.np_type, order='K', casting='safe', subok=False, copy=True)
            except:
                raise ValueError(f"{arr.dtype} is not safe-cast compatible with the histogram storage type {self.np_type}")

    def _dimension_pad(self, arr):
        lhs, rhs = arr.shape, self._get_shape()
        if lhs == rhs:
            return arr
        elif tuple([s+2 for s in lhs]) == rhs:
            # padding = tuple([(1, 1) for d in range(self.GetDimension())])
            padding = tuple([(1, 1)]*self.GetDimension())
            return np.pad(arr, padding, mode='constant', constant_values=0)
        else:
            raise ValueError(f"array with shape {arr.shape} is not dimension-paddable with histogram shape {self._get_shape()}")
            
        return None

    def _reshape_transpose(self, arr):
        """To match boost-histogram array layout, as well as expected axis slicing"""
        return arr.reshape(self._get_shape_inverted()).transpose(*[n for n in range(self.GetDimension(), -1)])

    def _transpose_reshape(self, arr):
        """To convert from boost-histogram array layout/expected axis slicing to internal buffer layout"""
        return arr.transpose(*[n for n in range(self.GetDimension(), -1)]).reshape(math.prod(self._get_shape_inverted()))

    def values(self, flow=False):
        # full = np.frombuffer(self.GetArray(), dtype=self.np_type, count=self.GetSumw2N()).reshape(self._get_shape())
        full = self._reshape_transpose(np.frombuffer(self.GetArray(), 
                                                     dtype=self.np_type, 
                                                     count=self.GetSumw2N()
                                                 )
                                   )
        if flow:
            return full
        else:
            return self._remove_flow(full)


    def set_values(self, arr):
        # _arr = self._dimension_pad(self._safe_cast(arr)).reshape(math.prod(self._get_shape()))
        _arr = self._transpose_reshape(self._dimension_pad(arr))
        _n = len(_arr)
        self.Set(_n, _arr)

    def __getitem__(self, slc):
        return self.values(flow=True)[slc]

    def __setitem__(self, slc, values):
        new_values = self.values(flow=True)
        if values.shape == new_values[slc].shape:
            new_values[slc] = values
            self.set_values(new_values)
        else:
            raise ValueError(f"array with shape {values.shape} is not compatible with histogram slice shape {new_values.shape}")

    def variances(self, flow=False):
        full = self._reshape_transpose(np.frombuffer(self.GetSumw2().GetArray(), 
                                                     dtype=self.np_type, 
                                                     count=self.GetSumw2N()
                                                 )
                                   )
        if flow:
            return full
        else:
            return self._remove_flow(full)

    def set_variances(self, arr):
        _arr = self._transpose_reshape(self._dimension_pad(self._safe_cast(arr)))
        _n = len(_arr)
        self.GetSumw2().Set(_n, _arr)

    if name not in ["TH1", "TH1C"]:
        klass._get_shape = _get_shape
        klass._get_shape_inverted = _get_shape_inverted
        klass._remove_flow = _remove_flow
        klass._safe_cast = _safe_cast
        klass._dimension_pad = _dimension_pad
        klass._reshape_transpose = _reshape_transpose
        klass._transpose_reshape = _transpose_reshape
        klass.values = values
        klass.variances = variances
        klass.set_values = set_values
        klass.set_variances = set_variances
        klass.__getitem__ = __getitem__
        klass.__setitem__ = __setitem__

def test_numpy_histogram_pythonization():
    print("\nHello There\n")
    # h1 = ROOT.TH1C("c", "", 10, 0, 10)
    h2 = ROOT.TH1S("s", "", 10, 0, 10)
    h3 = ROOT.TH1I("i", "", 10, 0, 10)
    h4 = ROOT.TH1F("f", "", 10, 0, 10)
    h5 = ROOT.TH1D("d", "", 10, 0, 10)
    h6 = ROOT.TH2D("d2", "", 3, 0, 3, 4, 0, 4)
    
    # h1.Fill(1.5)
    h2.Fill(1.5)
    h3.Fill(1.5)
    h4.Fill(1.5)
    h5.Fill(1.5)
    
    # h1.Fill(2.5, 2)
    h2.Fill(2.5, 2)
    h3.Fill(2.5, 2)
    h4.Fill(2.5, 2)
    h5.Fill(2.5, 2)
    
    h6.Fill(0.5, 0.5, 1)
    h6.Fill(0.5, 3.5, 3)
    h6.Fill(2.5, 3.5, 2)
    h6.Fill(2.5, 0.5, 4)
    
    
    print(h6.values(flow=True))
    print(h6.variances(flow=True))
    print(h6.values(flow=False))
    print(h6.variances(flow=False))
    
    # print(h1.values(flow=True))
    print(h2.values(flow=True))
    print(h3.values(flow=True))
    print(h4.values(flow=True))
    print(h5.values(flow=True))
    
    h3.set_values(h3.values(flow=True))
    h3.set_values(h3.values(flow=False))
    
    h6.set_values(h6.values(flow=True))
    h6.set_values(h6.values(flow=False))
