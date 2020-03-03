import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re

ROSTER_URLS = {'Dallas Renegades':'https://www.xfl.com/en-US/teams/dallas/renegades-articles/dallas-renegades-roster', 'DC Defenders':'https://www.xfl.com/en-US/teams/washington-dc/defenders-articles/dc-defenders-roster', 'Houston Roughnecks': 'https://www.xfl.com/en-US/teams/washington-dc/defenders-articles/dc-defenders-roster', 'Los Angeles Wildcats':'https://www.xfl.com/en-US/teams/los-angeles/wildcats-articles/la-wildcats-roster', 'New York Guardians':'https://www.xfl.com/en-US/teams/new-york/guardians-articles/new-york-guardians-roster', 'St.Loius BattleHawks': 'https://www.xfl.com/en-US/teams/st-louis/battlehawks-articles/st-louis-battlehawks-roster', 'Seattle Dragons':'https://www.xfl.com/en-US/teams/seattle/dragons-articles/seattle-dragons-roster', 'Tampa Bay Vipers': 'https://www.xfl.com/en-US/teams/tampa-bay/vipers-articles/tampa-bay-vipers-roster'}
TEAMS = {}
TEAM_LIST = ['Dallas Renegades', 'DC Defenders', 'Houston Roughnecks', 'Los Angeles Wildcats', 'New York Guardians', 'St.Loius BattleHawks', 'Seattle Dragons', 'Tampa Bay Vipers']

XFL_GAME1 = 'https://stats.xfl.com/5'
PARSER = 'html.parser'
OFF_SECTION = 'var offensiveStats = {"away":{'
TEAM_SECTION = 'var teamStats = {'




NAME = 'name'
PLAYER = 'player:'
RUSHING = 'rushing:'
RECEIVING = 'receiving:'
PASSING = 'passing:'
PLAYERNAME = 'displayName'
YARDS = 'yards'
TDS = 'touchdowns'
INTS = 'interceptions'

MAX_TEAM_SIZE = 16
MAX_START_SIZE = 9

FANT_PASS = 25
FANT_RUSH = 10
FANT_TDS = 6
FANT_PASS_TDS = 4
FANT_INTS = -2
FANT_FUMB = -1

FANT_DEFAULT = 10
FANT_YARD_AGN = -100
FANT_POINT_AGN = -10
FANT_DEF_TO = 1
FANT_DEF_SCORE = 3


ERROR1 = '\n**Error Here**'
ERR_ROST_FULL = "\n***ROSTER FULL***"
ERR_START_FULL = "\n**CAN ONLY START 9 PLAYERS"
ERR_NOT_REMOVED = "player is not in list"


def init():
    for item in TEAM_LIST:
        temp = Team(item)
        TEAMS[item] = temp

    pass

class Game:
    
    def __init__(self,url):
        self.winner = None
        self.gameStats = get_section(url, OFF_SECTION)
        gameInfo = get_section(XFL_GAME1, TEAM_SECTION)
        #self.awayTeam = Team(self.gameStats[:4],gameInfo[0])  
        #self.homeTeam = Team(self.gameStats[4:],gameInfo[1])
        self.awayteam = process_data(self.gameStats[3],NAME)
        self.hometeam = process_data(self.gameStats[7],NAME)
        pass
        
    
    def print(self):
        pass
        
