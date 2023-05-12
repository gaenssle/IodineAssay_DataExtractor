# DataExtractor for Iodine assays
created 2017 by gaenssle
written in python 3.5

for questions, write to algaenssle@gmx.com
Iodine Assay: https://doi.org/10.1016/j.ab.2020.113696

The Iodine Assay File Converter (By A.L.O.Gaenssle, University of Groningen, 2017) is a small but highly-flexible program to sped up the analysis of data obtained from the iodine assay conducted in 96-well plates by re-organizing the data from the spectrophotometer to a suitable table format
    • The program has been written to import files (single wavelengths and spectra as plain text (.txt) files) exported from spectrophotometers (the default type is set for Molecular Devices but it can be modified) and export plain text files suitable for programs such as Stata or Origin
    • It reads in and reorganizes the data depending on user input, being amongst others sample number, assay area, number and time of transferred aliquots
    • The data is then saved in columns of sample index, time(min), Wavelength (nm) (if applicable) and results for each multiplicate

There are two additional program scripts
    • The automated DataExtractor has the same function as the default version but it does not conduct a questionaire before starting
    • The MaxPointFinder takes a spectra file obtained from the DataExtractor and finds the maximum wavelength for each sample
