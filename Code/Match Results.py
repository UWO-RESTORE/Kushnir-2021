from collections import defaultdict
import os
import os.path
import pandas as pd

# ------------------------------------ USER DEFINED INPUTS ------------------------------------------------------------
DIR = "V:\\"
DIR_BASE = DIR + "5x12 lvl (Buffered) - 8 to 10\\"
# ------------------------------------ OPTIONAL: USER DEFINED INPUTS --------------------------------------------------
DATA_INPUT_FILE = "Experiment_to_Match.txt"

LOGK_INPUT_FILE = "LogKs.txt"
PROGRAM_INPUT_FILE = "Program_Code.txt"
# ----------------------------------- GLOBAL VARIABLES - HARD SET -----------------------------------------------------
# Directory List
DIR_LIST = (DIR_BASE+"User Input Files\\", # 0
            DIR_BASE+"Run Files (Summary)\\",  # 1-
            DIR_BASE+"Run Files (to delete)\\",  # 2
            DIR_BASE+"Results\\", # 3
            DIR_BASE+"Results\\Data Files\\", # 4
            DIR_BASE+"Analysis\\", # 5
            DIR_BASE+"Results\\Select Run and Output Files\\" #6
            )

DIR_LIST_ANALYSIS = DIR_BASE + "Analysis\\Matching\\"

#Output files
TITLE_OF_OUTPUT_FILE = "All Results"
SUMMARY_FILE = "Python Summary F ile.txt"
FACTORIAL_FILE = 'Factorial_Coded_File.txt'
FACTORIAL_FILE2 = 'Factorial_Uncoded_File.txt'
OUTPUT_TITLES_FILE = 'Output File Names.txt'
CONDITIONS_FILE = "Conditions File.txt"
CONDITIONS_FILE_PREFIX = "With Conditions-"
# ----------------------------------- GLOBAL VARIABLES - Generated or updated during Python Run -----------------------
ALL_LOGKS = defaultdict(list) # Generated
CONDITION_LIST = [] # Generated
CONDITION_SUMMARY = defaultdict(list) # Generated
ALLSPECIES = [] # Generated & can be updated after "import species"
NUMBERS = [] # [0] is number of levels, [1] is number of species, [2] is number of factorials, Generated
SPECIES_TITLES = []
TITLES = []
# ---------------------------------- GENERIC BASIC FUNCTIONS ----------------------------------------------------------
def combine_factorial_and_conditions():
    '''
    This function takes the factorial file from the main run program, and iterates over it for the conditions (Sept 2020
    you have to make this condition file by hand). The condition file should be 1 iteration of all conditions WITH a header.
    This saves the coded and uncoded version in RESULTS annotated as "Updated".
    :return:
    '''
    condition_input_file_name = DIR_LIST[0] + "Conditions Input.txt"

# Get Header Line
    with open(condition_input_file_name, "r") as f1:
        with open(DIR_LIST[1] + "Factorial_Uncoded_File.txt", "r") as f2:
            for line in f1.read().splitlines():
                h1 = line
                break
            for line in f2.read().splitlines():
                h2 = line
                break
            header = h1+ "\t"+h2 +"\n"


# Uncoded Factorial Creation
    uncoded_combined_factorial_output_name = DIR_LIST[3] + "Updated-Factorial_Uncoded_File.txt"
    uncoded_factorial_input_file_name = DIR_LIST[1] + "Factorial_Uncoded_File.txt"

    with open(uncoded_combined_factorial_output_name, "w") as f: # The Output File
        f.write(header)
        with open(uncoded_factorial_input_file_name, "r") as f2: # Open the Factorial File
            next(f2)                                             # Skip the Header
            for l2 in f2.read().splitlines():                     # For each line in the factorial run:
                with open(condition_input_file_name, "r") as f1:  # Open the Conditions File
                    next(f1)                                        # Skip Header
                    for l1 in f1.read().splitlines():                  # the full conditions
                        f.write(l1 + "\t"+ l2 +"\n")                   # write and combine

# Coded Factorial Creation
    coded_factorial_input_file_name = DIR_LIST[1] + "Factorial_Coded_File.txt"
    coded_combined_factorial_output_name = DIR_LIST[3] + "Updated-Factorial_Coded_File.txt"

    check_combination_length()

def check_combination_length():
    '''
    To Check the length of the combined factorial to print to consule to make sure it is correct. Remember it will be
    +1 from the other checks due to a header!
    :return:
    '''
    with open(DIR_LIST[3] + "Updated-Factorial_Uncoded_File.txt") as f:
        for i, l in enumerate(f):
            pass
    print("Combined Length = ", i + 1)


def create_folder(folder_name_and_loc):
    '''
    Create a Matching Folder (named above) to store the results of matching to
    :return:
    '''
    try:
        os.makedirs(folder_name_and_loc)
    except OSError:
        if os.path.exists(folder_name_and_loc):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def load_results_file(filename):
    print("Loading Results File")
    results = pd.read_csv(DIR_LIST[4] + filename, sep = " ", header=None) #Dir list 4 is Analysis\datafiles
    results.columns = ["Result"]
    return results

def load_factorial_file(filename):
    print("Loading Factorial File")
    fact = pd.read_csv(DIR_LIST[3] + filename, sep = "\t", header=0) #Dirlist 3 is the Results folder
    fact = fact.dropna(how="all", axis=1)
    return fact

