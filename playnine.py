from random import shuffle, choice, random, uniform #uniform is used as uniform(5,10) 5 can be chosen, 10 cant but 9.9999 can
import tkinter as tk

"""
general plan:
- card class, simple
- deck class, also simple
- board class, (no pair class)
- player class
- game class
- maybe a population class, not sure though
- training class
"""

#TODO: fix logic at lines 449 and 480 (it's the same fix)

debugging = False
print_drawn = False

class Card():
	#A simple card, it just has a value
    def __init__(self, value):
        self.value = value
        self.visible_value = "F"

    def flip(self):
        self.visible_value = self.value

    def copy(self):
        c = Card(self.value)
        c.visible_value = self.visible_value
        return c

class Deck():
	#A deck, which is just a list of cards
    def __init__(self):
        self.cards = []
        self.fill_deck()
        self.shuffle()

    def fill_deck(self):
        for i in range(13):
            for j in range(7):
                self.cards.append(Card(i))
        for i in range(3):
            self.cards.append(Card(-5))

    def shuffle(self):
        shuffle(self.cards)

    def print(self):
        for card in self.cards:
            print(card.value)

    def draw(self):
        self.cards[0].flip()
        if print_drawn:
            print("Drew " + str(self.cards[0].visible_value))
        return self.cards.pop(0)

    def draw_face_down(self):
        return self.cards.pop(0)



class Board():

    NEITHER_FLIPPED = 0
    ONE_FLIPPED = 1
    BOTH_FLIPPED = 2
    BOTH_MATCH = 3

    def __init__(self):
        self.cards = []
        self.fill_blank()

    def fill_blank(self):
        for col in range(4):
            inner = []
            for row in range(2):
                inner.append(Card(69))
            self.cards.append(inner)

    def print(self):
        for row in range(2):
            for col in range(4):
                if isinstance(self.cards[col][row].visible_value, str):
                    print(" F", end = " ")
                else:
                    print("{:2}".format(self.cards[col][row].visible_value), end = " ")
            print("")

    def copy(self):
        new_board = Board()
        for col in range(4):
            for row in range(2):
                new_board.cards[col][row] = self.cards[col][row]
        return new_board
    
    def flip_all(self):
        for col in range(4):
            for row in range(2):
                self.cards[col][row].flip()

    def all_flipped(self):
        for col in range(4):
            for row in range(2):
                if self.cards[col][row].visible_value != self.cards[col][row].value:
                    return False
        return True

    def get_unflipped_locations(self):
        unflipped = []
        for col in range(4):
            for row in range(2):
                if self.cards[col][row].visible_value == "F":
                    unflipped.append((col, row))
        return unflipped

    def get_unmatched(self):
        unmatched = []
        for col in range(4):
            if self.get_state(col) == Board.ONE_FLIPPED or self.get_state(col) == Board.BOTH_FLIPPED:
                for row in range(2):
                    if self.cards[col][row].visible_value != "F":
                        unmatched.append(self.cards[col][row].visible_value)
        # if debugging:
        #     print("get unmatched called, it returned:")
        #     print(unmatched)
        return unmatched

    def get_highest_unmatched(self):
        if len(self.get_unmatched()) > 0:
            return max(self.get_unmatched())
        else: return None

    def get_across_from_highest(self):
        highest = -6
        location = None
        realrow = None
        valrow = None
        for col in range(4):
            if self.get_state(col) == Board.ONE_FLIPPED:
                for row in range(2):
                    if self.cards[col][row].visible_value == "F":
                        realrow = row
                    else:
                        valrow = row #this is stupid but I think it should work
                val = self.cards[col][valrow].value
                if val > highest:
                    highest = val
                    location = (col, realrow)#there's a chance this doesn't work, but I think it should
        if debugging and location != None:
            print("Across from highest is at " + str(location[0]) + " and " + str(location[1]))
        return location

    def get_location(self, card_val):
        for col in range(4):
            for row in range(2):
                if self.get_state(col) != Board.BOTH_MATCH and self.get_state(col) != Board.NEITHER_FLIPPED:
                    if self.cards[col][row].visible_value == card_val:
                        return (col, row)

    def get_unflipped(self, col):
        if self.get_state(col) != Board.ONE_FLIPPED:
            return -1
        if self.cards[col][0].visible_value == "F":
            return 0
        else:
            return 1

    def get_matches(self):
        matches = []
        for col in range(4):
            if self.get_state(col) == Board.BOTH_MATCH:
                matches.append(self.cards[col][0])
        return matches

    def get_state(self, col):
        if self.cards[col][0].visible_value == "F" and self.cards[col][1].visible_value == "F":
            return Board.NEITHER_FLIPPED
        elif self.cards[col][0].visible_value == "F" or self.cards[col][1].visible_value == "F":
            return Board.ONE_FLIPPED
        elif self.cards[col][0].value == self.cards[col][1].value:
            return Board.BOTH_MATCH
        elif (self.cards[col][0].value == 0 or self.cards[col][0] == -5) and (self.cards[col][1].value == 0 or self.cards[col][1] == -5):
            return Board.BOTH_MATCH #makes joker and 0 count as a match
        else:
            return Board.BOTH_FLIPPED

    def get_score(self):
        score = 0
        matches = [] #could probably use new matches function here
        for i in range(4):
            if self.get_state(i) == Board.BOTH_FLIPPED:
                score += self.cards[i][0].value + self.cards[i][1].value
            elif self.get_state(i) == Board.BOTH_MATCH:
                if self.cards[i][0].value == -5:
                    score -= 10
                matches.append(self.cards[i][0].value)
        for val in matches:
            if matches.count(val) > 1:
                for i in range(matches.count(val)):
                    matches.remove(val)
                    score -= 5
        return score



class DNA():
    def __init__(self, genes = None):
        """
        the traits, (not) in order, are:
        horizontal or vertical: if it prefers flipping with a flipped card or a new col
        lowest to take (from discard): lowest number it will take from the discard pile (maybe only if there is an unflipped col)
        draw bias: how often it'll take the card if its low enough vs draw a new one (maybe these should be combined in a formula)
        lowest to keep: from drawing
        when to start mitigating (based on opponents number of unflipped cards)
        lowest to mitigate: lowest amount you need to save for it to mitigate
        joker placement: if joker goes in new spot or replaces a flipped card
        higest card to go for -10 with
        when to stop going for -10 (maybe could be linked with above, make one formula that determines if -10 is worth it later on)
        draw card that doesnt match and is low, replace flipped card or put it with a flipped card or discard
        
        """
        if genes == None:
            self.genes = []
            """old way
            #horizontal_preference (true or false)
            if(random() < 0.5):
                self.genes.append(True)
            else:
                self.genes.append(False)
            #drawing_bias (btwn 0 and 1)
            #flipping_bias (btwn 0 and 1)
            #minus10_bias (btwn 0 and 1)
            for i in range(3):
                self.genes.append(random())

            #time_multiplier (btwn 1 and 10) - might need to be slightly different
            self.genes.append(int(uniform(1, 10)))
            #lowst_to_keep (btwn 0 and 12)
            #lowest_for_minus10 (btwn 0 and 12)
            for i in range(2):
                self.genes.append(int(uniform(1, 12)))
            #lowest_to_go_out_with (btwn 0 and 10) - eventually will be based on opponents boards too
            self.genes.append(int(uniform(1, 10)))
            #get_all_flipped_bias
            self.genes.append(random())
            #lowest_to_mitigate
            self.genes.append(int(uniform(1, 12)))
            #higest_to_add_for_minus10
            self.genes.append(int(uniform(1, 10)))
            """
            for i in range(11):
                self.genes.append(self.random(i))
        else:
            self.genes = genes

    def random(self, gene):
        between_0_and_1 = [1, 2, 3, 8]
        between_1_and_10 = [4, 7]
        between_0_and_12 = [5, 6]
        if gene == 0:
            if(random() < 0.5):
                return True
            else:
                return False
        elif gene in between_0_and_1:
            return random()
        elif gene in between_1_and_10:
            return int(uniform(1, 10))
        elif gene in between_0_and_12:
            return int(uniform(0, 12))
        elif gene == 9:
            return int(uniform(1, 12))
        elif gene == 10:
            return int(uniform(1, 10))




    def print(self):
        print("horizontal_preference: " + str(self.genes[0]))
        print("drawing_bias (btwn 0 and 1): " + str(self.genes[1]))
        print("flipping_bias (btwn 0 and 1): " + str(self.genes[2]))
        print("minus10_bias (btwn 0 and 1): " + str(self.genes[3]))
        print("time_multiplier (btwn 1 and 10): " + str(self.genes[4]))
        print("lowest_to_keep (btwn 0 and 12): " + str(self.genes[5]))
        print("lowest_for_minus10 (btwn 0 and 12): " + str(self.genes[6]))
        print("lowest_to_go_out_with (btwn 0 and 10): " + str(self.genes[7]))
        print("get_all_flipped_bias (btwn 0 and 1): " + str(self.genes[8]))
        print("lowest_to_mitigate (btwn 1 and 12): " + str(self.genes[9]))
        print("highest_to_add_for_minus10 (btwn 1 and 10): " + str(self.genes[10]))



