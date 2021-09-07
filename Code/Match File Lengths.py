import os



name_run ="5x12 lvl (Buffered) - 8 to 10"
drive = "V:\\"
filelocation = "\\Analysis\\Matching\\"#Match 8 Through Match 5\\"
full_location = drive+name_run+filelocation

def get_length(fname):
    with open(fname) as f:
        for i, l in enumerate(f):
            pass
    return i #+ 1 the +1 is for counting the header.... so don't include

for fname in os.listdir(full_location):
    if fname.endswith(".txt"):
        print(fname, get_length(full_location+fname))

    else:
        continue
