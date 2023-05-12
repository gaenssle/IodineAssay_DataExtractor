#!/usr/bin/python
# The script has been written in Python 3.5

# IODINE ASSAY DATA EXTRACTOR for plates and spectrum text (.txt) files
# 2017 by A.L.O. Gaenssle (A.L.O.Gaenssle@rug.nl), 
# University of Groningen, the Netherlands

import os


# ---------------------------------------------------------------------------
# DEFAULT VALUES ------------------------------------------------------------
# ---------------------------------------------------------------------------

# Information: Backup the file if you change variables
# Information: The default values below are based on columns of input files
# Information: All columns are separted by a space 
# (check the number by copying the input file into a table e.g. Excel)

# Number of the column containing the wavelength in nm 
# (only required for spectra)
Default_WavelengthColumnIndex = 1       # Default = 1

# Number of the column containing the first column of results 
# (wells A-H1 for plate format, well A1 for column format)
Default_FirstDataColumnIndex = 3        # Default = 3

# The given text appearing at the beginning of the line directly
# above the data (only required for spectra) 
Default_BeforeDataText = "Wavelength"       # Default = "Wavelength"

# The given text appearing at the beginning of the line below the data
# (adjust Default_EmptyLinesBetweenDataAndAfterText for empty lines
# between data and label)
Default_AfterDataText = "~End"          # Default = "~End"

# Empty Lines between the last line containing data
# (Wells H1-12 for plate format, last Wavelength for column format)
# and Default_AfterDataText
Default_EmptyLinesBetweenDataAndAfterText = 1   # Default = 1

# Default settings (Default types of sample settings) 
# Warning: Do not change anything expect the values of the variables!
def GetDefaultSettings(DefaultType, SampleDirection):
    if SampleDirection == "v":          # Do not change!
        if DefaultType == "short":      # Do not change!

            # Number of time points (no extra wells) (whole number from 1-8)
            NTimePoints = 6             # Default = 6

            # Number of time points and extra wells (whole number from 1-8)
            SlopeCount = 8              # Default = 8

            # Number of identical samples per sample (whole number from 1-12)
            Muliplicates = 3            # Default = 3

            # Total number of samples on plate (samples * repetitions)
            # (whole number from 1-12)
            TotNSamples = 12            # Default = 12

            # List of time points in min at which aliquotes were taken
            # Default = [1, 2, 3, 5, 7, 10] (any list of numbers)
            TypeTimePoints = [1, 2, 3, 5, 7, 10]    
        else:
            NTimePoints = 14            # Default = 14 (whole number from 1-16)
            SlopeCount = 16             # Default = 16 (whole number from 1-16)
            Muliplicates = 2            # Default = 2 (whole number from 1-6)
            TotNSamples = 6             # Default = 6 (whole number from 1-6)

            # List of time points in min at which aliquotes were taken
            # Default = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]
            # (any list of numbers)
            TypeTimePoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 15, 20, 25, 30]
    else:
        NTimePoints = 10                # Default = 10 (whole number from 1-12)
        SlopeCount = 12                 # Default = 12 (whole number from 1-12)
        Muliplicates = 2                # Default = 2 (whole number from 1-8)
        TotNSamples = 8                 # Default = 8 (whole number from 1-8)

        # List of time points in min at which aliquotes were taken
        # Default = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10] (any list of numbers)
        TypeTimePoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    # Position of wells containing the ASSAY solution)  
    # (may be f, l, a or e)
    # (f=first, l=last, a=absent, e=end of first column/row)
    Lassay = "f"            # Default = "f"

    # Position of wells contianing the WASH solution)
    # (may be f, l, a or e)
    # (f=first, l=last, a=absent, e=end of first column/row)
    Lwash = "l"             # Default = "l" 
    AssayArea = "A1-H12"
    return (AssayArea, Lassay, Lwash, Muliplicates, NTimePoints, SlopeCount,
        TotNSamples, TypeTimePoints)

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
    print("THE IODINE ASSAY DATA EXTRACTOR\tby A.L.O. Gaenssle, 2017")
    print("\n","-"*75,"\n","-"*75,"\n")
    print("This program re-organizes text files from the spectrophotometer "
        "for analysis")
    print("\nThe program has been written to:"
        "\n- Import files from spectrophotometer "
        "(default Molecular Devices but variable)"
        "\n- Export files suitable for programs such as Stata or Origin"
        "\n- Extract and re-organize data depending on user input"
        "\n- Save data in columns of:\n\t- Sample index"
        "\n\t- Time(min)\n\t- (Wavelength (nm))"
        "\n\t- Results for each multiplicate"
        "\n\t- (Wavelength and absorbance at lambda(max))")
    print("\nContact A. Lucie Gaenssle for help and adaptions "
        "(A.L.O.Gaenssle@rug.nl)")
    print("\n","-"*75)
    print("\nInformation:\n- Complete input by clicking enter"
        "\n- Navigate within and between the inputs using the arrow keys"
        "\n- Terminate the program any time by:"
        "\n\t- Closing the terminal (window)"
        "\n\t- Ctrl + C")
    print("\n","-"*75,"\n QUESTIONAIRE\n","-"*75)

