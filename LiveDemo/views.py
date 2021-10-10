from django.shortcuts import render, redirect
from .forms import QuestionForm
from .demo import Conversation, ChatEntry
from pathlib import Path


# Create your views here.

# get goodbye before calling Ask() so that the goodbye entry can be printed on the screen
def Ask(question, conversation):
    i=3
    if question.lower().replace(".|?|!", "") in {"goodbye", "bye", "farewell"}:
        output = "Goodbye!"
    else:
        output = conversation.respond(question)

    new_entry = ChatEntry(question, output)
    conversation.entries.append(new_entry)


def index(request):
    return redirect('home')


def home(request, conversation=Conversation()):

    entries_before = conversation.entries

    form = QuestionForm
    welcome = '\nWelcome to PuppyChat! This is a project meant to showcase my skills in the python programming\n' \
              'language. PuppyChat intelligently answers trivia questions about the American Kennel Club\'s top 60\n' \
              'most popular dog breeds from 2019. You can ask about specific dogs, compare two dogs, or even ' \
              'compare one dog to the rest.\n' \
              '\nNOTE: All of the dog breed information is sourced from the American Kennel Club\'s Website.\n' \
              'None of the information supplied is mine.\n\n Anyways, any dog questions?\n\n'

    if 'input' in dict(request.POST).keys():
        question = dict(request.POST)['input'][0]

        if (len(list(conversation.entries)) == 0) or (str(question) != str(list(conversation.entries)[-1])):
            Ask(question, conversation)

        if (len(list(conversation.entries)) > 1) and (conversation.entries[-2].answer().startswith('Goodbye')):
            conversation.entries = [conversation.entries[-1]]
    else:
        conversation.entries = []

    context = {
        "welcome": welcome,
        "form": form,
        "entries": conversation.entries,
        "entries_before": entries_before,
        "conversation": conversation,
        'rp': dict(request.POST),
        'based': Path(__file__).resolve().parent.parent,
    }

    return render(request, "home.html", context)
