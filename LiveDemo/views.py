from django.shortcuts import render, redirect
from .forms import QuestionForm
from .demo import Conversation, ChatEntry
from pathlib import Path


# Create your views here.

# get goodbye before calling Ask() so that the goodbye entry can be printed on the screen
def Ask(request, question, conversation):
    i=3
    if question.lower().replace(".|?|!", "") in {"goodbye", "bye", "farewell"}:
        output = "Goodbye!"
    else:
        output = conversation.respond(question)

    request.session['chat_inputs'] = request.session['chat_inputs'] + [question]
    request.session['chat_outputs'] = request.session['chat_outputs'] + [output]

def startTalking(request):
    new_convo = {
        'topics': {
            'user': str(),
            'previous_dog1': None,
            'previous_dog2': None,
            'dog1': None,
            'dog2': None,
            'subject': None,
            'description_detail': 0,
            'compare': False,
            'comparison_keyword': None,
            'what/which': False
        },
        'disclaimer': "According to the American Kennel Club:\n",
        'first_question': True,
        'response': '',
        'sentence': None
    }
    request.session['conversation'] = new_convo
    request.session['chat_inputs'] = []
    request.session['chat_outputs'] = []

def updateConversation(request, conversation):
    request.session['conversation']['topics'] = conversation.topics
    request.session['conversation']['disclaimer'] = conversation.disclaimer
    request.session['conversation']['first_question'] = conversation.first_question
    request.session['conversation']['response'] = conversation.response
    request.session['conversation']['sentence'] = conversation.sentence

def createEntries(request):
    entries = []

    for i in range(len(request.session['chat_inputs'])):
        chat_input, chat_output = request.session['chat_inputs'][i], request.session['chat_outputs'][i]
        entry = ChatEntry(chat_input, chat_output)
        entries.append(entry)

    return entries

def home(request):
    i=3
    if request.method == 'GET' or 'conversation' not in dict(request.session).keys():
        startTalking(request)

    conversation = Conversation(request.session['conversation'])

    form = QuestionForm
    welcome = '\nWelcome to PuppyChat! This is a project meant to showcase my skills in the python programming\n' \
              'language. PuppyChat intelligently answers trivia questions about the American Kennel Club\'s top 60\n' \
              'most popular dog breeds from 2019. You can ask about specific dogs, compare two dogs, or even ' \
              'compare one dog to the rest.\n' \
              '\nNOTE: All of the dog breed information is sourced from the American Kennel Club\'s Website.\n' \
              'None of the information supplied is mine.\n\n Anyways, any dog questions?\n\n'

    if 'input' in dict(request.POST).keys():
        question = dict(request.POST)['input'][0]

        if (len(request.session['entries']) == 0) or (str(question) != str(request.session['entries'][-1])):
            Ask(request, question, conversation)

        if (len(request.session['entries']) > 1) and (request.session['entries'][-2].answer().startswith('Goodbye')):
            request.session['entries'] = request.session['entries'][-1:]
    else:
        request.session['entries'] = []


    entries = createEntries(request)

    context = {
        "conversation": conversation,
        "welcome": welcome,
        "form": form,
        "entries": entries,
        'rp': dict(request.POST),
        'based': Path(__file__).resolve().parent.parent,
    }

    updateConversation(request, conversation)
    request.session.modified = True

    return render(request, "home.html", context)
