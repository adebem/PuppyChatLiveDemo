from .parse import parse
from .models import Dog
from random import randint


# Class that stores context from previous questions and answers new questions
class Conversation:

    def __init__(self, convo_dict):
        # the information that PuppyChat needs to remember in order to properly answer the question
        self.topics = convo_dict['topics']
        self.disclaimer = convo_dict['disclaimer']
        self.first_question = convo_dict['first_question']
        self.response = convo_dict['response']
        self.sentence = convo_dict['sentence']
        self.parse_tree = dict()

    # true if the user input is a 'bye', 'goodbye', or 'farewell', false otherwise
    def Goodbye(self, user_input):
        if len(user_input) > 0:
            if not user_input[-1].isalpha():
                user_input = user_input[:-1]

            first_word = user_input.lower().split(' ')[0]
            if first_word in {'bye', 'goodbye', 'farewell'}:
                if self.topics['user']:
                    return f'Goodbye {self.topics["user"]}!'
                else:
                    return f'Goodbye!'
            else:
                return False

    # if there is a sentence tree in the parse tree, return the biggest sentence tree
    def getSentenceTree(self):
        if self.parse_tree:
            possible_trees = [t for t in list(self.parse_tree.values()) if (t.rule == 'S')]

            try:
                biggest_sentence, max_len = possible_trees[0], possible_trees[0].length()
            except IndexError:
                return None

            for possible_tree in possible_trees[1:]:
                if possible_tree.length() >= max_len:
                    biggest_sentence, max_len = possible_tree, possible_tree.length()

            return biggest_sentence

    # saves the dog name in whatever place is available
    def addDog(self, name):
        if self.topics['dog1']:
            self.topics['dog2'] = name
        else:
            self.topics['dog1'] = name

    # finds if there is a keyword to be saved from a given word
    # keywords need to be remembered for comparison questions
    def findKeyword(self, word):
        # 'shorter' is a special case: if the subject is also 'lifespan', then we save a special comparison keyword
        if (word == 'shorter') and (self.topics['subject'] == 'lifespan'):
            self.topics['comparison_keyword'] = 'shorter minimum life expectancy'

        # otherwise, different words imply different question subjects
        # certain words also warrant saving certain comparison keywords
        elif word in {'behave', 'act', 'personality', 'behavior'}:
            self.topics['subject'] = 'temperament'

        elif word in {'tall', 'taller', 'short', 'shorter'}:
            self.topics['subject'] = 'height'
            if word in {'taller', 'shorter'}:
                self.topics['comparison_keyword'] = word

        elif word in {'weigh', 'weighs', 'heavy', 'heavier', 'lighter'}:
            self.topics['subject'] = 'weight'
            if word == 'heavier':
                self.topics['comparison_keyword'] = 'more'
            elif word == 'lighter':
                self.topics['comparison_keyword'] = 'less'

        elif word in {'live', 'lives', 'longer'}:
            self.topics['subject'] = 'lifespan'
            if (not (self.topics['subject'] and self.topics['subject'] != 'lifespan')) and word == 'longer':
                self.topics['comparison_keyword'] = 'longer maximum life expectancy'

        elif word in {'describe', 'summarize, summary', 'description'}:
            self.topics['subject'] = 'description'

    # gathers information from the sentence tree
    def processTree(self, sentence_tree):

        leaves = sentence_tree.leaves()
        name_given = False

        for wordType, word in leaves:

            is_question_word = (word in {'temperament', 'height', 'weight', 'lifespan', 'group', 'description'})

            # if the user enters a question word or asks about a specific group
            # then the word given is the subject of the question
            if (wordType == 'group') or is_question_word:
                self.topics['subject'] = word
                continue

            # important if the following word is 'dogs'
            # if the user entered 'what/which dog(s)/breed(s)', then they want one-to-all comparison
            if word in {'what', 'which'}:
                self.topics['what/which'] = True

            # if 'dogs' doesn't follow 'what/which', forget that they typed 'what/which'
            elif (word not in {'dog', 'dogs', 'breed', 'breeds'}) and self.topics['what/which']:
                self.topics['what/which'] = False

            # all-to-one comparison if the user entered 'who' or 'what dogs'
            elif (word == 'who') or ((word in {'dog', 'dogs', 'breed', 'breeds'}) and self.topics['what/which']):
                self.addDog('ALL')

            # remember the keyword if the user wants to compare groups
            elif (wordType == 'GroupName') or (word in {'same', 'different'}):
                self.topics['comparison_keyword'] = word

            #  remember the keyword if the user wants to compare weight
            elif (self.topics['subject'] == 'weight') and (word in {'more', 'less'}):
                self.topics['comparison_keyword'] = word

            # remember the previous dog if the user types 'they', 'those', or 'them'
            elif (wordType == 'Pronoun') and (word in {'they', 'those', 'them'}):
                self.addDog(self.topics['previous_dog1'])

            elif wordType == 'Name':
                name = getDogName(word.title())
                if name:  # if it's a valid dog name, save that dog's name
                    self.addDog(name)
                elif self.response == '':
                    # if not, save it as the user's name and remember that the user's name was given
                    name_given = True
                    self.topics['user'] = word.title()

            elif wordType == 'Preposition':
                if word == 'like':
                    self.topics['subject'] = 'temperament'
                if word == 'than':
                    self.topics['compare'] = True

            # if the user entered an adjective, verb, or a noun: find if there is a keyword to be saved
            if wordType in {'Adjective', 'Verb', 'Noun'}:
                self.findKeyword(word)

        # if the user only mentioned their name
        if name_given and (not self.topics['subject']) and (not self.topics['dog1']):
            self.response += 'Hi, {}!\n'.format(self.topics['user'])

    # if the sentence is valid
    #     parses the sentence
    #     finds a sentence tree
    #     gathers information from the tree
    # returns false otherwise
    def parseQuestion(self, question):

        words = [word for word in question.split(' ') if (word != '')]

        if len(words) > 1:
            # updates the parse tree

            self.parse_tree = parse(words)

            try:
                # finds the sentence tree if possible
                sentence_tree = self.getSentenceTree()
                if sentence_tree:
                    # gathers information from that sentence tree
                    self.processTree(sentence_tree)
                    return True
                else:
                    return False
            except ValueError:
                return False

    # Generates output for a one-to-all comparison
    def findTopics(self):
        # finds the subject dog for the comparison (if there is one)
        if self.topics['dog1'] and (self.topics['dog1'] != 'ALL'):
            subject_dog = self.topics['dog1']
        elif self.topics['dog2'] and (self.topics['dog2'] != 'ALL'):
            subject_dog = self.topics['dog2']
        else:
            subject_dog = None

        group_names = {'sporting', 'hound', 'working', 'terrier', 'toy', 'non-sporting', 'herding'}
        higher_keywords = {'taller', 'more', 'longer maximum life expectancy'}
        lower_keywords = {'shorter', 'less', 'shorter minimum life expectancy'}

        # finds how the user wants to compare
        keyword = ''
        if self.topics['comparison_keyword'] in group_names:
            return dogsInGroup(self.topics['comparison_keyword'])
        if self.topics['comparison_keyword'] in higher_keywords:
            keyword = 'higher'
        elif self.topics['comparison_keyword'] in lower_keywords:
            keyword = 'lower'
        elif self.topics['comparison_keyword'] == 'same':
            keyword = self.topics['comparison_keyword']

        attr_question = (
                (self.topics['subject'] in {'height', 'weight', 'lifespan'}) and (keyword in {'higher', 'lower'}))
        group_question = ((self.topics['subject'] == 'group') and (keyword == self.topics['comparison_keyword']))

        # returns a response only if the user wants asks about attributes or group membership
        if attr_question or group_question:
            return findDogs(self.topics['subject'], subject_dog, keyword)
        else:
            return ''

    # Generates output for question about one particular dog breed
    def singularResponse(self, dog_name, proper_name):

        output = ''

        if self.topics['subject'] == 'temperament':
            output = getTemperament(dog_name, proper_name)

        elif self.topics['subject'] == 'description':
            self.topics['description_detail'] += 1
            output = getDescription(dog_name, self.topics['description_detail'])

        elif self.topics['subject'] in {'height', 'weight', 'lifespan', 'group'}:
            output = singularQuestion(dog_name, proper_name, self.topics['subject'])

        return output

    # Decides the type of question and generates its output
    def pickResponse(self, question_number):
        if self.topics['subject']:
            # if there are two subject dogs and the subject is group, then we compare
            if self.topics['dog2'] and (type(self.topics['subject']) == str) and (self.topics['subject'] == 'group'):
                self.topics['compare'] = True

            # if we remember two previous dogs:
            if self.topics['previous_dog1'] and self.topics['previous_dog2']:

                # if no new dog was mentioned, then we keep the last subject dog
                if not self.topics['dog1']:
                    self.topics['dog1'] = self.topics['previous_dog1']

                # if no second dog was mentioned, then we remember a previous dog
                if not self.topics['dog2']:
                    if self.topics['dog1'] != self.topics['previous_dog1']:
                        self.topics['dog2'] = self.topics['previous_dog1']
                    else:
                        self.topics['dog2'] = self.topics['previous_dog2']

            # if we want a description and no new dog was mentioned, then we keep the last subject dog
            if (self.topics['subject'] == 'description') and (not self.topics['dog1']) and \
                    (self.topics['previous_dog1']):
                self.topics['dog1'] = self.topics['previous_dog1']

            # if a new dog was mentioned:
            if self.topics['dog1']:

                # if that new dog isn't the last subject dog
                # we only describe at the most basic detail
                if self.topics['previous_dog1'] != self.topics['dog1']:
                    self.topics['description_detail'] = 0

                dog_name = self.topics['dog1']
                proper_name = dog_name.replace('_', ' ')

                # pick a comparison
                output = ''

                if 'ALL' in (self.topics['dog1'], self.topics['dog2']):  # one-to-all comparison
                    output = self.findTopics()

                elif self.topics['compare'] and self.topics['dog2']:  # one-to-one comparison
                    if self.topics['dog1'] == self.topics['dog2']:  # make sure we're not comparing the same dog
                        output = 'They\'re the same dog!\n'
                    else:
                        dog_name2 = self.topics['dog2']
                        proper_name2 = dog_name2.replace('_', ' ')
                        output = compare(dog_name, proper_name, dog_name2, proper_name2, self.topics['subject'],
                                         self.topics['comparison_keyword'])

                elif not self.topics['compare']:  # no comparison
                    output = self.singularResponse(dog_name, proper_name)

                if question_number > 0:
                    and_or_also = ['And', 'Also'][randint(0, 1)]

                    if not (output.startswith('Yes, ') or output.startswith('No, ')):
                        proper_names = [(output.startswith(e['name'].replace('_', ' '))) for e in
                                        list(Dog.objects.values('name'))]
                    else:
                        proper_names = [False]

                    if True in proper_names:
                        replacement = output[0]
                    else:
                        replacement = output[0].lower()

                    if (not (output.startswith('No, ') or output.startswith('Yes, '))) and (and_or_also == 'Also'):
                        output = output.replace(output[0], f'{and_or_also}, {replacement}', 1)
                    else:
                        output = output.replace(output[0], f'{and_or_also} {replacement}', 1)

                self.response += output

        return self.response

    def clearTopics(self):
        self.topics['dog1'] = None
        self.topics['dog2'] = None
        self.topics['subject'] = None
        self.topics['compare'] = None
        self.topics['comparison_keyword'] = None
        self.topics['what/which'] = False

        self.parse_tree = dict()
        self.sentence = None

    # After ever response, topics should be reset, but remember dogs mentioned in the previous question
    def resetTopics(self):
        if self.topics['dog1']:
            self.topics['previous_dog1'] = self.topics['dog1']
        if self.topics['dog2']:
            self.topics['previous_dog2'] = self.topics['dog2']
        self.clearTopics()

    # for each question:
    #     parses the user's question
    #     picks a response
    # afterwords, resets the self.topics
    def respond(self, user_input):

        goodbye = self.Goodbye(user_input)

        if goodbye:
            return goodbye

        self.resetTopics()

        self.response = ''

        user_input = f"{user_input}"

        questions = [q for q in user_input.lower().replace('.', '?').split('?') if q]

        for i, question in enumerate(questions):

            parsed = self.parseQuestion(question)

            if parsed:
                self.pickResponse(i)

            if self.response == '':
                return 'Sorry, I don\'t understand. Can you ask again?\n\n'

            elif (not self.response.startswith('Hi')) and self.first_question:

                # always disclaim in the first response that the American Kennel Club is the source of the information:
                if 'American Kennel Club' not in self.response:
                    proper_names = [(self.response.startswith(e['name'].replace('_', ' '))) for e in
                                    list(Dog.objects.values('name'))]

                    if True in proper_names:
                        self.response = self.disclaimer + self.response
                    else:
                        self.response = self.disclaimer + self.response[0].lower() + self.response[1:]

                self.first_question = False

        return ConversationalListing(self.response)


