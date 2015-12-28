# Shane Fenske
# Main script to be called to create DraftKings Fantasy Basketball Lineup
# Calls optimize.py which generates the lineup using either the csv specified as
# the first argument or if no arguments are given it calls scrape.py which goes and gets
# the current data.

import sys
import subprocess 

if len(sys.argv) == 1:
    try:
        subprocess.call(['python','scrape.py'])
        subprocess.call(['python','optimize.py'])
    except:
        sys.stderr.write("Failed scrape -- be sure there are NBA contests live on draftkings.com/lobby#/NBA/0/All\n")
        sys.exit(1)
elif len(sys.argv) == 2:
    subprocess.call(['python','optimize.py', sys.argv[1]])
elif len(sys.argv) == 3:
    subprocess.call(['python','optimize.py', sys.argv[1], sys.argv[2]])
else:  
    sys.stderr.write("Usage: python generate.py csv_to_use (optional) position (optional) \n")
    sys.exit(1)



