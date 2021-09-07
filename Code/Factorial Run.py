__author__ = 'Lynx'

import shutil
import ctypes  # An included library with Python install.
from collections import defaultdict
import subprocess
import sys
import time
from datetime import datetime
import os
import os.path
from functools import partial
import pandas as pd

from os import listdir
import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import OldScalarFormatter, ScalarFormatter
import math as m
from matplotlib.ticker import FormatStrFormatter


# ------------------------------------ USER DEFINED INPUTS ------------------------------------------------------------
DIR = "V:\\"
DIR_BASE = DIR + "5x12 lvl (Buffered) - 8 to 10\\"
# ------------------------------------ OPTIONAL: USER DEFINED INPUTS --------------------------------------------------
TITLE_IN_FILE = "Python Matching Factorial - For ACROS B"    # can change the title in the program run files
SLEEP = 0.1 # Delay in opening the files in run program files #0.05 = comfortable working on computer for minor processing work (25% CPU usage)
# User Input File Names
LOGK_INPUT_FILE = "LogKs.txt"
PROGRAM_INPUT_FILE = "Program_Code.txt"
# ----------------------------------- GLOBAL VARIABLES - HARD SET -----------------------------------------------------
# System files etc. linked through the code
DIR_SYSTEM_FILES = DIR + "System Files\\"
PROGRAM_CODE_EXE = "phreeqc_no_u_g.exe"
DATABASE_FILE = "minteq.v4.dat"
# Directory List
DIR_LIST = (DIR_BASE+"User Input Files\\", # 0
            DIR_BASE+"Run Files (Summary)\\",  # 1-
            DIR_BASE+"Run Files (to delete)\\",  # 2
            DIR_BASE+"Results\\", # 3
            DIR_BASE+"Results\\Data Files\\", # 4
            DIR_BASE+"Analysis\\", # 5
            DIR_BASE+"Results\\Select Run and Output Files\\" #6
            )

DIR_LIST_ANALYSIS = (
        "By Condition\\Data\\", # 0
        "By Condition\\Graphs\\", # 1
        "By Species\\Data\\", # 2
        "By Species\\Graphs\\", # 3
        "Interaction\\Data\\", # 4
        "Interaction\\Graphs\\", # 5
            )
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
def get_tab_file_multi_lines(text_file_name):
    with open(text_file_name) as f:
        return [line.split('\t') for line in f.read().splitlines()]

def Mbox(title, text, style):
    ctypes.windll.user32.MessageBoxA(0, text, title, style)

def create_DIR(DIR_NAME):
    try:
        os.makedirs(DIR_NAME)
    except OSError:
        if os.path.exists(DIR_NAME):
            # We are nearly safe
            pass
        else:
            # There was an error on creation, so make sure we know about it
            raise

def copy_file(FILE_NAME, DIR_SOURCE, DIR_DEST):
    if os.path.isfile(DIR_SOURCE+FILE_NAME):
        shutil.copyfile(DIR_SOURCE+FILE_NAME,DIR_DEST+FILE_NAME)
    else: # Ends code if the file does not exist
        sys.exit(FILE_NAME+" does not exist in target directory. Please ensure it is there, & start code again")

def timestamp():
    now = datetime.now()
    stamp = '%s/%s/%s %s:%s:%s' % (now.month, now.day, now.year, now.hour, now.minute, now.second)
    return stamp

def get_position(lines, item):
    for list_index, line in enumerate(lines):
        if item in line:
            list_index # Assume there is only 1 instance in lines[0]
            return list_index
            break
        else:
            position = 0

    if position == 0 :
        sys.exit(item+" cannot be found in provided lines/code. Check & restart code :)")

# ---------------------------------- PROGRAM FUNCTIONS ----------------------------------------------------------------
def generate_DIRs():
    # 1. Loop through DIR_LIST to create each DIR
    for directory in DIR_LIST:
        create_DIR(directory)

    # 2. Copy Program.exe and Database File.dat to the Run Directory (to be deleted or DIR_LIST[2])
    copy_file(PROGRAM_CODE_EXE,DIR_SYSTEM_FILES,DIR_LIST[2])
    copy_file(DATABASE_FILE,DIR_SYSTEM_FILES,DIR_LIST[2])

def import_species():
    print ("Importing Species from Program Code File")
    # 1. Import LogK input file, and read each line. Each line will be 1 species w length = levels
    for line in get_tab_file_multi_lines(DIR_LIST[0]+LOGK_INPUT_FILE)[1::]:

    # 2. Calculate the number of levels (NUMBERS[0])
        length = (len(line)-1)  # -1 to account fo the first column of labels, and not include it

    # 3. Modify the species name depending on solid or aqueous species
        if (line[0].split('*'))[0] == 'S':    # Split the species name by *, S = Solid Species (no hash added)
            ALL_LOGKS[(line[0].split('*'))[1]] = line[1::]
            ALLSPECIES.append((line[0].split('*'))[1])
        elif (line[0].split('*'))[0] == 'A':   # Split the species name by *, A = Aqueous Species (hash added)
            ALL_LOGKS["#"+(line[0].split('*'))[1]] = line[1::]
            ALLSPECIES.append("#"+(line[0].split('*'))[1])
        else:
            pass # There is currently no function for this one, but I left this for code extension
    print ("Imported LogK File")
    # 4. Calculate append the number of levels NUMBERS[0] and the number of species NUMBERS[1]
    NUMBERS.append(length)
    NUMBERS.append(len(ALLSPECIES))
    NUMBERS.append(pow(NUMBERS[0],NUMBERS[1]))

    # 5. Create Summary File & write to it
    with open(DIR_LIST[1]+SUMMARY_FILE, 'w') as f:
        f.write("Number of levels:" + '\t' + str(NUMBERS[0]) + '\n')
        f.write("Number of species:" + '\t' + str(NUMBERS[1]) + '\n')
        f.write("Total factorials:" + '\t' + str(NUMBERS[2]) + '\n')
        f.write("Species List:" + '\t')
        for species in sorted(ALLSPECIES):
            f.write(species + '\t')  # print 1 line of species

