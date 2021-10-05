from django.shortcuts import render
from .forms import QuestionForm
from .demo import Demo
from pathlib import Path

# Create your views here.
demo = Demo()

def Home(request):

    global demo

    form = QuestionForm
    welcome = '\nWelcome to PuppyChat! This is a project meant to showcase my skills in the python programming\n' \
              'language. PuppyChat intelligently answers trivia questions about the American Kennel Club\'s top 60\n' \
              'most popular dog breeds from 2019. You can ask about specific dogs, compare two dogs, or even' \
              'compare one dog to the rest.\n' \
              '\nNOTE: All of the dog breed information is sourced from the American Kennel Club\'s Website.\n' \
              'None of the information supplied is mine.\n\n Anyways, any dog questions?\n\n'

    if 'input' in dict(request.POST).keys():
        question = dict(request.POST)['input'][0]

        if (len(list(demo.entries)) == 0) or (str(question) != str(list(demo.entries)[-1])):
            demo.Ask(question)
    else:
        demo.entries = []

    goodbye = demo.goodbye

    context = {
        "welcome": welcome,
        "form": form,
        "entries": demo.entries,
        "demo": demo,
        "conversation": demo.conversation,
        'goodbye': goodbye,
        'rp': dict(request.POST),
        'based': Path(__file__).resolve().parent.parent,
    }

    return render(request, "home.html", context)
