import requests
from bs4 import BeautifulSoup
from requests_html import HTMLSession
import re


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


class Game:
    
    def __init__(self,url):
        self.winner = None
        self.gameStats = get_section(url, OFF_SECTION)
        gameInfo = get_section(XFL_GAME1, TEAM_SECTION)
        self.awayTeam = Team(self.gameStats[:4],gameInfo[0])  
        self.homeTeam = Team(self.gameStats[4:],gameInfo[1])

        
    
    def print(self):
        self.awayTeam.print()
        self.homeTeam.print()
        
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
   
    def __init__(self, stats, teamInfo):
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

        nameRaw = stats[3]
        
        self.name = process_data(nameRaw,NAME)
        self.populate_roster(stats[:3])
        self.set_points()
        self.set_score(teamInfo)
        self.pull_yards()

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
    def __init__(self, data):
        self.number = -1
        self.name = "John Doe"
        self.rushYards = 0
        self.passYards = 0
        self.recivingYards = 0
        self.rushTds = 0
        self.passTds = 0
        self.recvTds = 0
        self.ints = 0
        self.fumb = 0
        self.points = 0

        self.number = process_data(data, 'jerseyNumber')
        self.name = process_data(data, PLAYERNAME)


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
def get_rosters():
    session = HTMLSession()

    page = session.get('https://www.xfl.com/en-US/teams/dallas/renegades-articles/dallas-renegades-roster')

    soup2 = BeautifulSoup(page.content, PARSER)
    script = soup2.find_all('script')
    
    
    for tags in script:
       
        if ((tags.text.find('"title":"Dallas Renegades roster"')) >= 0):
          
            rosterData = tags.text[(tags.text.find('College')):]
            print('FOUND IT')
            rosterData = rosterData.replace('</td>', '').replace('\\','')

            print(rosterData)