def import_conditions():
    print ("Importing Conditions from Program File")
    # 1. Import Program Input File & Read line by line
    for line in get_tab_file_multi_lines(DIR_LIST[0]+PROGRAM_INPUT_FILE):

    # 2. Identify # Conditions noted in Program file and append to condition list (ie an in order of conditions run)
        if line[0] == "#Condition":
            print (line)
            CONDITION_LIST.append(line[1:3:]) # Skip line[0] because it is "#Condition", append the rest of it to 3 to allow for 2 conditions

    # 3. Split the conditions (aka the rest of it) and add it to a dict, to Summarize over all conditions
            for item in line[1:3:]:
                print (item)
                CONDITION_SUMMARY[(item.split(' '))[0]].append((item.split(' '))[1])

    # 4. filter the Summary Dict created in 3. to remove duplicates
    for key in CONDITION_SUMMARY:
        CONDITION_SUMMARY[key] = sorted(list(set(CONDITION_SUMMARY[key])))

    # 5. Append Information to Summary File
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write('\n'+'\n'+"Conditions - Summary")
        for key in CONDITION_SUMMARY:
            f.write('\n'+ key + "(" + str(len(CONDITION_SUMMARY[key]))+ ")" +':' + '\t')
            for value in CONDITION_SUMMARY[key]:
                f.write(value + '\t')

    # 6. Generate Conditions File (will overwrite any old ones there)
    with open(DIR_LIST[1]+CONDITIONS_FILE, 'w') as f:
        f.write("Number of Specific Conditions (total):"+"\t"+ str(len(CONDITION_LIST)))
        for line in CONDITION_LIST:
            f.write('\n')
            for item in line:
                f.write(item + '\t')

def generate_coded_factorials():
    print ("Generating Coded Factorials....")
    factorials = defaultdict(list) # lower case because this defined function only
    # 1. Update Numbers from Summary File
    update_ALLSPECIES()
    print ("-updated AllSpecies")
    update_NUMBERS()
    print ("-updated Numbers")

    # 2. Create Coded Factorial (1s and 2s)
    list1 = range(1,NUMBERS[0]+1) # NUMBERS[1] = number of species
    repeat_each_number = 1 # Initialize
    for i in range(NUMBERS[1]): # NUMBERS[1] = num species
        repeat_each_sequence = int(NUMBERS[2]/(repeat_each_number * NUMBERS[0]))# NUMBERS[0] = levels,[2] = total factorials
        factorials[i] = [m for m in list(list1) for y in range(repeat_each_number)] * repeat_each_sequence
        repeat_each_number = repeat_each_number * NUMBERS[0] # NUMBERS[0] = number of levels
    print ("-created coded factorial")

    # 3. Write Coded Factorial File
    with open(DIR_LIST[1]+FACTORIAL_FILE, 'w') as f:
        for species in sorted(ALLSPECIES):
            f.write(species+ '\t')
        f.write('\n')
        for i in range(NUMBERS[2]): # NUMBERS[2] = total factorials
            for j in reversed(range(NUMBERS[1])): # NUMBERS[1] = num species
                f.write(str(factorials[j][i]) + '\t')
            f.write('\n')
    print ("-wrote coded factorial")

    # 4. Update Summary File
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write('\n' + '\n' + "Program Run Summary")
        f.write('\n' + "Successful Coded Factorial File Write @ " + timestamp())

def generate_uncoded_factorials():
    print ("Generating UnCoded Factorials....")
    factorials2 = [] # temporary list for this def only

    # 1. import coded factorial, where 1 line = 1 run. For each item on line, replace by assocated logK in ALL_LOGKs dict
    for line in get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE)[1::]:
        temp = []
        for species,item in zip(sorted(ALLSPECIES),filter(None,line)):
            temp.append(ALL_LOGKS[species][int(item)-1])
        factorials2.append(temp)
    print ("-created uncoded factorial in memory")

    # 2. Write Uncoded Factorial File
    with open(DIR_LIST[1]+FACTORIAL_FILE2, 'w') as f:
        for species in sorted(ALLSPECIES):
            f.write(species+ '\t')
        f.write('\n')
        for line in factorials2:
            for item in line:
                f.write(item + '\t')
            f.write('\n')
    print ("-wrote uncoded factorial")

    # 3. Update Summary file with successful write statement
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write('\n' + "Successful Uncoded Factorial File Write @ " + timestamp())

def update_ALLSPECIES():
    # 1. Check for ALLSPECIES, and update if required
    if len(ALLSPECIES) >0:
        pass
    else:
        if os.path.isfile(DIR_LIST[1]+FACTORIAL_FILE2):
            for item in filter(None,get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[0]):
                ALLSPECIES.append(item)
        else:
            run_SetUp_A()

def update_NUMBERS():
    # 1. Update global variable from the Summary file that was written in import SPECIES function (if required)
    if len(NUMBERS)> 0:
        pass
    else:
        if os.path.isfile(DIR_LIST[1]+SUMMARY_FILE):
            for line in get_tab_file_multi_lines(DIR_LIST[1]+SUMMARY_FILE):
                if line[0] == "Number of levels:": NUMBERS.append(int(line[1]))
                if line[0] == "Number of species:": NUMBERS.append(int(line[1]))
                if line[0] == "Total factorials:": NUMBERS.append(int(line[1]))
        else:
            run_SetUp_A()

def update_output_file_TITLES():
    if len(TITLES)> 0:
        pass
    else:
        if os.path.isfile(DIR_LIST[1]+OUTPUT_TITLES_FILE):
            for line in get_tab_file_multi_lines(DIR_LIST[1]+OUTPUT_TITLES_FILE)[2::]:
                TITLES.append(line[0]) # the [0] is there so it doesn't import as a list of lists, rather than just a list
        else:
            pass # Can force it to fetch all if you'd like.... but I haven't

def update_species_TITLES():
    for line in get_tab_file_multi_lines(DIR_LIST[1]+SUMMARY_FILE):
        if line[0] == 'Species List:':
            for item in line[1::]:
                if item == "":
                    pass
                else:
                    SPECIES_TITLES.append(item)
            break

def make_run_files(file_name,print_code,program_code,index,line):
    # 1. Re-run/create all Run Files!!! Even if they exist!
    print_code[get_position(program_code,'DATABASE')][1] = DIR_LIST[2]+DATABASE_FILE # update database line
    print_code[get_position(program_code,'-file')][1] = DIR_LIST[2]+'Out-Run-%s.txt' % index # update file output
    print_code[get_position(program_code,'TITLE')][1] = TITLE_IN_FILE # update title
    print_code[get_position(program_code,'TITLE')][2] = timestamp() # update the timestamp beside the title
    for species,value in zip(sorted(ALLSPECIES),filter(None,line)):
        print_code[get_position(program_code,species)+2][1] = value  # replace the logKs in the file based on species

    with open(DIR_LIST[2]+file_name+'.txt', 'w') as f:
        f.writelines('\t'.join(str(j) for j in i) + '\n' for i in print_code)

