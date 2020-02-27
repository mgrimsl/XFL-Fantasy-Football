
import game
import sys

def main():
    game0 = game.Game('https://stats.xfl.com/5')
    game1 = game.Game('https://stats.xfl.com/6')
    
 

    games = [game0,game1]

    #  print (x.homeTeam.name)
    #  print (x.awayTeam.name)

    #PORTER= ['Porter','Seattle Dragons'      ,'M.McGloin','T.Cook'    ,'J.Butler' ,'N.Spruce'  ,'M.McKay'    ,'C.Pearson']
    #MITCH = ['Mitch' ,'Houston Roughnecks'   ,'J.Ta\'amu','D.Smith'   , 'E.Hood'  ,'D.Williams','C.Phillips' , 'J.Tolliver']
    #JOHN  = ['John'  ,'New York Guardians'   ,'A.Murray' ,'J.Pressley','D.Victor' ,'A.Proehl'  ,'N.Truesdell','D.Pierson-El']
    #MIKE  = ['Mike'  ,'St. Louis BattleHawks','P.Walker' ,'M.Jones'   , 'K.Farrow','E.Rogers'  , 'F.Nagel'   , 'A.Russell']    
    DUMMY = ['Dummy', 'New York Gaurdians', 'Hello']

#    Mike = game.FantasyTeam(MIKE,games)
 #   Mitch = game.FantasyTeam(MITCH,games)
  #  Porter = game.FantasyTeam(PORTER,games)
   # John = game.FantasyTeam(JOHN,games)
    Dummy = game.FantasyTeam(DUMMY,games)


 #   Mike.print_points()
  #  John.print_points()
  #  Porter.print_points()
  #  Mitch.print_points()
    Dummy.print_points()



    print(game0.awayTeam.score)

    
   # print(game0.homeTeam.yards)
   # print(game0.awayTeam.yards)

    #game.print_renegades()
    



if __name__ == "__main__":
    main()