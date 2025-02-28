Play with the model:  
**Action Potential initiation and backpropagation in Neocortical L5 Pyramidal Neuron (Hu et al. 2009)**  
https://modeldb.science/123897

### Installation:
1) `pip install neuron requests numpy matplotlib`
2) `git clone https://github.com/ctrl-z-9000-times/HuEtAl2009.git`
3) `py HuEtAl2009/main.py -v`  


### Usage:
`./mechanisms/MY_MOD/*mod` contains your mechanism files.  

`./mechanisms/orig/*mod` contains the original mechanism files.  

`py main.py -v --mod MY_MOD` compiles and executes with your mechanisms.  

`./recording/MY_MOD.dat` contains the output voltage traces.  

`py compare_results.py MY_MOD1 MY_MOD2` plots and compares the given voltage traces.

`py main.py -v --mod orig --dt .001 && mv recording/orig.dat recording/gold.dat`  Sets the gold standard for accuracy.

`nrngui init.hoc` starts the GUI using the most recently used mechanisms.  
Use option "1. Action Potential Initiation in Neocortical L5 Pyramidal Cell (Figure 5d,e)"  
Use option "1. Free Play"  

