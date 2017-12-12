#!/usr/bin/python3

# # # # # # # # # # # # # # # # #
# SNOW DESTROYER 9000           #
# Snowball Fight Robot          #
# Model 101                     #
#                               #
# For ICS-3UI                   #
# 2016 - 2017                   #
#                               #
# By: Benjamin Raskin           #
#     Donny Ren                 #
#                               #
# (c) Benjamin Raskin and       #
#     Donny Ren 2017            #
# # # # # # # # # # # # # # # # #

from random import choice as random
from random import randint

RELOAD = "RELOAD"
THROW = "THROW"
DUCK = "DUCK"

#Refine these variables; for different bots a different set of values will work best
initialAggressiveness = 19 #19 is usually a good number
carefulDiminishingRate = 0.34 #Bigger number means more careful over time; should not be over 1.00
anticipationImportance = 2.4 #Normally 2.4 for unknown bot, 1.9 for human, and anything bigger than 50 for fun

aggressiveness = initialAggressiveness #Set sggressiveness
carefulness = 25 #This is the starting carefulness
anticipation = [RELOAD] #Change this to assume what


#Checking for an illegal move
def checkLegality(checkMove, myBalls, myDucksUsed):
  
  #check for illegal
  if checkMove != DUCK and checkMove != THROW and checkMove != RELOAD: return False
  elif myDucksUsed == 5 and checkMove == DUCK: return False
  elif myBalls == 0 and checkMove == THROW: return False
  elif myBalls == 10 and checkMove == RELOAD: return False

  #if all ok
  return True

  
#To check for "dumb" moves
def checkLogistics(checkMove, oppBalls, oppScore, myBalls, myDucksUsed):
  if oppBalls == 0 and checkMove == DUCK:
    #No ducking when opponent has no balls
    return False
  if oppBalls != 0 and oppScore == 2 and checkMove == RELOAD:
    #Do not reload when you are behind!
    if myBalls != 0 or myDucksUsed != 5:
      #Don't reload!
      return False
    else:
      #Unless you have to
      return True
  else:
    #Ok, your move is not dumb
    return True
  
  
#Anticipation is the opponent's predicted move through finding repetition in opponent's moves
#Anticipation is then put in as an influence on the bot's next move
def anticipateNextMove(oppMovesSoFar):
  foundMove = False
  #A set of possible next moves derived from all instances of previous moves from opp
  oppProbNextMoves = []
  #Check all possible repetitions of previous moves
  for i in range(len(oppMovesSoFar), 0, -1):
    #Previous moves
    pastOppMoves = oppMovesSoFar[-i:]
    #Checking through the entire array
    for j in range(len(oppMovesSoFar) - i): # No need checking itself hence the " - i "
      #If the moves currently being checked match opponent's previous moves
      if oppMovesSoFar[j:j+i] == pastOppMoves:
        #If the longer pastOppMoves are the more importance is placed on likelyhood of it appearing as opponents next move
        for k in range(i**2):
          #Add the predicted next move to probable next move array
          oppProbNextMoves.append(oppMovesSoFar[j + i])
          #Found a move!
          foundMove = True
  #If no moves are found then return "None"
  if foundMove == False:
    #*** Here is what it filters out -- the "None" (Refer to function checkLegality to see what I mean)
    return "None"
  #If a move is found then return the most occuring instance of a move in the set of probable moves
  return max(set(oppProbNextMoves), key=oppProbNextMoves.count)


#This should return the correct move for the given opponent's move
def getNextCorrectMove(checkMove, oppMovesSoFar):
  #If opponent is going to reload then throw or reload
  #Throwing should be more dominant later in the game
  if checkMove == RELOAD:
    return [THROW] * int(len(oppMovesSoFar) / 4) + [RELOAD] # every four turns there is a bigger probability of getting throw
  #If opponent is going to throw then duck
  elif checkMove == THROW:
    return [DUCK]
  #If opponent is going to duck then reload
  elif checkMove == DUCK:
    return [RELOAD]
  #If no move is anticipated then return a blank move
  elif checkMove == "None":
    #This will be caught by the check legality function
    return []

  
