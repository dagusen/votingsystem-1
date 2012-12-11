#encoding=utf8


from votingsystem.sondages.models import *
from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
from votingsystem.commun import context
from votingsystem import ldapINSA
from votingsystem.sondages.forms import *


def newpoll(request):
    """Appelée lors de la demande du formulaire de création d'un nouveau sondage"""

    ctx=context(request)


    if not ctx["connected"]:
        return redirect("/")


    if(request.method=='POST'):
        return newpollsave(request)
    else:
        try:
            del request.session['newPoll']
        except:
            pass
        try:
            del request.session['lesQuestions']
        except:
            pass
        try:
            del request.session['lesChoix']
        except:
            pass
    ctx['targetForm']="/add"
    ctx['pollform']=PollForm(prefix="newpoll")
    #ctx['number']=QuestionsNumber({'number':'0'})#,prefix="newpollnumber")
    return render_to_response("sondages/newpoll.html",ctx)#redirect("/")

def newpollsave(request):
    """Appelée lorsque l'utilisateur a rentré les informations globales du sondage (titre, date de fin...) et veut y ajouter de nouvelles questions"""

    ctx=context(request)

    pollform = PollForm(request.POST,prefix="newpoll")
    #print request.POST
    if pollform.is_valid():
        if request.session.get('newPoll')==None:
            userldap=ldapINSA.rechercheLDAPUid(request.session.get('username'))
            user,created = INSAUser.objects.get_or_create(uid=request.session.get('username'),defaults={"fullname":userldap.get('nom')+' '+userldap.get('prenom')})
            poll=pollform.save(commit=False)
            poll.pubDate=datetime.date.today()
            poll.pollster = user
            request.session['newPoll']=poll
        else:
            poll = request.session.get('newPoll')
            p2 = pollform.save(commit=False)
            poll.title=p2.title
            poll.endDate=p2.endDate
            poll.anonymous=p2.anonymous
            
    poll=request.session.get('newPoll')
    updatePoll(request,ctx,poll)
    
    
    
    if request.POST.get('button')=="envoyer" and poll != None :
        poll.editable=False
        poll.save()
        if(saveQuestions(request,ctx,poll)):
            del request.session['newPoll']
            del request.session['lesQuestions']
            del request.session['lesChoix']
            return redirect("/liste")

    elif request.POST.get('buttonAddQ')!=None:#"ajouter une question normale": 
        ctx['questionforms'].append((QuestionForm(prefix="newQuestion"),[]))

    elif request.POST.get('buttonAddMCQ')!=None:#"ajouter une question à choix multiple":
        ctx['questionforms'].append((MCQuestionForm(prefix="newMCQuestion"),[]))



    else:
        trouve=False
        #print ctx['questionforms']
        for i in range(0,len(ctx['questionforms'])):
            if not trouve:
                if request.POST.get('buttonAddTextualChoicequestion'+str(i))!=None:#ajouter un choix à une question multiple:
                    ctx['questionforms'][i][1].append(TextualChoiceForm(prefix="question"+str(i)+"newchoice"))
                    trouve=True
                if request.POST.get('buttonAddImageChoicequestion'+str(i))!=None:#ajouter un choix à une question multiple:
                    ctx['questionforms'][i][1].append(ImageChoiceForm(prefix="question"+str(i)+"newchoice"))
                    trouve=True
                if request.POST.get('buttonAddFileChoicequestion'+str(i))!=None:#ajouter un choix à une question multiple:
                    ctx['questionforms'][i][1].append(FileChoiceForm(prefix="question"+str(i)+"newchoice"))
                    trouve=True
        if(len(ctx['questionforms'])>0):
            if request.POST.get('buttonAddTextualChoicenewMCQuestion')!=None:#ajouter un choix à une question multiple:
                ctx['questionforms'][max(0,len(ctx['questionforms'])-1)][1].append(TextualChoiceForm(prefix="question"+str(len(ctx['questionforms'])-1)+"newchoice"))
                trouve=True
            if request.POST.get('buttonAddImageChoicenewMCQuestion')!=None:#ajouter un choix à une question multiple:
                ctx['questionforms'][max(0,len(ctx['questionforms'])-1)][1].append(ImageChoiceForm(prefix="question"+str(len(ctx['questionforms'])-1)+"newchoice"))
                trouve=True
            if request.POST.get('buttonAddFileChoicenewMCQuestion')!=None:#ajouter un choix à une question multiple:
                ctx['questionforms'][max(0,len(ctx['questionforms'])-1)][1].append(FileChoiceForm(prefix="question"+str(len(ctx['questionforms'])-1)+"newchoice"))
                trouve=True

    ctx['targetForm']="/add"
    ctx['pollform']=pollform
    return render_to_response("sondages/newpoll.html",ctx)
    
    
def getChoix(request):
    """Renvoie les choix déjà remplis par l'utilisateur"""

    lesChoix=request.session.get('lesChoix')
    if not lesChoix:
        lesChoix={}
    return lesChoix
    
def getQuestions(request):
    """Revoie les questions que l'utilisateur a déjà ajoutées au sondage"""

    lesQuestions=request.session.get('lesQuestions')
    if not lesQuestions:
        lesQuestions=[]
    return lesQuestions


