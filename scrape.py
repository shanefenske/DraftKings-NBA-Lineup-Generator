#Shane Fenske
# Not to be called by used. Walks from DraftKings nBA lobby into a contest
# and downloads that days Lineup of available players and their salaries
# into player_data.csv. It then searches for every player in this csv on basketball-reference.com,
# enters their individual page, and writes to player_data.csv the data it finds on their previous 4 games.
# Each player's projection is written as the avg of their last 2 games in the column 'lastTwo'
# If they scored more in th 2 games prior to their most recent 2 they are removed from player_data.csv
#  as we do not want players with negative momentum

import json
import re
import urllib2
import csv
from bs4 import BeautifulSoup
import os

# takes in list of games in BasketballReference json format and returns average points scored in these games
def avgPoints(games):
    return sum(d['pts'] for d in games) / len(games)

dkURL = "https://www.draftkings.com/"
brRefURL = "http://www.basketball-reference.com/" 

# gets json that populates DraftKings NBA lobby
lobby = urllib2.urlopen(dkURL + 'lobby#/NBA/0/All').read()
lobbyData = json.loads(re.search(r"packagedContests\s*=\s*(.*);", lobby).group(1))

# each DK contest is dict element of lobbyData list -- must make sure we get NBA one
lobbyData  = [d for d in lobbyData if "NBA" in d.get('n')]
contestDict = lobbyData[0] # only need one -- does not matter which
contestID = contestDict['id']

# enter individual contest webpage and download csv from the link on it, would be cleaner with json
# Use string as I did not realize the json library needs the online json to be cleaned up (see below with DFS data)
contest = urllib2.urlopen(dkURL + "contest/draftteam/" + str(contestID)).read()
contestInfo = re.search(r"contestData\s*=\s*?(.*?);", contest, flags=re.DOTALL).group(1)
idNums = "".join( filter(lambda x: 'contestTypeId' in x or 'draftGroupId' in x, contestInfo.split('\n')) )
ctID, gID  = re.findall(r'\d+', idNums)
csvURL =  dkURL + "lineup/getavailableplayerscsv?contestTypeId=" + ctID + "&draftGroupId=" + gID

f = urllib2.urlopen(csvURL)
data = f.read()
with open("player_data.csv", "wb") as file_f:
    file_f.write(data)

f = open('player_data.csv')
new = open('new_player_data.csv',"wb")
reader = csv.reader(f)
writer = csv.writer(new, lineterminator='\n')

all = []
row = next(reader)
row.append('prevTwo')
row.append('lastTwo')
all.append(row)

# loop through csv and search for each player on basketball reference populating prevTwo and lastTwo with scraped data
for row in reader:
    prevTwo, lastTwo = 0, 0  
    firstName = row[1].split()[0]
    lastName = row[1].split()[1]

    # Currently no NBA players with same name so can enter first search result -- should add safety checks in future
    searchURL = brRefURL + "search/search.fcgi?search=" + firstName + "+" + lastName
    search = urllib2.urlopen(searchURL)
    if searchURL != search.geturl():
        row.append(prevTwo)
        row.append(lastTwo)
        continue # if redirect then player has not played this year
    soup = BeautifulSoup(search.read(), 'html.parser')
    playerURL = brRefURL + soup.find("div", class_="search-item").find('a')["href"]
    #  get player's recent DFS data from basketball reference
    player = urllib2.urlopen(playerURL).read()

    # find json that populatates DFS graph
    player = re.search(r"dk_data\s*=\s*?(.*?);", player, flags=re.DOTALL)
    if player == None:
        row.append(prevTwo)
        row.append(lastTwo)
        continue # if redirect then player has not played this year
    player = player.group(1)

    # # remove remove trailing comma and lines that incluce javascript date functions to make it valid json
    player = re.sub(r',\s*}', '\n}',player)
    player = re.sub(r"\"date\"\s*:\s*sr_parseDate\(.*?\),", "", player, flags=re.DOTALL)
    player = re.sub(r"\"tickVals\"\s*:\s*(.*?)\],", "", player, flags=re.DOTALL)
    playerData = json.loads(player)
    games = playerData['games']
    if len(games) > 2:  
        prevTwo = avgPoints(games[-4:-2])
    if len(games) > 0:   
        lastTwo = avgPoints(games[-2:])

    row.append(prevTwo)
    row.append(lastTwo) 
    # only want to consider player if he has positive momentum
    if lastTwo > prevTwo:   
        all.append(row)



writer.writerows(all)
os.remove('player_data.csv') 
os.rename('new_player_data.csv', 'player_data.csv')