class Player():
    #Layout for a player, by default is a computer player
    def __init__(self, dna = None):
        #make their board and a var for the card they last discarded
        self.board = Board()
        self.card_discarded = None
        #make their score variable
        self.score = 0
        #make a variable for if they won
        self.winner = None
        #make a variable for their fitness
        #self.fitness = None              might not actually need this
        #set up their dna
        if dna == None:
            self.dna = DNA()
        else:
            self.dna = dna
        gene_iterator = iter(self.dna.genes)
        self.horizontal_preference = next(gene_iterator)
        self.drawing_bias = next(gene_iterator)
        self.flipping_bias = next(gene_iterator)
        self.minus10_bias = next(gene_iterator)
        self.time_multiplier = next(gene_iterator)
        self.lowest_to_keep = next(gene_iterator)
        self.lowest_for_minus10 = next(gene_iterator)
        self.lowest_to_go_out_with = next(gene_iterator)
        self.get_all_flipped_bias = next(gene_iterator)
        self.lowest_to_mitigate = next(gene_iterator)
        self.highest_to_add_for_minus10 = next(gene_iterator)
        
        #variables for taking the turn
        self.one_flipped_per_row = False
        self.going_for_minus10 = []

    def flip_two(self):
        #will always flip this one
        self.board.cards[0][0].flip()
        #other one determined by preference
        if(self.horizontal_preference):
            if debugging:
                print("Flipping horizontal card")
            self.board.cards[1][0].flip()
        else:
            if debugging:
                print("Flipping vertical card")
            self.board.cards[0][1].flip()

    def take_turn(self, deck, discarded, opponents):
        if debugging:
            print("Turn is being started")
        #var to see if turn is done yet
        turn_done = False
        #figure out if you're in first or second stage:
        if self.horizontal_preference and not self.one_flipped_per_row:
            self.one_flipped_per_row = True
            for col in range(4):
                if(self.board.get_state(col) == Board.NEITHER_FLIPPED):
                    self.one_flipped_per_row = False
        #if you have horizontal preference and you're in the first stage, do this
        if self.horizontal_preference and not self.one_flipped_per_row:
            if debugging:
                print("Horizontal preference and first stage, so checking discarded card")
            turn_done = self.check_card(discarded, 1, "discard", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't take discarded card, so drawing a card")
                card_drawn = deck.draw()
                turn_done = self.check_card(card_drawn, 1, "deck", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't use drawn card so just flipping")
                self.flip_card(1, card_drawn)
                turn_done = True
        #if none of this happens, we not in stage 1, so let's check if we're in stage 3
        one_flipped_count = 0
        neither_flipped_count = 0
        for col in range(4):
            if self.board.get_state(col) == Board.ONE_FLIPPED:
                one_flipped_count += 1
            if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                neither_flipped_count += 1
        if one_flipped_count == 1 and neither_flipped_count == 0:
            #we are in stage 3
            if debugging:
                print("We are in stage 3")
                print("Checking discarded card")
            turn_done = self.check_card(discarded, 3, "discard", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't take discarded card, so drawing a card")
                card_drawn = deck.draw()
                turn_done = self.check_card(card_drawn, 3, "deck", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't use drawn card so just discarding")
                self.card_discarded = card_drawn
                turn_done = True

        #if we aren't in stage 3 or stage 1, we must be in stage 2
        if not turn_done:
            #this is now what is used until there is only one card left
            if debugging:
                print("We are now in stage 2")
                print("Checking discarded card")
            turn_done = self.check_card(discarded, 2, "discard", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't take discarded card, so drawing a card")
                card_drawn = deck.draw()
                turn_done = self.check_card(card_drawn, 2, "deck", opponents)
            if not turn_done:
                if debugging:
                    print("Didn't use drawn card so just flipping")
                self.flip_card(2, card_drawn)
                turn_done = True
            #turn should now be done no matter what




        if debugging:
            print("Turn is ending")
        return self.board.all_flipped()

    def take_last_turn(self, deck, discarded, opponents):
        turn_done = False
        if debugging:
            print("On last turn")
            print("checking discarded card")
        #really this should be a lot more complex than I'll make it initially
        #it should change depending on if you still need to make matches
        turn_done = self.check_card(discarded, 4, "discard", opponents)
        if not turn_done:
            if debugging:
                print("Didn't take discarded card, so drawing a card")
            card_drawn = deck.draw()
            turn_done = self.check_card(card_drawn, 4, "deck", opponents)
        if not turn_done:
            if debugging:
                print("Didn't use drawn card so just discarding")
            self.card_discarded = card_drawn
            turn_done = True


        self.board.flip_all()

    def check_card(self, card, stage, card_is_from, opponents):
        #figure out which bias we need to use, drawing or flipping
        bias = None
        if card_is_from == "discard":
            bias = self.drawing_bias
        else:
            bias = self.flipping_bias
        #figure out time multiplier things
        highest_unflipped_opponent = 0
        for o in opponents:
            if len(o.board.get_unflipped_locations()) > highest_unflipped_opponent:
                highest_unflipped_opponent = len(o.board.get_unflipped_locations())
        if debugging:
            print("Highest amount of unflipped cards of opponents is: " + str(highest_unflipped_opponent))
        #seperate logic just for jokers (-5s)
        if card.value == -5:
            if debugging:
                print("Card is a joker")
            if stage != 4:
                #check if there is another joker
                if card.value in self.board.get_unmatched():
                    #match it, going for -10 doesn't matter here cuz you wouldn't discard a joker for -10 (technically sometimes you should tho)
                    col, row = self.board.get_location(card.value)
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the joker")
                    return True
                elif 0 in self.board.get_unmatched():
                    col, row = self.board.get_location(0)
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Matching the joker with a 0")
                    return True
                else:
                    #nothing to match it with, so either put it in new col or replace highest unflipped card
                    for col in range(4):
                        if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                            self.switch_cards(card, col, 0)
                            if debugging:
                                print("Putting joker in a new col")
                                return True
                    #if not done yet
                    col, row = self.board.get_location(self.board.get_highest_unmatched())
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    if debugging:
                        print("Replacing highest unmatched with a joker")
                    return True

            else:
                #if we are on the last turn, replace highest card if it it above 5, otherwise replace facedown card
                if self.board.get_highest_unmatched() != None:
                    if self.board.get_highest_unmatched() > 5:
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        if row == 0:
                            row = 1
                        else:
                            row = 0
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Replacing highest unmatched with a joker")
                        return True
                    else:
                        col, row = self.board.get_unflipped_locations()[0]
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Replacing unflipped card with a joker")
                        return True
            
        #if we are in the first stage
        if stage == 1:
            #check if card is a match
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("The discarded card matches an unmatched card, so we're matching it")
                col = self.board.get_location(card.value)[0]
                row = self.board.get_unflipped(col)
                self.switch_cards(card, col, row)
                return True
            #if we get here, it doesn't match anything so we check if it is low or same as another match
            #figuring out if we are going for -10
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
                #gotta actually put this in, then paste it into other stages
            if card.value in self.board.get_matches() and card.value <= (self.lowest_for_minus10 - self.time_multiplier / highest_unflipped_opponent):
                col = None
                row = 0
                for column in range(4):
                    if self.board.get_state(column) == Board.NEITHER_FLIPPED:
                        col = column
                self.switch_cards(card, col, row)
                self.going_for_minus10.append(card.value)
                if debugging:
                    print("Card matches a match we already have and is low enough to go for -10, so we use it")
                    print("Card value: " + str(card.value) + " is lower than lowest for minus 10: "
                    + str(self.lowest_for_minus10) + " minus time multiplier: " + str(self.time_multiplier)
                    + " over lowest unflipped from opponents: " + str(highest_unflipped_opponent))
                return True
            #if we get here, card isnt same as a match we already have, so we see if it's low enough to take
            if card.value <= (self.lowest_to_keep - self.time_multiplier / highest_unflipped_opponent):
                #low enough to keep, just need to choose where to put it
                for column in range(4):
                        if self.board.get_state(column) == Board.NEITHER_FLIPPED:
                            col = column
                self.switch_cards(card, col, 0)
                if debugging:
                    print("Card is low enough to keep, so we use it")
                    print("Card value: " + str(card.value) + " is lower than lowest to keep: "
                    + str(self.lowest_to_keep) + " minus time multiplier: " + str(self.time_multiplier)
                    + " over lowest unflipped from opponents: " + str(highest_unflipped_opponent))
                return True
        elif stage == 2:
            #in here we are in stage 2, which we are in from the start if there is vertical preference
            if debugging:
                print("Starting looking at card in stage 2")
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("Card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                #check if this will give us -10:
                if self.board.cards[col][row].visible_value in self.going_for_minus10:
                    #switch it for sure
                    if debugging:
                        print("This gives us -10, so matching")
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    self.going_for_minus10.remove(self.board.cards[col][row].value)
                    return True

                if row == 0:
                    row = 1
                else:
                    row = 0
                #have location of where to switch, just need to check if the card there is going for -10
                if self.board.cards[col][row].value in self.going_for_minus10:
                    #going to see if we should replace it or keep going for -10
                    if self.board.cards[col][row].value <= (self.lowest_for_minus10 - self.time_multiplier / highest_unflipped_opponent) and random() < self.minus10_bias:
                        #we don't switch it
                        if debugging:
                            print("Other card is going for -10 and is still low enough, and -10 bias is higher than random, so still going for -10")
                    else:
                        #we switch it and match the card
                        if debugging:
                            print("Switching the cards")
                        self.switch_cards(card, col, row)
                        if self.board.cards[col][row].value in self.going_for_minus10:
                            self.going_for_minus10.remove(self.board.cards[col][row].value)
                        else:
                            if debugging:
                                print("")
                                print("Card should be in going for -10 but isnt, fix this")
                                print("")
                        return True
                else:
                    #we switch it and match the card
                    if debugging:
                        print("Switching the cards")
                    self.switch_cards(card, col, row)
                    return True #guaranteed there's a better way to do this than having it twice in a row
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
            #if we're here, discard doesn't match anything, so check if it's same as a match we already have
            if card.value in self.board.get_matches() and card.value <= (self.lowest_for_minus10 - self.time_multiplier / highest_unflipped_opponent) and random() < self.minus10_bias:
                if debugging:
                    print("Card is same as match we already have, low enough, and random was lower than -10 bias")
                #now figure out where to put it
                #first check if there is empty col
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        if debugging:
                            print("There is an empty col, so putting it there")
                        self.switch_cards(card, col, 0)
                        self.going_for_minus10.append(card.value)
                        return True
                #if that doesn't happen, we can either replace a flipped card or an unflipped card
                if self.board.get_highest_unmatched() != None:
                    if random() > self.get_all_flipped_bias and (self.board.get_highest_unmatched() - card.value) >= (self.lowest_to_mitigate - (self.time_multiplier / highest_unflipped_opponent)):
                        if debugging:
                            print("random was above get_all_flipped_bias, and we are mitigating more than lowest to mitigate minus time multiplier stuff, so replacing our highest card")
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        return True
                    else:
                        if self.board.get_across_from_highest() != None:
                            if debugging:
                                print("Putting card across from highest card with an unflipped card across from it")
                            col, row = self.board.get_across_from_highest()
                            self.switch_cards(card, col, row)
                            return True
                else:
                    if self.board.get_across_from_highest() != None:
                        if debugging:
                            print("Putting card across from highest card with an unflipped card across from it")
                        col, row = self.board.get_across_from_highest()
                        self.switch_cards(card, col, row)
                        return True
                #theoretically we should never get here
                if debugging:
                    print("Something is wrong, we should never get here I think (line 448)")
            #if we are still here, card doesn't match a match we already have, so if drawing or flipping bias is low and the card is low enough, we will take the discard
            if random() > bias and card.value <= (self.lowest_to_keep - self.time_multiplier / highest_unflipped_opponent):
                if debugging:
                    print("random is less than bias, and card is low enough to keep, so keeping it")
                #now just need to figure out where to put it
                #gonna try using same logic as for where to put -10 one
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        if debugging:
                            print("There is an empty col, so putting it there")
                        self.switch_cards(card, col, 0)
                        self.going_for_minus10.append(card.value)
                        return True
                #if that doesn't happen, we can either replace a flipped card or an unflipped card
                if self.board.get_highest_unmatched() != None:
                    if random() > self.get_all_flipped_bias and (self.board.get_highest_unmatched() - card.value) >= (self.lowest_to_mitigate - (self.time_multiplier / highest_unflipped_opponent)):
                        if debugging:
                            print("random was above get_all_flipped_bias, and we are mitigating more than lowest to mitigate minus, so replacing our highest card")
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        return True
                    else:
                        if self.board.get_across_from_highest() != None:
                            if debugging:
                                print("Putting card across from highest card with an unflipped card across from it")
                            col, row = self.board.get_across_from_highest()
                            self.switch_cards(card, col, row)
                            return True
                else:
                    if self.board.get_across_from_highest() != None:
                        if debugging:
                            print("Putting card across from highest card with an unflipped card across from it")
                        col, row = self.board.get_across_from_highest()
                        self.switch_cards(card, col, row)
                        return True
            #that should be everything I think
        elif stage == 3:
            #get value of card in last row with an unflipped card
            last_card = None
            for col in range(4):
                if self.board.get_state(col) == Board.ONE_FLIPPED:
                    row = self.board.get_unflipped(col)
                    last_card = self.board.cards[col][row].value
            #check if card matches unmatched card
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("Card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                if row == 0:
                    row = 1
                else:
                    row = 0
                #see if card will make us go out
                if self.board.cards[col][row].value == last_card: #doesn't work well if there are multiples of the last card
                    if debugging:
                        print("Card matches with last card, seeing if we wanna go out")
                    #see if going out is worth it
                    test_board = self.board.copy()
                    test_board.cards[col][row] = card
                    test_score = test_board.get_score()
                    if test_score <= self.lowest_to_go_out_with:
                        #then go out
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Will end with low enough score, so going out")
                        return True
                #check if it replaces a card we're going for -10 with
                elif (row == 0 and self.board.cards[col][1].visible_value in self.going_for_minus10) or (row == 1 and self.board.cards[col][0].visible_value in self.going_for_minus10):
                    #switch it for sure
                    if debugging:
                        print("This gives us -10, so matching")
                    if row == 0:
                        row = 1
                    else:
                        row = 0
                    self.switch_cards(card, col, row)
                    self.going_for_minus10.remove(self.board.cards[col][row].value)
                    return True
                elif card.value <= (self.lowest_for_minus10 - self.time_multiplier / highest_unflipped_opponent) and random() < self.minus10_bias and card.value in self.going_for_minus10:
                    #we don't switch it
                    if debugging:
                        print("Other card is going for -10 and is still low enough, and -10 bias is higher than random, so still going for -10")
                else:
                    #not gonna make us go out, or replace one we're going for -10 with, so switch it in
                    if debugging:
                        print("Not gonna make us go out or replace a -10 card (or was biased agaisnt keeping the -10 card)")
                    self.switch_cards(card, col, row)
                    return True
            #if we're here, card doesn't match an unmatched card
            if card.value == 0 and -5 in self.board.get_unmatched():
                #put it with a joker if there is one
                col, row = self.board.get_location(-5)
                if row == 0:
                    row = 1
                else:
                    row = 0
                self.switch_cards(card, col, row)
                if debugging:
                    print("Matching the zero with a joker")
                return True
            #check if card matches a match we already have
            if card.value in self.board.get_matches() and random() < self.minus10_bias:
                #might go for -10, gonna see if its worth it
                #first check if it's lower than our highest unmatched card
                if self.board.get_highest_unmatched() != None:
                    if card.value < self.board.get_highest_unmatched():
                        if debugging:
                            print("Card makes -10 and is lower than highest unmatched, so taking it")
                        self.going_for_minus10.append(card.value)
                        col, row = self.board.get_location(board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        return True
                    #now see if its not too much higer than our highest unmatched
                    if card.value <= (self.board.get_highest_unmatched() + self.highest_to_add_for_minus10):
                        if debugging:
                            print("Doesn't add too much, so going for -10 with it")
                        self.going_for_minus10.append(card.value)
                        col, row = self.board.get_location(board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
            #if we're here, we are not going for -10

            #now check if we wann just go out with some points
            test_board = self.board.copy()
            #get location of last card
            col = None
            for column in range(4):
                if self.board.get_state(column) == Board.ONE_FLIPPED:
                    col = column
                    row = self.board.get_unflipped(col)
            test_board.cards[col][row] = card
            test_score = test_board.get_score()
            if test_score <= self.lowest_to_go_out_with:
                #then go out
                self.switch_cards(card, col, row)
                if debugging:
                    print("Will end with low enough score, so going out")
                return True

            #if this is a drawn card, if it mitigates, we might mitigate
            if self.board.get_highest_unmatched() != None:
                if card.value < self.board.get_highest_unmatched() and (card_is_from == "deck" or (card_is_from == "discard" and random() > self.drawing_bias)):
                    #check if highest card is going for -10
                    if self.board.get_highest_unmatched() in self.going_for_minus10:
                        #if we are, see if we wanna mitigate or not
                        if card.value <= (self.lowest_for_minus10 - self.time_multiplier / highest_unflipped_opponent) and random() < self.minus10_bias:
                            #keep the -10 one, so mitigate next highest if there is one
                            highest = -5
                            for val in self.board.get_unmatched():
                                if val not in self.going_for_minus10 and val > highest:
                                    highest = val
                            #found next highest, see if it is higher than drawn
                            if card.value < highest:
                                #switch these
                                col, row = self.board.get_location(highest)
                                self.switch_cards(card, col, row)
                                if debugging:
                                    print("Keeping -10 one, so mitigating next highest")
                                return True
                            else:
                                if debugging:
                                    print("This should return false now I think, so we should just discard the drawn one and end the turn")
                        else:
                            #we replace the -10 one
                            col, row = self.board.get_location(self.board.get_highest_unmatched())
                            self.switch_cards(card, col, row)
                            if debugging:
                                print("We mitigate and replace the -10 card")
                            return True
                    else:
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Mitigating")
                        return True
                        #again, there's definetely a better way to do this 
            #if we are here, card doesn't match, go for -10, or mitigate, and we don't wanna go out, so we should return false and move on
        elif stage == 4:
            #we are on the last turn
            #we check for a match
            if card.value in self.board.get_unmatched():
                if debugging:
                    print("The discarded card matches an unmatched card")
                col, row = self.board.get_location(card.value)
                if row == 0:
                    row = 1
                else:
                    row = 0
                if self.board.get_highest_unmatched() != None:
                    if (card.value + self.board.cards[col][row].value) > (self.board.get_highest_unmatched() - card.value):
                        if debugging:
                            print("Matching saves more than mitigating")
                        self.switch_cards(card, col, row)
                        return True
                    else:
                        if debugging:
                            print("Matching saves less than mitigating")
                else:
                        if debugging:
                            print("Matching saves less than mitigating")
            #if no match or match saves less than mitigating, we either mitigate a flipped card (if it's above 5) or an unflipped card, or draw
            if debugging and self.board.get_highest_unmatched() != None:
                print("Highest unmatched: " + str(self.board.get_highest_unmatched()) + " minus card value: " + str(card.value) + " is " + str(self.board.get_highest_unmatched() - card.value))
                print("lowest to mitigate: " + str(self.lowest_to_mitigate) + " minus time multiplier: " + str(self.time_multiplier) + " is " + str(self.lowest_to_mitigate - self.time_multiplier))
            real_lowest = self.lowest_to_mitigate - self.time_multiplier
            if real_lowest < 1:
                real_lowest = 1
            if debugging:
                print("Real lowest is: " + str(real_lowest))
            if self.board.get_highest_unmatched() != None:
                if card_is_from == "discard" and (random() > self.drawing_bias or (self.board.get_highest_unmatched() - card.value) <= real_lowest):
                    #might wanna take drawing bias out of this
                    if debugging:
                        print("Drawing bias is higher than random, or we don't mitigate enough, so we will draw a card and hope that's better")
                else:
                    #we don't want to draw, we want to mitigate (if we mitigate enough)
                    if self.board.get_highest_unmatched() > 5 and card.value < self.board.get_highest_unmatched():
                        #we want to replace the highest unmatched card
                        col, row = self.board.get_location(self.board.get_highest_unmatched())
                        self.switch_cards(card, col, row)
                        if debugging:
                            print("Replacing highest unmatched card")
                        return True
                    elif card.value < 5:
                        #we want to replace a facedown card
                        for col in range(4):
                            if self.board.get_state(col) == Board.ONE_FLIPPED:
                                row = self.board.get_unflipped(col)
                                self.switch_cards(card, col, row)
                                if debugging:
                                    print("Replacing an unflipped card")
                                return True


        else:
            if debugging:
                print("I shouldn't get here, stage should only be 1, 2, or 3")

        #if the turn is never done (no switch is made) return false
        return False

    def flip_card(self, stage, to_discard):
        if stage == 1:
            for col in range(4):
                if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                    self.board.cards[col][0].flip()
                    self.card_discarded = to_discard
                    if self.board.cards[col][0].value in self.board.get_matches():
                        self.going_for_minus10.append(self.board.cards[col][0].value)
                    return 0
        elif stage == 2:
            if self.horizontal_preference:
                for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        self.board.cards[col][0].flip()
                        self.card_discarded = to_discard
                        if self.board.cards[col][0].value in self.board.get_matches():
                            self.going_for_minus10.append(self.board.cards[col][0].value)
                        return 0
            #otherwise flip opposite highest col
            if self.board.get_across_from_highest() != None:
                if debugging:
                    print("Flipping card across from highest card with an unflipped card across from it")
                col, row = self.board.get_across_from_highest()
                self.board.cards[col][row].flip()
                self.card_discarded = to_discard
                if self.board.cards[col][row].value in self.board.get_matches():
                    self.going_for_minus10.append(self.board.cards[col][row].value)
                return 0
            #if there isn't one, flip new col
            for col in range(4):
                    if self.board.get_state(col) == Board.NEITHER_FLIPPED:
                        self.board.cards[col][0].flip()
                        self.card_discarded = to_discard
                        if self.board.cards[col][0].value in self.board.get_matches():
                            self.going_for_minus10.append(self.board.cards[col][0].value)
                        return 0
        return -1


    def switch_cards(self, card, col, row):
        self.card_discarded = self.board.cards[col][row]
        self.card_discarded.flip()
        self.board.cards[col][row] = card

    #evolution functions

    def calc_fitness(self):
        #map score from 150 to -150 to be between 0 and 50
        fitness = ((self.score - 150) / (-150 - 150)) * 50
        #double score if winner
        if self.winner:
            fitness *= 2
        return int(fitness)

    def mate(self, partner):
        new_dna = DNA()
        for i in range(len(new_dna.genes)):
            if random() < 0.5:
                new_dna.genes[i] = self.dna.genes[i]
            else:
                new_dna.genes[i] = partner.dna.genes[i]
        return Player(new_dna)

    def mutate(self, mutation_rate):
        for i in range(len(self.dna.genes)):
            if random() < mutation_rate:
                self.dna.genes[i] = self.dna.random(i)



class User(Player):
    def __init__(self):
        super(User, self).__init__()

    def flip_two(self):
        col = int(input("Enter col of card to flip ")) - 1
        while col < 0 or col > 3:
            print("Must be between 1 and 4")
            col = int(input("Enter col of card to flip ")) - 1

        row = int(input("Enter row of card to flip ")) - 1
        while row < 0 or row > 1:
            print("Must be between 1 and 2")
            row = int(input("Enter row of card to flip ")) - 1

        col2 = int(input("Enter col of second card to flip ")) - 1
        while col2 < 0 or col2 > 3:
            print("Must be between 1 and 4")
            col2 = int(input("Enter col of card to flip ")) - 1

        row2 = int(input("Enter row of second card to flip ")) - 1
        while row2 < 0 or row2 > 1:
            print("Must be between 1 and 2")
            row2 = int(input("Enter row of card to flip ")) - 1

        while(col == col2 and row == row2):
            print("You need to flip 2 different cards")
            col2 = int(input("Enter col of second card to flip ")) - 1
            while col2 < 0 or col2 > 3:
                print("Must be between 1 and 4")
                col2 = int(input("Enter col of card to flip ")) - 1

            row2 = int(input("Enter row of second card to flip ")) - 1
            while row2 < 0 or row2 > 1:
                print("Must be between 1 and 2")
                row2 = int(input("Enter row of card to flip ")) - 1

        self.board.cards[col][row].flip()
        self.board.cards[col2][row2].flip()

    def take_turn(self, deck, discarded):
        draw_card = input("Enter draw to draw a card, or discard to use the discarded card ")
        while draw_card.lower() != "discard" and draw_card.lower() != "draw":
            print("Invalid input")
            draw_card = input("Enter draw to draw a card, or discard to use the discarded card ")
        if draw_card.lower() == "draw":
            drawn = deck.draw()
            print("You drew " + str(drawn.visible_value))
            keep = input("Do you want to keep the card you drew (enter keep), or flip a card on your board (enter flip)? ")
            while keep.lower() != "keep" and keep.lower() != "flip":
                print("Invalid input")
                keep = input("Do you want to keep the card you drew (enter keep), or flip a card on your board (enter flip)? ")
            if keep.lower() == "keep":
                col = int(input("Enter col of where to put your card ")) - 1
                while col < 0 or col > 3:
                    print("Must be between 1 and 4")
                    col = int(input("Enter col of card to flip ")) - 1

                row = int(input("Enter row of where to put your card ")) - 1
                while row < 0 or row > 1:
                    print("Must be between 1 and 2")
                    row = int(input("Enter row of card to flip ")) - 1

                self.card_discarded = self.board.cards[col][row]
                self.card_discarded.flip()
                self.board.cards[col][row] = drawn
            elif keep.lower() == "flip":
                col = int(input("Enter col of card to flip ")) - 1
                while col < 0 or col > 3:
                    print("Must be between 1 and 4")
                    col = int(input("Enter col of card to flip ")) - 1

                row = int(input("Enter row of card to flip ")) - 1
                while row < 0 or row > 1:
                    print("Must be between 1 and 2")
                    row = int(input("Enter row of card to flip ")) - 1

                self.board.cards[col][row].flip()
                self.card_discarded = drawn
        elif draw_card.lower() == "discard":
            col = int(input("Enter col of where to put your card ")) - 1
            while col < 0 or col > 3:
                print("Must be between 1 and 4")
                col = int(input("Enter col of card to flip ")) - 1

            row = int(input("Enter row of where to put your card ")) - 1
            while row < 0 or row > 1:
                print("Must be between 1 and 2")
                row = int(input("Enter row of card to flip ")) - 1

            self.card_discarded = self.board.cards[col][row]
            self.card_discarded.flip()
            self.board.cards[col][row] = discarded
        return self.board.all_flipped()





class Game():
    #basic game, only with 2 players for now
    def __init__(self, playable, show_text, player1 = None, player2 = None):
        self.players = []
        self.show_text = show_text
        if playable:
            self.players.append(Player())
            self.players.append(User())
        else:
            self.players.append(player1)
            self.players.append(player2)
        self.discard_pile_card = None

    def print_discarded(self):
        print(str(self.discard_pile_card.visible_value) + " F")

    def deal(self, deck):
        for p in self.players:
            for col in range(4):
                for row in range(2):
                    p.board.cards[col][row] = deck.draw_face_down()

    def play(self):
        game_done = False
        for i in range(9):
            self.play_round()
        self.end_game()

    def play_round(self):
        #for debugging
        # turns = 0
        #basic setup
        deck = Deck()
        self.deal(deck)
        self.discard_pile_card = deck.draw()
        #start the game
        for p in self.players:
            p.flip_two()
        #variables needed to know the state of the round
        round_over = False
        someone_went_out = False
        last_turn = False
        p_who_went_out = None

        #play each player's turn
        while not round_over:
            # turns += 1
            for i in range(len(self.players)):
                p = self.players[i]
                #make list of all opponents
                opponents = self.players.copy()
                opponents.remove(p)

                if p != p_who_went_out:
                    if self.show_text:
                        print("")
                        print("")
                        print("Player " + str(i + 1) + "'s turn")
                        print("")
                        self.print_discarded()
                        print("")
                        p.board.print()

                    if not last_turn:
                        someone_went_out = p.take_turn(deck, self.discard_pile_card, opponents)
                        self.discard_pile_card = p.card_discarded
                    else:
                        p.take_last_turn(deck, self.discard_pile_card, opponents)#likely don't need opponents, just here for now for debugging
                        self.discard_pile_card = p.card_discarded

                    if someone_went_out and not last_turn:
                        if self.show_text:
                            print("Someone went out")
                        p_who_went_out = p
                        last_turn = True
                    if self.show_text:
                        print("After the turn:")
                        print("")
                        p.board.print()
                else:
                    round_over = True
                    break
        if self.show_text:
            print("")
            print("The round is over")
        #add each player's score for the round to their total score
        for p in self.players:
            p.score += p.board.get_score()
        #print the scores
        if self.show_text:
            print("The scores for this round are: ")
            for i in range(len(self.players)):
                print("Player " + str(i + 1) + ": " + str(self.players[i].board.get_score()))
            print("The total scores are:")
            for i in range(len(self.players)):
                print("Player " + str(i + 1) + ": " + str(self.players[i].score))



    def end_game(self):
        if debugging and self.show_text:
            print("The game is over")
        #probably just gonna be used to calculate the player's fitness
        scores = []
        winner_indexes = []
        #find all the scores
        for p in self.players:
            scores.append(p.board.get_score())
        #find the lowest score
        winning_score = min(scores)
        #see who had that score
        for i in range(len(self.players)):
            if self.players[i].board.get_score() == winning_score:
                winner_indexes.append(i)
        #if your score is a winning score, you're a winner, otherwise you're a loser
        for i in range(len(self.players)):
            if i in winner_indexes:
                self.players[i].winner = True
            else:
                self.players[i].winner = False
        #this makes everyone lose if there's a tie (this can be commented out)
        if len(winner_indexes) > 1:
            for p in self.players:
                p.winner = False


class Evolution():
    def __init__(self, display_window = True):
        #need to set up both actual evolution stuff and tkinter window stuff
        #evolution stuff
        self.population_size = 50 #must be even number
        self.mutation_rate = 0.01
        self.population = []
        self.mating_pool = []
        self.games = []
        self.generations = 0
        self.paused = True
        self.first_run = True

        #for stats
        self.best_score = 150
        self.average_score = None
        self.total_of_scores = 0
        self.total_scores = 0
        self.best_dna = None


        self.display_window = display_window


        #make the window
        #set up window basics
        if display_window:
            self.window = tk.Tk()
            self.stat_frm = tk.Frame(master = self.window, width=100, height=100)
            self.btn_frm = tk.Frame(master = self.window, width=100, height=100)
            self.title_lbl = tk.Label(text = "PlayNine Evolution", fg = "black", width = 20, height = 3)
            #self.window.configure(background="white")
            # self.stat_frm.config(bg = "white")
            # self.btn_frm.config(bg = "white")
            # self.title_lbl.config(bg = "white")
            self.title_lbl.pack()

            #set up label frame
            self.lbl_frame_labels = []
            #generations
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Generations: 0"))
            #best score
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best score: Waiting for first run"))
            #average score
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Average score: Waiting for first run"))
            #best genes
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best genes:"))
            #horizontal_preference (true or false)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal_preference: Waiting for first run"))
            #drawing_bias (btwn 0 and 1)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "drawing_bias (btwn 0 and 1): Waiting for first run"))
            #flipping_bias (btwn 0 and 1)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "flipping_bias (btwn 0 and 1): Waiting for first run"))
            #minus10_bias (btwn 0 and 1)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "minus10_bias (btwn 0 and 1): Waiting for first run"))
            #time_multiplier (btwn 1 and 10) - might need to be slightly different
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "time_multiplier (btwn 1 and 10): Waiting for first run"))
            #lowst_to_keep (btwn 0 and 12)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_keep (btwn 0 and 12): Waiting for first run"))
            #lowest_for_minus10 (btwn 0 and 12)
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_for_minus10 (btwn 0 and 12): Waiting for first run"))
            #lowest_to_go_out_with (btwn 0 and 10) - eventually will be based on opponents boards too
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_go_out_with (btwn 0 and 10): Waiting for first run"))
            #get_all_flipped_bias
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "get_all_flipped_bias (btwn 0 and 1): Waiting for first run"))
            #lowest_to_mitigate
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_mitigate (btwn 1 and 12): Waiting for first run"))
            #higest_to_add_for_minus10
            self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest_to_add_for_minus10 (btwn 1 and 10): Waiting for first run"))

            #add all labels to the frame
            for l in self.lbl_frame_labels:
                l.pack(anchor = "w")
                #l.config(bg = "white")
                if debugging:
                    l.config(borderwidth=1, relief="solid")

            #set up button frame
            self.btn_frame_buttons = []
            #start button
            self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Start", command = self.start))
            #stop button
            self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Stop", command = self.stop))
            #load button
            self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load", command = self.load))
            #save button
            self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Save", command = self.save))

            #add all buttons to the frame
            for b in self.btn_frame_buttons:
                b.pack()

            #add the frames to the window
            self.btn_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
            self.stat_frm.pack(fill=tk.BOTH, side=tk.RIGHT)


            #start up the window loop
            self.window.mainloop()


    def start(self):
        #start button
        if debugging:
            print("Start button pressed")
        #make paused false, call run
        self.paused = False
        self.run()

    def stop(self):
        #stop button
        if debugging:
            print("Stop button pressed")
        #make paused true
        self.paused = True


    def load(self):
        #load button
        if debugging:
            print("Load button pressed")


    def save(self):
        #save button
        if debugging:
            print("Save button pressed")


    def run(self, times_to_run = None):
        #create the first random population
        if self.first_run:
            for i in range(self.population_size):
                self.population.append(Player())
            self.first_run = False
        if times_to_run != None:
            self.paused = False
        while not self.paused:
            #add one to generations
            self.generations += 1
            #see if we wanna stop
            if times_to_run != None:
                if self.generations > times_to_run - 1:
                    self.paused = True #for this to really work I need this to not display the window while it goes I think, maybe not tho
            #clear the old games
            self.games.clear()
            #fill up the games
            for i in range(0, self.population_size - 1, 2):
                self.games.append(Game(False, False, self.population[i], self.population[i + 1]))
            #play the games
            if debugging:
                print("Games size: " + str(len(self.games)))

            for g in self.games:
                g.play()
            #calculate all the fitnesses, add to mating pool
            self.mating_pool.clear()
            for p in self.population:
                fitness = p.calc_fitness()
                for i in range(fitness):
                    self.mating_pool.append(p)
                #check if fitness is a new record
                if p.board.get_score() < self.best_score:
                    self.best_score = p.board.get_score()
                    self.best_dna = DNA(p.dna.genes)
                #adjust average score
                self.total_of_scores += p.board.get_score()
                self.total_scores += 1
                self.average_score = self.total_of_scores / self.total_scores
            if debugging:
                print("Mating pool size: " + str(len(self.mating_pool)))

            #now make new population
            self.population.clear()
            for i in range(self.population_size):
                #choose 2 random players that aren't the same
                p1 = choice(self.mating_pool)
                p2 = choice(self.mating_pool)
                while p1 == p2:
                    p2 = choice(self.mating_pool)
                child = p1.mate(p2)
                child.mutate(self.mutation_rate)
                self.population.append(child)

            if debugging:
                print("Population size: " + str(len(self.population)))
                print("")

            if self.display_window:
                #update the window
                self.update_window()
                self.window.update()

        

    def update_window(self):
        self.lbl_frame_labels[0]["text"] = "Generations: " + str(self.generations)
        self.lbl_frame_labels[1]["text"] = "Best score: " + str(self.best_score)
        self.lbl_frame_labels[2]["text"] = "Average score: " + str(self.average_score)
        self.lbl_frame_labels[4]["text"] = "horizontal_preference: " + str(self.best_dna.genes[0])
        self.lbl_frame_labels[5]["text"] = "drawing_bias (btwn 0 and 1): " + str(self.best_dna.genes[1])
        self.lbl_frame_labels[6]["text"] = "flipping_bias (btwn 0 and 1): " + str(self.best_dna.genes[2])
        self.lbl_frame_labels[7]["text"] = "minus10_bias (btwn 0 and 1): " + str(self.best_dna.genes[3])
        self.lbl_frame_labels[8]["text"] = "time_multiplier (btwn 1 and 10): " + str(self.best_dna.genes[4])
        self.lbl_frame_labels[9]["text"] = "lowest_to_keep (btwn 0 and 12): " + str(self.best_dna.genes[5])
        self.lbl_frame_labels[10]["text"] = "lowest_for_minus10 (btwn 0 and 12): " + str(self.best_dna.genes[6])
        self.lbl_frame_labels[11]["text"] = "lowest_to_go_out_with (btwn 0 and 10): " + str(self.best_dna.genes[7])
        self.lbl_frame_labels[12]["text"] = "get_all_flipped_bias (btwn 0 and 1): " + str(self.best_dna.genes[8])
        self.lbl_frame_labels[13]["text"] = "lowest_to_mitigate (btwn 1 and 12): " + str(self.best_dna.genes[9])
        self.lbl_frame_labels[14]["text"] = "highest_to_add_for_minus10 (btwn 1 and 10): " + str(self.best_dna.genes[10])



class Fights():
    def __init__(self, pool = None):
        #need to set up both actual evolution stuff and tkinter window stuff
        #fight stuff
        self.fighter = None
        self.total_fights = 0
        self.current_players_fights = 0
        #maybe add a setting for what it's the best out of
        self.out_of = 5

        self.pool = pool

        #stuff for running it
        self.paused = True
        self.first_run = True

        #for stats
        self.best_dna = DNA() #it's easier to just have it start as a random one


        #make the window
        #set up window basics
        self.window = tk.Tk()
        self.stat_frm = tk.Frame(master = self.window, width=100, height=100)
        self.btn_frm = tk.Frame(master = self.window, width=100, height=100)
        self.title_lbl = tk.Label(text = "PlayNine Evolution", fg = "black", width = 20, height = 3)
        #self.window.configure(background="white")
        # self.stat_frm.config(bg = "white")
        # self.btn_frm.config(bg = "white")
        # self.title_lbl.config(bg = "white")
        self.title_lbl.pack()
        #set up label frame
        self.lbl_frame_labels = []
        #total fights
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Total Fights: 0"))
        #total players fights
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Current player's fights: Waiting for first run"))
        #best genes
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "Best genes:"))
        #horizontal_preference (true or false)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "horizontal_preference: Waiting for first run"))
        #drawing_bias (btwn 0 and 1)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "drawing_bias (btwn 0 and 1): Waiting for first run"))
        #flipping_bias (btwn 0 and 1)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "flipping_bias (btwn 0 and 1): Waiting for first run"))
        #minus10_bias (btwn 0 and 1)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "minus10_bias (btwn 0 and 1): Waiting for first run"))
        #time_multiplier (btwn 1 and 10) - might need to be slightly different
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "time_multiplier (btwn 1 and 10): Waiting for first run"))
        #lowst_to_keep (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_keep (btwn 0 and 12): Waiting for first run"))
        #lowest_for_minus10 (btwn 0 and 12)
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_for_minus10 (btwn 0 and 12): Waiting for first run"))
        #lowest_to_go_out_with (btwn 0 and 10) - eventually will be based on opponents boards too
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_go_out_with (btwn 0 and 10): Waiting for first run"))
        #get_all_flipped_bias
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "get_all_flipped_bias (btwn 0 and 1): Waiting for first run"))
        #lowest_to_mitigate
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "lowest_to_mitigate (btwn 1 and 12): Waiting for first run"))
        #higest_to_add_for_minus10
        self.lbl_frame_labels.append(tk.Label(self.stat_frm, text = "highest_to_add_for_minus10 (btwn 1 and 10): Waiting for first run"))

        #add all labels to the frame
        for l in self.lbl_frame_labels:
            l.pack(anchor = "w")
            #l.config(bg = "white")
            if debugging:
                l.config(borderwidth=1, relief="solid")

        #set up button frame
        self.btn_frame_buttons = []
        #start button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Start", command = self.start))
        #stop button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Stop", command = self.stop))
        #load button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Load", command = self.load))
        #save button
        self.btn_frame_buttons.append(tk.Button(master = self.btn_frm, text = "Save", command = self.save))

        #add all buttons to the frame
        for b in self.btn_frame_buttons:
            b.pack()

        #add the frames to the window
        self.btn_frm.pack(fill=tk.BOTH, side=tk.RIGHT)
        self.stat_frm.pack(fill=tk.BOTH, side=tk.RIGHT)

        #start up the window loop
        self.window.mainloop()


    def start(self):
        #start button
        if debugging:
            print("Start button pressed")
        #make paused false, call run
        self.paused = False
        self.run()

    def stop(self):
        #stop button
        if debugging:
            print("Stop button pressed")
        #make paused true
        self.paused = True


    def load(self):
        #load button
        if debugging:
            print("Load button pressed")


    def save(self):
        #save button
        if debugging:
            print("Save button pressed")


    def run(self):
        if self.first_run:
            self.fighter = Player()
            self.first_run = False
        while not self.paused:
            winner = None
            opponent_score = 0
            fighter_score = 0
            #add one to generations
            self.total_fights += 1
            self.current_players_fights += 1
            #make the opponent
            if self.pool == None or isinstance(self.pool, Player):
                opponent = Player()
            else:
                opponent = choice(self.pool)
                opponent.mutate(0.01)
            #make the game and play it
            while winner == None:
                game = Game(False, False, self.fighter, opponent)
                game.play()
                #check for winner
                if opponent.winner:
                    opponent_score += 1
                    if opponent_score > self.out_of / 2:
                        winner = opponent
                else:
                    fighter_score += 1
                    if fighter_score > self.out_of / 2:
                        winner = self.fighter

                    
            #once there's a winner, do this
            self.fighter = winner
            if winner == opponent:
                self.best_dna = DNA(opponent.dna.genes)
                self.current_players_fights = 0
            # else:
            #     print("Fighter won")
            # if self.fighter.winner:
            #     print("Fighter won, from other if")
            #otherwise fighter stays
            #update the window
            self.update_window()
            self.window.update()

        

    def update_window(self):
        self.lbl_frame_labels[0]["text"] = "Total Fights: " + str(self.total_fights)
        self.lbl_frame_labels[1]["text"] = "Current Player's Fights: " + str(self.current_players_fights)
        self.lbl_frame_labels[3]["text"] = "horizontal_preference: " + str(self.best_dna.genes[0])
        self.lbl_frame_labels[4]["text"] = "drawing_bias (btwn 0 and 1): " + str(self.best_dna.genes[1])
        self.lbl_frame_labels[5]["text"] = "flipping_bias (btwn 0 and 1): " + str(self.best_dna.genes[2])
        self.lbl_frame_labels[6]["text"] = "minus10_bias (btwn 0 and 1): " + str(self.best_dna.genes[3])
        self.lbl_frame_labels[7]["text"] = "time_multiplier (btwn 1 and 10): " + str(self.best_dna.genes[4])
        self.lbl_frame_labels[8]["text"] = "lowest_to_keep (btwn 0 and 12): " + str(self.best_dna.genes[5])
        self.lbl_frame_labels[9]["text"] = "lowest_for_minus10 (btwn 0 and 12): " + str(self.best_dna.genes[6])
        self.lbl_frame_labels[10]["text"] = "lowest_to_go_out_with (btwn 0 and 10): " + str(self.best_dna.genes[7])
        self.lbl_frame_labels[11]["text"] = "get_all_flipped_bias (btwn 0 and 1): " + str(self.best_dna.genes[8])
        self.lbl_frame_labels[12]["text"] = "lowest_to_mitigate (btwn 1 and 12): " + str(self.best_dna.genes[9])
        self.lbl_frame_labels[13]["text"] = "highest_to_add_for_minus10 (btwn 1 and 10): " + str(self.best_dna.genes[10])