# stores a chat entry's input and output
class ChatEntry:
    def __init__(self, question, answr):
        self.i = question
        self.o = answr

    def __str__(self):
        return self.i

    def answer(self):
        return self.o


# HELPER FUNCTIONS

# returns a dog name if the given name is a valid dog name
# returns nothing otherwise
def getDogName(name):
    # first, we find the first letter of the given name and get that index
    first_letter = name[0]

    name_index = Dog.objects.filter(name__startswith=first_letter)
    # then, we search all dog names and nicknames in that index for the name of the dog
    for dog in name_index:
        is_name = (name == dog.getName())
        is_nickname = (dog.getNicknames() and (name in dog.getNicknames()))
        if is_name or is_nickname:
            return dog.getName()

    # if the name wasn't in that list, check the nicknames of every dog not that list
    other_dogs = Dog.objects.exclude(name__startswith=first_letter)
    for dog in other_dogs:
        # skip the index that we already searched through and only check the nicknames
        if dog.getNicknames() and (name in dog.getNicknames()):
            return dog.getName()


# displays a pluralized version of a breed name if needed
def makePlural(name):
    if name.lower() == 'cane corso':
        return name[:3] + 'i' + name[4:9] + 'i'
    if name[-1] == 'y':
        return name[:-1] + 'ies'
    elif (name[-1] != 's') and ((len(name) <= 2) or name[-3:] != 'ese'):
        return name + 's'
    else:
        return name