# Complete questionaire
def CompleteQuestionaire():
    # Determine if input is in plate or column format 
    # (Subfunction to CompleteQuestionaire)
    def GetInputFormat():
        InputFormat = input("\nIs your data stored in plate format "
            "(single wavelength) or columns (spectra)?"
            "\n(p=plate, c=columns)\n")
        while InputFormat not in ("p", "c"):
            InputFormat = input("\nPlease enter 'p' or 'c'!"
                "\n(only the letter)\n")
        if InputFormat == "p":
            InputFormatFull = "plate"
        else:
            InputFormatFull = "columns"
        return (InputFormat, InputFormatFull)

    # Get slope direction
    # (Subfunction to GetSlopeCount)
    def GetDirection():
        SampleDirection = input("\nWhat is the direction of your time points "
            "(slope)? \n(h=horizontal, v=vertical)\n")
        while SampleDirection not in ("v", "h"):
            SampleDirection = input("\nPlease enter 'h' or 'v'!"
                "\n(only the letter)\n")
        if SampleDirection == "v":
            DirectionFull = "columns"
        else:
            DirectionFull = "rows"
        return (DirectionFull, SampleDirection)

    # Check if detault setting have been used
    # (Subfunction to CompleteQuestionaire)
    def CheckIfDefaultSettings(SampleDirection):
        if SampleDirection == "v":
            DefaultType = "short"
            (AssayArea, Lassay, Lwash, Muliplicates, NTimePoints, SlopeCount,
                TotNSamples, TypeTimePoints) = GetDefaultSettings(
                DefaultType, SampleDirection)
            Correct = input("The default settings (%s assay) are:"
                "\n\n- %d samples, each %d time(s)"
                "\n- Assay wells in %s. row, wash wells in %s. row "
                "(f=first, l=last, a=absent)"
                "\n- %d time points taken at min %s"
                "\n- Your total assay area is %s"
                "\n\nDoes your experiment have these settings?"
                "\n(y=yes, n=no)\n"
                % (DefaultType, TotNSamples/Muliplicates,
                Muliplicates, Lassay, Lwash, NTimePoints,
                TypeTimePoints, AssayArea))
            while Correct not in ("y", "n"):
                Correct = input("\nPlease enter 'y' or 'n'!\n")
            if Correct == "n":
                DefaultType = "long"
                (AssayArea, Lassay, Lwash, Muliplicates, NTimePoints,
                    SlopeCount, TotNSamples, TypeTimePoints) = \
                    GetDefaultSettings(DefaultType, SampleDirection)
                Correct = input("The default settings (%s assay) are:"
                            "\n\n- %d samples, each %d time(s)"
                            "\n- Assay wells in %s. row, wash wells in %s."
                            "row\n  (f=first, l=last, a=absent, "
                            "e=end of first columns)"
                            "\n- %d time points taken at min %s"
                            "\n- Your total assay area is %s"
                            "\n\nDoes your experiment have these settings?"
                            "\n(y=yes, n=no)\n" 
                            % (DefaultType, TotNSamples/Muliplicates, 
                            Muliplicates, Lassay, Lwash, NTimePoints,
                            TypeTimePoints, AssayArea))
        else:
            DefaultType = "normal"
            (AssayArea, Lassay, Lwash, Muliplicates, NTimePoints,
                SlopeCount, TotNSamples, TypeTimePoints) = \
                GetDefaultSettings(DefaultType, SampleDirection)
            Correct = input("The default settings are:"
                        "\n\n- %d samples, each %d time(s)"
                        "\n- Assay wells in %s. column, "
                        "wash wells in %s.column "
                        "(f=first, l=last, a=absent)"
                        "\n- %d time points taken at min %s"
                        "\n- Your total assay area is %s"
                        "\n\nDoes your experiment have these settings?"
                        "\n(y=yes, n=no)\n"
                        % (TotNSamples/Muliplicates, Muliplicates,
                        Lassay, Lwash, NTimePoints, TypeTimePoints,
                        AssayArea))
        while Correct not in ("y", "n"):
            Correct = input("\nPlease enter 'y' or 'n'!\n")
        if Correct == "y":
            Default = True      
        else:
            print("\nSee manual, if you want to modiy the default settings"
                "\n\nThe questionaire will be conducted") 
            Default = False
        return (Default, DefaultType)

    # Determine location of assay and wash wells
    # (Subfunction to GetSlopeCount)
    def GetLocationOfExtraWells():
        Lassay = 0
        Lwash = 0
        while Lassay == Lwash:
            Lassay = input("\nWhere are your ASSAY solutions located?"
                "\n(f=first row/column, l=last row/column, "
                "e=end of first row/column, a=absent\n")
            while Lassay not in ("f", "l", "e", "a"):
                Lassay = input("\nPlease enter 'f', 'l', 'e', or 'a'\n")
            Lwash = input("\nWhere are your WASH solutions located?"
                "\n(f=first row/column, l=last row/column, "
                "e=end of first row/column, a=absent\n")
            while Lwash not in ("f", "l", "e", "a"):
                Lwash = input("\nPlease enter 'f', 'l', 'e', or 'a'\n")
            if Lassay == Lwash:
                print("\nAssays and wash solutions cannot be "
                    "located in the same wells!")
        SlopeCount = 0
        if Lassay in ("f", "l", "e"):
            SlopeCount += 1
        if Lwash in ("f", "l", "e"):
            SlopeCount += 1
        return (Lassay, Lwash, SlopeCount)

    # Get number of time points
    # (Subfunction to GetSlopeCount)
    def GetSlope(SampleDirection, SlopeCount):
        Correct = False
        while Correct == False:
            try:
                if SampleDirection == "v":
                    NTimePoints = int(input(
                        "\nEnter your number of time points"
                        "\n(between 1 and 16, usually 6 or 14)\n"))
                else:
                    NTimePoints = int(input(
                        "\nEnter your number of time points"
                        "\n(between 1 and 12, usually 10)\n"))
            except ValueError:
                print("\nPlease enter a number!")
            else:
                SlopeCount = SlopeCount + NTimePoints
                Correct = True
        return (NTimePoints, SlopeCount)

    # Get total number of wells/sample and check if within allowed range
    # (Subfunction to Questionaire)
    def GetSlopeCount():
        Correct = False
        while Correct == False:
            DirectionFull, SampleDirection = GetDirection()
            Lassay, Lwash, SlopeCount = GetLocationOfExtraWells()
            NTimePoints, SlopeCount = GetSlope(SampleDirection, SlopeCount)
            if SampleDirection == "v" and SlopeCount > 16:
                print("\nYour wells/sample (%d) exceed the "
                    "allowed number of 16!\n(%d time points +%d extra wells)"
                    % (SlopeCount, NTimePoints, (SlopeCount - NTimePoints)))
            elif SampleDirection == "h" and SlopeCount > 12:
                print("\nYour wells/sample (%d) exceed the "
                    "allowed number of 12!\n(%d time points +%d extra wells)"
                    % (SlopeCount, NTimePoints, (SlopeCount - NTimePoints)))
            else:
                Correct = True
                break
        return (DirectionFull, Lassay, Lwash, NTimePoints, SampleDirection,
            SlopeCount)
            
    # Get number of multiplicates
    # (Subfunction to GetSampleNumber)
    def GetMultiplicates():
        Muliplicates = 0
        while Muliplicates == 0:
            try:
                Muliplicates = int(input("\nEnter the number of identical "
                    "samples (multiplicates)\nIdentical samples are assumed "
                    "to be next to on another\n(e.g. 2=duplicates)\n"))     
            except ValueError:
                print("\nThis is not a number!")
                continue
            else:
                break
        return (Muliplicates)

    # Set the number of samples
    # (Subfunction to Questionaire)
    def GetSampleNumber(SampleDirection):
        Muliplicates = GetMultiplicates()
        NSamples= 0
        while NSamples == 0:
            try:
                NSamples = int(input("\nEnter the number of individual "
                    "samples\n(e.g 4)\n"))      
            except ValueError:
                print("\nThis is not a number!")
                continue
            else:
                TotNSamples = NSamples*Muliplicates
                if SampleDirection == "v" and not 1 <= TotNSamples <= 12:
                    print("\nYour total number of samples (%d), "
                        "samples*multiplicates (%d*%d),"
                        "\n exeeds the maximal column number of 12!"
                        % (TotNSamples, NSamples, Muliplicates))
                    Muliplicates = GetMultiplicates()
                    NSamples = 0
                elif SampleDirection == "h" and not 1 <= TotNSamples <= 8:
                    print("\nYour total number of samples (%d), "
                        "samples*multiplicates (%d*%d),"
                        "\n exeeds the maximal row number of 8!"
                        % (TotNSamples, NSamples, Muliplicates))
                    Muliplicates = GetMultiplicates()
                    NSamples = 0
                else:
                    break
        return (Muliplicates, NSamples, TotNSamples)

    # Get sample area on plate
    #(Subfunction to Questionaire)
    def GetAssayArea(SampleDirection, SlopeCount, TotNSamples):
        AssayArea = "A1-H12"
        Correct = False
        AreaSize = 96
        while Correct == False:
            try:
                StartWell, EndWell = AssayArea.split('-')
                StartRow = ord(StartWell[0])
                StartColumn = int(StartWell[1:])
                EndRow = ord(EndWell[0])
                EndColumn = int(EndWell[1:])
                NRows = EndRow-StartRow+1
                NColumns = EndColumn-StartColumn+1
            except ValueError:
                AssayArea = input("\nThis is not a valid format!"
                    "\nWhat is the plate range of your experiment?"
                    "\n(96 well plates, e.g. A1-H6)\n")
                if (" ") in AssayArea:
                    AssayArea = input("\nWrong format! "
                        "Please do not include spaces!"
                        "\nWhat is the plate range of your experiment?"
                        "\n(e.g. A1-H6)\n")
            else:
                AreaSize = NRows*NColumns
                if not 65 <= StartRow <= 72 or not 65 <= EndRow <= 72:
                    AssayArea = input("\nYour start row (%s) and/or end row "
                        "(%s) is not within the allowed range!"
                        "\nPlease enter another assay area\n(between A1-H12)\n"
                        % (chr(StartRow), chr(EndRow)))
                elif not 1 <= AreaSize <= 96:
                    AssayArea = input("\nYour assay area (%d) is not within "
                        "the allowed range of 96!\nPlease enter another one\n"
                        % AreaSize)
                elif NColumns > 12:
                    AssayArea = input("\nYour number of columns (%d) is not "
                        "within the allowed range of 12!"
                        "\nPlease enter another assay area\n(between A1-H12)\n"
                        % NColumns)
                elif NRows > 8:
                    AssayArea = input("\nYour number of rows (%d) is not "
                        "within the allowed range of 8!"
                        "\nPlease enter another assay area\n(between A1-H12)\n"
                        % NRows)
                elif TotNSamples*SlopeCount < AreaSize:
                    AssayArea = input("\nPlease enter your assay area "
                        "(inculding analysis, assay and wash wells)"
                        "\nYour samples (%d) and wells/sample (%d) do not "
                        "cover a whole plate\n(between A1-H12)\n"
                        % (TotNSamples, SlopeCount))
                else:
                    Correct = True
                    break
        if SampleDirection == "v" and SlopeCount > 8:
            NColumns = NColumns/2
            NRows = NRows*2     
        return (AssayArea, AreaSize, EndWell, NColumns, NRows, StartWell)

    # Go through questionaire
    # (Subfunction to CompleteQuestionaire)
    def Questionaire(InputFormat, InputFormatFull):
        Confirmation = False
        Correct = "n"
        while Correct == "n":
            while Confirmation == False:
                repetition = 0              
                (DirectionFull, Lassay, Lwash, NTimePoints, SampleDirection,
                    SlopeCount) = GetSlopeCount()
                Muliplicates, NSamples, TotNSamples =  \
                    GetSampleNumber(SampleDirection)
                AssayArea, AreaSize, EndWell, NColumns, NRows, StartWell = \
                    GetAssayArea(SampleDirection, SlopeCount, TotNSamples)
                while TotNSamples not in (NRows, NColumns) and repetition <= 1:
                    if SampleDirection == "v":
                        print("\nYour number of samples (%d) is not equal "
                            "to your number of columns (%d)!"
                            % (TotNSamples, NColumns))
                    else:
                        print("\nYour number of samples (%d) is not equal "
                            "to your number of rows (%d)!"
                            % (TotNSamples, NRows))
                    Muliplicates, NSamples, TotNSamples = \
                        GetSampleNumber(SampleDirection)
                    if TotNSamples in (NRows, NColumns):
                        break
                    (AssayArea, AreaSize, EndWell, NColumns, NRows,
                        StartWell) = GetAssayArea(SampleDirection,
                            SlopeCount, TotNSamples)
                    repetition += 1
                while SlopeCount not in (NRows, NColumns) and repetition <= 1:
                    if SampleDirection == "v":
                        print("\nYour number of wells/sample (%d) is not "
                        "equal to your number of rows (%d)!"
                        % (SlopeCount, NRows))
                    else:
                        print("\nYour number of wells/sample (%d) is not "
                            "equal to your number of columns (%d)!"
                            % (SlopeCount, NColumns))
                    (DirectionFull, Lassay, Lwash, NTimePoints,
                        SampleDirection, SlopeCount) = GetSlopeCount()
                    if SlopeCount in (NRows, NColumns):
                        break
                    (AssayArea, AreaSize, EndWell, NColumns, NRows,
                        StartWell) = GetAssayArea(SampleDirection,
                        SlopeCount, TotNSamples)
                    repetition += 1
                if (SampleDirection == "v" and TotNSamples == NColumns
                    and SlopeCount == NRows):
                    Confirmation = True
                    break
                elif (SampleDirection == "h" and TotNSamples == NRows
                    and SlopeCount == NColumns):
                    Confirmation = True
                    break
                else:
                    print("\nThere is something not correct with your input"
                        "\n(the questionaire will thus be repeated)\n")
                    print("\n","-"*20)
            print("\n","-"*20)
            Correct = input("Summary:"
                "\n\nYour input file is stored in %s format"
                "\nYour sample number is %d*%d"
                "\nYou have %d time points +%d extra wells/sample in %s"
                "\nYour total assay area is %s"
                "\n\nIs this correct?\n(y=yes, n=no)\n"
                % (InputFormatFull, NSamples, Muliplicates,
                NTimePoints, (SlopeCount-NTimePoints),
                DirectionFull, AssayArea))
            while Correct not in ("y", "n"):
                Correct = input("\nPlease enter 'y' or 'n'!"
                    "\n(only the letter)\n")
            if Correct == "n":
                Confirmation = False
                InputFormat, InputFormatFull = GetInputFormat()
        return (AssayArea, InputFormat, Lassay, Lwash, Muliplicates,
            NTimePoints, SampleDirection, SlopeCount, TotNSamples)

    # Get type (min) of time points
    # (Subfunction to CompleteQuestionaire)
    def GetTypeTimePoints(NTimePoints):
        Correct = "n"
        Default = True
        Repetition = 0
        Restart = "n"
        while Correct != "y":
            if Default == True and NTimePoints in (6, 10, 14):
                if NTimePoints == 6:
                    TypeTimePoints = [1, 2, 3, 5, 7, 10]
                elif NTimePoints == 10:
                    TypeTimePoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
                else:
                    TypeTimePoints = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
                        15, 20, 25, 30]
            else:
                try:
                    InputString = input("\nEnter your time points in min, "
                        "separated by a space\n(e.g. 1 2 3.5 4 5.5 15)\n")
                    TypeTimePoints = InputString.split(" ")
                    for i in TypeTimePoints:
                        TypeTimePoints = [float(x) for x in TypeTimePoints]
                except ValueError:
                    print("\nPlease enter a series of numbers separated "
                        "by a single space each!")
            if NTimePoints != len(TypeTimePoints):
                print("\nYour number of time points are not equal to number"
                    "entered earlier!")
            else:
                Correct = input("\nSamples were taken at the follwing minutes:"
                    "\n%s\nIs this correct?\n(y=yes, n=no)\n" % TypeTimePoints)
                while Correct not in ("y", "n"):
                    Correct = input("\nPlease enter 'y' or 'n'!\n")
                if Correct == "n":
                    Default = False
                    if Repetition >= 1:
                        Restart = input("\nDo you want to restart the "
                            "questionaire?\n(y=yes, n=no)\n")
                        while Restart not in ("y", "n"):
                            Restart = input("\nPlease enter 'y' or 'n'!\n")
                        if Restart == "y":
                            Correct = "y"
            Repetition += 1
        return(Restart, TypeTimePoints)

    # Start of CompleteQuestionaire script
    InputFormat, InputFormatFull = GetInputFormat()
    DirectionFull, SampleDirection = GetDirection()
    Default, DefaultType = CheckIfDefaultSettings(SampleDirection)
    if Default == True:
        (AssayArea, Lassay, Lwash, Muliplicates, NTimePoints, SlopeCount,
            TotNSamples, TypeTimePoints) = GetDefaultSettings(DefaultType,
            SampleDirection)
    else:
        (AssayArea, InputFormat, Lassay, Lwash, Muliplicates,
            NTimePoints, SampleDirection, SlopeCount, TotNSamples) = \
            Questionaire(InputFormat, InputFormatFull)
        Restart, TypeTimePoints = GetTypeTimePoints(NTimePoints)
        while Restart == "y":
            (AssayArea, InputFormat, Lassay, Lwash, Muliplicates,
                NTimePoints, SampleDirection, SlopeCount, TotNSamples) = \
                Questionaire(InputFormat, InputFormatFull)
            Restart, TypeTimePoints = GetTypeTimePoints(NTimePoints)
    return (AssayArea, Default, DirectionFull, InputFormat, Lassay, Lwash,
        Muliplicates, NTimePoints, SampleDirection, SlopeCount, TotNSamples,
        TypeTimePoints)

