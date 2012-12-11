#encoding=utf8

from votingsystem.sondages.models import *
from django import forms
from django.forms.extras.widgets import SelectDateWidget
from django.forms.widgets import HiddenInput
import datetime

#from django.forms.widgets import RadioSelect,CheckboxSelectMultiple

from votingsystem.sondages.widgetsTest import RadioSelect

class PollForm(forms.ModelForm):
    """Formulaire de création d'un nouveau sondage (titre, date de fin, anonymat, etc.)"""

    class Meta:
        model = Poll
        exclude = ('pollster', 'pubDate','editable','answerCount')

    def __init__(self, *args, **kwargs):
        super(PollForm,self).__init__(*args, **kwargs)
        self.fields['title'].label = "Titre "
        self.fields['endDate'].label = "Date de fin du sondage "
        self.fields['anonymous'].label = "Anonyme "
        self.fields['endDate'].widget = SelectDateWidget()
        self.fields['endDate'].initial = str(datetime.date.today()+datetime.timedelta(15))

class QuestionsNumber(forms.Form):
    number=forms.CharField(widget=HiddenInput())

class QuestionType(forms.Form):
    type=forms.CharField(widget=HiddenInput()) #forms.Select(choices=(('qtxt',"Textual Question"),("mcq","Mutliple Choice Question"))))

class QuestionForm(forms.ModelForm):
    class Meta:
        model = TextualQuestion
        exclude = ("poll",)

class MCQuestionForm(forms.ModelForm):
    class Meta:
        model = MCQuestion 
        exclude = ("poll","possibleChoicesNumber","orderedChoices")
    def mcquestion(self):
        return True

class TextualAnswerForm(forms.ModelForm):
    class Meta:
        model = TextualAnswer
        exclude = ("question","ipAddress","date","signature")

class TextualChoiceForm(forms.ModelForm):
    class Meta:
        model = TextualChoice
        exclude = ('question',)

class ImageChoiceForm(forms.ModelForm):
    class Meta:
        model = ImageChoice
        exclude = ('question',)

class FileChoiceForm(forms.ModelForm):
    class Meta:
        model = FileChoice
        exclude = ('question',)

    
    
class MCQAnswerForm(forms.ModelForm):

    class Meta:
        model = MCQAnswer
        exclude = ("ipAddress","date","question","preference","signature")

    choice = forms.ModelChoiceField(queryset=Choice.objects.all(),widget = RadioSelect(),empty_label = None)

    def __init__(self, question, *args, **kwargs):
        super(MCQAnswerForm,self).__init__(*args, **kwargs)
        self.fields['choice'].queryset = queryset=question.choice_set.all()
        #self.fields['choice'].widget = forms.RadioSelect()
    def setChoice(self,question):
        self.choice = forms.ModelChoiceField(queryset=question.choice_set.all(),widget = RadioSelect(),empty_label = None)
    
