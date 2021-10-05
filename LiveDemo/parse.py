# parse.py
# Parses valid user input to produce sentence trees.
# Expands upon the well known CYK Parse algorithm.
# Anthony de Bem 2021

from .tree import Node
from LiveDemo.models import DictionaryEntry, GrammarRule

# saved variables that the parsing algorithm needs to remember
words = []
trees = dict()


# returns:
#     bool: whether or not the phrase is a valid plural word
#     str: the singular version of the word
def pluralCheck(phrase):
    phrase = phrase.lower()
    valid_plural = False
    singular_form = ''

    if len(phrase) > 0:
        d_index = list(DictionaryEntry.objects.filter(word__startswith=phrase[0].lower()))

        entries = [e.getWord() for e in d_index]

        if len(phrase) > 2:  # two endings for plural words: 's' and 'ies'. Check for both.
            if (phrase[-1] == 's') and (phrase[:-1]) in entries:
                valid_plural, singular_form = True, phrase[:-1]
            elif (len(phrase) > 3) and (phrase[-3:] == 'ies'):
                singular = (phrase[:-3] + 'y')
                if singular in entries:
                    valid_plural, singular_form = True, singular
    return valid_plural, singular_form


# creates a multi-word phrase of a given length at a given index
# updates the saved word list to include the phrase if the phrase is in the saved dictionary
def checkPhrase(index, p_len):
    phrase_words = words[index: (index + p_len)]
    phrase = '_'.join(phrase_words)

    if len(phrase) > 0:

        # gets the dictionary index where the phrase may be
        d_index = list(DictionaryEntry.objects.filter(word__startswith=phrase[0].lower()))

        for entry in d_index:  # for every definition in that index
            comparator = entry.getWord()  # the word for that definition

            # checks if the phrase matches the comparator
            singular_defined = (phrase == comparator)
            valid_plural, singular_form = pluralCheck(phrase)
            plural_match = (valid_plural and (singular_form == comparator))

            if singular_defined or plural_match:
                words.insert(index, comparator)  # inserts the phrase at the index of the phrase's first word
                for i in range(0, p_len):
                    words.pop(index + 1)  # removes the words that the phrase replaces

# corrects the saved word list to include any multi-word dictionary entries
def correct():
    index = 0
    while index < len(words):  # for every index (the length of the word list may change)

        # we check every possible multi-word phrase following that index starting at length 2
        p_len = 2
        while p_len <= (len(words) - index):
            checkPhrase(index, p_len)
            p_len += 1

        index += 1


# generator that yields any possible (word, word type) pair given any (word, index) pair
def findTypes(word):
    rule_found = False

    index = list(DictionaryEntry.objects.filter(word__startswith=word[0].lower()))

    for entry in index:
        entry_word, word_type = entry.getWord(), entry.getType()

        singular_match = (entry_word == word)
        valid_plural, singular_form = pluralCheck(word)
        plural_match = (word_type == 'Name') and valid_plural and (entry_word == singular_form)

        if singular_match or plural_match:
            rule_found = True
            yield entry_word, word_type  # yield the matching entry and the word type

    if not rule_found:
        yield 1, 1


# updates the dictionary of trees to include the words within the save word list
def findWords():
    for i in range(len(words)):  # for each word, find that word's index in the dictionary
        for word, word_type in findTypes(words[i]):
            if (type(word_type) == int) and (i > 0) and (words[i - 1] == 'i\'m'):
                # if 'I'm' proceeds the word, assume that it's a name.
                word, word_type = words[i], 'Name'
                if not word[-1].isalpha():
                    word = word[:-1]  # Make sure to leave out punctuation, though

            if type(word_type) == str:  # for every valid word type known of that word
                key = (word_type + '|' + str(i) + '|' + str(i))  # construct a key denoting its type and sentence index
                # at that key in the dictionary, add a node containing the word
                trees[key] = Node(word_type, word)


# returns the indexes needed for every possible
# one-phrase and two-phrase subspan for a sentence of a given length
def getSubspans(total_len):
    for word_index in range(total_len):  # subspan indexes for one-phrase rules
        yield word_index, word_index, -1

    for current_len in range(2, total_len + 1):  # indexes for two-phrase rules
        for lower_index in range(0, (total_len - current_len + 1)):
            upper_index = lower_index + current_len - 1
            for middle_index in range(lower_index, upper_index):
                yield lower_index, middle_index, upper_index


# generator that yields every rule of a given list of rules
# that is either one or two phrases
def findRules(phrase_number):

    rules = GrammarRule.objects.all()

    for rule in rules:
        parent_rule = rule.getRule()
        child_rules = rule.getAddends()

        if (phrase_number == 1) and (child_rules[1] == 'N/A'):
            yield parent_rule, child_rules[0]  # yield the one-word rule
        elif (phrase_number == 2) and (child_rules[1] != 'N/A'):
            yield parent_rule, child_rules[0], child_rules[1]  # yield the two-word rule


# adds any possible sentence component to that dictionary (including sentences)
def findComponents():
    # get the indexes needed for every possible subspan
    for lower_index, middle_index, upper_index in getSubspans(len(words)):
        if upper_index == -1:  # one-phrase subspans
            for rule in findRules(1):  # for all one-phrase rules

                # each key denotes a rule and the indexes that that rule may span across
                parent_key = rule[0] + '|' + str(lower_index) + '|' + str(middle_index)
                child_key = rule[1] + '|' + str(lower_index) + '|' + str(middle_index)

                # if the sentence contains the phrase needed for the rule at the right index
                if child_key in trees.keys():
                    # update the dictionary with that rule
                    trees[parent_key] = Node(rule[0], trees[child_key])

        else:  # two-phrase subspans
            for rule in findRules(2):  # for all two-phrase rules

                # each key denotes a rule and the indexes that that rule may span across
                parent_key = rule[0] + '|' + str(lower_index) + '|' + str(upper_index)
                child_key1 = rule[1] + '|' + str(lower_index) + '|' + str(middle_index)
                child_key2 = rule[2] + '|' + str(middle_index + 1) + '|' + str(upper_index)

                # if the sentence contains the phrases needed for the rule at the right indexes
                if (child_key1 in trees.keys()) and (child_key2 in trees.keys()):
                    # update the dictionary with that rule
                    trees[parent_key] = Node(rule[0], trees[child_key1], trees[child_key2])


# constructs a dictionary of trees from a given set of rules and returns it
def parse(word_list):
    global words, trees

    # save the words, and dictionary as global variables
    words = word_list

    # reset the dictionary of trees
    trees = dict()

    try:
        correct()  # corrects the given word list to include any multi-word dictionary entries
    except KeyError:
        return

    findWords()  # adds any known words to the sentence
    findComponents()  # adds any possible sentence component to that dictionary (including sentences)

    return trees