class FantasyTeam:
    def __init__(self, ros, games):
        self.points = 10
        self.players = {}
        self.starting = {}
        self.defense = ros[1]
        self.name = ros[0]
        self.starters = ros[2:]

        self.get_points(games)

    
    def get_points(self, games):
    
        for x in games:
                if x.homeTeam.name == self.defense:
                    self.points+=int(x.awayTeam.yards/FANT_YARD_AGN)
                    self.points+=int(x.awayTeam.TDs*-1)
                    self.points+=int(x.awayTeam.giveAways*FANT_DEF_TO)
                    self.points+=int(x.awayTeam.DTD*3)
                if x.awayTeam.name == self.defense:
                    self.points+=int(x.homeTeam.yards/FANT_YARD_AGN)
                    self.points+=int(x.homeTeam.TDs*-1)
                    self.points+=int(x.homeTeam.giveAways*FANT_DEF_TO)
                    self.points+=int(x.homeTeam.DTD*3)

                for item in self.starters:
                    if x.homeTeam.roster.get(item, 0):
                        self.points += x.homeTeam.roster[item].points
                    if x.awayTeam.roster.get(item, 0):
                        self.points += x.awayTeam.roster[item].points
    
    def print_points(self):
        print(self.name, 'Has', self.points, 'points')

    def populate_random(self, playerList):
        pass
    def add_player(self, player):
        if len(self.players) < MAX_TEAM_SIZE:
            self.players[player.name] = player
        else:
            print(ERR_ROST_FULL)
    def start_player(self, key):
        if len(self.starting) < MAX_START_SIZE:
            self.starting[key] = self.players[key]
        else:
            print(ERR_START_FULL)
    def bench_player(self, key):
        if self.starting.pop(key,1) == 1:
            print(ERR_NOT_REMOVED)
                    
class Team:
   
    def __init__(self, name):
        

        

        self.roster = {}
        self.score = 0
        self.threePointXPAT = 0
        self.twoPointXPAT = 0
        self.onePointXPAT = 0
        self.FGs = 0
        self.TDs = 0
        self.yards = 0

        self.DTD = 0
        self.Sacks = 0
        self.interceptions = 0
        
        self.fumbLost = 0
        self.giveAways = 0

        self.points = 0

        #nameRaw = stats[3]
        #self.name = process_data(nameRaw,NAME)
        
        self.name = name

        self.set_roster(ROSTER_URLS[self.name])
        print("hello")
        #self.populate_roster(stats[:3])
        #self.set_points()
        #self.set_score(teamInfo)
        #self.pull_yards()

    def set_points(self):

        for player in self.roster.values():
            player.set_points()
            self.points += player.points

    def pull_yards(self):

        for x in self.roster.values():
            self.yards += x.passYards
            self.yards += x.rushYards
            self.TDs += x.passTds
            self.TDs += x.rushTds
            self.giveAways += x.ints + x.fumb
            
    def set_score(self, stats):
        
        self.score += 6*int(process_data(stats, "TDDefensive"))
        self.DTD = self.score
        self.score += 6*int(process_data(stats, "TDRushing"))
        self.score += 6*int(process_data(stats, "TDPassing"))
        self.onePointXPAT += 1*int(process_data(stats, "OnePointXPConverts"))
        self.twoPointXPAT += 2*int(process_data(stats, "TwoPointXPConverts"))
        self.threePointXPAT += 3*int(process_data(stats, "ThreePointXPConverts"))
        self.score += self.onePointXPAT + self.threePointXPAT + self.threePointXPAT
        self.FGs += 3*int(process_data(stats, "FGs"))
        self.score += self.FGs


        pass

    def set_roster(self,URL):
        rawRoster = self.get_rosters(URL)
        for listing in rawRoster:
            if len(listing.split()) != 0:
                player = Player(listing.split())
                self.roster[player.name] = player

    def populate_roster(self,stats):
        for data in stats:
            player_data = data.split(PLAYER)
            
            for player in player_data[1:]:
                playerObj = Player(player)
                
                if playerObj not in self.roster.values():
                    self.roster[playerObj.name] = playerObj
                if playerObj in self.roster.values() and player_data[0].find(RUSHING) >= 0 : 
                    for x in self.roster.values():
                        if x == playerObj:
                            x.set_rush(player)
                if playerObj in self.roster.values() and player_data[0].find(RECEIVING) >= 0:
                    for x in self.roster.values():
                        if x == playerObj:
                            x.set_recv(player)
                if playerObj in self.roster.values() and player_data[0].find(PASSING) >= 0:
                    for x in self.roster.values():
                        if x == playerObj:
                            x.set_pass(player)

    def get_rosters(self,URL):
    

        rawRoster = []
        procRoster = []
        session = HTMLSession()

        page = session.get(URL)

        soup = BeautifulSoup(page.content, 'html.parser')
        i = 0
        j = -1
        script = soup.find_all("td")

        for tags in script:
            if isinstance(tags.next,str):
                rawRoster.append(tags.next.replace("\'","-").replace('"','').replace(',','').replace('\xa0',''))
        ####################
        
        ####################
        if self.name == 'Seattle Dragons':
            for info in rawRoster:
                if info == 'P\xa0':
                    info = 'P'
            
                if i%5 == 0:
                    procRoster.append(info)
                    j+=1
                else:
                    procRoster[j]+=" "
                    procRoster[j]+=info
                i+=1 
            return procRoster  
        for info in rawRoster:
            if info == 'P\xa0':
                info = 'P'
            if info == '':
                continue

            if i%6 == 0:
                procRoster.append(info)
                j+=1
            else:
                procRoster[j]+=" "
                procRoster[j]+=info
            
            i+=1 
        return procRoster  

    def print_name(self):
        print(self.name)
    def print_TDS(self):
        print("TDs :  ",self.TDs)
    def print_yards(self):
        print("Yards :  ",self.yards)
    def print_roster(self):
        for player in self.roster.values():
            player.print()
    def print(self):
        self.print_name()
        self.print_yards()
        self.print_TDS()
        self.print_roster()
            