# returns the American Kennel Club's description of a breed's temperament
def getTemperament(dog_name, proper_name):
    response = 'According to the American Kennel Club:\n{} are known to be '.format(makePlural(proper_name))
    temperament = getDog(dog_name).getTemperament()

    for i in range(len(temperament)):
        if (i + 1) == len(temperament):
            response += 'and '
        response += temperament[i]
        if (i + 1) < len(temperament):
            response += ', '

    return response + '.\n'


# returns the American Kennel Club's description of a breed, depending on the given description detail
def getDescription(dog_name, detail):
    response = ''
    if detail == 1:
        response += 'Here\'s what the American Kennel Club website has to say:\n\n'
        response += getDog(dog_name).getDescriptionShort()
    elif detail == 2:
        response += 'According to the American Kennel Club:\n\n'
        response += getDog(dog_name).getDescriptionLong()
    return response


# retrieves breed information from the Dog database given a breed name
def getDog(dog_name):
    subj_dog = Dog.objects.get(name=dog_name)
    return subj_dog


# supplies the answer for a question about a specific dog's attribute
def answer(subj, attr):
    if subj == 'group':
        # attr variable will already contain the group name
        return 'are in the {} group.\n'.format(attr)

    phrases = {
        'height': ['are typically', 'inches tall', 'be'],
        'weight': ['typically weigh', 'pounds', 'weigh'],
        'lifespan': ['live', 'years long', 'live']
    }

    keywords = phrases[subj]
    response = keywords[0]

    # constructing the response depends on the dog's attribute
    if type(attr) == list:  # there is a more than one value
        if type(attr[1]) in {int, float}:  # there is a range of values
            response += ' between {} and {} '.format(attr[0], attr[1])
        elif type(attr[1]) == list:  # special case: there is a smaller and bigger variety of the breed
            response = 'come in two varieties:\n'
            response += '    The smaller ones can {} up to {} {}.\n'.format(keywords[2], attr[0], keywords[1])
            response += '    The bigger ones {} between {} and {} '.format(keywords[0], attr[1][0], attr[1][1])

    elif type(attr) == tuple:  # there is ambiguity in the value, so add a qualifier to the response
        if attr[1] == 'and over':
            response += 'at least '
        elif attr[1] == 'and under':
            response += 'up to '
        response += '{} '.format(attr[0])

    elif type(attr) in {int, float}:  # there is only one value
        response += ' around {} '.format(attr)

    if response != '':
        response += '{}.\n'.format(keywords[1])

    return response