def check_file_creation(addition):
    # 1. Check to see if all files have been created
    if os.path.isfile(DIR_LIST[2]+'Run-'+str(NUMBERS[2])+'.txt'):
        note = "Successful " + addition
    else:
        note = "ERROR!!!!! Not successful at " + addition

    # 2. Update Python Summary
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write('\n' + note + " of Program Run Files @ " + timestamp()+'\t'+'Keyword: '+addition)

def fetch_all(solutions = 56):
    #Caluclate how many samples are supposed to be in each sample run, and limit the data to that number
    maxdata = (solutions*2)-2

    TITLES = []
    # 1. Create a blank file for each species in the output folder.
    title_file = DIR_LIST[2]+'Out-Run-1.txt' #%s % index #Only scan 1st output file
    for line in get_tab_file_multi_lines(title_file):
        for item in line:
            TITLES.append(item.strip())
        break # Only take the first line!

    # 2. Consolidate the data into the results folder!
    for title in TITLES:
        print ("Fetching and Combining Data for: "+title)
        with open(DIR_LIST[4]+title+'-Results.txt','a') as f:
            for index, x in (enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1)): #for each factorial line
                out_file = DIR_LIST[2]+'Out-Run-%s.txt' % index
                for line in get_tab_file_multi_lines(out_file)[2::2]:
                        # [6631::] : take every line starting on 6632 line (conditions * conditions etc + 1 here)
                        # [2::2]: take every other line starting on 3rd line (aka 2nd line)
                        # Make sure this matches the Pb function below
                        index = TITLES.index(title)
                        f.write(line[index].replace(" ","") +'\n')

    # 3. Update Summary file with successful copying of data
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write("\n" + "Successfully Transferred ALL Results to -Results.txts @ " + timestamp())

    with open(DIR_LIST[1]+OUTPUT_TITLES_FILE, 'w') as f:
        f.write("Titles of Output Files:"+"\n")
        for title in sorted(TITLES): # Sort here so we don't loose our index spots above
            f.write(title + "\n")

    # 4. Delete the extraneous "-Results.txt" if its required to be deleted
    if os.path.isfile(DIR_LIST[4]+"-Results.txt"):
        os.remove(DIR_LIST[4]+"-Results.txt")

TITLES = [] # declared a list for the titles/headers to be taken from 1 file declared outside the function so it is globally available.

def fetch_Pb(filename_addition = 0):
    print ("Fetching Pb")
    # 1. create the titles/headers based on the title. You only need to look at 1 header from 1 file which is why the Out-Run-1 is hard coded.
    title_file = DIR_LIST[2]+'Out-Run-1.txt' #%s % index #Only scan 1st output file
    for line in get_tab_file_multi_lines(title_file):
        for item in line:
            TITLES.append(item.strip())

    # 2. fopen output/results Pb file, then for each Out File as required by factorial file, open output and add to appropriate title!
    n=0
    with open(DIR_LIST[4] + 'Pb'+str(filename_addition)+'-Results.txt', 'w') as f: #CREATE THE OUTPUT Pb-Results file!
        for index, line in enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1): #for each factorial line
            print (index) #this is here to see what run it is currently on
            out_file = DIR_LIST[2]+'Out-Run-%s.txt' % index #designate the output file, and iterate over the factorial (total runs)
            for line in get_tab_file_multi_lines(out_file)[2::2]: # THIS LINE DETERMINES HOW THE DATA IS PULLED FROM THE FILE
                # Format: [START:STOP:STEP]
                # Option 1: Every Other Line starting on line 2: [2::2]
                # Option 2: All lines, starting on line = CONDITIONS + 1 (Title, then the initialized conditions, THEN the results): [57::] (56 conditions)
                #print line # this is here for testing 1 iteration/file to make sure its pulling the correct data
                n = n+1
                #print n # this is here for testing 1 iteration/file to make sure its pulling the correct data
                #print line[TITLES.index("Pb")].strip() # this is here for testing 1 iteration/file to make sure its pulling the correct data
                f.write(line[TITLES.index("Pb")].strip() + "\n")
            #break # this is here for testing 1 iteration/file to make sure its pulling the correct data
    # 3. Update Summary file with successful copying of data
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write("\n" + "Successfully Transferred Only Pb Results to -Results.txts @ " + timestamp())

    with open(DIR_LIST[1]+OUTPUT_TITLES_FILE, 'a') as f:
        f.write("Titles of Output Files:"+"\n")
        f.write("Pb" + "\n")

    # 4. Delete the extraneous "-Results.txt" if its required to be deleted
    if os.path.isfile(DIR_LIST[4]+"-Results.txt"):
        os.remove(DIR_LIST[4]+"-Results.txt")

def fetch_rewrite():
    # 1. Create a blank file for each species in the output folder.
    # --This should create a null file called '-Results.txt'
    # --Only run for the 1st line of the 1st Output files
    title_file = DIR_LIST[2]+'Out-Run-1.txt' #%s % index #Only scan 1st output file
    for line in get_tab_file_multi_lines(title_file):
        for item in line:
            TITLES.append(item.strip())
        break # Only take the first line!

    # 2. for each output, open output/results file, then for each Out File as required by factorial file, open output and add to appropriate title!
    for title in TITLES:
        with open(DIR_LIST[4]+title+'-Results.txt','a') as f:
            for index, x in (enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1)): #for each factorial line
                out_file = DIR_LIST[2]+'Out-Run-%s.txt' % index
                for line in get_tab_file_multi_lines(out_file)[6632::]: # take every other line starting on 6633rd line
                        index = TITLES.index(title)
                        f.write(line[index].replace(" ","") +'\n')

    # 3. Update Summary file with successful copying of data
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write("\n" + "Successfully Rewrote ALL Results to -Results.txts @ " + timestamp())

    # 4. Delete the extraneous "-Results.txt" if its required to be deleted
    if os.path.isfile(DIR_LIST[4]+"-Results.txt"):
        os.remove(DIR_LIST[4]+"-Results.txt")

