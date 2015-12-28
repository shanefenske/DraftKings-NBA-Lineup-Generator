# Shane Fenske
# Uses the csv specified as arg1 else "player_data.csv" to find the optimum lineup for that day's fantasy basketball.
# scrape.py which generates the csv's implements a version of the momentum trading strategy by splitting players' last 
# 6 games into 2 sets of 2. If the average value of a player's last 2 games is worse than the average value of 
# the prior 2 then that player is ineligible for the optimized team. 
# If they are not eliminated based on this criteria, then the optimizer finds the lineup of # PG, SG, SF, PF, C, G, F, and UTIL.
# with the highest projected score for the night's game using the average score from the previous 3 games
# as the players projection.
import sys
import csv
from operator import itemgetter

# returns sum of projections for all players in lineup
def value(lineup):
    return sum([player[0] for player in lineup])

# returns cost of all players in lineup
def cost(lineup):
    return sum([player[1] for player in lineup])

# prints sorted list of best players at position
def topValues(position,items,pgs,sgs,sfs,pfs,cs,gs,fs):
    if(position == "forward"):
        printPlayerList(fs)
    if(position == "powerforward"):
        printPlayerList(pfs)
    if(position == "smallforward"):
        printPlayerList(sfs)
    if(position == "guard"):
        printPlayerList(gs)
    if(position == "pointguard"):
        printPlayerList(pgs)    
    if(position == "shootingguard"):
        printPlayerList(sgs) 
    if(position == "util"):
        printPlayerList(items)
    if(position == "center"):
        printPlayerList(cs)

# prints lineup nicely formatted
def printPlayerList(lineup):
    for player in lineup:
        print '%25s' %  player[2], '%3s' %  player[3], "Projection:", '%6s' %  player[0], '%5s' %  "$"+str(player[1]), "Value", round(player[4],2)                                          

salary = 50000

if len(sys.argv) == 1:
    sys.argv.append('player_data.csv')
try:
    f = open(sys.argv[1])
except:
    sys.stderr.write("Error opening first argument. If included, it must specify the name of csv to use.\n")
    sys.exit(1)    

reader = csv.reader(f)
reader.next()
items = []
for row in reader:
    items.append([float(row[7]),int(row[2]),row[1],row[0], float(row[7]) / (int(row[2]) / 1000)])

# sort by value
items = sorted(items, key=itemgetter(4), reverse=True)
pgs = [item for item in items if item[3] == "PG"]
sgs = [item for item in items if item[3] == "SG"]
sfs = [item for item in items if item[3] == "SF"]
pfs = [item for item in items if item[3] == "PF"]
cs = [item for item in items if item[3] == "C"]
gs = [item for item in items if item[3] == "SG" or item[3] == "PG"]
fs = [item for item in items if item[3] == "PF" or item[3] == "SF"]

# if position is included then print sorted position list
if len(sys.argv) == 3:
    topValues(sys.argv[2],items,pgs,sgs,sfs,pfs,cs,gs,fs)
    sys.exit(1)

util = False
g = False
f = False
firstThree = []

# first we will fill lineup spots G, F, and UTIL using the highest value players that can fill the 3 positions 
for item in items:
    if item[3] == "C" and not util:
        firstThree.append(item)
        util = True
    elif (item[3] == "PG" or item[3] == "SG") and not g:
        firstThree.append(item)
        g = True
    elif (item[3] == "PG" or item[3] == "SG") and g and not util:
        firstThree.append(item)
        util = True
    elif (item[3] == "SF" or item[3] == "PF") and not f:
        firstThree.append(item)
        f = True     
    elif (item[3] == "SF" or item[3] == "PF") and f and not util:
        firstThree.append(item)
        util = True                
    if len(firstThree) == 3:
        break

# now we will try every combination of lineups that are possible given position constraints and remaining salary
lineupValue = 0
salary = salary - cost(firstThree)

for pg in pgs:
    for sg in sgs:
        for sf in sfs:
            for pf in pfs:
                for c in cs:
                    currLineup = [pg,sg,sf,pf,c]
                    intersect = [val for val in firstThree if val in currLineup]
                    if cost(currLineup) <= salary and len(intersect) == 0:
                        currValue = value(currLineup)
                        if currValue > lineupValue:
                            lineupValue = currValue
                            lineup = currLineup

# combine G F and UTIL and just found 5
for player in firstThree:
    lineup.append(player)
lineupValue = value(lineup)

# Reccomendation and explanation generation
if lineupValue < 270:
    print """It is not recommended that you play DraftKings fantasy basketball today. The lineup we project to
    score the highest today only projects to score """ + str(lineupValue) + """points. Given the high variance of
    players' performance, this play is unlikely to score enough points to win. This lineup consisted of the 
    following players:"""
    print printPlayerList(lineup)
else:
    print "The following lineup is projected to score well enough to win the majority of DraftKings NBA 50-50s."
    print "Lineup cost:", cost(lineup) 
    print "Projected lineup score:", lineupValue
    printPlayerList(lineup)
    if lineupValue > 310:
        print """This lineup is projected to score extremely well and you should consider 
                    entering it in the riskier DraftKings contests."""
    else: 
        print """This lineup is projected to score good, but not great. You should consider 
                    entering it only in head to heads and 50-50s as they are lower risk"""               