# answers a question about one particular breed's height, weight, lifespan, or group
def singularQuestion(dog_name, proper_name, subj):
    subject = getDog(dog_name).getSubject(subj)
    response, qualifier = '', ''

    # constructing the response depends on if there are any varieties of the breed
    if (subj != 'group') and (type(subject) == str):
        response += 'The American Kennel Club describes the {}\'s {} as "{}."'.format(proper_name, subj, subject)
    else:
        proper_name = makePlural(proper_name)

        if type(subject) == dict:
            # there are varieties to the dog breed
            varieties = [k.title() for k in list(subject.keys())]
            attributes = [subject[variety.lower()] for variety in varieties]

            # to make PuppyChat more conversational, don't mention the breed name more than once
            for i in range(len(attributes)):
                if i == 0:
                    response += '{} {} '.format(varieties[0], proper_name)
                else:
                    response += '{}s '.format(varieties[1])

                response += answer(subj, attributes[i])  # appends the answer to the response

        else:
            # when there are no varieties, just append the name and the answer to the response
            response += ('{} '.format(proper_name) + answer(subj, subject))

    return response


# constructs a response to a one-to-one group comparison
def compareGroups(dog_name1, proper_name1, dog_name2, proper_name2, comparison_keyword):
    response = ''
    group1, group2 = getDog(dog_name1).getGroup(), getDog(dog_name2).getGroup()
    is_same = ((comparison_keyword == 'same') and (group1 == group2))
    is_different = ((comparison_keyword == 'different') and (group1 != group2))

    # the response depends on the keyword and the comparison results
    if is_same or is_different:
        response += 'Yes, '
    else:
        response += 'No, '

    if group1 == group2:
        response += '{} and {} are both in the {} group.\n' \
            .format(proper_name1, proper_name2, group1)
    else:
        response += '{} are in the {} group and {} are in the {} group.\n' \
            .format(proper_name1, group1, proper_name2, group2)

    return response