RENEGADES = [['1'],['Jazz'],['Ferguson'],['WR'],['6-5'],['218'],['Northwestern State']],[['2'],['Drew'],['Galitz'],['P'],['6-0'],['191'],['Baylor']],[['3'],['Flynn'],['Nagel'],['WR'],['5-11'],['195'],['Northwestern']],[['7'],['Eric'],['Dungey'],['QB'],['6-3'],['236'],['Syracuse']],[['8'],['Austin'],['MacGinnis'],['K'],['5-11'],['176'],['Kentucky']],[['9'],['Philip'],['Nelson'],['QB'],['6-2'],['209'],['East Carolina']],[['11'],['Joshua'],['Crockett'],['WR'],['6-2'],['192'],['Central Oklahoma']],[['12'],['Landry'],['Jones'],['QB'],['6-4'],['234'],['Oklahoma']],[['13'],['Jeff'],['Badet'],['WR'],['5-11'],['178'],['Oklahoma']],[['16'],['Jerrod'],['Heard'],['WR'],['6-2'],['203'],['Texas']],[['18'],['Freddie'],['Martino'],['WR'],['6-0'],['208'],['North Greenville']],[['20'],['Tenny'],['Adewusi'],['S'],['6-0'],['205'],['Delaware']],[['21'],['Micah'],['Abernathy'],['S'],['6-0'],['198'],['Tennessee']],[['22'],['Marquis'],['Young'],['RB'],['6-0'],['216'],['Massachusetts']],[['23'],['Josh'],['Thornton'],['CB'],['5-11'],['183'],['Southern Utah']],[['24'],['Treston'],['Decoud'],['CB'],['6-2'],['208'],['Oregon State']],[['25'],['Lance'],['Dunbar'],['RB'],['5-9'],['192'],['North Texas']],[['26'],['Donatello'],['Brown'],['CB'],['6-0'],['185'],['Valdosta State']],[['27'],['Austin'],['Walter'],['RB'],['5-8'],['197'],['Rice']],[['28'],['Josh'],['Hawkins'],['CB'],['5-10'],['190'],['East Carolina']],[['31'],['Derron'],['Smith'],['S '],['6-0'],['197'],['Fresno State']],[['34'],['Cameron'],['Artis-Payne'],['RB'],['5-10'],['215'],['Auburn']],[['40'],['Tre'],['Watson'],['LB'],['6-1'],['240'],['Maryland']],[['41'],['Dashaun'],['Phillips'],['CB'],['5-11'],['191'],['Tarleton State']],[['43'],['Christian'],['Kuntz'],['LB'],['6-2'],['237'],['Duquesne']],[['44'],['Hau\'oli'],['Kikaha'],['OB'],['6-3'],['250'],['Washington']],[['45'],['Doyin'],['Jibowu'],['S'],['6-1'],['196'],['Fort Hays State']],[['46'],['Tegray'],['Scales'],['LB'],['6-1'],['236'],['Indiana']],[['47'],['Tobenna'],['Okeke'],['OLB'],['6-3'],['251'],['Fresno State']],[['48'],['Greer'],['Martini'],['LB'],['6-4'],['233'],['Notre Dame']],[['49'],['Donald'],['Parham'],['TE'],['6-8'],['257'],['Stetson']],[['50'],['Reshard '],['Cliett'],['LB'],['6-2'],['243'],['South Florida']],[['51'],['Ray Ray'],['Davison'],['LB'],['6-3'],['231'],['California']],[['52'],['John'],['Keenoy'],['OG'],['6-3'],['295'],['Western Michigan']],[['55'],['James'],['Folston'],['OB'],['6-4'],['238'],['Pittsburgh']],[['57'],['Frank'],['Alexander'],['DE'],['6-4'],['282'],['Oklahoma']],[['58'],['Asantay'],['Brown'],['LB'],['6-0'],['229'],['Western Michigan']],[['59'],['Johnathan'],['Calvin'],['OB'],['6-3'],['254'],['Mississippi State']],[['61'],['Maurquice'],['Shakir'],['OG'],['6-3'],['311'],['Middle Tennessee']],[['62'],['Darius'],['James'],['OT'],['6-4'],['315'],['Auburn']],[['64'],['Salesi'],['Uhatafe'],['OG'],['6-4'],['332'],['Utah']],[['65'],['Alex'],['Balducci'],['OC'],['6-4'],['300'],['Oregon']],[['66'],['Josh'],['Allen'],['OG'],['6-2'],['280'],['UL Monroe']],[['70'],['Willie'],['Beavers'],['OT'],['6-5'],['320'],['Western Michigan']],[['71'],['Justin'],['Evans'],['OT'],['6-6'],['335'],['South Carolina State']],[['77'],['Pace'],['Murphy'],['OT'],['6-6'],['310'],['Northwestern State']],[['80'],['Sean'],['Price'],['TE/H'],['6-3'],['252'],['South Florida']],[['86'],['Julian'],['Allen'],['TE/H'],['6-2'],['244'],['Southern Mississippi']],[['91'],['Tomasi'],['Laulile'],['DT'],['6-3'],['318'],['BYU']],[['93'],['Tony'],['Guerad'],['DT'],['6-4'],['326'],['UCF']],[['96'],['Winston'],['Craig'],['DE'],['6-3'],['299'],['Richmond']],[['98'],['Gelen'],['Robinson'],['DE'],['6-1'],['302'],['Purdue']]
DEFENDERS = [['1'],['DeAndre'],['Thompkins'],['WR'],['5-11'],['187'],['Penn State']],[['2'],['Ty'],['Rausa'],['K'],['5-9'],['189'],['Boise State']],[['3'],['Tyree'],['Jackson'],['QB'],['6-7'],['250'],['Buffalo']],[['4'],['Eli'],['Rogers'],['WR'],['5-11'],['176'],['Louisville']],[['7'],['Hunter'],['Niswander'],['P'],['6-5'],['230'],['Northwestern']],[['9'],['Jalen'],['Rowell'],['WR'],['6-4'],['220'],['Air Force']],[['10'],['Simmie '],['Cobbs'],['WR'],['6-3'],['220'],['Indiana']],[['12'],['Cardale'],['Jones'],['QB'],['6-5'],['264'],['Ohio State']],[['15'],['Rashad'],['Ross'],['WR'],['6-0'],['180'],['Arizona St. ']],[['16'],['Tyler'],['Palka'],['WR'],['6-0'],['197'],['Gannon']],[['19'],['Malachi'],['Dupre'],['WR'],['6-4'],['195'],['LSU']],[['20'],['Carlos'],['Merritt'],['S'],['6-0'],['190'],['Campbell']],[['21'],['Doran'],['Grant'],['DB'],['5-10'],['195'],['Ohio State']],[['22'],['Matt'],['Elam'],['S'],['5-10'],['205'],['Florida']],[['24'],['Donnel'],['Pumphrey'],['RB'],['5-8'],['178'],['San Diego State']],[['25'],['Desmond'],['Lawrence'],['DB'],['5-11'],['187'],['North Carolina']],[['26'],['Jhurell'],['Pressley'],['RB'],['5-10'],['209'],['New Mexico']],[['28'],['Elijah'],['Campbell'],['DB'],['5-11'],['192'],['Northern Iowa']],[['29'],['Tyree'],['Kinnel'],['S'],['5-11'],['210'],['Michigan']],[['31'],['Nick'],['Brossette'],['RB'],['5-11'],['210'],['Louisiana State']],[['32'],['Khalid'],['Abdullah'],['RB'],['5-9'],['226'],['James Madison']],[['38'],['Shamarko'],['Thomas'],['S'],['5-9'],['205'],['Syracuse']],[['42'],['Brian'],['Khoury'],['LS'],['6-3'],['238'],['Carnegie Mellon']],[['45'],['Rahim'],['Moore'],['S'],['6-1'],['196'],['UCLA']],[['51'],['Dorian'],['Johnson'],['OG'],['6-5'],['291'],['Pittsburgh']],[['52'],['Jonathan'],['Celestin'],['ILB'],['6-0'],['227'],['Minnesota']],[['53'],['Jameer'],['Thurman'],['ILB'],['6-0'],['223'],['Indiana State']],[['54'],['Jonathan'],['Massaquoi'],['LB'],['6-2'],['265'],['Troy']],[['55'],['Antwione'],['Williams'],['MLB'],['6-3'],['245'],['Georgia Southern']],[['56'],['KeShun'],['Freeman'],['OLB'],['6-2'],['259'],['Georgia Tech']],[['58'],['Scooby'],['Wright'],['ILB'],['6-0'],['228'],['Arizona']],[['59'],['A.J.'],['Tarpley'],['ILB'],['6-2'],['225'],['Stanford']],[['64'],['Jon'],['Toth'],['OC'],['6-5'],['298'],['Kentucky']],[['69'],['Cole'],['Boozer'],['OT'],['6-5'],['306'],['Temple']],[['72'],['Logan'],['Tuley-Tillman'],['OT'],['6-6'],['308'],['Michigan']],[['74'],['Rishard'],['Cook'],['OG'],['6-3'],['364'],['Alabama-Birmingham']],[['75'],['Chris'],['Brown'],['OG'],['6-4'],['315'],['Southern California']],[['77'],['James'],['O\'Hagan'],['OC'],['6-2'],['299'],['Buffalo']],[['78'],['Malcolm'],['Bunche'],['OT'],['6-6'],['326'],['UCLA']],[['79'],['De\'Ondre'],['Wesley'],['OT'],['6-6'],['320'],['Brigham Young']],[['80'],['Donnie'],['Ernsberger'],['TE'],['6-3'],['241'],['Western Michigan']],[['85'],['Derrick'],['Hayward'],['TE'],['6-5'],['260'],['Maryland']],[['86'],['Khari'],['Lee'],['TE'],['6-4'],['255'],['Bowie State']],[['90'],['Siupeli'],['Anau'],['DT'],['6-2'],['286'],['Northern Arizona']],[['91'],['Tavaris'],['Barnes'],['DE'],['6-4'],['267'],['Clemson']],[['92'],['Elijah'],['Qualls'],['NT'],['6-1'],['337'],['Washington']],[['93'],['Tracy'],['Sprinkle'],['DT'],['6-2'],['287'],['Ohio State']],[['94'],['Kalani'],['Vakameilalo'],['NT'],['6-3'],['322'],['Oregon State']],[['95'],['Kenny'],['Bigelow'],['DT'],['6-3'],['308'],['West Virginia']],[['96'],['Jay'],['Bromley'],['DT'],['6-3'],['297'],['Syracuse']],[['99'],['Sam'],['Montgomery'],['OLB'],['6-3'],['248'],['Louisiana State']]
def print_renegades():
    for item in RENEGADES:
        print(item)