def check_lengths():
    update_CONDITION_LIST()
    update_NUMBERS()
    # Check Lengths of Various Files. Should be (in order: [(#LVL)^(#PARM)]*#COND, (#LVL)^(#PARM) (+1 for title), [(#LVL)^(#PARM)]*#COND). Write a few lines in appropriate places to "check" the length of all of these. Note, if Results are wrong = rerun create_results, if

    print ("Check Factorial (no condition) length")
    with open(DIR_LIST[1]+FACTORIAL_FILE) as f:
         len_Fact = len(filter(None,[line.split('\t') for line in f.read().splitlines()]))

    print ("Check Results (full) file length")
    with open(DIR_LIST[4]+"Pb-Results.txt") as r:
        len_Results = len(filter(None,[line.split('\t') for line in r.read().splitlines()]))

    print ("Check Factorial (with conditions) length")
    with open(DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE) as f:
         len_conFact = len(filter(None,[line.split('\t') for line in f.read().splitlines()]))

    if len_Fact != NUMBERS[2]+1:
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write('\n' + "Factorial file length (without Conditions) failed required length @ " + timestamp())
        sys.exit("Given Factorial File (%s) is incorrect length (%s). Should be (%s).") % (DIR_LIST[1]+FACTORIAL_FILE,len_Fact,NUMBERS[2]+1)
    elif len_Results != (NUMBERS[2]*len(CONDITION_LIST)-1):
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write('\n' + "Results file length failed required length @ " + timestamp())
        sys.exit("Given Results File (%s) is incorrect length (%s). Should be (%s).") % (DIR_LIST[4]+"Pb-Results.txt",len_Results,len(CONDITION_LIST) - 1)
    elif len_conFact != (NUMBERS[2]*len(CONDITION_LIST)-1):
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write('\n' + "Factorial file length (with Conditions) failed required length @ " + timestamp())
        sys.exit("Given Results File (%s) is incorrect length (%s). Should be (%s).") % (DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE2, len_conFact,(NUMBERS[2]*len(CONDITION_LIST)))
    else:
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write('\n' + "Successfully Checked Results and Factorials (with and without Conditions) File Lengths @ " + timestamp())

def import_dataframe(dir_of_fact_file, result_file_choice, cond= 'none', min=7, max=10.5):
    print ("Import Dataframe for Factorial and Result")

    data = pd.read_csv(dir_of_fact_file, sep= "\t") # use the coded conditioned factorial file
    print ("Imported Dataframe, prepare for addition of Pb")
    for col in data.columns:
        if 'Unnamed' in col:
            del data[col]
    #data.insert(0,"Pb",pd.read_csv(result_file_choice),)

    # Apply conditional modifier if required
    if cond == 'none':
        return data
    else:
        data = data[data[cond] > min]
        data = data[data[cond] < max]
        return data

def analyse_factorial(dir_save_spot,dir_of_fact_file, result_file_choice, cond, min, max):
    update_species_TITLES()
    data = import_dataframe(dir_of_fact_file, result_file_choice, cond, min, max)

    for species in SPECIES_TITLES:
        print ("Analysing: "+species)
        con = ["pH","DIC"]
        con.append(species)
        condition = data.groupby(con)
        summary1 = condition["Pb"].mean()
        summary1.to_csv(dir_save_spot+DIR_LIST_ANALYSIS[0]+species+" - Mean (by species).txt", sep='\t', index=True, header=True)

    # Calculate Main Effects By Species!
        by_species = data.groupby([species])
        summary = by_species["Pb"].mean()
        summary.to_csv(dir_save_spot+DIR_LIST_ANALYSIS[2]+species+" - Mean (by species).txt", sep='\t', index=True, header=True)

    # Calculate Interaction Effects!
        for species2 in SPECIES_TITLES:
            if species == species2:
                pass
            else:
                by_species = data.groupby([species,species2])
                summary = by_species["Pb"].mean()
                summary.to_csv(dir_save_spot+DIR_LIST_ANALYSIS[4] + species + " vs "+ species2 + " - Interaction.txt", sep='\t', index=True, header=True)

def plot_interactions(dir_root_save_spot,code=True, MW=207.21):

    LegendFont = FontProperties()
    LegendFont.set_size('10')
    LegendFont.set_family('Times New Roman')
    timesfont1 = {'fontname' : 'Times New Roman', 'weight' : 'bold'}
    timesfont2 = {"fontsize" : '12', "fontname" : 'Times New Roman'}

    if code == True:
        keyword = "Level"
    else:
        keyword = "LogK"

    for file in listdir(dir_root_save_spot+DIR_LIST_ANALYSIS[4]):
        legend = []
        xrange = []
        # Import the datafame from where "analysis" saved it. This allows for graphing code to be indepenedent of analysis
        df = pd.read_csv(dir_root_save_spot+DIR_LIST_ANALYSIS[4]+file, sep= "\t")
        # Identify the headers in the df
        headers = df.columns.values.tolist()
        # create the data frame for graphing
        to_graph = (df.pivot(index=headers[0], columns=headers[1]))*MW*1000
        # Set up legend and note of "plot of"
        for leg in to_graph.columns.values.tolist():
            legend.append(headers[1]+" @ "+keyword+": "+str(leg[1]))
            plot_of = leg[0]
        # Set up x axis range
        range_df = to_graph.reset_index()
        for value in range_df[headers[0]]:
            xrange.append(value)
        #Plot Graph
        fig = to_graph.plot(legend=None,figsize=(6,4),xticks=xrange,fontsize=10)
        #Set up Graph!
        plt.title("Interaction Plot", fontsize=14, **timesfont1) # of: "+headers[0]+" and "+headers[1]
        plt.xlabel(headers[0] + " "+keyword, fontsize=12, **timesfont1)
        plt.ylabel("Average " + plot_of + " (mg/L)", fontsize=12, **timesfont1)
        #plt.xticks(**timesfont2)
        #plt.yticks(**timesfont2)
        fig.ticklabel_format(style='sci', axis='y', scilimits=(0,0),useOffset=False)
        plt.legend(legend, loc='upper center', prop= LegendFont,bbox_to_anchor=(0.5,-0.2), fancybox=True, ncol=len(legend))
        plt.grid(True)
        #plt.tight_layout()
        #plt.xticks(xrange)
        fig.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        # Save Graph
        plt.savefig(dir_root_save_spot+DIR_LIST_ANALYSIS[5]+"Interaction Plot - "+file.split(" - Interaction.txt")[0]+".png", bbox_inches='tight')
        # Clear Graph
        plt.close()