# for unspecific dog attributes that we need to know the min/max of:
#    if the attribute contains the desired min/max desired: return it
#    else: return the name of the dog and keyword associated with its ambiguous attribute
def unspecificMinMax(name, attribute, f):
    max_given = ((f == max) and (attribute[1] == 'and under'))
    min_given = ((f == min) and (attribute[1] == 'and over'))

    if max_given or min_given:
        return attribute[0]
    else:
        return name, attribute[1]


# attempts to obtain a min/max of a particular dog's given attribute
def getMinOrMax(name, attribute, f):
    attr = getDog(name).getSubject(attribute)

    if type(attr) == str:
        # the attribute is completely ambiguous
        return name

    elif type(attr) in {int, float}:
        # the attribute is both the minimum and the maximum
        return attr

    elif type(attr) == tuple:
        # the attribute is partially ambiguous
        return unspecificMinMax(name, attr, f)

    elif type(attr) == dict:
        # the different varieties of the dog have different attributes to compare
        values = list(attr.values())
        comparators = []  # the min/max of these values will be calculated
        for i in range(0, 2):
            value = values[i]
            if type(value) == list:
                # add the min/max of this variety's attributes to the comparator list
                comparators.append(f(value[0], value[1]))
            elif type(value) == tuple:
                # this variety's attribute is partially unspecific
                return unspecificMinMax(name, value, f)
            elif type(value) in {int, float}:
                comparators.append(value)
            elif type(value) == str:
                return name
        return f(comparators[0], comparators[1])

    elif type(attr) == list:
        if type(attr[1]) == list:
            val2 = max(attr[1][0], attr[1][1])
        else:
            val2 = attr[1]

        return f(attr[0], val2)


# returns four key pieces of information about a one-to-one comparison:
#    max_difference: difference between the maximum values of the each dog's attribute
#    min_difference: difference between the minimum values of the each dog's attribute
#    always_taller: whether or not the first dog is always taller than the second dog
#    always_shorter: whether or not the first dog is always shorter than the second dog
def getDifferences(dog_name1, dog_name2, subject) -> object:
    max1 = getMinOrMax(dog_name1, subject, max)
    min1 = getMinOrMax(dog_name1, subject, min)
    max2 = getMinOrMax(dog_name2, subject, max)
    min2 = getMinOrMax(dog_name2, subject, min)

    if str in {type(max1), type(min1), type(max2), type(min2)}:
        # conveniently returns the name of the dogs that have the completely ambiguous attributes
        if str in {type(max1), type(min1)}:
            return max1, min1, False, False
        elif str in {type(max2), type(min2)}:
            return max2, min2, False, False

    if tuple in {type(max1), type(max2), type(min1), type(min2)}:
        # if one dog has an ambiguous maximum or minimum value for an attribute:
        # then we cannot know if one dog is always taller or always shorter
        always_taller = False
        always_shorter = False
    else:
        always_taller = (min1 > max2)
        always_shorter = (min2 > max1)

    # for max_difference and min_difference:
    #     if a dog's attribute was ambiguous, make the difference the attribute
    #     else, calculate the difference

    # find max_difference
    if type(max1) == tuple:
        max_difference = max1
    elif type(max2) == tuple:
        max_difference = max2
    else:
        max_difference = max1 - max2

    # find min_difference
    if type(min1) == tuple:
        min_difference = min1
    elif type(min2) == tuple:
        min_difference = min2
    else:
        min_difference = min1 - min2

    return max_difference, min_difference, always_taller, always_shorter


