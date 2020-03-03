# XFL-Fantasy-Football
  An application that presents the live fantasy football scores using standard ESPN scoring of a list of players for a given weekend of games using beautiful soup web scraping.


# Work In Progress 
  This is a person project That I am working on between my work at Clemson University. I plan to update weekly with a new feture or system the fallowing section shows of each weeks work, along with some of the challenges and soulutions.
  
## Week 0
 This week I prototyped some of the core features of the system. I mainly wanted to see if I would be able pull information from a website (specifically stats.xfl.com) as its updated live with the game. I decided to use the request library along with beautiful soup to do this. I ran into trouble becuse this is a dynamic website the html source uses javaScript witch I am not very familiar with. I was able to get it working in what seams like a convoluted way. Needs updating.
  I was also able to nail down some of my basic objects. Although I think I have too much bad coupling between the objects that made the porject become unweildly quickly. By the end of the week I was able to get the scores to update live with the game although there are a few bugs.
  
## Week 1
  Updated the Team class and added intial code to the game.py that will scrape from the xfl team websites the roster data to populate the rosters attribute of team calss with players.objs. This will allow me to be more flexable in feture devlopment as I know at the begining I have all the teams in my programs with all the players postions things. If need to combine this new functionallity with with old, that is pulling yards from live games to get most of the functionality i am looking for.
