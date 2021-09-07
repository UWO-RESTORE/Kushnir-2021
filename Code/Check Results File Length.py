name_run ="5x12 lvl (Buffered) - 8 to 10"
drive = "V:\\"
filelocation = "\\Results\\Data Files\\"
full_location = drive+name_run+filelocation

filename_original = "Pb-Results.txt"
filename_extra = "Pb0-Results.txt"
filename_test = "Test.txt"
f_original = full_location+filename_original
f_extra = full_location+filename_extra
f_test = full_location+filename_test

def file_length(fname):
    # Includes header and every line
    # Does not include any empty lines at the end of the file
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i + 1


print("Pb-Results Length:", file_length(f_original))
print("Pb0-Results Length:", file_length(f_extra))