# constructs a specific response if there is ambiguity between the given dogs' attributes
def unspecificDifferences(differences, subject, comparison_keyword):
    response = ''

    if subject in {'height', 'weight', 'lifespan'}:
        comparing_better = (comparison_keyword in {'taller', 'more', 'longer maximum life expectancy'})
        comparing_worse = (comparison_keyword in {'shorter', 'less', 'shorter minimum life expectancy'})
        maximum, minimum = differences[0], differences[1]
        ambiguous_max = ((type(maximum) in {str, tuple}) and comparing_better)
        ambiguous_min = ((type(minimum) in {str, tuple}) and comparing_worse)

        phrases = {
            'height': ['is taller', 'is shorter'],
            'weight': ['weighs more', 'weighs less'],
            'lifespan': ['lives longer', 'lives a shorter life'],
        }

        if ambiguous_max or ambiguous_min:  # the construction of the response depends on what is ambiguous

            if type(maximum) in {str, tuple}:
                ambiguity = maximum
            else:
                ambiguity = minimum

            if type(ambiguity) == str:
                proper_name = makePlural(ambiguity.replace('_', ' '))
                response += 'It is unclear which {} and which {}.\nThe American Kennel Club does not specify a {} for' \
                            ' {}.'.format(phrases[subject][0], phrases[subject][1], subject, proper_name)
            elif type(ambiguity) == tuple:
                proper_name = makePlural(ambiguity[0].replace('_', ' '))
                if ambiguity == maximum:
                    index = 0
                    min_or_max = 'maximum'
                else:
                    index = 1
                    min_or_max = 'minimum'

                response += 'It is unclear which dog {}.\nThe American Kennel Club does not specify a {} {} ' \
                            'for {}.'.format(phrases[subject][index], min_or_max, subject, proper_name)

    return response


# constructs a response specific to interesting comparison outcomes given two dogs, their differences, and a suffix
def specificResponses(differences, proper_name1, proper_name2, comparison, suffix):
    response = ''
    max_difference, min_difference, always_better, always_worse = differences
    phrase_dict = {
        'height': ('are taller', 'are shorter', 'are actually', 'taller maximum height', 'shorter minimum height'),
        'weight': ['weigh more', 'weigh less', 'are actually', 'heavier maximum weight', 'lighter minimum weight'],
        'lifespan': ['should live longer', 'don\'t live as long', 'actually have', 'longer maximum life expectancy',
                     'shorter minimum life expectancy'],
    }

    # definite answers are only given if the comparison is always true or always false
    if always_better or always_worse:
        comparing_better = (suffix in {'taller', 'more', 'longer maximum life expectancy'})
        comparing_worse = (suffix in {'shorter', 'less', 'shorter minimum life expectancy'})

        if (always_better and comparing_better) or (always_worse and comparing_worse):
            response += 'Yes, '
        else:
            response += 'No, '

    phrases = phrase_dict[comparison]

    # construction of the rest of the answer depends on certain comparison outcomes
    if always_better:
        response += '{} {} than {}.\n'.format(proper_name1, phrases[0], proper_name2)
    elif always_worse:
        response += '{} {} '.format(proper_name1, phrases[1])
        if comparison == 'lifespan':
            response += 'as'
        else:
            response += 'than'
        response += ' {}.\n'.format(proper_name2)
    elif (type(max_difference) == type(min_difference)) and (type(max_difference) in {int, float}):
        if max_difference == min_difference:
            response += 'Both breeds {} the same {}.\n'.format(phrases[2], comparison, proper_name2)
        elif ((max_difference > 0) and (min_difference < 0)) or ((max_difference < 0) and (min_difference > 0)):
            return_str = 'Interestingly, ', ' have a {} and a {}.\n'.format(phrases[3], phrases[4])
            if max_difference > 0:
                response += (return_str[0] + proper_name1 + return_str[1])
            else:
                response += (return_str[0] + proper_name2 + return_str[1])
    return response


# constructs an answer string given a comparison winner, qualifier word, a suffix, and a comparison loser
def constructAnswer(dog_name1, qualifier, suffix, dog_name2):
    prefix = ''  # the prefix of the answer depends on the suffix
    if suffix in {'longer maximum life expectancy', 'shorter minimum life expectancy'}:
        return '{} have a {} when compared to {}.'.format(dog_name1, suffix, dog_name2)

    if suffix in {'taller', 'shorter'}:
        prefix = 'are '
    elif suffix in {'more', 'less'}:
        prefix = 'weigh '
    return '{} {}{} {} than {}.'.format(dog_name1, prefix, qualifier, suffix, dog_name2)