class Evolving_Fights():
    def __init__(self):
        self.start()

    def start(self):
        #make a genetic algorithm run for 150 generations
        genetic = Evolution(False)
        print("Running Evolution")
        genetic.run(150)
        #pool = genetic.population #if its entire pool
        pool = Player(genetic.best_dna)#use best dna from evolution as a starting point
        fighting = Fights(pool)








#pause button will make paused True, unpause button will make paused False and call Run
#label["text"] = "whatever"   is how you change label text



# game = Game(False, Player(), Player())
# for p in game.players:
#     print("Stats")
#     print("")
#     p.dna.print()
#     print("")
# game.play()


#evolve = Evolution()
#fight = Fights()
ef = Evolving_Fights()

"""
Testing stuff to learn tkinter

def button():
    print("Button clicked")

window = tk.Tk()
stat_frame = tk.Frame(master=window, width=100, height=100, bg="red")
button_frame = tk.Frame(master=window, width=100, height=100, bg="yellow")

label = tk.Label(text = "PlayNine Evolution", fg = "black", bg = "white", width = 20, height = 3)
label.pack()
button_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
stat_frame.pack(fill=tk.BOTH, side=tk.RIGHT)
test_button = tk.Button(master = button_frame, text = "Testing", command = button)
test_button.pack()


window.mainloop()
"""
# dna = DNA()
# dna.print()


