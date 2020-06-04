import FWCore.ParameterSet.Config as cms
from FWCore.ParameterSet.VarParsing import VarParsing

defaults = {
    "mineta": -3.,
    "maxeta": 3.,
    "minphi": -3.14159265359,
    "maxphi": 3.14159265359,
}

options = VarParsing("analysis")
options.register("particle", "electron", VarParsing.multiplicity.singleton, VarParsing.varType.string)
options.register("mult", 1, VarParsing.multiplicity.singleton, VarParsing.varType.int) # number of particles
options.register("minenergy", 1, VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("maxenergy", 0, VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("mineta", defaults["mineta"], VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("maxeta", defaults["maxeta"], VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("minphi", defaults["minphi"], VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("maxphi", defaults["maxphi"], VarParsing.multiplicity.singleton, VarParsing.varType.float)
options.register("maxEventsIn", -1, VarParsing.multiplicity.singleton, VarParsing.varType.int)
options.register("output", True, VarParsing.multiplicity.singleton, VarParsing.varType.bool)
options.parseArguments()

# choose particle
options._pdgid = 0
if options.particle=="electron": options._pdgid = 11
elif options.particle=="positron": options._pdgid = -11
elif options.particle=="photon": options._pdgid = 22
else: raise ValueError("Unsupported particle: "+options.particle)

# check options
if options.maxEventsIn==-1: options.maxEventsIn = options.maxEvents
if options.maxenergy==0.: options.maxenergy = options.minenergy

# basic name definition
nametmp = options.particle+"_energy"+str(options.minenergy)+("to"+str(options.maxenergy) if options.minenergy!=options.maxenergy else "")+"_mult"+str(options.mult)
if any([defaults[x] != getattr(options,x) for x in defaults]):
    nametmp = nametmp+"_eta"+str(options.mineta)+"to"+str(options.maxeta)+"_phi"+str(options.minphi)+"to"+str(options.maxphi)
# gen name definition
options._genname = "gen_"+nametmp+"_n"+str(options.maxEventsIn)
# sim name definition
options._simname = "sim_"+nametmp+"_n"+str(options.maxEvents)
# ntuple name definition
options._ntupname = "ntup_"+nametmp+"_n"+str(options.maxEvents)