# returns a response that compares two dog breeds on a given attribute
def compare(dog_name1, proper_name1, dog_name2, proper_name2, attribute, comparison_keyword):
    proper_name1, proper_name2 = makePlural(proper_name1), makePlural(proper_name2)
    if (type(attribute) == str) and (attribute == 'group') and (comparison_keyword in 'same', 'different'):
        # comparing groups requires a separate helper function
        return compareGroups(dog_name1, proper_name1, dog_name2, proper_name2, comparison_keyword)

    # compare anything else
    else:
        diffs = getDifferences(dog_name1, dog_name2, attribute)
        response = unspecificDifferences(diffs, attribute, comparison_keyword)

        if response == '':  # if there is no ambiguity between both dogs' attributes
            specific_responses = specificResponses(diffs, proper_name1, proper_name2, attribute, comparison_keyword)

            # there are specific responses for special interesting cases
            if specific_responses != '':
                return specific_responses

            # normal responses are constructed depending on the comparison keyword and ambiguity
            suffixes = {
                'height': ['taller', 'shorter'],
                'weight': ['more', 'less'],
                'lifespan': ['longer maximum life expectancy', 'shorter minimum life expectancy'],
            }

            max_comparable = (comparison_keyword == suffixes[attribute][0])
            min_comparable = (comparison_keyword == suffixes[attribute][1])

            max_difference, min_difference, always_taller, always_smaller = diffs
            not_bigger = (max_comparable and max_difference < 0)
            not_smaller = (min_comparable and min_difference > 0)

            if response != '':
                response += '\n'

            slightly_more = (max_comparable and (0 < abs(max_difference) < 1))
            slightly_less = (min_comparable and (0 < abs(min_difference) < 1))

            if slightly_more or slightly_less:
                qualifier = 'slightly'
            else:
                qualifier = 'a bit'

            if max_comparable or min_comparable:

                if comparison_keyword == suffixes[attribute][0]:
                    min_or_max = 'maximum'
                else:
                    min_or_max = 'minimum'

                if (max_comparable and (max_difference == 0)) or (min_comparable and (min_difference == 0)):
                    response += 'Both breeds are the same at their {} {}.'.format(min_or_max, attribute)
                else:
                    if not_bigger or not_smaller:
                        response += 'No, '
                        comparison_keyword = [kw for kw in suffixes[attribute] if kw != comparison_keyword][0]
                    else:
                        response += 'Yes, '
                    response += constructAnswer(proper_name1, qualifier, comparison_keyword, proper_name2)

        return response + '\n'


# lists all dogs in a given group
def dogsInGroup(group_name):
    response = 'These are some of the most popular breeds in the {} group:\n'.format(group_name)
    for dog in Dog.objects.all():
        if dog.getGroup() == group_name:
            proper_name = dog.getName().replace('_', ' ')
            response += ' {},'.format(makePlural(proper_name))

    return response[:-1] + "."


# there is ambiguity in the desired dog's attribute:
#     a report on that ambiguity will be returned
def checkForAmbiguity(keyword, attribute, subject_dog):
    response = ''
    reference = getDog(subject_dog).getSubject(attribute)
    unspecified_both, unspecified_max, unspecified_min = False, False, False
    ambiguity_info = tuple()

    # the ambiguity depends on the desired dog's attribute
    if type(reference) == str:
        unspecified_both = True
    elif type(reference) == dict:
        for val in reference.values():
            if type(val) == tuple:
                ambiguity_info = val
                break
    elif type(reference) == tuple:
        ambiguity_info = reference

    if ambiguity_info != tuple():
        unspecified_max = ((keyword == 'higher') and (ambiguity_info[1] == 'and over'))
        unspecified_min = ((keyword == 'lower') and (ambiguity_info[1] == 'and under'))

    if unspecified_both or unspecified_max or unspecified_min:
        response += 'Actually, I\'m unsure.\nThe American Kennel Club doesn\'t '

        if unspecified_both:
            response += 'clearly specify the {}\'s {}.\n'.format(subject_dog.replace('_', ' '), attribute)
        else:
            response += 'specify a '
            if unspecified_max:
                response += 'maximum {}'.format(attribute)
            else:
                response += 'minimum {}'.format(attribute)

            response += ' for the {}.\n'.format(subject_dog.replace('_', ' '))

    return response


# produces a list of dogs that satisfy the comparison
def getDogList(attribute, subject_dog, keyword):
    dog_list = []

    # the value that we reference depends on the keyword
    if keyword == 'higher':
        reference = getMinOrMax(subject_dog, attribute, max)
    elif keyword == 'lower':
        reference = getMinOrMax(subject_dog, attribute, min)
    else:
        reference = getDog(subject_dog).getSubject(attribute)

    if reference:  # if we have a value to reference
        for dog in Dog.objects.all():
            # find a comparator value for every dog besides the subject dog
            if dog.getName() != subject_dog:
                # the comparator also depends on the keyword
                satisfies = False

                if keyword in {'higher', 'lower'}:
                    if keyword == 'higher':
                        comparator = getMinOrMax(dog, attribute, max)
                    else:
                        comparator = getMinOrMax(dog, attribute, min)

                    if type(comparator) in {int, float}:
                        if keyword == 'higher':
                            satisfies = (comparator > reference)
                        else:
                            satisfies = (comparator < reference)

                elif attribute == 'group':
                    comparator = getDog(dog).getGroup()
                    satisfies = (comparator == reference)

                if satisfies:
                    dog_list.append(dog.getName().replace('_', ' '))
    return dog_list


