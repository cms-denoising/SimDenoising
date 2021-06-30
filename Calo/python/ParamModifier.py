import FWCore.ParameterSet.Config as cms

def getAllClasses(module):
    import inspect
    vm = vars(module)
    exclude = ["ParamModifier"]
    all_classes = [v for v in vm if v not in exclude and inspect.isclass(vm[v])]
    return all_classes

class ParamModifier(object):
    def __init__(self, nparams):
        self.nparams = nparams
        self.params = []
    def setValues(self, params):
        if len(params)!=self.nparams: raise RuntimeError("Expected number of params for {} is {}, but {} were provided".format(self.__class__.__name__,self.nparams,len(params)))
        self.params = params
    def apply(self, process):
        pass

class ProductionCut(ParamModifier):
    def __init__(self):
        super(ProductionCut,self).__init__(1)
    def apply(self, process):
        process.g4SimHits.Physics.CutsPerRegion = cms.bool(False)
        process.g4SimHits.Physics.DefaultCutValue = cms.double(self.params[0])
        return process

class EnergyThSimple(ParamModifier):
    def __init__(self):
        super(EnergyThSimple,self).__init__(1)
    def apply(self, process):
        process.g4SimHits.MagneticField.ConfGlobalMFM.OCMS.StepperParam.EnergyThSimple = cms.double(self.params[0])
        return process