#Aggression is the immediate analysis of the game state, returning the best move of the current situation
#Aggression is refreshed every turn, so there it is not influenced by the previous turns' outcomes
def getCurrentAggression(myScore, myBalls, myDucksUsed, oppScore, oppBalls, oppDucksUsed):
  global aggressiveness
  
  #Set it to initial aggressiveness every single turn
  aggressiveness = initialAggressiveness
  
  #For each difference in score aggressiveness is adjusted accordingly
  aggressiveness += ((myScore - oppScore) * 2) ** 5 / 2
  
  #How many snowballs each player has also plays a role in determining aggressiveness
  #My amount of snowballs is weighted heavier than opponent's snowballs
  aggressiveness += myBalls ** 3
  aggressiveness -= oppBalls ** 2
  #Then the difference in snowballs is noted
  aggressiveness += 2 * (myBalls - oppBalls)
  
  #If opponent has no snowballs then attack!
  if oppBalls == 0:
    aggressiveness += 20
  
  #Take into account how many ducks have been used
  aggressiveness += myDucksUsed - 2 #If have lots of ducks go defensive
  aggressiveness += oppDucksUsed ** 2 #The amount of ducks opponent used is a big influence
  #Should not have negative aggression -- negative numbers cannot be raised to fractional power
  if aggressiveness < 0:
    aggressiveness = 0
  #Retrun final aggressiveness value
  return aggressiveness


#Carefulness is accumulated throughout the game; the more careful you are the bigger the tendency to duck
#Carefulness is obtained by a current assessment of the game situation, which is stored and added to every turn
def updateCarefulness(myScore, myBalls, myDucksUsed, oppScore, oppBalls, oppDucksUsed):
  global carefulness
  #Here is where carefulness diminishing rate does its role
  carefulness = int(carefulness * carefulDiminishingRate)
  
  #Increases significantly by opponent's score
  carefulness += (oppScore + 2) ** 3
  #Increases as opponent's stored snowballs increases
  carefulness += oppBalls
  #The greater my score is, the more carefulness can be sacrificed
  carefulness -= (myScore + 1) ** 2
  #The more snowballs stored up the less careful I should be
  carefulness -= 2 * myBalls
  #Get more careful later in the game when lots of ducks have been used
  #The strategy is not really conventional but it works against robots :)
  carefulness += myDucksUsed
  #If opponent used up all 5 ducks then they are more likely to throw instead of duck
  carefulness += oppDucksUsed
  
  #Finally make sure that carefulness is not less than 1
  if carefulness <= 1:
    carefulness = 1

    
#Main function
def getMove( myScore, myBalls, myDucksUsed, myMovesSoFar,
             oppScore, oppBalls, oppDucksUsed, oppMovesSoFar):
  global carefulness
  
  #Using all functions listed above to update values of agression, carefulness, and anticipation
  aggression = getCurrentAggression(myScore, myBalls, myDucksUsed, oppScore, oppBalls, oppDucksUsed)
  updateCarefulness(myScore, myBalls, myDucksUsed, oppScore, oppBalls, oppDucksUsed)
  anticipation = anticipateNextMove(oppMovesSoFar)
  
  #Next move means what should be used given an opponent's predicted move
  nextMove = getNextCorrectMove(anticipation, oppMovesSoFar)
  
  #To prevent division by zero
  if aggression - carefulness == 0:
    carefulness -= 1
  
  #rF is reload factor, tF is throw factor, dF is duck factor
  rF = int(120/abs((aggression - carefulness)))
  tF = int(aggression ** 1.8 / 15)
  dF = int(30 * (0.8 ** aggression) * carefulness)
  
  #Negative values are baaad - messes up the program
  factors = [rF, tF, dF]
  for factor in range(len(factors)):
    #Here set them all to 1 if they are less than 1
    if factors[factor] < 1:
      factors[factor] = 1
  #We want them all to be 1 or more
  #Reason being when you divide by 0.1 you get 10 times what you started with -- Not good
  rF, tF, dF = factors
   
  #These lines are only used for testing
  ##print("Aggressiveness: " + str(agression), "   Carefulness:", carefulness, "\nreloadChance =", rF, "   throwChance =", tF, "   duckChance =", dF)
  ##print("\nMaybe opponent will use", anticipation, ". If so, I will use", nextMove, " then\n")
  
  #Using an array of possible moves where ratios are used to pick next move
  possibleMoves = [THROW] * tF + [RELOAD] * rF + [DUCK] * dF + nextMove * int((tF + rF + dF) * anticipationImportance)
  
  #Choose the move from array
  #The porportional values of the moves play into account here
  move = random(possibleMoves)
  
  #Check legality of current move
  while checkLegality(move, myBalls, myDucksUsed) == False:
    #Remove all instances of the move from array if it is illegal
    possibleMoves = [x for x in possibleMoves if x != move]
    #Then choose another move
    move = random(possibleMoves)
  
  #Checking logistics of the new move
  while checkLogistics(move, oppBalls, oppScore, myBalls, myDucksUsed) == False:
    #Remove all instances of the bad/dumb move
    possibleMoves = [x for x in possibleMoves if x != move]
    #Choose new move
    move = random(possibleMoves)
  
  #Again check legality of the new move
  while checkLegality(move, myBalls, myDucksUsed) == False:
    #Remove illegal move
    possibleMoves = [x for x in possibleMoves if x != move]
    #New move
    move = random(possibleMoves)
  
  #Submit move to defeat the opponent!
  return move