# if the question was valid, returns a response to a one-to-all comparison question
def findDogs(subject, subject_dog, keyword):
    response = ''

    # checks if there is ambiguity in the desired attribute of the subject dog
    # if so, there will be an ambiguity report
    ambiguity_report = ''
    if subject != 'group':
        ambiguity_report = checkForAmbiguity(keyword, subject, subject_dog)

    # if there was ambiguity, return the ambiguity report
    if len(ambiguity_report) > 0:
        return ambiguity_report

    # if there wasn't ambiguity, get the list of the dogs that satisfy
    dog_list = getDogList(subject, subject_dog, keyword)

    # these are used to construct the answers
    sentence_fragments = {
        'height': ['stand', 'inches tall', 'can be taller', 'can be shorter'],
        'weight': ['weigh', 'pounds', 'can weigh more', 'can weigh less'],
        'lifespan': ['live', 'years long', 'can live longer', 'have shorter minimum lifespans'],
        'group': ['are', 'in the {} group'.format(getDog(subject_dog).getGroup()), 'are also in that group']
    }

    # the response is constructed based on the given keyword, the subject, and the results of the comparison
    if keyword in {'higher', 'same', 'lower'}:
        proper_name = makePlural(subject_dog.replace('_', ' '))

        verb = sentence_fragments[subject][0]
        value = ' '
        minimum, maximum, min_is_numeric, max_is_numeric = False, False, False, False

        if subject != 'group':
            minimum = getMinOrMax(subject_dog, subject, min)
            maximum = getMinOrMax(subject_dog, subject, max)
            min_is_numeric = (type(minimum) in {int, float})
            max_is_numeric = (type(maximum) in {int, float})

            if minimum and maximum and min_is_numeric and max_is_numeric:
                if minimum == maximum:
                    value = ' {} '.format(minimum)
                else:
                    value = ' between {} and {} '.format(minimum, maximum)
            elif minimum and min_is_numeric:
                value = ' at least {} '.format(minimum)
            elif maximum and max_is_numeric:
                value = ' at most {} '.format(maximum)

        measurement = sentence_fragments[subject][1]

        if keyword in {'higher', 'same'}:
            description = sentence_fragments[subject][2]
        else:
            description = sentence_fragments[subject][3]

        if len(dog_list) > 0:  # if there are dogs that satisfy the comparison

            response += '{} {}{}{}. These breeds {}:\n' \
                .format(proper_name, verb, value, measurement, description)

            measurements = {'height': 'in', 'weight': 'lbs', 'lifespan': 'yrs'}

            for dog in dog_list:
                response += '    {},'.format(makePlural(dog))

                if subject in {'height', 'weight', 'lifespan'}:

                    response = response[:-1]

                    if keyword == 'higher':

                        dog_value = getMinOrMax(dog.replace(' ', '_'), subject, max)
                    else:
                        dog_value = getMinOrMax(dog.replace(' ', '_'), subject, min)

                    dog_measurement = measurements[subject]

                    response += ' ({} {}), '.format(dog_value, dog_measurement)

                response += '\n'

        elif len(dog_list) == 0:  # if there are no dogs that satisfy the comparison

            if keyword in {'higher', 'same'}:
                description = sentence_fragments[subject][2]

                if maximum and max_is_numeric:
                    value = maximum
            else:
                description = sentence_fragments[subject][3]

                if minimum and min_is_numeric:
                    value = minimum

            response += 'I do not know of any dogs that {} than {} ({} {})\n' \
                .format(description, proper_name, value, measurement)

    # remove commas from the end of the response if needed
    if response[-4:] == '), \n':
        return response[:-3] + ' \n'
    elif response[-2:] == ',\n':
        return response[:-1]
    else:
        return response


#  makes a multi-sentence response more conversational by adding in 'and' and 'also'
def ConversationalListing(string):
    sentences = [s.strip() for s in string[:-1].split('. ') if s != ' ']

    if len(sentences) >= 2:
        output = f'{sentences[0]}. '
        for sentence in sentences[1:]:
            and_or_also = ['And', 'Also'][randint(0, 1)]

            sentence = sentence.replace('Yes, ', f'{and_or_also} yes, ', 1)
            sentence = sentence.replace('No, ', f'{and_or_also} no, ', 1)

            if sentence[-1] == ".":
                output += f'{sentence} '
            else:
                output += f'{sentence}. '

        return output[:-1]

    else:
        return string