"""
NOTES:
Should (probably) be 3 stages to the game:
1. Getting one card flipped in each col
2. Filling in board till one card left
3. Finishing the round
Alternatively, if vertical is preferred (would rather place cards in same col as already flipped cards):
Same but without step 1

Logic for each stage:
1. 
a. Check if discard matches a card you're trying to match, if it is match it (obviously)
b. If drawing bias is low enough and it is low enough, or if it is low enough and is same as a match you already 
   have take the discarded card and put it in a new unflipped col
c. Otherwise, draw a card
d. If card drawn matches, put it with the match
e. If it is low enough, or if it is low enough and is same as a match you already have, put it in a new unflipped col
f. Otherwise, flip a card in a new unflipped col
Note: Steps are essentially the same for checking the card, which should be in its own function

2.
a. Check if discard matches a card you're trying to match, if it is match it (obviously) (unless the other card is going for -10 already)
b. If the discard card is same as a match you've already made and it is early enough and it is low enough, take it and replace your highest
   unmatched card if you save enough otherwise put it across from your highest card (tough choice here, plus it makes a tough choice later on
   if you can match the highest card)
c. If discard is low enough and it is late enough and the drawing bias is low, replace highest card with discard (mitigate)
d. If it is low enough and drawing bias is low, place the discarded card with the highest card
e. Otherwise, draw a card
f. Check if it matches a card you're trying to match, if it is match it (obviously) (unless the other card is going for -10 already)
g. If the drawn card is same as a match you've already made and it is early enough and it is low enough, take it and replace your highest
   unmatched card if you save enough otherwise put it across from your highest card (tough choice here, plus it makes a tough choice later on
   if you can match the highest card)
h. If drawn card is low enough and it is late enough, replace highest card with discard (mitigate)
i. If it is low enough and flipping bias is low, place the drawn card with the highest card
j. Otherwise, flip a card across from the highest card

3. 
a. If discard matches an unmatched card that doesn't end the game, match it (duh) (unless the other card is going for -10 already)
b. If the discard matches the card that ends the game, and you'll end with a low enough amount of points, match it
c. If discard is same as a match you have and isn't too much higher than your highest unmatched card and -10 bias is high, replace highest
   unmatched card with discard
d. If discard is lower than your highest unmatched card and it mitigates enough and your drawing bias is low, replace highest card with discard
e. Otherwise, draw a card
f. If drawn card matches an unmatched card that doesn't end the game, match it (duh) (unless the other card is going for -10 already)
g. If the drawn card matches the card that ends the game, and you'll end with a low enough amount of points, match it
h. If drawn card is same as a match you have and isn't too much higher than your highest unmatched card and -10 bias is high, replace highest
   unmatched card with discard
i. If drawn is lower than your highest unmatched card and your highest unmatched card isn't going for -10 if -10 bias is high, replace highest 
   card with discard (need to figure out the math for this step with -10 bias), otherwise replace next highest unmatched card


Variables that each step use (not final):
1.
a. -10 bias, latest you go for -10, lowest for -10 (possibly something else about how much you save, or just factor that into calculation with -10 bias)
b. drawing bias, lowest for -10, lowest to keep
c. None
d. -10 bias, latest you go for -10, lowest for -10 (same as step a)
e. lowest for -10, lowest to keep (same as b but without drawing bias)
f. None

2.
a. -10 bias, latest you go for -10. lowest for -10
b. -10 bias, latest you go for -10. lowest for -10, some kind of mitigation factor and time factor
c. mitigation factor, time factor, drawing bias
d. lowest to keep, drawing bias
e. None
f. -10 bias, latest you go for -10. lowest for -10
g. -10 bias, latest you go for -10. lowest for -10, some kind of mitigation factor and time factor
h. mitigation factor, time factor
i. flipping bias, lowest to keep (maybe should be different from lowest to keep)
j. None

3.
a. -10 bias, latest you go for -10. lowest for -10
b. Lowest to go out with
c. -10 bias, highest you'll gain for -10
d. drawing bias, possibly a new mitigation factor (might just somehow multiply drawing bias by how much you'll save)
e. None
f. -10 bias, latest you go for -10. lowest for -10 (not sure these are exactly what I want here)
g. Lowest to go out with
h. -10 bias, highest you'll gain for -10
i. -10 bias (maybe a different version of it though)


NOTE: Flipping bias is only for flipping across from a flipped card, not flipping a card in a totally unflipped row, since there is definitive mathematical
      logic for taking cards below 5 and not otherwise
NOTE: There should probably be one time factor for anything related to time, and you multiply it by how many unflipped cards your opponent with the
      lowest amount of unflipped cards has left, to determine how much you care about the time left
NOTE: In general, the more variables the better, since some variable values may do well early game but may do not as well in very similar but slightly
      different situations later in the game
NOTE: At all points, if a 0 is drawn and there is an unmatched joker the 0 should be put with the joker

Trying to figure out conditions for each step:
1.
a. Does it match? If yes, match it (in theory this is always replacing a face down card at this point) (including matching joker with 0)
b. If discard is a joker, keep it (in unmatched col). Is discard same as match you already have? If yes, is it low enough to go for -10 (is it lower than 
   lowest for -10 times time multiplier over how many unflipped cards opponent has)? Then keep it, otherwise, if it is lower than lowest to keep and 
   random number btwn 0 and 1 is higher than drawing bias (so that a high drawing bias means you draw more often), keep it
c. Nothing
d. Does it match? If yes, match it
e. Is it same as match you already have? If yes, is it low enough to go for -10 (is it lower than lowest for -10 times time multiplier over how many 
   unflipped cards opponent has), then keep it.


List of all DNA variables:
horizontal_preference (true or false)
drawing_bias (btwn 0 and 1)
flipping_bias (btwn 0 and 1)
minus10_bias (btwn 0 and 1)
time_multiplier (btwn 1 and 10) - might need to be slightly different
lowest_to_keep (btwn 0 and 12)
lowest_for_minus10 (btwn 0 and 12)
lowest_to_go_out_with (btwn 0 and 10) - eventually will be based on opponents boards too





Time multiplier:

Opponent can have between 6 and 1 cards unflipped. 1 over these gives a range from 0.16 to 1. Maybe it can work like time multiplier over cards unflipped
is how much you subtract from lowest to keep (normal and -10), and lowest youll mitigate to save



Should put joker logic here seperately (since it can be handled seperately in an initial if statement when checking a card):

Known bugs:

If we have a situation like:
 0  2 11  F
 F  2  0  F
and then we match one of the 0s, 0 isn't added to going for -10

Card can be kept not because it goes for -10 but because it is low enough, even if it goes for -10,
and if that happens it isn't added to going for -10

Possible bug: If both cards in a col are going for -10 with different numbers, they might not get matched since
they'd have to replace a -10 to do it. This might never happen with how I wrote it though
- should be fixed now hopefully (if I did it well)




What I have left to do:
Really need to fix bugs related tp -10, they'll likely have a big effect on what strategy is best

Other idea:
Have player play random players till it loses, then have that player fight random players till it loses
Now combine it with genetic algorithm somehow
"""