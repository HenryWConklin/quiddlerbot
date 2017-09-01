from wordsWithLetters import uwordsl, wordse, letterHash, charMap

import csv
cardpoints = {}
class Deck:
    def __init__(self, cards):
        self.cards = cards
    
    # Number of cards left in the deck
    def ncardsleft(self):
        s = 0
        for c in self.cards:
           s += self.cards[c]
        return s

    # Expected point value of a card drawn from the deck
    def expval(self):
        return float(sum([self.cards[x]* cardpoints[x] for x in self.cards]))/self.ncardsleft()

    # Card with highest probability to be drawn
    def maxprob(self):
        return max(self.cards, key=lambda x: self.cards[x])

    # Card with maximum expected value 
    def maxval(self):
        return max(self.cards, key=lambda x: self.cexval(x))

    # Number of a given card left in the deck
    def nleft(self, c):
        return self.cards[c]

    # Point value of given card
    def cpoints(self, c):
        return cardpoints[c]

    def remove(self,c):
        self.cards[c] -= 1
        return self.cards[c]
    # Expected value of a given card, probability of drawing * point value
    def cexval(self,c):
        return float(self.cards[c])/self.ncardsleft() * cardpoints[c]

def scoreWord(h):
    ps = 0
    for c in charMap:
        while h % charMap[c] == 0:
            h/=charMap[c]
            ps += cardpoints[c]
    return ps

# Returns a triplet of (points, all cards used, words)
def evalHand(h, ws = None):
    res = _evalHand(letterHash(h), ws)
    return res[0], res[1], res[2]
def _evalHand(lh, ws = None):
    ws = sorted(uwordsl(lh, ws), key=lambda x: -len(x[0]))
    if not ws and lh == 1:
        return (0,True,[])
    elif not ws: 
        return (-scoreWord(lh), False,[])
    else:
        maxp = 0
        maxo = False
        maxw = []
        for w in ws:
            cp, co, cw = evalHand(lh/w[1], ws)
            cp += scoreWord(w[1])
            if cp > maxp:
                maxp = cp
                maxo = co
                maxw = [w] + cw
            if maxo:
                break
        return maxp, maxo, maxw

def chooseDiscard(h):
    max = (-1, False, [])
    maxd = ''
    for j in h:
        lhand = list(h)
        lhand.remove(j)
        curr = evalHand(lhand)
        if curr > max or maxd == '':
            maxd = j
            max = curr
    return max, maxd

def readCard(p):
    res = raw_input(p).strip()
    while res not in cardpoints:
        print "Invalid card"
        res = raw_input(p).strip()
    return res

def readChoice(p, cs):
    res = raw_input("{} ({}): ".format(p, ", ".join(cs))).strip()
    while res not in cs:
        print "Invalid choice"
        res = raw_input(p).strip() 
    return res

def loadDeck():
    cards = {}
    with open('cardcounts.csv') as ifile:
        creader = csv.reader(row for row in ifile if not row.startswith('#'))
        for row in creader:
            cards[row[0]] = int(row[1])
            cardpoints[row[0]] = int(row[2])
    return Deck(cards)

