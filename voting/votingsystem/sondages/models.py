#encoding=utf8

from django.db import models
import uuid
from django.utils.html import escape, conditional_escape
from django.utils.encoding import force_unicode


class INSAUser(models.Model):
    """Un acteur de l'INSA ayant un compte dans le LDAP"""

    uid = models.CharField(max_length=50,unique=True)
    fullname = models.CharField(max_length=150)
    def __unicode__(self):
        return unicode(self.uid)

class INSAGroup(models.Model):
    """Un groupe de l'INSA présent dans le LDAP"""

    gid = models.CharField(max_length=50)

    def __unicode__(self):
        return unicode(self.gid)

class Poll(models.Model):
    """Un sondage"""

    #editable = models.BooleanField(default=True)
    #"""Si le sondage est en cours d'édition ou non"""
    title = models.CharField(max_length=200)
    """Titre du sondage"""
    pubDate = models.DateTimeField("publication date")
    """Date de publication"""
    pollster = models.ForeignKey(INSAUser)
    """Utilisateur ayany publié le sondage"""
    endDate = models.DateTimeField("end date", default="")
    """Date de fin de validité du sondage"""
    anonymous = models.BooleanField(default=True)
    """Si oui, le sondage ne sera pas signé"""
    answerCount = models.PositiveIntegerField(default=0)

    def answered(self):
        self.answerCount+=1
    
    def get_anonymous_display(self):
        if self.anonymous:
            return "Oui"
        else:
            return "Non"

    def get_endDate_display(self):
        return self.endDate.strftime("%d/%m/%Y")
        
    def alreadyAnwsered(self,uid):
        if self.anonymous:
            return False
        else:
            try:
                sig=Signature.objects.filter(poll=self,user=INSAUser.objects.get(uid=uid))
            except:
                return False
            return len(sig)>0

    def questions_number(self):
        return len(self.question_set.all())
    
    def __unicode__(self):
        return unicode(self.title)

    def wasPublishedToday(self):
        return self.pubDate.date() == datetime.date.today()

class Authorization(models.Model):
    """Une autorisation de voir et de répondre à un sondage.
    Est abstraite"""

    class Meta:
        abstract = True

    poll = models.ForeignKey(Poll)

class UserAuthorization(Authorization):
    """Une autorisation donnée à un utilisateur particulier"""

    user = models.ForeignKey(INSAUser)

    def __unicode__(self):
        return u"%s for '%s'" % (self.user, self.poll)

class GroupAuthorization(Authorization):
    """Une autorisation donnée à un groupe LDAP particulier"""

    group = models.ForeignKey(INSAGroup)

    def __unicode__(self):
        return u"%s for '%s'" % (self.group, self.poll)

class FullAuthorization(Authorization):
    """Une autorisation donnée à tous les utilisateurs"""

    def __unicode__(self):
        return u"Full auth. for '%s'" % (self.poll)

class Question(models.Model): # Meant to be abstract
    """Une question appartennant à un sondage. Il s'agit d'un simple texte.
    Est abstraite, bien que non implémentée comme telle pour des raisons techniques inhérentes à Django (une classe abstraite ne peut pas être pointée par des ForeignKey)"""

    poll = models.ForeignKey(Poll)
    text = models.CharField(max_length=500)
    
    
    def answer(self):
        if hasattr(self,'textualquestion'):
            return self.textualquestion.textualanswer_set
        elif hasattr(self,'mcquestion'):
            return self.mcquestion.countanswer()
        else:
            return None

    def __unicode__(self):
        return unicode(self.text)


class MCQuestion(Question):
    """Une question à choix multiple"""

    possibleChoicesNumber = models.PositiveSmallIntegerField(default=1)
    """Lorsqu'on répond à une question à choix multiple, on peut choisir une ou plusieurs réponses"""
    orderedChoices = models.BooleanField(default=False)
    """Lorsqu'on donne plusieurs réponses, on peut les ordonner"""

    def countanswer(self):
        answer=[]
        for choice in self.choice_set.all():
            answer.append((choice,choice.mcqanswer_set.count()))
        return answer

