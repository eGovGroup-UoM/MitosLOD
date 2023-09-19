# cpsv-ap-transformation
# WEB SERVICE, TO CSV STORAGE, TO RDF MAP
# Part of my MsC Thesis
# dev13nt - kntoutsos@gmail.com


#Execute Core functionality
python3 asyncMain.py
#Automatically / Programmaticaly (in async time) calls processorMain.py as well

#After asyncMain finishes, execute TTLGeneralOutput.py to produce RDF
python3 TTLGeneralOutput.py