def process_data(data,find):
    splitData = data.split(",")
    cond = -1
    for items in splitData:
        cond = items.find(find)
        if cond >= 0:
            name = items.split(':')
            return name[1]
    return -1



class Player:
    def __init__(self, listing):
        self.pos = ''
        self.number = listing[0]
        self.name = listing[1]
        self.name += ' '
        self.name += listing[2]
        if listing[2] == 'III':
            self.name += ' '
            self.name += listing[3]
            self.pos += listing[4]
        else:
            self.pos = listing[3]
   

        

        self.rushYards = 0
        self.passYards = 0
        self.recivingYards = 0
        self.rushTds = 0
        self.passTds = 0
        self.recvTds = 0
        self.ints = 0
        self.fumb = 0
        self.points = 0

        #self.number = process_data(data, 'jerseyNumber')
        #self.name = process_data(data, PLAYERNAME)

    def set_points(self):
       self.points += int(self.rushYards/FANT_RUSH)
       self.points += int(self.recivingYards/FANT_RUSH)
       self.points += int(self.passYards/FANT_PASS)

       self.points += int(self.passTds*FANT_PASS_TDS)
       self.points += int(self.recvTds*FANT_TDS)
       self.points += int(self.rushTds*FANT_TDS)
       self.points += int (self.ints*FANT_INTS)

    def set_rush(self,data):
        self.rushYards = int(process_data(data, YARDS))
        self.rushTds = int(process_data(data, TDS))
        pass
    def set_pass(self,data):
        self.passYards = int(process_data(data, YARDS))
        self.ints = int(process_data(data, INTS))
        self.passTds = int(process_data(data, TDS))
        pass
    def set_recv(self,data): 
        self.recivingYards = int(process_data(data, YARDS))
        self.recvTds = int(process_data(data, TDS))
        pass
    def __eq__(self,other):
        return self.name == other.name
    def print(self):
        print(self.name, self.number, "Fantasy Points: " , self.points)
        print("         Yards TDs")
        print("Passing:  ", self.passYards, " ", self.passTds)
        print("Rushing:  ", self.rushYards, " ", self.rushTds)
        print("Receiving:", self.recivingYards, "", self.recvTds)
        print()
    def print_pass(self):
        print(self.passYards)
    def print_recv(self):
        print(self.recivingYards)
    def print_rush(self):
        print(self.rushYards)
    def print_recv_tds(self):
        print(self.recvTds)
    def print_rush_tds(self):
        print(self.rushTds)
    def print_pass_tds(self):
        print(self.passTds)

def get_html_data(URL):
    session = HTMLSession()

    page = session.get(URL)

    soup2 = BeautifulSoup(page.content, PARSER)
    script = soup2.find_all('script',type='text/javascript')
    
    return script

def get_section(url, section):
    count = 0 
    script = get_html_data(url)
    for tags in script:
        if tags.text.find(section) >= 0:
            rep = tags.text.replace(section,'').replace('{','').replace('}','').replace(']','home').replace('[','').replace('"','')
            split = rep.split('home')
            return split
        
        count +=1

def get_team_stats(url):
    
    
    pass