def plot_individual_ME_graphs(dir_root_save_spot,code=True, MW=207.21):

    #Set up font, etc etc. Some methods didn't work for some items, and I just lost patience and kitbashed it.
    LegendFont = FontProperties()
    LegendFont.set_size('10')
    LegendFont.set_family('Times New Roman')
    timesfont1 = {'fontname' : 'Times New Roman', 'weight' : 'bold'}
    timesfont2 = {"fontsize" : '12', "fontname" : 'Times New Roman'}

    # determine keyword based on if it is Coded or Uncoded
    if code == True:
        keyword = "Level"
    else:
        keyword = "LogK"

    # create graph for each file
    for file in listdir(dir_root_save_spot+DIR_LIST_ANALYSIS[2]):

        # import the data frame
        df = pd.read_csv(dir_root_save_spot+DIR_LIST_ANALYSIS[2]+file, sep= "\t")

        # obtain the headers of the dataframe, and calculate the specific x-axis data range
        xrange = []
        headers = df.columns.values.tolist()
        for value in df[headers[0]]:
            xrange.append(value)

        #Modify the dataframe
        df = df.set_index(headers[0])
        df = df*MW*1000

        # Graph the dataframe
        fig = df.plot(legend=None,figsize=(6,4),xticks=xrange,fontsize=10)

        # # Set up Graph!
        plt.title("Main Effects Plot: "+headers[0],fontsize=14, **timesfont1)
        plt.xlabel(headers[0] + " "+keyword, fontsize=12, **timesfont1)
        #plt.xticks(**timesfont2)
        #plt.xticks(xrange)
        plt.ylabel("Average Pb (mg/L)", fontsize=12, **timesfont1)
        #plt.yticks(**timesfont2)
        plt.ticklabel_format(style='sci', axis='y', scilimits=(0,0),useOffset=False)
        plt.grid(True)
        #plt.tight_layout()

        # fig, ax = plt.subplots()
        fig.yaxis.set_major_formatter(FormatStrFormatter('%.2f'))
        plt.savefig(dir_root_save_spot+DIR_LIST_ANALYSIS[3]+"ME Plot - "+file.split("- Mean")[0]+".png",bbox_inches='tight')
        plt.close()

def plot_contour_plots(data_dir, MW=207.21):
    save_data_dir = data_dir+DIR_LIST_ANALYSIS[0]+"Part Analysis\\"
    create_DIR(save_data_dir)

    LegendFont = FontProperties()
    LegendFont.set_size('12')
    LegendFont.set_family('Times New Roman')
    timesfont1 = {'fontname' : 'Times New Roman', 'weight' : 'bold'}
    timesfont2 = {"fontsize" : '12', "fontname" : 'Times New Roman'}

    for file in listdir(data_dir+DIR_LIST_ANALYSIS[0]):
        if os.path.isdir(data_dir+DIR_LIST_ANALYSIS[0]+file) == True:
            pass
        else:
            # Import original By Condition File to calculate difference
            df = pd.read_csv(data_dir+DIR_LIST_ANALYSIS[0]+file, sep= "\t")
            headers = df.columns.values.tolist()
            print (headers)

            cond1 = headers[0]
            unit1 = ""
            cond2 = headers[1]
            unit2 = "(mg C/L)"
            species = headers[2]
            bottom_level = df[species].min()
            top_level = df[species].max()

            # Reformat the By Condition File, to include the "Difference" column, and save this to file (for later use)
            for_contour = df.pivot_table(headers[3], [cond1, cond2], species)
            for_contour['Difference'] = for_contour[top_level] - for_contour[bottom_level]
            table = for_contour['Difference']
            table.to_csv(save_data_dir+"Contour Data - "+species, sep=' ', index=True, header=True)

            # Import difference data, and pivot!
            df = pd.read_csv(save_data_dir+"Contour Data - "+species, sep=' ')
            data = df.pivot_table('Difference',[cond2],cond1)

            max_value = df['Difference'].max()

            X = data.columns.values
            Y = data.index.values

            if max_value*MW*1000 < 0.1:
                max_cont = m.ceil(max_value*MW*1000*1000)
                unit3 = "ug/L"
                Z = (data.values)*1000*MW*1000
            else:
                max_cont = m.ceil(max_value*MW*1000)
                unit3 = "mg/L"
                Z = (data.values)*1000*MW

            #contour_range = list(range(-20,191,1))


            fig = plt.contourf(X,Y,Z,100,figsize=(6,4))
            cbar = plt.colorbar(fig, orientation='horizontal')
            cbar.ax.set_xlabel('Average Effect: Difference of Max - Min (' + species + 'in ' + unit3 + ")")

            plt.title("Main Effects Contour Plot: "+ species, fontsize= 14, **timesfont1)
            plt.xlabel(cond1+" "+unit1, fontsize=13, **timesfont1)
            plt.ylabel(cond2+" "+unit2, fontsize=13, **timesfont1)
            plt.xticks(**timesfont2)
            plt.tight_layout(w_pad=0.5,h_pad=2)

            plt.savefig(data_dir+DIR_LIST_ANALYSIS[1]+"Contour Plot - "+species+".png")
            plt.close()