if __name__ == "__main__":

    d = loadDeck() 
    r = int(readChoice("Starting round", map(str, range(1,9))))
    myscore = 0
    opscore = 0
    ophand = []
    myhand = []
    ophandscore = 0
    myhandscore = 0
    mycanout = False
    myws = []
    topcard = ''
    while r <= 8:
        turn = readChoice("Who first", ['cpu', 'opponent'])
        turn = (turn == 'cpu')
        # Draw new hand
        ophand = []
        myhand = []
        print "Round " + str(r)
        print "Deal me a hand"
        for i in range(r+2):
            myhand.append(readCard("Card #{:d}: ".format(i+1)))
        print "My hand: {}".format(", ".join(myhand))

        for x in myhand:
            d.remove(x)

        # Get the top discard card
        topcard = readCard("Discard top: ")
        d.remove(topcard)
        
        # Predict opponent's hand value as expected value of deck
        ophandscore = (r+2) * d.expval()
        print "Expected opponent hand value: {:.2f}".format(ophandscore)
        
        # Turn loop
        turnc = 1
        firstOut = None
        while True:
            # If CPU's turn first
            if turn:
                myhandscore,canout, ws = evalHand(myhand)
                print
                print "Turn {}".format(turnc)
                print "Current score: " + str(myhandscore)
                print "Can make: " + ", ".join(map(lambda x: x[0], ws))
                print ("Can" if canout else "Can't") + " go out"
                print

                # Calculate expected value of draw from deck
                drawsum = 0
                for c in d.cards:
                    if d.nleft(c) == 0:
                        continue
                    drawsum += d.nleft(c) * chooseDiscard(myhand + [c])[0][0]
                    print chooseDiscard(myhand + [c])
                drawsum /= float(d.ncardsleft())
                print "Expected value from deck: " + str(drawsum)

                discard = chooseDiscard(myhand + [topcard])
                print discard
                print "Discard value: " + str(discard[0][0])
                print

                if discard[0][0] >= drawsum:
                    print "I want a the discard, " + topcard
                    myhand = myhand + [topcard]

                    dres = chooseDiscard(myhand) 
                    print "Discard the: " + dres[1]
                    topcard = dres[1]

                    myws = map(lambda x: x[0], dres[0][2])
                    print
                    print "New score: " + str(dres[0][0])
                    print "With: " + ", ".join(myws)

                    myhand.remove(dres[1])
                    myhandscore = dres[0][0]
                    mycanout = dres[0][1]
                else:
                    print "I want to draw a card."
                    dcard = readCard("Draw: ")
                    d.remove(dcard)
                    myhand = myhand + [dcard]

                    dres = chooseDiscard(myhand) 
                    print "Discard the: " + dres[1]
                    topcard = dres[1]
                    myws = map(lambda x: x[0], dres[0][2])
                    print
                    print "New score: " + str(dres[0][0])
                    print "With: " + ", ".join(myws)

                    myhand.remove(dres[1])
                    myhandscore = dres[0][0]
                    mycanout = dres[0][1]

                print
                # Go out if think better than predicted opponent hand
                if myhandscore > ophandscore and mycanout:
                    print "I want to go out"
                    print "My hand is: " + ", ".join(myws)
                    print "For {:d} points.".format(myhandscore)
                    print
                    firstOut = 'cpu'
                    break
                print
                turn = not turn


            # Opponent's turn
            opac = readChoice("Opponent's action", ['draw', 'discard'])
            if opac == 'discard':
                ophand.append(topcard)
            
            topcard = readCard("Opponent's discard: ")
            if topcard in ophand:
                ophand.remove(topcard)
            else:
                d.remove(topcard)

            opac = readChoice("Opponent goes out", ['y','n'])
            if opac == 'y':
                firstOut = 'opponent'
                break
            turn = not turn
        

        # If opponent went out, have one more turn
        if firstOut == 'opponent':
        
            # Get to see opponent's hand
            print "Opponent's known hand: " + ", ".join(ophand)
            noph = []
            for x in range(r+2):
                rc = readCard("Opponent's hand #{:d}: ".format(x))
                noph.append(rc)
                if rc in ophand:
                    ophand.remove(rc)
                else:
                    d.remove(c)
            ophand = noph

            
            myhandscore,canout, ws = evalHand(myhand)
            print
            print "Current score: " + str(myhandscore)
            print "Can make: " + ", ".join(map(lambda x: x[0], ws))
            print ("Can" if canout else "Can't") + " go out"
            print

            # Calculate expected value of draw from deck
            drawsum = 0
            for c in d.cards:
                if d.nleft(c) == 0:
                    continue
                drawsum += d.nleft(c) * chooseDiscard(myhand + [c])[0][0]
                print chooseDiscard(myhand + [c])
            drawsum /= float(d.ncardsleft())
            print "Expected value from deck: " + str(drawsum)

            discard = chooseDiscard(myhand + [topcard])
            print "Discard value: " + str(discard[0][0])
            print

            if discard >= drawsum:
                print "I want a the discard, " + topcard
                myhand = myhand + [topcard]

                dres = chooseDiscard(myhand) 
                print "Discard the: " + dres[1]
                topcard = dres[1]

                myws = map(lambda x: x[0], dres[0][2])
                print "New score: " + str(dres[0][0])
                print "With: " + ", ".join(myws)

                myhand.remove(dres[1])
                myhandscore = dres[0][0]
                mycanout = dres[0][1]
            else:
                print "I want to draw a card."
                dcard = readCard("Draw: ")
                d.remove(dcard)
                myhand = myhand + [dcard]

                dres = chooseDiscard(myhand) 
                print "Discard the: " + dres[1]
                topcard = dres[1]
                myws = map(lambda x: x[0], dres[0][2])
                print "New score: " + str(dres[0][0])
                print "With: " + ", ".join(myws)

                myhand.remove(dres[1])
                myhandscore = dres[0][0]
                mycanout = dres[0][1]

        # CPU out first, opponent gets one more turn
        else:

            # Opponent's turn
            opac = readChoice("Opponent's action", ['draw', 'discard'])
            if opac == 'discard':
                ophand.append(topcard)
            
            topcard = readCard("Opponent's discard: ")
            if topcard in ophand:
                ophand.remove(topcard)
            else:
                d.remove(topcard)


            # Get to see opponent's hand
            print "Opponent's known hand: " + ", ".join(ophand)
            noph = []
            for x in range(r+2):
                rc = readCard("Opponent's hand #{:d}: ".format(x))
                noph.append(rc)
                if rc in ophand:
                    ophand.remove(rc)
                else:
                    d.remove(c)
            ophand = noph

            
            myhandscore,canout, ws = evalHand(myhand)
            print
            print "Current score: " + str(myhandscore)
            print "Can make: " + ", ".join(map(lambda x: x[0], ws))
            print ("Can" if canout else "Can't") + " go out"
            print

        print

        opres = evalHand(ophand)
        print "Opponent result: " + str(opres)
        opscore += max(0, opres[0])
        myscore += max(0,evalHand(myhand)[0]) 
        print
        print "New score: {:d} me, {:d} opponent".format(myscore,opscore)
        print
        r += 1     

