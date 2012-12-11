#encoding=utf8

from votingsystem.sondages.models import *
from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
from votingsystem.commun import context
from votingsystem import ldapINSA
from votingsystem.sondages.forms import *
from datetime import datetime

def poll(request):
    """Appelée lorsque l'on souhaite répondre à un sondage"""

    ctx=context(request)
    id=int(request.GET.get("poll"))
    #print request.POST
    if id:

        try:
            poll=Poll.objects.get(id=id)
        except:
            return redirect("/liste")
        
        if not poll.anonymous and not ctx["connected"]:
            return redirect("/liste")



        ctx['poll']=poll


        lesQuestions=poll.question_set.all()
        ctx['lesQuestions']=[]

        #si on a des arguments en POST c'est que l'on a une réponse, sinon on crée les formulaires.

        #print type(request.session.get('username'))
        #print poll.alreadyAnwsered(request.session.get('username'))
        
        if poll.alreadyAnwsered(request.session.get('username')) or poll.endDate < datetime.today():
            return redirect('/poll?poll='+str(id))

        if request.method=="POST":
            lesReponses = []
            valid=True
            for i in range(0,len(lesQuestions)):
                q=lesQuestions[i]
                if hasattr(q,"textualquestion"):
                    af = TextualAnswerForm(request.POST,prefix="Anwser"+str(i))
                    q=q.textualquestion
                    
                elif hasattr(q,"mcquestion"):
                    af = MCQAnswerForm(q.mcquestion,request.POST,prefix="Answer"+str(i))
                    q=q.mcquestion
                valid = valid and af.is_valid()
                ctx['lesQuestions'].append((q,af))
                if valid:
                    answer=checkQuestion(af,q,poll,request)
                    lesReponses.append(answer)
            if valid:
                sig = None
                if(not poll.anonymous):
                    sig = Signature()
                    userldap=ldapINSA.rechercheLDAPUid(request.session.get('username'))
                    user,created = INSAUser.objects.get_or_create(uid=request.session.get('username'),defaults={"fullname":userldap.get('nom')+' '+userldap.get('prenom')})
                    sig.user=user
                    sig.poll=poll
                    sig.save()

                for i in range(0,len(lesReponses)):
                    saveQuestion(lesReponses[i],poll,request,sig)
                poll.answered()
                poll.save()
                return redirect('/liste')
           #on précise que le sondage a été répondu.
        else:
            for i in range(0,len(lesQuestions)):
                q=lesQuestions[i]
                if hasattr(q,"textualquestion"):
                    ctx['lesQuestions'].append((q.textualquestion,TextualAnswerForm(prefix="Anwser"+str(i))))
                elif hasattr(q,"mcquestion"):
                    mcqaf=MCQAnswerForm(q.mcquestion,prefix="Answer"+str(i))
                    #mcqaf.setChoice(q.mcquestion)
                    ctx['lesQuestions'].append((q.mcquestion,mcqaf))
        return render_to_response("sondages/votePoll.html",ctx)
    else:
        return redirect("/liste")



def checkQuestion(form,question,poll,request):
    answer = form.save(commit=False)
    ip = request.META.get('REMOTE_ADDR')
    answer.ipAddress=ip
    answer.date=datetime.today()
    answer.question=question
    return answer

def saveQuestion(answer,poll,request,signature):
    answer.save()
    if signature:
        signature.answer.add(answer)
        signature.save()
    return answer
