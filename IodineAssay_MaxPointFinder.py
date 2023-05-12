#!/usr/bin/python
# The script has been written in Python 3.5

# IODINE ASSAY MAX POINT FINDER for already converted spectrum (.txt) files
# 2017 by A.L.O. Gaenssle (A.L.O.Gaenssle@rug.nl), 
# University of Groningen, the Netherlands

import os
    

# -----------------------------------------------------------------------------
# DEFAULT VALUES -------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Default start value of input data for shift values
# (wavelength and absorbance at lambda(max))
def getABandWLMax():
    # Minimum wavelength to have the maximum abosrbance
    # (set value to e.g. 450 if measuring spectra from 280 nm)
    # (any whole number)
    WLMax = 0   # Default = 0 
    ABMax = 0   # Do not change!
    return (ABMax, WLMax)


# -----------------------------------------------------------------------------
# FUNCTIONS -------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Print header
def PrintHeader():
    print("\n","-"*75,"\n","-"*75,"\n")
    print("THE IODINE ASSAY MAX POINT FINDER\tby A.L.O. Gaenssle, 2017")
    print("\n","-"*75,"\n","-"*75,"\n")
    print("This program imports text files from the "
        "IODINE ASSAY DATA EXTRACTOR")
    print("\nThe program has been written to:"
        "\n- Import files already converted files in the correct format"
        "\n- Find lambda(max) (max absorbance) for each spectrum"
        "\n- Export files suitable for programs such as Stata or Origin"
        "\n- Save data in columns of:\n\t- Sample index"
        "\n\t- Time(min)"
        "\n\t- Results for each multiplicate in wavelength-absorbance pairs")
    print("\nContact A. Lucie Gaenssle for help and adaptions "
        "(A.L.O.Gaenssle@rug.nl)")
    print("\n","-"*75)
    print("\nInformation:\n- Complete input by clicking enter"
        "\n- Navigate within and between the inputs using the arrow keys"
        "\n- Terminate the program any time by:"
        "\n\t- Closing the terminal (window)"
        "\n\t- Ctrl + C")
    print("\n","-"*75,"\n FILE INPUT\n","-"*75)

# Get file name and import it
def GetInputFile():
    # Get file name
    # (Subfunction to GetInputFile)
    def GetFileName(DirectoryName):
        InputPath = input("\nEnter your file name:"
            "\n- If file and python script in the same folder: e.g. Test.txt"
            "\n- If file in subfolder of folder with python script: e.g. "
            "IodineAssay\Test.txt\n- Otherwise enter full path: e.g. "
            "X:\Experiments\IodineAssay\Test_converted.txt"
            "\n\nHint: Your current directory is:\n%s\n"
            % DirectoryName)
        FileFormat = False
        while FileFormat == False:
            while os.path.isfile(InputPath) == False:
                InputPath = input("\nThis file does not exist!"
                    "\nPlease enter a correct name"
                    "\n(Check the file path by right clicking on "
                    "the file and selecting 'Properties')"
                    "\n(To not rewrite whole path, use arrows on keyboard)\n")
            if InputPath.endswith(".txt") or InputPath.endswith(".csv"):
                FileFormat = True
            else:
                InputPath = input("\nYour file does not have the correct "
                    "format!\nPlease enter a name ending with .txt or .csv\n")
        return (InputPath)

    # Import table, store data in list(lines) of lists(columns)
    # (Subfunction to GetInputFile)
    def GetFile(InputPath):
        InputData = []
        try:

            for DecodedLineOfFile in open(InputPath, 'r', encoding='UTF-16'):
                DecodedLineOfFile = DecodedLineOfFile.rstrip()
                LineOfFile = DecodedLineOfFile.split('\t')
                InputData.append(LineOfFile)
        except UnicodeError:
            try: 
                for DecodedLineOfFile in open(InputPath, 'r'):
                    DecodedLineOfFile = DecodedLineOfFile.rstrip()
                    LineOfFile = DecodedLineOfFile.split('\t')
                    InputData.append(LineOfFile)
            except UnicodeError:
                print("\nThe program is for a file encoded with UTF-8 or "
                    "UTF-16\nIf you have another file format, "
                    "contact Lucie Gaenssle\n(A.L.O.Gaenssle@rug.nl)"
                    "\n\nThe program will now be terminated")
                quit()
        return (InputData)

    # Start of GetInputFile script
    DirectoryName, ScriptName = os.path.split(os.path.abspath(__file__))
    os.chdir(DirectoryName)
    InputPath = GetFileName(DirectoryName)
    InputData = GetFile(InputPath)
    return(DirectoryName, InputData, InputPath)

# Convert all items in file to floats
def ConverToNUmbers(InputData):
    InputDataFloat = []
    for Lines in InputData[1:]:
        try:
            LinesFloat = [float(Items) for Items in Lines]
        except ValueError:
            print("This is not the correct file format"
                "\n(data contains not only numbers)"
                "\n\nThe program will now be terminated")
            quit()
        InputDataFloat.append(LinesFloat)
    return(InputDataFloat)