class Choice(models.Model): # Meant to be abstract
                            # See http://docs.djangoproject.com/en/dev/topics/db/models/#multi-table-inheritance
    """Un choix possible pour une MCQuestion.
    Est abstraite, bien que non implémentée comme telle"""

    question = models.ForeignKey(MCQuestion,blank=True,null=True)

    def __unicode__(self):
        if hasattr(self,"textualchoice"):
            return self.textualchoice.__unicode__()
        elif hasattr(self,"imagechoice"):
            return self.imagechoice.__unicode__()
        elif hasattr(self,"filechoice"):
            return self.filechoice.__unicode__()
        return "Choice for '%s'" % (self.question)

class TextualChoice(Choice):
    """Un choix textuel (basiquement un bouton radio ou une checkbox assortie d'un label) pour une MCQuestion"""

    text = models.CharField(max_length=200)

    def __unicode__(self):
        return u"%s" % (conditional_escape(self.text))

    def as_table(self):
        return "<tr><th><label >Texte:</label></th><td>"+self.text+"</td></tr>"


def setPath(mdl, filename):
    """Donne l'endroit où sera uploadé un fichier sur le serveur"""
    #print "files/%s/%s" % (mdl.question.id, force_unicode(filename.replace(" ","_").replace("\\","_").replace("/","_")))
    return "files/%s/%s" % (uuid.uuid4(), force_unicode(filename.replace(" ","_").replace("\\","_").replace("/","_")))

class ImageChoice(Choice):
    """Un choix (pour une MCQuestion) dont le label est une image"""

    image = models.ImageField(upload_to=setPath)

    def __unicode__(self):
        #print self.image.name,self.image.path
        if self.image.height > self.image.width:
            options = "height=\"250\""
        else:
            options = "width=\"250\""
        return u"%s <br/> <center><img src=\"/%s\" alt=\"test\" title=\"pouik \" %s/></center>" % (self.image.name.split("/")[-1], self.image.name, options)

    def as_table(self):
        return "<tr><th><label >Image:</label></th><td><img src=\""+self.image.name+"\" alt=\"test\" title=\"pouik \" width=\"250\"/></td></tr>"


class FileChoice(Choice):
    """Un choix (pour une MCQuestion) dont le label est un lien vers un fichier"""

    file = models.FileField(upload_to=setPath)

    def __unicode__(self):
        return u"<a href=\""+self.file.name+"\"> "+self.file.name.split("/")[-1]+"</a>" % ( self.file)

    def as_table(self):
        print "file as table"
        return "<tr><th><label >Fichier:</label></th><td><a href=\""+self.file.name+"\"> "+self.file.name.split("/")[-1]+"</a></td></tr>"


class TextualQuestion(Question):
    """Une question ouverte, à laquelle les utilisateurs répondront en tapant un texte"""
    pass



class Answer(models.Model): # Meant to be abstract
    """Une réponse à une question d'un Poll.
    Est abstraite"""

    ipAddress = models.IPAddressField()
    date = models.DateTimeField("answer date")
    
class MCQAnswer(Answer):
    """Un choix pour une question à choix multiple (MCQuestion)"""

    preference = models.PositiveSmallIntegerField(default=1)
    """Si la MCQuestion demande des choix ordonnés, ceci donne le numéro de ce choix"""

    question = models.ForeignKey(MCQuestion)

    choice = models.ForeignKey(Choice) #, limit_choices_to={'question_id': Question.objects.get(id=question)})
    
    def __unicode__(self):
        return unicode(self.choice)

    def display(self):
        return u"%s" % self.choice

class TextualAnswer(Answer):
    """Une réponse à une TextualQuestion. Il s'agit simplement d'un texte saisi"""

    question = models.ForeignKey(TextualQuestion)
    text = models.CharField(max_length=500,blank=True)

    def display(self):
        return u"%s" % self.text

    def __unicode__(self):
        return u"%s: %s" % (self.question, self.text)

class Signature(models.Model):
    """Associe une réponse à un utilisateur. (Cas des sondages non anonymes)"""

    answer = models.ManyToManyField(Answer)
    user = models.ForeignKey(INSAUser)
    poll = models.ForeignKey(Poll)

    def __unicode__(self):
        return u"%s for '%s'" % (self.user, self.poll)