def renderQuestion(request,poll,typeForm=QuestionForm,*args,**options):
    """Renvoie l'objet Question associé à un QuestionForm"""

    qf=typeForm(*args,**options)
    #print qf.is_valid()
    if qf.is_valid():
        q=qf.save(commit=False)
        #q.poll=poll
        return q
    return None
    
def createQuestionForm(request,question,index,*args,**options):
    """Crée un formulaire pour l'ajout d'une nouvelle question"""

    if isinstance(question,TextualQuestion):
        return (QuestionForm(instance=question,*args,**options),[])
    elif isinstance(question,MCQuestion):
        choix=getChoix(request).get(index)
        print choix
        choicesForm=[]
        if choix:
            for j in range(0,len(choix)):
                #choicesForm.append(createChoiceForm(request,choix[j],prefix=options.get("prefix")+"choice"+str(j)))
                choicesForm.append(choix[j])
        return (MCQuestionForm(instance=question,*args,**options),choicesForm)

def renderChoice(request,question,index,typeChoiceForm=TextualChoiceForm,*args,**options):
    """Renvoie l'object Choice associé à un ChoiceForm"""

    cf=typeChoiceForm(*args,**options)
    if cf.is_valid():
        choice=cf.save(commit=False)
        choice.question=question
        choice.save()
        return choice
    return None

def createChoiceForm(request,choice,*args,**options):
    """Crée un formulaire pour un choix de MCQuestion en fonction du type de ce choix"""

    #print choice
    if isinstance(choice,TextualChoice):
        return TextualChoiceForm(instance=choice,*args,**options)
    elif isinstance(choice,ImageChoice):
        return ImageChoiceForm(instance=choice,*args,**options)
    elif isinstance(choice,FileChoice):
        return FileChoiceForm(instance=choice,*args,**options)

def updateQuestion(request,question,index,*args,**options):
    """Met à jour les informations contenues dans la session sur une question en fonction de son ancien état et de ce qu'a entré l'utilisateur"""

    qf=None
    if isinstance(question,TextualQuestion):
        qf=QuestionForm(request.POST,*args,**options)
    elif isinstance(question,MCQuestion):
        qf=MCQuestionForm(request.POST,**options)
    if qf and qf.is_valid():
        q=qf.save(commit=False)
        q_old=question
        if isinstance(question,MCQuestion):
            lesChoix=getChoix(request)
            choix=lesChoix.get(index)
            if choix != None:
                lesChoix[index]=choix
            request.session['lesChoix']=lesChoix
        return q
    return question

def updatePoll(request,ctx,poll):
    """Met à jour les informations contenues dans la session sur un sondage en fonction de son ancien état et de ce qu'a entré l'utilisateur"""
    
    lesQuestions = getQuestions(request)


    #on update les questions
    for i in range(0,len(lesQuestions)):
        lesQuestions[i]=updateQuestion(request,lesQuestions[i],i,prefix="question"+str(i))

    #on ajoute une question textuelle si il y en a une
    q=renderQuestion(request,poll,QuestionForm,request.POST,prefix="newQuestion")
    if q!=None:
        lesQuestions.append(q)
    #on ajoute une question à choix multiple si il y en a une
    q2=renderQuestion(request,poll,MCQuestionForm,request.POST,prefix="newMCQuestion")
    if q2!=None:
        lesQuestions.append(q2)
    #on sauvegarde les questions
    request.session['lesQuestions']=lesQuestions

    lesChoix = getChoix(request)
    #on ajoute les nouveaux choix
    for i in range(0,len(lesQuestions)):
        c=None
        if request.POST.get("question"+str(i)+"newchoice-text"):
            c=renderChoice(request,lesQuestions[i],i,TextualChoiceForm,request.POST,prefix="question"+str(i)+"newchoice")
        elif request.FILES.get("question"+str(i)+"newchoice-image"):
            c=renderChoice(request,lesQuestions[i],i,ImageChoiceForm,request.POST,request.FILES,prefix="question"+str(i)+"newchoice")
        elif request.FILES.get("question"+str(i)+"newchoice-file"):
            c=renderChoice(request,lesQuestions[i],i,FileChoiceForm,request.POST,request.FILES,prefix="question"+str(i)+"newchoice")
        if c!=None:
            choix = lesChoix.get(i)
            if choix :
                choix.append(c)
                lesChoix.update({i:choix})
                print choix
            else:
                lesChoix[i]=[c]

    request.session['lesChoix']=lesChoix            

    #Enfin on crée les formulaires pour chaque question        
    qfs=[]
    for i in range(0,len(lesQuestions)):
        qf=createQuestionForm(request,lesQuestions[i],i,prefix="question"+str(i))
        qfs.append(qf)
    ctx['questionforms']=qfs
    
    return
    
def saveQuestions(request,ctx,poll):
    """Sauvegarde l'état actuel des questions en BD"""

    lesQuestions=getQuestions(request)
    lesChoix=getChoix(request)

    error=False
    if lesQuestions!=[]:
        for i in range(0,len(lesQuestions)):
            choix=lesChoix.get(i)
            lesQuestions[i].poll=poll
            lesQuestions[i].save()
            if type(lesQuestions[i])==MCQuestion:
                if choix:
                    for j in choix:
                        j.question=lesQuestions[i]
                        #print j
                        j.save()
                else:
                    ctx['error']="une question à choix multiple doit avoir au moin un choix"
                    error=True
    else:
        ctx['error']="un sondage doit avoir au moin une question"
        error=True

    return not error