def copy_selected_files():
    update_NUMBERS()
    print (NUMBERS[2])
    for i in range(10):
        print (i+1)
    interval = [0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9]

    for mult in interval:
        for i in range(10):
            x = i+int(NUMBERS[2]*mult)+1
            file_name_copy = 'Run-%s.txt' % str(x)
            file_copy = DIR_LIST[2]+file_name_copy

            subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file_copy])
            time.sleep(SLEEP)

    for i in range(10):
        x = int(NUMBERS[2]-i)

        file_name_copy = 'Run-%s.txt' % str(x)
        file_copy = DIR_LIST[2]+file_name_copy

        subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file_copy])
        time.sleep(SLEEP)

        copy_file("Out-Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
        copy_file("Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
        copy_file("Run-"+str(x)+".txt.out",DIR_LIST[2],DIR_LIST[6])


    time.sleep(60)


    for mult in interval:
        for i in range(10):
            x = i+int(NUMBERS[2]*mult)+1
            file_name_copy = 'Run-%s.txt' % str(x)
            file_copy = DIR_LIST[2]+file_name_copy

            copy_file("Out-Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
            copy_file("Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
            copy_file("Run-"+str(x)+".txt.out",DIR_LIST[2],DIR_LIST[6])

    for i in range(10):
        x = int(NUMBERS[2]-i)

        file_name_copy = 'Run-%s.txt' % str(x)
        file_copy = DIR_LIST[2]+file_name_copy

        copy_file("Out-Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
        copy_file("Run-"+str(x)+".txt",DIR_LIST[2],DIR_LIST[6])
        copy_file("Run-"+str(x)+".txt.out",DIR_LIST[2],DIR_LIST[6])


    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write('\n' + "Files Rerun and Copied to Summary Folder Successfully @ " + timestamp())

# ----------------------------------------- RUN DEF in ORDER ----------------------------------------------------------
def run_SetUp_A():
    if os.path.isfile(DIR_LIST[1]+SUMMARY_FILE):
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write("\n" + "Restart Program @ " + timestamp())
            print ("Updated Summary File")
    else:
        generate_DIRs()
        # Check if Input Files are present, and request if they arn't.....
        while os.path.isfile(DIR_LIST[0]+LOGK_INPUT_FILE) == False:
            Mbox('Please Save File to Directory', LOGK_INPUT_FILE + " in: " + DIR_LIST[0], 0)
        while os.path.isfile(DIR_LIST[0]+PROGRAM_INPUT_FILE) == False:
            Mbox('Please Save File to Directory', PROGRAM_INPUT_FILE + " in: " + DIR_LIST[0], 0)

    import_species()
    print ("Imported Species")
    import_conditions()
    print ("Imported Conditions")
    generate_coded_factorials()
    print ("Coded Factorial Generated")
    generate_uncoded_factorials()
    print ("Uncoded Factorials Generated")


def run_SetUp_B(run_type='rewrite'):
    # 1. Update global variables
    update_ALLSPECIES()
    print ("-Updated AllSpecies")
    update_NUMBERS()
    print ("-Updated Numbers")

    # 2. read the program code to memory
    program_code = get_tab_file_multi_lines(DIR_LIST[0]+PROGRAM_INPUT_FILE)
    print ("-imported program code to memory")

    # 3. read the factorial file line by line (aka run by run)
    print ("creating individual program code files and saving them...")
    for index, line in (enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1)): #for each factorial line
        print_code = program_code # reset the print_code at the start of each line so that we deal with fresh print data
        file_name = 'Run-%s' % index # changes the title of the Program Run file for each line
        print (file_name)

    # 4. run styles based on command input
        if run_type == 'rewrite':
            make_run_files(file_name,print_code,program_code,index,line)
        elif run_type == 'pass':
            if os.path.isfile(DIR_LIST[2]+file_name+'.txt'):
                pass # aka next line
            else:
                make_run_files(file_name,print_code,program_code,index,line)
        elif run_type == 'skip':
            pass

    if run_type == "rewrite" or "check":
        check_file_creation(run_type)

def run_Program_Files(run_type='rerun'):
    # 1. update ALL species and NUMBERS (in case being run independently from set-up A and B)
    update_ALLSPECIES()
    update_NUMBERS()
    did_run = False
    delay = 1500

    # 2. open each file from 1 (the +1) to NUMBERS[2] (total factorial #)
    for index,i in enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1): # i not used

        file_name = 'Run-%s.txt' % index
        file = DIR_LIST[2]+file_name
        if run_type == 'rerun':
            subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file])
            time.sleep(SLEEP) # slow the program down (change in USER defined variables)
            did_run = True

            # file2 = DIR_LIST[2]+ 'Run-%s.txt' % (index-delay)
            # if os.path.isfile(file2):
            #     os.remove(file2+".OUT")
            # else:
            #     pass

        elif run_type == 'pass':
            if os.path.isfile(DIR_LIST[2]+'Out-'+file_name):
                pass
            else:
                subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file])
                time.sleep(SLEEP) # slow the program down (change in USER defined variables)
                did_run = True

        elif run_type == 'skip':
            pass

    time.sleep(1) # wait for disk drive to finish writing before check for completion

    if did_run == True:
        # 4. Check to see if Unsuccessful of running each one.
        if os.path.isfile(DIR_LIST[2]+'Out-Run-'+str(NUMBERS[2])+'.txt'):
            note = "Successful Run"
        else:
            note = "ERROR!!!!! Error for running"

        # 5. Write update to file!
        with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            f.write('\n' + note + "/Opening of Program Run Filess @ " + timestamp()+'\t'+"Keyword: "+run_type)

def create_results(run_type='fetch-all', solutions =56):

    if os.path.exists(DIR_LIST[2])==True:
        if run_type == "fetch-all":
            #time.sleep(0.1) # Wait 1 hour before actually fetching the results, to allow for the program to "cool off" and for the drive to finish writing
            fetch_all(solutions)
        elif run_type == "Pb":
            fetch_Pb()
        elif run_type == "rewrite":
            fetch_rewrite()
        else:
            pass
    else:
        sys.exit("directory of File Runs has been deleted, and so this cannot be done. Sorry!")

def update_CONDITION_LIST():
    del CONDITION_LIST[:] # Ensures the global list is empty!!

    if os.path.isfile(DIR_LIST[1]+CONDITIONS_FILE):
        for line in get_tab_file_multi_lines(DIR_LIST[1]+CONDITIONS_FILE)[1::]:
            line = filter(None, line)
            condition_titles = []
            for item in line:
                condition_titles.append(item.split(" ")[0])
            CONDITION_LIST.append(condition_titles)
            break # assume all titles are in the same order and location as the first condition title

        for line in get_tab_file_multi_lines(DIR_LIST[1]+CONDITIONS_FILE)[1::]:
            line = filter(None, line)
            temp_line = []
            for item in line:
                temp_line.append(item.split(" ")[1])
            CONDITION_LIST.append(temp_line)
    else:
        print ("Condition File Does Not Exist. Try running setupA")
        pass

