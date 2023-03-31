from pathlib import Path
import argparse
import time
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('--duration', type=float, default=0)
parser.add_argument('--mod', type=str, default='orig')
parser.add_argument('--dt', type=float, default=0.01, help='milliseconds')
args = parser.parse_args()


# TODO: Make an argument for the number of cells, for memeory perf benchmarking.



repo = Path(__file__).parent
import os
os.chdir(repo)

if not Path('init.hoc').exists():
    ascension_number = 123897
    model_url = f"https://senselab.med.yale.edu/modeldb/eavBinDown?o={ascension_number}&a=23&mime=application/zip"
    print(f'Downloading:', model_url)
    import requests
    myfile = requests.get(model_url)
    zip_filename = Path(f'HuEtAl2009.zip')
    with open(zip_filename, 'wb') as f:
      f.write(myfile.content)
    print(f"Unzipping:", zip_filename)
    import zipfile
    zipfile.ZipFile(zip_filename).extractall()
    zip_filename.unlink()
    # Move the files into place.
    unzip_dir = Path('./HuEtAl2009/').resolve()
    for file in unzip_dir.iterdir():
      file.rename(file.parent.parent / file.name)
    unzip_dir.rmdir()
    # Move the mechanisms into a new subdir.
    mechanism = Path('mechanism')
    original  = Path('orig')
    mechanism.rename(original)
    mechanism.mkdir()
    original.rename(mechanism / original)



build_dir = Path("x86_64")
if build_dir.exists():
    subprocess.run(['rm', '-rf', str(build_dir)], check=True)
subprocess.run(["nrnivmodl", "mechanism/"+args.mod], check=True)



from neuron import h, gui
from neuron.units import ms, mV, µm


h("""
/* -----------------------------------------------------
    Layer V Cortical Pyramidal Cell
    
    Based on Yu Yuguo ( May 1, 2008)
----------------------------------------------------- */

xopen("$(NEURONHOME)/lib/hoc/noload.hoc")  
nrnmainmenu()

objref somatodendritic, dendritic


// --------------------------------------------------
//    Parameter Settings
// --------------------------------------------------

/* Global */
dt = """+str(args.dt)+"""
celsius   = 37
steps_per_ms = 1/dt
tstop = 100
v_init = -70

/* Others */
delay = 2  // global delay for preparing
axonOnSoma=1

/* Passive membrane */
ra        = 150  // decrease ad to decrease of soma vth variability, increase axon's vth variability
global_ra = ra
rm        = 30000   // g_pas=1/rm
c_m       = 0.5
cm_myelin = 0.02
g_pas_node = 0.02

/* Active channels */
// Nav
Ena = 60
gna12_soma = 80
gna12_dend = 80 
gna12_ais_max = 3200   // Nav1.2 
gna16_ais_max = 3200   // Nav1.6
gna16_nakeaxon= 300    
gna12_myelin=20       // Nav1.2 at myelins
gna16_node = 3200     // Nav1.6 at node

vhalf_na12 = -30
vhalf_na16 = -43
vhalf_na = -30

// Kv
Ek = -90  
gkv_soma = 20
gkv_dend = 10 
gkv_axon = 1000

// Km
gkm = .3
gkm_soma = gkm

// Kca
gkca = 3
gkca_soma = gkca

// Ca
Eca=140
gca = .3
gca_soma = gca



// ------------------------------------------------
//    Cell Geometry
// ------------------------------------------------
 

// Clean up
forall delete_section()

// Soma and Dendrites
load_file("morphology/P_Soma_Dendrites.hoc")

// build a sectionlist for soma and dendrites
somatodendritic = new SectionList()
forall {
  if (L/nseg>40) {
    nseg = L/40 + 1 
  }    // make sure no segments exceed 40 uM length. Note, soma.nseg remains 10.
  somatodendritic.append()  // soma and dendrites are all included
}

// build a sectionlist for dendrites only
dendritic = new SectionList()
forsec somatodendritic dendritic.append()
soma  dendritic.remove()     // remove soma for pure dendritic sectionlist

/* Axon */
load_file ("morphology/P_Axon.hoc") 
create_axon()

/* Spines */
aspiny = 0  // 0 for spiny
if (!aspiny) {
  load_file ("morphology/P_Spines.hoc")
  add_spines(dendritic,spine_dens)
}

distance(0,axonOnSoma)  // set the point where axon seated on soma as the origin



// ----------------------------------------------------
//  Insert Density Mechanisms
// ----------------------------------------------------

load_file ("lib/P_DensityMech.hoc") 

// Install passive membrane properties
install_passive()  
// Install active channels
install_channels()



// ----------------------------------------------------
//  Setup Simulation
// ----------------------------------------------------

// Inject soma, the original one
// xopen("experiment/Pyramidal/inject_soma.hoc")

""")

h("secondorder = 2")

stim = h.IClamp(h.soma(.5))
stim.dur = 5000
stim.delay = 50
stim.amp = 1

if args.verbose:
    h('xopen("lib/P_Recording.hoc")')
    h.finitialize(-65 * mV) # Recording does not take effect until after reset.

h.finitialize(-65 * mV)
time.sleep(0)
start_time = time.time()
h.continuerun(args.duration * ms)
if args.duration:
    print('Elapsed time: %.4g'%(time.time() - start_time))

if args.verbose:
    h('xopen("session/P_full.ses")') # Open the visualizers.
    h.dt = args.dt

    h.continuerun(100 * ms)

    h.saveV()
    Path("recording/allVTraces.dat").rename(f"recording/{args.mod}.dat")

    from compare_results import compare_results
    compare_results("gold", args.mod, show=True)
