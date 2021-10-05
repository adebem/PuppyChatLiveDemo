from django.db import models
from .convert import GetValue
# Create your models here.

class Dog(models.Model):
    name = models.CharField(max_length=30)
    temperament = models.CharField(max_length=50)
    height = models.CharField(max_length=80)
    weight = models.CharField(max_length=80)
    lifespan = models.CharField(max_length=50)
    group = models.CharField(max_length=50)
    description_short = models.TextField()
    description_long = models.TextField()
    nicknames = models.CharField(max_length=100)

    def getName(self):
        return f"{self.name}"

    def getTemperament(self):
        return f"{self.temperament}".split(",")

    def getHeight(self):
        return GetValue(f"{self.height}")

    def getWeight(self):
        return GetValue(f"{self.weight}")

    def getLifespan(self):
        return GetValue(f"{self.lifespan}")

    def getGroup(self):
        return f"{self.group}"

    def getDescriptionShort(self):
        return f"{self.description_short}"

    def getDescriptionLong(self):
        return f"{self.description_long}"

    def getNicknames(self):
        if self.nicknames:
            return f"{self.nicknames}".split(",")
        else:
            return False

    def getSubject(self, subj):
        if subj == 'name':
            return self.getName()
        elif subj == 'temperament':
            return self.getTemperament()
        elif subj == 'height':
            return self.getHeight()
        elif subj == 'weight':
            return self.getWeight()
        elif subj == 'lifespan':
            return self.getLifespan()
        elif subj == 'group':
            return self.getGroup()
        elif subj == 'description_short':
            return self.getDescriptionShort()
        elif subj == 'description_long':
            return self.getDescriptionLong()
        elif subj == 'nicknames':
            return self.getNicknames()

    def setName(self, n):
        self.name = n

    def setTemperament(self, t):
        self.temperament = t

    def setHeight(self, h):
        self.height = h

    def setWeight(self, w):
        self.weight = w

    def setLifespan(self, span):
        self.lifespan = span

    def setGroup(self, g):
        self.group = g

    def setDescriptionShort(self, ds):
        self.description_short = ds

    def setDescriptionLong(self, dl):
        self.description_long = dl

    def setNicknames(self, n):
        if self.nicknames:
            self.nicknames = n

    def __str__(self):
        return f"{self.name}"

class DictionaryEntry(models.Model):
    word = models.CharField(max_length=30)
    word_type = models.CharField(max_length=30)

    def getWord(self):
        return f"{self.word}"

    def getType(self):
        return f"{self.word_type}"

class GrammarRule(models.Model):
    rule = models.CharField(max_length=30)
    addends = models.CharField(max_length=30)

    def getRule(self):
        return f"{self.rule}"

    def getAddends(self):
        addends = self.addends.split(', ')

        return f"{addends[0][1:]}", f"{addends[1][:-1]}"