def create_conditioned_factorial_files():

    update_CONDITION_LIST()

    update_NUMBERS()

    # Obtain the Titles of the conditions, and then remove from CONDITION LIST (so no fancy footwork for later)
    for condition_title in CONDITION_LIST[0]: # This is the titles of the conditions
        TITLES.append(condition_title)
    del CONDITION_LIST[0]

    # Obtain the Titles of the Species, and then skip the first line in the factorial file being used. Append to TITLEs
    with open(DIR_LIST[1]+FACTORIAL_FILE) as f:
        for line in f.read().splitlines():
            for item in line.split('\t'):
                TITLES.append(item)
            break # Ensures only the first line is read, and incorporated!

    # 2. Create Coded Conditions Factorial Titles
    with open(DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE, 'w') as f:
        #A. Print Titles
        for title in TITLES:
            f.write(title + "\t")
        f.write("\n")

        #B. Write in Coded factorial body afterwards
        dummy = 0
        for factorial in get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE)[1::]: #start on 1 to skip titles!
            for condition in CONDITION_LIST: # No need to specify, since we del the titles form condition list
                for c in condition:
                    f.write(c + "\t")
                for run in factorial:
                    f.write(run + "\t")
                dummy = dummy+1
                f.write("\n")
        f.close()
        #dummy

    # 3. Update Summary File
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write("\n" + "Successfully Created with New Code Conditioned Coded Facotorial File @ " + timestamp())
        f.write("\n" + "Successfully Created with New Code Conditioned Coded Facotorial File with length: " + str(dummy))

    # 4. Create Coded Conditions Factorial Titles
    with open(DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE2, 'w') as f:
        #A. Print Titles
        for title in TITLES:
            f.write(title + "\t")
        f.write("\n")

        #B. Write in Coded factorial body afterwards
        dummy = 0
        for factorial in get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::]: #start on 1 to skip titles!
            for condition in CONDITION_LIST: # No need to specify, since we del the titles form condition list
                for c in condition:
                    f.write(c + "\t")
                for run in factorial:
                    f.write(run + "\t")
                dummy = dummy+1
                f.write("\n")
        f.close()
        #dummy

    # 3. Update Summary File
    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
        f.write("\n" + "Successfully Created with New Code Conditioned UNCoded Facotorial File @ " + timestamp())
        f.write("\n" + "Successfully Created with New Code Conditioned UNCoded Facotorial File with length: " + str(dummy))

def analyse_plot_ALL(result_file,cond='none', min=0, max=0,run_type='all', MW=207.21):
    # run_type = 'all' (analysis AND graph), 'graph only' (only graphs (all)), 'analysis only'

    with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:

        if cond == 'none':
            root = "All Conditions"
            DIR_ROOT_CODE = DIR_LIST[5]+"\\"+result_file.split(".")[0]+"\\"+root+"\\Coded\\" # DIR_BASE+"Analysis\\", + specified name# 5
            DIR_ROOT_UnCODE = DIR_LIST[5]+"\\"+result_file.split(".")[0]+"\\"+root+"\\UnCoded\\" # DIR_BASE+"Analysis\\", + specified name# 5
        else:
            root = cond+"- " +str(min) + " to "+ str(max)
            DIR_ROOT_CODE = DIR_LIST[5]+"\\"+result_file.split(".")[0]+"\\"+root+"\\Coded\\" # DIR_BASE+"Analysis\\", + specified name# 5
            DIR_ROOT_UnCODE = DIR_LIST[5]+"\\"+result_file.split(".")[0]+"\\"+root+"\\UnCoded\\" # DIR_BASE+"Analysis\\", + specified name# 5


        for dir in DIR_LIST_ANALYSIS:
            create_DIR(DIR_ROOT_CODE+dir)
            f.write("\n" + "Success! Created Analysis Subfolders: "+DIR_ROOT_CODE+dir+ "@ " + timestamp())
            create_DIR(DIR_ROOT_UnCODE+dir)
            f.write("\n" + "Success! Created Analysis Subfolders: "+DIR_ROOT_UnCODE+dir+ "@ " + timestamp())

        if run_type == 'all':
            print ("Analyse factorial (coded)")
            analyse_factorial(DIR_ROOT_CODE,DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE,DIR_LIST[4]+result_file, cond, min, max)
            f.write("\n" + "Success! Analysis of coded: "+root+result_file+ "@ " + timestamp())

            print ("Analyse factorial (uncoded)")
            analyse_factorial(DIR_ROOT_UnCODE,DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE2,DIR_LIST[4]+result_file, cond, min, max)
            f.write("\n" + "Success! Analysis of uncoded: "+root+result_file+ "@ " + timestamp())

            print ("Plot Interactions (coded)")
            plot_interactions(DIR_ROOT_CODE, True, MW)
            f.write("\n" + "Success! Plotting Coded Interactions for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Interactions (uncoded)")
            plot_interactions(DIR_ROOT_UnCODE, False, MW)
            f.write("\n" + "Success! Plotting Uncoded Interactions for: "+root+result_file+ "@ " + timestamp())

            print ("Plot ME (coded)")
            plot_individual_ME_graphs(DIR_ROOT_CODE, True, MW)
            f.write("\n" + "Success! Plotting Coded Singular Main Effects for: "+root+result_file+ "@ " + timestamp())

            print ("Plot ME (uncoded)")
            plot_individual_ME_graphs(DIR_ROOT_UnCODE, False, MW)
            f.write("\n" + "Success! Plotting Unoded Singular Main Effects for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Contours (coded)")
            plot_contour_plots(DIR_ROOT_CODE, MW)
            f.write("\n" + "Success! Plotting Coded Contours for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Contours (uncoded)")
            plot_contour_plots(DIR_ROOT_UnCODE, MW)
            f.write("\n" + "Success! Plotting Uncoded Contours for: "+root+result_file+ "@ " + timestamp())

        elif run_type == "graph only":
            print ("Plot Interactions (coded)")
            plot_interactions(DIR_ROOT_CODE, True, MW)
            f.write("\n" + "Success! Plotting Coded Interactions for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Interactions (uncoded)")
            plot_interactions(DIR_ROOT_UnCODE, False, MW)
            f.write("\n" + "Success! Plotting Uncoded Interactions for: "+root+result_file+ "@ " + timestamp())

            print ("Plot ME (coded)")
            plot_individual_ME_graphs(DIR_ROOT_CODE, True, MW)
            f.write("\n" + "Success! Plotting Coded Singular Main Effects for: "+root+result_file+ "@ " + timestamp())

            print ("Plot ME (uncoded)")
            plot_individual_ME_graphs(DIR_ROOT_UnCODE, False, MW)
            f.write("\n" + "Success! Plotting Unoded Singular Main Effects for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Contours (coded)")
            plot_contour_plots(DIR_ROOT_CODE, MW)
            f.write("\n" + "Success! Plotting Coded Contours for: "+root+result_file+ "@ " + timestamp())

            print ("Plot Contours (uncoded)")
            plot_contour_plots(DIR_ROOT_UnCODE, MW)
            f.write("\n" + "Success! Plotting Uncoded Contours for: "+root+result_file+ "@ " + timestamp())

        elif run_type == "analysis only":
            print ("Analyse factorial (coded)")
            analyse_factorial(DIR_ROOT_CODE,DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE,DIR_LIST[4]+result_file, cond, min, max)
            f.write("\n" + "Success! Analysis of coded: "+root+result_file+ "@ " + timestamp())

            print ("Analyse factorial (uncoded)")
            analyse_factorial(DIR_ROOT_UnCODE,DIR_LIST[3]+CONDITIONS_FILE_PREFIX+FACTORIAL_FILE2,DIR_LIST[4]+result_file, cond, min, max)
            f.write("\n" + "Success! Analysis of uncoded: "+root+result_file+ "@ " + timestamp())