# Read data into a list of dictionaries
def ReadInData(InputDataFloat):
    Data = {}
    Spectrum = {}
    Wavelength = {}
    Muliplicates = len(InputDataFloat[1]) - 3
    SampleID = InputDataFloat[0][0]
    Time = InputDataFloat[0][1]
    for Lines in range(len(InputDataFloat)):
        if SampleID == InputDataFloat[Lines][0]:
            if Time == InputDataFloat[Lines][1]:
                Wavelength.update({InputDataFloat[Lines][2]:
                    InputDataFloat[Lines][3:]})
            else:
                Spectrum.update({Time:Wavelength})
                Time = InputDataFloat[Lines][1]
                Wavelength = {}
                Wavelength.update({InputDataFloat[Lines][2]:
                    InputDataFloat[Lines][3:]})
        else:
            Spectrum.update({Time:Wavelength})
            Data.update({SampleID:Spectrum})
            Spectrum = {}
            Spectrum.update({Time:Wavelength})
            Wavelength = {}
            Wavelength.update({InputDataFloat[Lines][2]:
                InputDataFloat[Lines][3:]})
            SampleID = InputDataFloat[Lines][0]
            Time = InputDataFloat[Lines][1]
    Spectrum.update({Time:Wavelength})
    Data.update({SampleID:Spectrum})                
    return(Data, Muliplicates)

# Find max values and create shift
def FindMax(AllData, Muliplicates):
    Shift = {}
    for Samples in AllData:
        ShiftSamples = {}
        for TimePoints in AllData[Samples]:
            ShiftTimePoint = []
            for Exp in range(Muliplicates):
                ABMax, WLMax = getABandWLMax()
                for Wavelength in AllData[Samples][TimePoints]:
                    try:
                        if (float(AllData[Samples][TimePoints][Wavelength]
                            [Exp]) > float(ABMax)):
                            ABMax = (AllData[Samples][TimePoints]
                                [Wavelength][Exp])
                            WLMax = int(Wavelength)
                    except IndexError:
                        break
                ShiftTimePoint.append({WLMax:ABMax})
            ShiftSamples.update({TimePoints:ShiftTimePoint})
        Shift.update({Samples:ShiftSamples})
    return(Shift)

# Check if file exists and should be replaced
def CheckPresenceOfFile(InputPath):
    OutputShiftPath = InputPath.split(".")[0] + "_Shift.txt"
    while os.path.isfile(OutputShiftPath) == True:
        Replace = input("\n%s already exists!"
            "\nShould the file be replaced?\n(y=yes, n=no)\n"
            % OutputShiftPath)
        while Replace not in ("y", "n"):
            Replace = input("\nPlease enter 'y' or 'n'!\n")
        if Replace == "y":
            break
        else:
            OutputShiftPath = input("\nEnter a new file name with "
                "extention '.txt'\n(e.g. Output.txt)\n")
            while OutputShiftPath.endswith(".txt") == False:
                OutputShiftPath = input(
                    "\nThis is not a correct format!"
                    "\nPlease enter a file name with "
                    "extention '.txt'\n(e.g. Output.txt)\n")
    return(OutputShiftPath)

# Create labels for the multiplicates in the output file
def CreateLabelList(Muliplicates):
    LabelListShift = []
    Count = 0
    for Count in range(1, Muliplicates+1):
        LabelShiftWL = "E" + str(Count) + "-WL"
        LabelShiftAb = "E" + str(Count) + "-Ab"
        Count += 1
        LabelListShift.append(LabelShiftWL)
        LabelListShift.append(LabelShiftAb)
    return (LabelListShift)

# Print to file
def PrintToFile(LabelListShift, OutputShiftPath, Shift):
    OutputShiftFile = open(OutputShiftPath, "w")
    OutputShiftFile.write("Sample\tT(min)\t")
    OutputShiftFile.write("\t".join(map(str, LabelListShift)))      
    for Samples in sorted(Shift.keys()):
        for TimePoints in sorted(Shift[Samples].keys()):
            OutputShiftFile.write("\n%s\t%s" % (int(Samples), TimePoints))
            for WLMax in range(len(Shift[Samples][TimePoints])):
                OutputShiftFile.write("\t")
                OutputShiftFile.write("\t".join(map(str,
                    Shift[Samples][TimePoints][WLMax])))
                OutputShiftFile.write("\t")
                OutputShiftFile.write("\t".join(map(str,
                    Shift[Samples][TimePoints][WLMax].values())))
    print("\nThe shift file has been created"
        "\n(If unaltered: Same name and folder, "
        "ending on '_shift.txt')")
    Status = "completed"
    return (OutputShiftFile, Status)

# Open output file
def OpenFile(OutputFormat, OutputPath):
    Open = input("\nDo you want to view the %s file?\n(y=yes, n=no)\n"
        % OutputFormat)
    while Open not in ("y", "n"):
        Open = input("\nPlease enter 'y' or 'n'!\n")
    if Open == "y":
        os.startfile(OutputPath)


# -----------------------------------------------------------------------------
# SCRIPT ----------------------------------------------------------------------
# -----------------------------------------------------------------------------

# Print header
PrintHeader()

# Import file and convert data
DirectoryName, InputData, InputPath = GetInputFile()
InputDataFloat = ConverToNUmbers(InputData)
Data, Muliplicates = ReadInData(InputDataFloat)
Shift = FindMax(Data, Muliplicates)

# Print to file
OutputShiftPath = CheckPresenceOfFile(InputPath)
LabelListShift = CreateLabelList(Muliplicates)
OutputShiftFile, Status = PrintToFile(LabelListShift, OutputShiftPath, Shift)

# Open file
OutputFormat = "shift"
OpenFile(OutputFormat, OutputShiftPath)

print("\n","-"*75,"\n End of program\n","-"*75,"\n","-"*75)
