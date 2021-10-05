from django import forms


class QuestionForm(forms.Form):
    input = forms.CharField(max_length=500, widget=forms.TextInput(attrs={'autofocus': True}))
