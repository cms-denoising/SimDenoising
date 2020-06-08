from Condor.Production.jobSubmitter import *
import sys, shlex

def makeNameSim(self,num):
    return self.name+"_part"+str(num)

protoJob.makeName = makeNameSim

class jobSubmitterSim(jobSubmitter):
    def __init__(self):
        # these extra attrs need to be defined before super class init
        self.allowed_steps = ["gen","sim"]
        self.step_files = {
            "gen": "runGen.py",
            "sim": "runSim.py",
        }
        super(jobSubmitterSim,self).__init__()

    def addExtraOptions(self,parser):
        super(jobSubmitterSim,self).addExtraOptions(parser)
        parser.add_option("-o", "--output", dest="output", default="", help="path to output directory in which root files will be stored (required) (default = %default)")
        parser.add_option("-F", "--firstPart", dest="firstPart", default=1, help="first part to process, in case extending a sample (default = %default)")
        parser.add_option("-N", "--nParts", dest="nParts", default=1, help="number of parts to process (default = %default)")
        parser.add_option("-i", "--indir", dest="indir", default="", help="input file directory (LFN) (default = %default)")
        parser.add_option("-d", "--redir", dest="redir", default="root://cmseos.fnal.gov/", help="input file redirector (default = %default)")
        parser.add_option("-S", "--step", dest="step", default="", help="step ("+', '.join(self.allowed_steps)+") (default = %default)")
        parser.add_option("-A", "--args", dest="args", default="", help="common args to use for all jobs, should include maxEvents (default = %default)")

    def checkExtraOptions(self,options,parser):
        super(jobSubmitterSim,self).checkExtraOptions(options,parser)
        if options.step not in self.allowed_steps:
            parser.error("Unknown step: "+options.step+" (known: "+' '.join(self.allowed_steps)+")")
        if len(options.output)==0:
            parser.error("Required option: --output [directory]")
        if options.step=="sim" and len(options.indir)==0:
            parser.error("Required option: --indir [directory]")
        if "maxEvents=" not in options.args:
            parser.error("Required: provide maxEvents=# in -A/--args")

    def generateSubmission(self):
        # create protojob
        job = protoJob()

        # get name from optGenSim
        # set sys args before importing optGenSim (VarParsing always tries to read them)
        sys.argv[1:] = shlex.split(self.args)
        import SimDenoising.Calo.optGenSim as gs
        if self.step=="gen": job.name = gs.options._genname
        elif self.step=="sim": job.name = gs.options._simname

        self.generatePerJob(job)

        # write job options to file - will be transferred with job
        if self.prepare:
           with open("input/args_"+job.name+".txt",'w') as argfile:
               argfile.write(self.args)

        for iJob in xrange(int(self.nParts)):
            # get real part number
            iActualJob = iJob+self.firstPart
            job.njobs += 1
            job.nums.append(iActualJob)

        # append queue comment
        job.queue = '-queue "Process in '+','.join(map(str,job.nums))+'"'

        # store protojob
        self.protoJobs.append(job)

    def generateExtra(self,job):
        super(jobSubmitterSim,self).generateExtra(job)
        job.patterns.update([
            ("JOBNAME",job.name+"_part$(Process)_$(Cluster)"),
            ("EXTRAINPUTS","input/args_"+job.name+".txt"),
            ("EXTRAARGS","-j "+job.name+" -p $(Process) -o "+self.output+" -s "+self.step_files[self.step]+(" -i "+self.indir if len(self.indir)>0 else "")+(" -x "+self.redir if len(self.redir)>0 else "")),
        ])