def combine_dataframes():
    results = load_results_file("Pb-Results.txt")
    fact = load_factorial_file("Updated-Factorial_Uncoded_File.txt")

    print("Combining Dataframes")
    frames = [fact, results]
    dat = pd.concat(frames, axis=1)
    return dat

def match_single(value, std, tol, pH, DIC, save_loc):


    df = combine_dataframes()

    upper = value + (std*tol)
    lower = value - (std*tol)

    if lower < 0: lower = 0

    filtered = df[(df["pH"] == pH) & (df["DIC"] == DIC) & (df["Result"] > lower) & (df["Result"] < upper)]

    std_tol_mg_L = std*tol*207.21*1000

    fname = "pH%s DIC%s Matching - %smg_L.txt" %(pH, DIC, (str(std_tol_mg_L)[:5]))

    filtered.to_csv(save_loc+fname, index=True, sep="\t")
    #print(filtered)

def iterate_match_file(tol):
    # create sub folder for the iteration, because you should only have to run this once
    folder_loc = DIR_LIST_ANALYSIS+"Tolerance = %s\\" %(tol)
    create_folder(folder_loc)

    # read file
    experiment = DIR_LIST[0]+"Experimental Data.txt"
    with open(experiment, "r") as f:
        next(f)
        for line in f.read().splitlines():
            line = line.split("\t")
            pH = int(line[0])
            DIC = int(line[1])
            Result = float(line[2])
            std = float(line[3])
            match_single(value=Result, std=std, tol=tol, pH=pH, DIC=DIC, save_loc = folder_loc)

def determine_duplicates(tol):
    folder_loc = DIR_LIST_ANALYSIS+"Tolerance = %s\\" %(tol)
    df = pd.DataFrame()

    for filename in os.listdir(folder_loc):
        if filename.endswith(".txt"):
            temp_df = pd.read_csv(folder_loc + filename, sep = "\t", header=0)
            #print(temp_df)
            df = pd.concat([df, temp_df], axis=0)
        else:
            continue

    #print(df)
    dup_table = df.pivot_table(index=['Hydrocerrusite', 'Cerrusite', '#Pb(CO3)2-2', '#PbCO3','#PbOH+'], aggfunc='size')

    # Have to Save and Reload to change the Match Column Name
    fname_duptable = "Dup Table Tol=%s.txt" %tol
    fname_match9 = "Tol=%s for Match 9.txt" %tol
    dup_table.to_csv(DIR_LIST_ANALYSIS + fname_duptable, index=True, sep="\t")
    # read and change column name
    dup_table = pd.read_csv(DIR_LIST_ANALYSIS + fname_duptable, sep="\t", header=0)
    dup_table.rename(columns={"0": 'Match'}, inplace=True)
    # resave with new column name
    dup_table.to_csv(DIR_LIST_ANALYSIS + fname_duptable, index=True, sep="\t")

    # Save Match 9 Only
    dup_table9 = dup_table.query("Match >= 9")
    dup_table9.to_csv(DIR_LIST_ANALYSIS + fname_match9, index=True, sep="\t")

    DIR_LIST_ANALYSIS_ADD = DIR_LIST_ANALYSIS + "Match 8 Through Match 5\\"
    create_folder(DIR_LIST_ANALYSIS_ADD)
    # Save Match 8 Only
    fname_match8 = "Tol=%s for Match 8.txt" % tol
    dup_table8 = dup_table.query("Match == 8")
    dup_table8.to_csv(DIR_LIST_ANALYSIS_ADD + fname_match8, index=True, sep="\t")

    # Save Match 7 Only
    fname_match7 = "Tol=%s for Match 7.txt" % tol
    dup_table7 = dup_table.query("Match == 7")
    dup_table7.to_csv(DIR_LIST_ANALYSIS_ADD + fname_match7, index=True, sep="\t")

    # Save Match 6 Only
    fname_match6 = "Tol=%s for Match 6.txt" % tol
    dup_table6 = dup_table.query("Match == 6")
    dup_table6.to_csv(DIR_LIST_ANALYSIS_ADD + fname_match6, index=True, sep="\t")

    # Save Match 5 Only
    fname_match5 = "Tol=%s for Match 5.txt" % tol
    dup_table5 = dup_table.query("Match == 5")
    dup_table5.to_csv(DIR_LIST_ANALYSIS_ADD + fname_match5, index=True, sep="\t")


###################################################### Run Order
#combine_factorial_and_conditions()
#create_folder(DIR_LIST_ANALYSIS)
iterate_match_file(tol=1)
determine_duplicates(tol=1)
iterate_match_file(tol=2)
determine_duplicates(tol=2)
iterate_match_file(tol=3)
determine_duplicates(tol=3)
iterate_match_file(tol=4)
determine_duplicates(tol=4)
iterate_match_file(tol=5)
determine_duplicates(tol=5)
iterate_match_file(tol=6)
determine_duplicates(tol=6)
iterate_match_file(tol=7)
determine_duplicates(tol=7)
iterate_match_file(tol=8)
determine_duplicates(tol=8)
iterate_match_file(tol=9)
determine_duplicates(tol=9)
iterate_match_file(tol=10)
determine_duplicates(tol=10)

