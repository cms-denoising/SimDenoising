import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing
import SimDenoising.Calo.ParamModifier as pm

defaults = {
    "mineta": -3.,
    "maxeta": 3.,
    "minphi": -3.14159265359,
    "maxphi": 3.14159265359,
}

particles = {
    "electron": 11,
    "positron": -11,
    "photon": 22,
}

params = pm.getAllClasses(pm)

options = VarParsing()
options.register("particle", "electron", VarParsing.multiplicity.singleton, VarParsing.varType.string, "particle to generate (choices: {})".format(','.join(sorted(particles))))
options.register("mult", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "number of particles to generate") # number of particles
options.register("minenergy", 1, VarParsing.multiplicity.singleton, VarParsing.varType.float, "minimum energy to generate")
options.register("maxenergy", 0, VarParsing.multiplicity.singleton, VarParsing.varType.float, "maximum energy to generate (0: max = min)")
options.register("mineta", defaults["mineta"], VarParsing.multiplicity.singleton, VarParsing.varType.float, "minimum eta to generate")
options.register("maxeta", defaults["maxeta"], VarParsing.multiplicity.singleton, VarParsing.varType.float, "maximum eta to generate")
options.register("minphi", defaults["minphi"], VarParsing.multiplicity.singleton, VarParsing.varType.float, "minimum phi to generate")
options.register("maxphi", defaults["maxphi"], VarParsing.multiplicity.singleton, VarParsing.varType.float, "maximum phi to generate")
options.register("maxEvents", -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "Number of events to process (-1 for all)")
options.register("maxEventsIn", -1, VarParsing.multiplicity.singleton, VarParsing.varType.int, "maximum number of input events (if different from maxEvents)")
options.register("part", 0, VarParsing.multiplicity.singleton, VarParsing.varType.int, "part number")
options.register("redir", "", VarParsing.multiplicity.singleton, VarParsing.varType.string, "xrootd redirector")
options.register("indir", "", VarParsing.multiplicity.singleton, VarParsing.varType.string, "input directory")
options.register("xmin", 1300, VarParsing.multiplicity.singleton, VarParsing.varType.int, "minimum x coordinate for image")
options.register("xmax", 1500, VarParsing.multiplicity.singleton, VarParsing.varType.int, "maximum x coordinate for image")
options.register("ymin", -5, VarParsing.multiplicity.singleton, VarParsing.varType.int, "minimum y coordinate for image")
options.register("ymax", 5, VarParsing.multiplicity.singleton, VarParsing.varType.int, "maximum y coordinate for image")
options.register("xbins", 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "number of x bins for image")
options.register("ybins", 100, VarParsing.multiplicity.singleton, VarParsing.varType.int, "number of y bis for image")
options.register("imageonly", False, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "only save image (not steps) in ntup tree")
options.register("resetrandom", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "reset random number generator state for each event")
options.register("paramNames", "", VarParsing.multiplicity.list, VarParsing.varType.string, "Geant4 parameters to modify (choices: {})".format(','.join(sorted(params))))
options.register("paramValues", "", VarParsing.multiplicity.list, VarParsing.varType.float, "values for modified Geant4 parameters")

options.parseArguments()

# choose particle
if options.particle in particles: options._pdgid = particles[options.particle]
else: raise ValueError("Unsupported particle: "+options.particle)

# check options
if options.maxEventsIn==-1: options.maxEventsIn = options.maxEvents
if options.maxenergy==0.: options.maxenergy = options.minenergy

# handle parameters
paramValueCounter = 0
options._params = []
# create parameter classes, assign values, assemble name
_pnames = []
for p in options.paramNames:
    if p not in params:
        raise ValueError("Unsupported param: "+p)
    else:
        options._params.append(getattr(pm,p)())
        options._params[-1].setValues(options.paramValues[paramValueCounter:paramValueCounter+options._params[-1].nparams])
        _pnames.append(p+','.join(str(pp) for pp in options._params[-1].params))
        paramValueCounter += options._params[-1].nparams
if paramValueCounter != len(options.paramValues):
    raise ValueError("Used {} paramValues, but {} were provided".format(paramValueCounter,len(options.paramValues)))
_pnametmp = '_'.join(_pnames)

# basic name definition
nametmp = options.particle+"_energy"+str(options.minenergy)+("to"+str(options.maxenergy) if options.minenergy!=options.maxenergy else "")+"_mult"+str(options.mult)
if any([defaults[x] != getattr(options,x) for x in defaults]):
    nametmp = nametmp+"_eta"+str(options.mineta)+("to"+str(options.maxeta) if options.mineta!=options.maxeta else "")+"_phi"+str(options.minphi)+("to"+str(options.maxphi) if options.minphi!=options.maxphi else "")
_partname = "_part"+str(options.part) if options.part>0 else ""
# gen name definition: does not include parameter variations
options._genname = "gen_"+nametmp+"_n"+str(options.maxEventsIn)+_partname
# sim name definition
if len(_pnametmp)>0:
    nametmp += "_"+_pnametmp
options._simname = "sim_"+nametmp+"_n"+str(options.maxEvents)+_partname
# ntuple name definition
options._ntupname = "ntup_"+nametmp+"_n"+str(options.maxEvents)+_partname

def resetSeeds(process,options):
    # reset all random numbers to ensure statistically distinct but reproducible jobs
    from IOMC.RandomEngine.RandomServiceHelper import RandomNumberServiceHelper
    randHelper = RandomNumberServiceHelper(process.RandomNumberGeneratorService)
    randHelper.resetSeeds(options.maxEvents*options.part+1)
    if process.source.type_()=='EmptySource' and options.part>0: process.source.firstEvent = cms.untracked.uint32((options.part-1)*options.maxEvents+1)
    return process