def check_length_to_rerun(run_number_to_compare=1):
    # Set up initial length for checking; assume Run 1 is correct length
    file1 = DIR_LIST[2]+'Out-Run-' + str(run_number_to_compare) + '.txt'
    b = os.path.getsize(file1) #DIR_LIST[2]+'Out-'+file_name

    for index,i in enumerate(get_tab_file_multi_lines(DIR_LIST[1]+FACTORIAL_FILE2)[1::], start=1):
        file_name2 = 'Out-Run-%s.txt' % index
        file_name3 = 'Run-%s.txt' % index
        file2 = DIR_LIST[2]+file_name2
        file3 = DIR_LIST[2]+file_name3
        # print os.path.getsize(file2)
        # count = 0

        if os.path.isfile(file2)==True:
            #
            # with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            #     f.write('\n' + "Checked Output File Existance, all required Outputs Exist  @ " + timestamp())

            if os.path.getsize(file2) == b:
                pass
                #print "File: " + file_name3 + " Matches"
                # with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
                #     f.write('\n' + "Checked Output File Length, all met Length Requirements @ " + timestamp())
            else:
                subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file3])
                time.sleep(SLEEP)
                # count = count+1
                # with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
                #     f.write('\n' + "Checked Output File Length, and Reran " + str(count) + " @ "+ timestamp())
        else:
            subprocess.Popen([DIR_LIST[2]+PROGRAM_CODE_EXE, file3])
            time.sleep(SLEEP)
            # count = count+1
            # with open(DIR_LIST[1]+SUMMARY_FILE, 'a') as f:
            #     f.write('\n' + "Checked Output File Existance, and Reran " + str(count) + " @ "+ timestamp())


# ---------------------------------------------- RUN ------------------------------------------------------------------


def experimet_match_data_slim(runnum = 40, cond = 49): #52 because i screwed up and there are still 3 extra runs on the end
    #Caluclate how many samples are supposed to be in each sample run, and limit the data to that number

    data_file = DIR_LIST[4]+'Pb2-Results.txt'

    # 1. Create a blank file for run in the output folder.
    output_file = DIR_LIST[3]+'DataFile_RunNum_'+str(runnum)+'.txt' #put in RESULTS folder from DIRLIST

    with open(output_file, 'w') as f:
        for line in get_tab_file_multi_lines(data_file)[runnum-1::cond]: #runnum-1 to account for no title in the output fieles (start from 0)
            print (line)
            f.write(line[0]+'\n')








# 1.
# print ("################################################## Run Set Up A ################################################## ")
# run_SetUp_A()
# print ("IMPORTING COMPLETE")
# print ("SetUpA Complete")
# # # # # #
#
# # # # # # # 2.
# print ("################################################## RUN SET UP B ################################################## ")
# run_SetUp_B("pass") # rewrite = overwrite program files, pass = rerun only if missing, skip = no reruns
# print ("GENERATED ALL RUN FILES")
# print ("SetUpB Complete")
# # #  # # # # # #
# # # # # # # # # # 3.
# print ("Running Files Now")
# run_Program_Files("pass") # rerun = rerun all, even if they already exist. pass = rerun only if missing, skip = no reruns
# print ("RUN COMPLETE")
# # # # # #
# # # # # # 4.
# # # check_length_to_rerun(14641) #823543compare output file to the selected output file (the number is for Out-Run-#)
# # # #
# # # # # # 5.
# create_results("fetch-all", solutions = 12) # fetch-all = ... fetch all, Pb = only Pb, #re-write = overwrite ones already there, skip = skip, solutions is number of conditions (see summary file for number)
# # # #
# create_results("Pb")
# # #
# # # # # 6.
# create_conditioned_factorial_files()
# # # # #
# # # # # # 7.
# copy_selected_files()
# #
# 8.
analyse_plot_ALL("Pb0-Results.txt")
# analyse_plot_ALL("pH-Results.txt")
# analyse_plot_ALL("d_Cerrusite-Results.txt")
# analyse_plot_ALL("d_Hydrocerrusite-Results.txt")

# analyse_plot_ALL("Cerrusite-Results.txt",run_type="graph only",MW=267.21)
# analyse_plot_ALL("d_Cerrusite-Results.txt",run_type="graph only",MW=267.21)
# analyse_plot_ALL("d_Hydrocerrusite-Results.txt",run_type="graph only",MW=775.63)
# analyse_plot_ALL("Hydrocerrusite-Results.txt",run_type="graph only",MW=775.63)
# analyse_plot_ALL("la_H+-Results.txt",run_type="graph only",MW=1)
# analyse_plot_ALL("pH-Results.txt",run_type="graph only",MW=207.21)
# analyse_plot_ALL("Pb-Results.txt",run_type="graph only")
# analyse_plot_ALL("Pb-Results.txt",) # 'none' or no condition will analyse across entire factorial conditions, min, max (will NOT be included)
# analyse_plot_ALL("Pb-Results.txt",'DIC',-1,200)
# analyse_plot_ALL("Pb-Results.txt",'DIC',-1,100)

# # ----------------------------------------------- Scratch Work --------------------------------------------------------