# Get file name and import it
def GetInputFile(InputFormat):
    # Get file name
    # (Subfunction to GetInputFile)
    def GetFileName(DirectoryName):
        InputPath = input("\nEnter your file name:"
            "\n- If file and python script in the same folder: e.g. Test.txt"
            "\n- If file in subfolder of folder with python script: e.g. "
            "IodineAssay\Test.txt\n- Otherwise enter full path: e.g. "
            "X:\Experiments\IodineAssay\Test.txt"
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

    # Check which files should be created
    def GetWantedFiles(InputFormat):
        if InputFormat == "c": 
            WantedFiles = 0
            print("\nWhich files do you want to create?"
                "\nChoose one of these options (enter the number):"
                "\n1 - only spectra"
                "\n2 - only shift (wavelength and absorbance at lambda(max))"
                "\n3 - both spectra and shift (separate files)"
                "\n4 - nothing (quit program)")
            while WantedFiles not in (1, 2, 3, 4):
                try:
                    WantedFiles = int(input())
                    if WantedFiles not in (1, 2, 3, 4):
                        print("\nPlease enter a number between 1 and 4!")
                except ValueError:
                    print("\nThis is not a number!"
                        "\nPlease enter a number between 1 and 4!")
            if WantedFiles == 4:
                print("\nThe program will now be terminated")
                quit()
        else:
            WantedFiles = 1
        return(WantedFiles)

    # Start of GetInputFile script
    DirectoryName, ScriptName = os.path.split(os.path.abspath(__file__))
    os.chdir(DirectoryName)
    InputPath = GetFileName(DirectoryName)
    InputData = GetFile(InputPath)
    WantedFiles = GetWantedFiles(InputFormat)
    return(DirectoryName, InputData, InputPath, WantedFiles)

# Get the number of experiments and the index of the last line of data
def GetNExperimentsAndLastLineIndex(Default_AfterDataText,
    Default_EmptyLinesBetweenDataAndAfterText, InputData, InputFormat):
    Correct = False
    Count = 0
    NPlates = 0
    PlateIndex = 0  
    if any(Default_AfterDataText == Lines[0] for Lines in InputData) == False:
        PresenceEnd = False
        while Correct == False:
            try:
                if InputFormat == "p":
                    LastLineIndex = (int(input("\nThe endline '%s' is missing "
                        "in your file!\nEnter the line (row) index of the "
                        "wells H1-12 of your input plate"
                        "\n(if you have no data in row H, enter "
                        "the line index where the data would be)"
                        "\n(find index: open input file with "
                        "Notpad, Tab 'View'>'Status Bar'>'Ln')"
                        "\n(else see manual to modify the default end line)"
                        "\n(most likely 11 for the first plate)\n"
                        % Default_AfterDataText)) - 1)
                else:
                    LastLineIndex = (int(input("\nThe endline '%s' is missing "
                        "in your file!\nEnter the line (row) index containing "
                        "the last data of your input plate"
                        "\n(find index: open input file with "
                        "Notpad, Tab 'View'>'Status Bar'>'Ln')"
                        "\n(else see manual to modify the default end line)"
                        "\n(most likely 154 for the first plate)\n"
                        % Default_AfterDataText)) - 1)      
            except ValueError:
                print("\nPlease enter a number!")
            else:
                NPlates = 1
                PlateIndex = 1
                break
    else:
        PresenceEnd = True
        for Lines in InputData:
            if Lines[0] == Default_AfterDataText:
                NPlates += 1
        if NPlates > 1:
            while PlateIndex == 0:
                try:
                    PlateIndex = int(input("\nYou have %s plates in your "
                        "file! Which one should be converted?"
                        "\n(insert a number (e.g. 2), only one at a time can "
                        "be converted)\n" % NPlates))
                except ValueError:
                    print("\nThis is not a number!")
                    continue
                else:
                    if PlateIndex > NPlates:
                        print("\nYour input number (%s) is not within your "
                            "number of plates (%s)!")
                    else:
                        break
        else:
            PlateIndex = 1
        for LastLineIndex in range(len(InputData)):
            if InputData[LastLineIndex][0] == Default_AfterDataText:
                Count += 1
                if Count == PlateIndex:
                    LastLineIndex -= \
                        Default_EmptyLinesBetweenDataAndAfterText + 1
                    break
    return (LastLineIndex, NPlates, PlateIndex, PresenceEnd)

# Check and get column and row indices of wavelength and first data point
def GetLocationIndices(AssayArea, Default_BeforeDataText,
    Default_FirstDataColumnIndex, Default_WavelengthColumnIndex, InputData,
    InputFormat, LastLineIndex, PlateIndex, PresenceEnd, SampleDirection):
    # Check for presence and requirement of label 'Wavelength'
    # (Subfunction to GetLocationIndices)
    def CheckPresenceWavelength(Default_BeforeDataText, InputData, InputFormat,
        PresenceEnd):
        Option = 0
        AskForFirstLineIndex = False
        if (any(Default_BeforeDataText == Lines[0] for Lines in InputData) ==
            False):
            PresenceWavelength = False
            if InputFormat == "c":
                print("\nYour file does not contain a '%s' label!"
                    "\nChoose one of these options (enter the number):"
                    "\n1 - Change format from column to plate "
                    "(single wavelength)\n2 - Enter the index of the "
                    "first line (row) containing the data"
                    "\n3 - quit program (see manaul to modify default "
                    "first line)" % Default_BeforeDataText)
                while Option not in (1, 2, 3):
                    try:
                        Option = int(input())
                        if Option not in (1, 2, 3):
                            print("\nPlease enter a number between 1 and 3!")
                    except ValueError:
                        print("\nThis is not a number!\nPlease enter a number "
                            "between 1 and 3!")
                if Option == 1:
                    InputFormat = "p"
                elif Option == 2:
                    AskForFirstLineIndex = True
                else:
                    print("\nThe program will now be terminated")
                    quit()
        else:
            PresenceWavelength = True
            if InputFormat == "p":
                Confirmation = input("\nYour input file seems to be in a "
                    "column format (spectrum)!"
                    "\nDo you want to change the format from "
                    "'plate' to 'columns'?\n(y=yes, n=no)\n")
                while Confirmation not in ("y", "n"):
                    Confirmation = input("\nPlease enter 'y' or 'n'!\n")
                if Confirmation == "y":
                    InputFormat = "c"
                else:
                    print("\nThe file will be imported in a plate format "
                        "(there might be some problems)"
                        "\nCheck your output file afterwards")
        return(AskForFirstLineIndex, PresenceWavelength)

    # Get index of first line (Subfunction to GetLocationIndices)
    def GetFirstLineIndex(AskForFirstLineIndex, Default_BeforeDataText,
        InputData, InputFormat, LastLineIndex, PlateIndex, PresenceEnd,
        PresenceWavelength):
        Correct = False
        PlateCount = 0
        if InputFormat == "p":
            FirstLineIndex = LastLineIndex - 7
        else:
            if PresenceWavelength == True:
                for Line in range(len(InputData)):
                    if InputData[Line][0] == Default_BeforeDataText:
                        PlateCount += 1
                        if PlateCount == PlateIndex:
                            FirstLineIndex = Line + 1
                            break
            elif AskForFirstLineIndex == True:
                while Correct == False:
                    try:
                        FirstLineIndex = (int(input("\nEnter the line (row) "
                            "index containing the first data of your single "
                            "input plate"
                            "\n(See manaul to change default column)"
                            "\n(most likely 3 or 4 for plate 1)\n")) -1)
                    except ValueError:
                        print("\nPlease enter a number!")
                    else:
                        break
            else:
                FirstLineIndex = 3
        return(FirstLineIndex)

    # Check if wavelengths are located in the first column
    # (Subfunction to GetLocationIndices)
    def GetWavelengthColumnIndex(Default_WavelengthColumnIndex, FirstLineIndex,
        InputData, InputFormat, LastLineIndex):
        Correct = False
        Count = 0
        WavelengthColumnIndex = Default_WavelengthColumnIndex - 1
        if InputFormat == "c":
            while Correct == False:
                try:
                    if (all(float(Lines[WavelengthColumnIndex])
                        in range(200,800) for Lines in
                        InputData[FirstLineIndex:(LastLineIndex+1)]) == True):
                        break
                    else:
                        WavelengthColumnIndex = (int(input(
                            "\nYour wavelengths don't seem to be in "
                            "the first column!"
                            "\n(range contains data not in range 200-800)"
                            "\n\nEnter the column index containing the "
                            "wavelength"
                            "\n(See manaul to change default column)"
                            "\n(columns are separated by spaces)\n")) - 1)
                        if (WavelengthColumnIndex not in
                            range(len(InputData[FirstLineIndex]))):
                            WavelengthColumnIndex = (int(input(
                                "\nThis is not a valid column number!"
                                "\n(columns are separated by spaces)\n")) -1)
                except ValueError:
                    WavelengthColumnIndex = (int(input(
                        "\nYour wavelengths don't seem to be in the "
                        "first column!"
                        "\n(range contains not only numbers)"
                        "\n\nEnter the column index containing the wavelength"
                        "\n(See manaul to change default column)"
                        "\n(columns are separated by spaces)\n")) -1)
                Count += 1
                if Count > 1:
                    QuitProgram = input("\nPlease check your input file!"
                        "\nDo you want to quit the program?\n(y=yes, n=no)\n")
                    while QuitProgram not in ("y", "n"):
                        QuitProgram = input("\nPlease enter 'y' or 'n'!\n")
                    if QuitProgram == "y":
                        quit()
        return(WavelengthColumnIndex)

    # Check if location of first data point is correct
    # (Subfunction to GetLocationIndices)
    def GetFirstDataColumnIndex(AssayArea, Default_FirstDataColumnIndex,
        FirstLineIndex, InputData, InputFormat,
        LastLineIndex, SampleDirection):
        Correct = False
        Count = 0
        FirstDataColumnIndex = Default_FirstDataColumnIndex - 1
        StartWell, EndWell = AssayArea.split('-')
        StartRow = ord(StartWell[0]) - 65
        StartColumn = int(StartWell[1:]) -1
        FirstTestLineIndex = FirstLineIndex
        LastTestLineIndex = LastLineIndex
        while Correct == False:
            if InputFormat == "p":
                FirstResultsColumnIndex = FirstDataColumnIndex + StartColumn
                if SampleDirection == "h":
                    FirstResultsColumnIndex += 1
                else:
                    FirstTestLineIndex += 1
                    LastTestLineIndex -+ 1
            else:           
                FirstResultsColumnIndex = (FirstDataColumnIndex + StartColumn +
                    StartRow*12 + 1)
                if SampleDirection == "v":
                    FirstResultsColumnIndex += 12
            try:
                if (all(0 <= float(Lines[FirstResultsColumnIndex]) <= 5
                    for Lines in 
                    InputData[FirstTestLineIndex:(LastTestLineIndex)])
                    == True):
                    break
                else:
                    FirstDataColumnIndex = (int(input(
                        "\nYour first data column does not seem "
                        "to be in the default column (=3)!"
                        "\n(range contains data not in range 0-5)"
                        "\n\nEnter the column index containing "
                        "the spectrum of well A1"
                        "\n(if you have no data in A1, enter the "
                        "column where this data would be)"
                        "\n(See manual to change default column)"
                        "\n(columns are separated by spaces)"
                        "\n(most likely 3)\n")) - 1)
                    if (FirstResultsColumnIndex not in 
                        range(len(InputData[FirstLineIndex]))):
                        FirstDataColumnIndex = (int(input(
                            "\nThis is not a valid column number!"
                            "\n(columns are separated by spaces)\n")) - 1)
            except ValueError:
                FirstDataColumnIndex = (int(input(
                    "\nYour first data column does not seem "
                    "to be in the default column (=3)!"
                    "\n(range contains not only numbers)"
                    "\n\nEnter the column index containing "
                    "the spectrum of well A1"
                    "\n(if you have no data in A1, enter the "
                    "column where this data would be)"
                    "\n(See manual to change default column)"
                    "\n(columns are separated by spaces)"
                    "\n(most likely 3)\n")) - 1)
            Count += 1
            if Count > 1:
                QuitProgram = input("\nPlease check your input file!"
                    "\nDo you want to quit the program?\n(y=yes, n=no)\n")
                while QuitProgram not in ("y", "n"):
                    QuitProgram = input("\nPlease enter 'y' or 'n'!\n")
                if QuitProgram == "y":
                    quit()
        return(FirstDataColumnIndex)

    # Start of GetLocationIndices script
    AskForFirstLineIndex, PresenceWavelength = CheckPresenceWavelength(
        Default_BeforeDataText, InputData, InputFormat, PresenceEnd)
    FirstLineIndex = GetFirstLineIndex(AskForFirstLineIndex,
        Default_BeforeDataText, InputData, InputFormat, LastLineIndex,
        PlateIndex, PresenceEnd, PresenceWavelength)
    WavelengthColumnIndex = GetWavelengthColumnIndex(
        Default_WavelengthColumnIndex, FirstLineIndex, InputData, InputFormat,
        LastLineIndex)
    FirstDataColumnIndex = GetFirstDataColumnIndex(AssayArea,
        Default_FirstDataColumnIndex, FirstLineIndex, InputData, InputFormat,
        LastLineIndex, SampleDirection)
    return(FirstDataColumnIndex, FirstLineIndex, WavelengthColumnIndex)

# Extract data from input file
def GetData(AssayArea, FirstDataColumnIndex, FirstLineIndex, InputData,
    InputFormat, LastLineIndex, PlateIndex, WavelengthColumnIndex):
    # Extract wavelengths of input data
    def GetWavelengthList(InputData, InputFormat, FirstLineIndex,
        LastLineIndex, WavelengthColumnIndex):
        WavelengthList = []
        if InputFormat == "c":
            for Line in range(FirstLineIndex, LastLineIndex+1):
                try:
                    float(InputData[Line][WavelengthColumnIndex])
                    WavelengthList.append(float(InputData[Line]
                        [WavelengthColumnIndex]))
                except ValueError:
                    print("There are not only numbers in the first column!"
                        "\nPlease check your text file")
                    break
            if len(WavelengthList) == 0:
                print("There is not label above the list of wavelength!"
                    "\nSee manual to change the default label"
                    "\nElse contact Lucie Gaenssle (A.L.O.Gaenssle@rug.nl)"
                    "\n\nThe program will now be terminated")
                quit()
        return (WavelengthList)

    # Read data into lists and store in plate format
    def ReadDataToPlateFormat(InputData, InputFormat, FirstDataColumnIndex,
        FirstLineIndex, LastLineIndex):
        DataPoints = []
        CombinedData = []
        if InputFormat == "c":
            for Column in range(FirstDataColumnIndex, 
                (FirstDataColumnIndex+96)):
                for Line in range(FirstLineIndex, LastLineIndex+1):
                    try:
                        DataPoints.append(InputData[Line][Column])
                    except IndexError:
                        DataPoints.append("0")
            DataListofLists = ([DataPoints[index:(index+LastLineIndex-
                FirstLineIndex+1)] for index in 
                range(0, len(DataPoints), LastLineIndex-FirstLineIndex+1)])
            DataPlateFormat = ([DataListofLists[index:index+12] for index in
                range(0, len(DataListofLists), 12)])
        else:
            for Line in range(FirstLineIndex, LastLineIndex+1):
                for Column in range(FirstDataColumnIndex,
                    (FirstDataColumnIndex+12)):
                    try:
                        DataPoints.append(InputData[Line][Column])
                    except IndexError:
                        DataPoints.append("0")
            DataPlateFormat = ([DataPoints[index:index+12] for index in
                range(0, len(DataPoints), 12)])
        return (DataPlateFormat)
            
    # Extract total assay area
    # (Subfunction to ConvertData)
    def ExtractAssayArea(AssayArea, DataPlateFormat, InputFormat):
        Plate = []
        StartWell, EndWell = AssayArea.split('-')
        StartRow = ord(StartWell[0]) - 65
        StartColumn = int(StartWell[1:]) - 1 
        EndRow = ord(EndWell[0]) - 64
        EndColumn = int(EndWell[1:])
        for Line in DataPlateFormat[(StartRow):(EndRow)]:
            Rows = Line[(StartColumn):(EndColumn+1)]
            Plate.append(Rows)
        return (Plate)

    # Start of GetData script
    WavelengthList = GetWavelengthList(InputData, InputFormat, FirstLineIndex,
        LastLineIndex, WavelengthColumnIndex)
    DataPlateFormat = ReadDataToPlateFormat(InputData, InputFormat,
        FirstDataColumnIndex, FirstLineIndex, LastLineIndex)
    Plate = ExtractAssayArea(AssayArea, DataPlateFormat, InputFormat)
    return(Plate, WavelengthList)
        
# Convert data to be exported into output file
def ConvertData(InputFormat, Lassay, Lwash, Muliplicates, Plate,
    SampleDirection, SlopeCount, TotNSamples, TypeTimePoints, WavelengthList):
    # transpose plate to create list of lists independent of sample direction
    # (Subfunction to ConvertData)
    def ConvertPlate(Plate, SampleDirection, SlopeCount, TotNSamples):
        ConvertedPlate = []
        if SampleDirection == "v":
            for Column in range(len(Plate[0])):
                ConvertedPlate.append([Row[Column] for Row in Plate])   
            if SlopeCount > 8:
                i = 0
                while i < len(ConvertedPlate)/2:
                    ConvertedPlate[i] = (ConvertedPlate[i] + 
                        ConvertedPlate[i+TotNSamples])
                    i += 1  
                del ConvertedPlate[TotNSamples:]    
        else:
            ConvertedPlate = Plate  
        return (ConvertedPlate)

    # Extract time point area
    # (Subfunction to ConvertData)
    def ExtractTimePointArea(FinalPlate, Lassay, Lwash):
        for Row in FinalPlate:
            if  Lassay == "e" or Lwash == "e":
                del Row[int(len(Row)/2)-1]
            if Lassay == "f" or Lwash == "f":
                del Row[0]
            if Lassay == "l" or Lwash == "l":
                del Row[-1]
        return (FinalPlate)

    # Split large list in sublists for each sample
    # (Subfunction to ConvertData)
    def SubdivideList(FinalPlate, Muliplicates, TotNSamples):
        Samples = []
        x = 0
        for Slope in FinalPlate:
            while x < TotNSamples:
                List = FinalPlate[x:x+Muliplicates]
                x = x + Muliplicates
                Samples.append(List)
        return (Samples)

    # Convert list of time points to dictionary with time point labels
    # (Subfunction to ConvertData)
    def AddTimePointLabels(InputFormat, Samples, TypeTimePoints,
        WavelengthList):
        FirstDictionaryList = []
        SecondDictionaryList = []
        AllData = []
        if InputFormat == "p":
            for Assays in range(len(Samples)):
                CondensedList = list(zip(*Samples[Assays]))
                for DataPoints in range(len(CondensedList[0])):
                    CondensedDictionary = dict(zip(TypeTimePoints,
                        CondensedList))
                AllData.append(CondensedDictionary)
        else:
            for Assays in range(len(Samples)):
                FirstList = list(zip(*Samples[Assays]))
                for TimePoints in range(len(TypeTimePoints)):
                    SecondList = list(zip(*FirstList[TimePoints]))
                    FirstDictionary = dict(zip(WavelengthList, SecondList))
                    FirstDictionaryList.append(FirstDictionary)
                SecondDictionary = dict(zip(TypeTimePoints,
                    FirstDictionaryList))
                FirstDictionaryList.clear() 
                AllData.append(SecondDictionary)
        return (AllData)

    # Create labels for the multiplicates in the output file
    # (Subfunction to ConvertData)
    def CreateLabelList(Muliplicates):
        LabelList = []
        LabelListShift = []
        Count = 0
        for Count in range(1, Muliplicates+1):
            Label = "Exp" + str(Count)
            LabelShiftWL = "E" + str(Count) + "-WL"
            LabelShiftAb = "E" + str(Count) + "-Ab"
            Count += 1
            LabelList.append(Label)
            LabelListShift.append(LabelShiftWL)
            LabelListShift.append(LabelShiftAb)
        return (LabelList, LabelListShift)

    # Start of ConvertData script
    ConvertedPlate = ConvertPlate(Plate, SampleDirection, SlopeCount,
        TotNSamples)
    FinalPlate = ExtractTimePointArea(ConvertedPlate, Lassay, Lwash)
    Samples = SubdivideList(FinalPlate, Muliplicates, TotNSamples)
    AllData = AddTimePointLabels(InputFormat, Samples, TypeTimePoints,
        WavelengthList)
    LabelList, LabelListShift = CreateLabelList(Muliplicates)
    return (AllData, LabelList, LabelListShift)

# Find max values and create shift
# (Subfunction to ExportData and AppendData)
def FindMax(AllData, Muliplicates):
    Shift = {}
    for Samples in range(len(AllData)):
        ShiftSamples = {}
        for TimePoints in AllData[Samples]:
            ShiftTimePoint = []
            for Exp in range(Muliplicates):
                ABMax, WLMax = getABandWLMax()
                for Wavelength in AllData[Samples][TimePoints]:
                    try:
                        if (float(AllData[Samples][TimePoints]
                            [Wavelength][Exp]) > float(ABMax)):
                            ABMax = (AllData[Samples][TimePoints]
                                [Wavelength][Exp])
                            WLMax = int(Wavelength)
                    except IndexError:
                        break
                ShiftTimePoint.append({WLMax:ABMax})
            ShiftSamples.update({TimePoints:ShiftTimePoint})
        Shift.update({Samples:ShiftSamples})
    PreviousExperiments = Samples + 2
    return(PreviousExperiments, Shift)

# Export data to file
def ExportData(AllData, InputFormat, InputPath, LabelList, LabelListShift,
    Muliplicates):
    # Create file of converted data
    # (Subfunction to ExportData)
    def CreateSpectraFile(AllData, InputFormat, InputPath, LabelList):
        OutputSpectraPath = InputPath.split(".")[0] + "_converted.txt"
        while os.path.isfile(OutputSpectraPath) == True:
            Replace = input("\n%s already exists! Should the file be replaced?"
                "\n(y=yes, n=no)\n" % OutputSpectraPath)
            while Replace not in ("y", "n"):
                Replace = input("\nPlease enter 'y' or 'n'!\n")
            if Replace == "y":
                break
            else:
                OutputSpectraPath = input("\nEnter a new name for the spectra "
                    "file with extention '.txt'\n(e.g. Output.txt)\n")
                while OutputSpectraPath.endswith(".txt") == False:
                    OutputSpectraPath = input("\nThis is not a correct format!"
                        "\nPlease enter a file name with extention '.txt'"
                        "\n(e.g. Output.txt)\n")
        OutputSpectraFile = open(OutputSpectraPath, "w")
        if InputFormat == "p":
            OutputSpectraFile.write("Sample\tT(min)\t")
            OutputSpectraFile.write("\t".join(map(str, LabelList)))
            for Experiments in range(len(AllData)):
                for Muliplicates in sorted(AllData[Experiments].keys()):
                    OutputSpectraFile.write("\n%s\t%s\t"
                        % (Experiments+1, Muliplicates))
                    OutputSpectraFile.write("\t".join(map(str,
                        AllData[Experiments][Muliplicates])))
        else:
            OutputSpectraFile.write("Sample\tT(min)\tWL(nm)\t")
            OutputSpectraFile.write("\t".join(map(str, LabelList)))
            for Experiments in range(len(AllData)):
                for TimePoints in sorted(AllData[Experiments].keys()):
                    for WavelengthData in sorted(AllData[Experiments]
                        [TimePoints].keys()):
                        OutputSpectraFile.write("\n%s\t%s\t%s\t"
                            % (Experiments+1, TimePoints, int(WavelengthData)))
                        OutputSpectraFile.write("\t".join(map(str,
                            AllData[Experiments][TimePoints][WavelengthData])))
        print("\nThe spectra file has been created\n(If unaltered: "
            "Same name and folder, ending on '_converted.txt')")
        Status = "completed"
        PreviousExperiments = Experiments + 2
        return (OutputSpectraFile, OutputSpectraPath,
            PreviousExperiments, Status)

    # Create file of converted data
    # (Subfunction to ExportData)
    def CreateShiftFile(AllData, InputPath, LabelListShift, Muliplicates):
        # Check if file exists and should be replaced
        # (Subfunction to CreateShiftFile)
        def CheckPresenceOfFile(InputPath):
            OutputShiftPath = InputPath.split(".")[0] + "_shift.txt"
            while os.path.isfile(OutputShiftPath) == True:
                Replace = input("\n%s already exists! "
                    "Should the file be replaced?\n(y=yes, n=no)\n"
                    % OutputShiftPath)
                while Replace not in ("y", "n"):
                    Replace = input("\nPlease enter 'y' or 'n'!\n")
                if Replace == "y":
                    break
                else:
                    OutputShiftPath = input("\nEnter a new name for the shift "
                        "file with extention '.txt'\n(e.g. Output.txt)\n")
                    while OutputShiftPath.endswith(".txt") == False:
                        OutputShiftPath = input(
                            "\nThis is not a correct format!"
                            "\nPlease enter a file name with "
                            "extention '.txt'\n(e.g. Output.txt)\n")
            return(OutputShiftPath)

        # Print to file
        # (Subfunction to CreateShiftFile)
        def PrintToFile(LabelListShift, OutputShiftPath, Shift):
            OutputShiftFile = open(OutputShiftPath, "w")
            OutputShiftFile.write("Sample\tT(min)\t")
            OutputShiftFile.write("\t".join(map(str, LabelListShift)))      
            for Samples in sorted(Shift.keys()):
                for TimePoints in sorted(Shift[Samples].keys()):
                    OutputShiftFile.write("\n%s\t%s" % (Samples+1, TimePoints))
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

        # Start of CreateShiftFile script
        OutputShiftPath = CheckPresenceOfFile(InputPath)
        PreviousExperiments, Shift = FindMax(AllData, Muliplicates)
        OutputShiftFile, Status = PrintToFile(LabelListShift,
            OutputShiftPath, Shift)
        return(OutputShiftFile, OutputShiftPath, PreviousExperiments, Shift,
            Status)

    # start of ExportData script
    OutputSpectraFile = None
    OutputShiftFile = None
    OutputSpectraPath = None
    OutputShiftPath = None  
    PreviousSpectraExperiments = 0
    PreviousShiftExperiments = 0
    if WantedFiles in (1,3):
        (OutputSpectraFile, OutputSpectraPath, PreviousSpectraExperiments,
            Status) = CreateSpectraFile(AllData, InputFormat, InputPath,
            LabelList)
    if WantedFiles in (2,3):
        (OutputShiftFile, OutputShiftPath, PreviousShiftExperiments, Shift,
            Status) = CreateShiftFile(AllData, InputPath, LabelListShift,
                Muliplicates)
    return(OutputShiftFile, OutputShiftPath, OutputSpectraFile,
        OutputSpectraPath, PreviousShiftExperiments,
        PreviousSpectraExperiments, Shift, Status)

# Append data from same input file to same output file
def AppendData(AssayArea, Default_AfterDataText, Default_BeforeDataText,
    Default_FirstDataColumnIndex, Default_EmptyLinesBetweenDataAndAfterText,
    Default_WavelengthColumnIndex, InputData, InputFormat, Lassay, Lwash,
    Muliplicates, NPlates, OutputShiftFile, OutputSpectraFile,
    PreviousShiftExperiments, PreviousSpectraExperiments, SampleDirection,
    Shift, SlopeCount, TotNSamples, TypeTimePoints, WantedFiles):
    # Append data to previous file
    # (Subfunction to AppendData)
    def AppendSpectraFile(AllData, OutputSpectraFile, PreviousExperiments):
        if InputFormat == "p":
            for Experiments in range(len(AllData)):
                for Muliplicates in sorted(AllData[Experiments].keys()):
                    OutputSpectraFile.write("\n%s\t%s\t"
                        % (Experiments+PreviousExperiments, Muliplicates))
                    OutputSpectraFile.write("\t".join(map(str,
                        AllData[Experiments][Muliplicates])))
        else:
            for Experiments in range(len(AllData)):
                for TimePoints in sorted(AllData[Experiments].keys()):
                    for WavelengthData in sorted(AllData[Experiments]
                            [TimePoints].keys()):
                        OutputSpectraFile.write("\n%s\t%s\t%s\t"
                            % (Experiments+PreviousExperiments, TimePoints,
                            int(WavelengthData)))
                        OutputSpectraFile.write("\t".join(map(str,
                            AllData[Experiments][TimePoints][WavelengthData])))
        print("\nThe data has been appended to the spectra file\n")
        Status = "completed"
        PreviousExperiments = Experiments + PreviousExperiments + 1
        return (PreviousExperiments, Status)

    # Append data to previous file
    # (Subfunction to AppendData)
    def AppendShiftFile(OutputShiftFile, PreviousExperiments, Shift):
        for Samples in sorted(Shift.keys()):
            for TimePoints in sorted(Shift[Samples].keys()):
                OutputShiftFile.write("\n%s\t%s"
                    % (Samples+PreviousExperiments, TimePoints))
                for WLMax in range(len(Shift[Samples][TimePoints])):
                    OutputShiftFile.write("\t")
                    OutputShiftFile.write("\t".join(map(str,
                        Shift[Samples][TimePoints][WLMax])))
                    OutputShiftFile.write("\t")
                    OutputShiftFile.write("\t".join(map(str,
                        Shift[Samples][TimePoints][WLMax].values())))
        print("\nThe data has been appended to the shift file\n")
        Status = "completed"
        PreviousExperiments = Samples + PreviousExperiments + 1
        return (PreviousExperiments, Status)
    
    # Start of AppendData script
    InsertedPlates = 1
    while InsertedPlates < NPlates:
        Append = input("\nYour file contains %s other plate(s), "
            "do you want to add another?\n(y=yes, n=no)\n"
            % (NPlates-InsertedPlates))
        while Append not in ("y", "n"):
            Append = input("\nPlease enter 'y' or 'n'!\n")
        if Append == "n":
            break
        else:
            LastLineIndex, NPlates, PlateIndex, PresenceEnd = \
            GetNExperimentsAndLastLineIndex(Default_AfterDataText,
                Default_EmptyLinesBetweenDataAndAfterText, InputData,
                InputFormat)
            Same = input("\nAre the settings the same as for the previous "
                "plate?\n(y=yes, n=no)\n")
            while Same not in ("y", "n"):
                Same = input("\nPlease enter 'y' or 'n'!\n")
            if Same == "n":
                (AssayArea, Default, DirectionFull, InputFormat, Lassay, Lwash,
                    Muliplicates, NTimePoints, SampleDirection, SlopeCount,
                    TotNSamples, TypeTimePoints) = CompleteQuestionaire()
            FirstDataColumnIndex, FirstLineIndex, WavelengthColumnIndex = \
                GetLocationIndices(AssayArea, Default_BeforeDataText,
                Default_FirstDataColumnIndex,
                Default_WavelengthColumnIndex, InputData, InputFormat,
                LastLineIndex, PlateIndex, PresenceEnd, SampleDirection)
            Plate, WavelengthList = GetData(AssayArea, FirstDataColumnIndex,
                FirstLineIndex, InputData, InputFormat, LastLineIndex,
                PlateIndex, WavelengthColumnIndex)
            AllData, LabelList, LabelListShift = ConvertData(InputFormat,
                Lassay, Lwash, Muliplicates, Plate, SampleDirection,
                SlopeCount, TotNSamples, TypeTimePoints, WavelengthList)
            if WantedFiles in (1,3):
                PreviousSpectraExperiments, Status = AppendSpectraFile(
                    AllData, OutputSpectraFile, PreviousSpectraExperiments)
            if WantedFiles in (2,3):
                PreviousExperiments, Shift = FindMax(AllData, Muliplicates)
                PreviousShiftExperiments, Status = AppendShiftFile(
                    OutputShiftFile, PreviousShiftExperiments, Shift)
            InsertedPlates += 1
    return (InsertedPlates)

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

# Conduct questionaire
(AssayArea, Default, DirectionFull, InputFormat, Lassay, Lwash, Muliplicates,
    NTimePoints, SampleDirection, SlopeCount, TotNSamples, TypeTimePoints) = \
    CompleteQuestionaire()

# Import file
DirectoryName, InputData, InputPath, WantedFiles = GetInputFile(InputFormat)
LastLineIndex, NPlates, PlateIndex, PresenceEnd = \
    GetNExperimentsAndLastLineIndex(Default_AfterDataText,
    Default_EmptyLinesBetweenDataAndAfterText, InputData, InputFormat)
FirstDataColumnIndex, FirstLineIndex, WavelengthColumnIndex = \
    GetLocationIndices(AssayArea, Default_BeforeDataText,
    Default_FirstDataColumnIndex, Default_WavelengthColumnIndex, InputData,
    InputFormat, LastLineIndex, PlateIndex, PresenceEnd, SampleDirection)

# Convert data
Plate, WavelengthList = GetData(AssayArea, FirstDataColumnIndex,
    FirstLineIndex, InputData, InputFormat, LastLineIndex, PlateIndex,
    WavelengthColumnIndex)
AllData, LabelList, LabelListShift = ConvertData(InputFormat, Lassay, Lwash,
    Muliplicates, Plate, SampleDirection, SlopeCount, TotNSamples,
    TypeTimePoints, WavelengthList)

# Export files
(OutputShiftFile, OutputShiftPath, OutputSpectraFile, OutputSpectraPath,
    PreviousShiftExperiments, PreviousSpectraExperiments, Shift, Status) = \
    ExportData(AllData, InputFormat, InputPath, LabelList, LabelListShift,
    Muliplicates)
InsertedPlates = AppendData(AssayArea, Default_AfterDataText,
    Default_BeforeDataText, Default_FirstDataColumnIndex,
    Default_EmptyLinesBetweenDataAndAfterText, Default_WavelengthColumnIndex,
    InputData, InputFormat, Lassay, Lwash, Muliplicates, NPlates,
    OutputShiftFile, OutputSpectraFile, PreviousShiftExperiments,
    PreviousSpectraExperiments, SampleDirection, Shift, SlopeCount,
    TotNSamples, TypeTimePoints, WantedFiles)

# Open file
if WantedFiles in (1,3):
    OutputFormat = "spectra"
    OpenFile(OutputFormat, OutputSpectraPath)
if WantedFiles in (2,3):
    OutputFormat = "shift"
    OpenFile(OutputFormat, OutputShiftPath)

print("\n","-"*75,"\n End of program\n","-"*75,"\n","-"*75)