#encoding=utf8

from votingsystem.sondages.models import *
from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
from votingsystem.commun import context
from votingsystem import ldapINSA
from votingsystem.sondages.forms import *
from datetime import datetime

def poll(request):
    """Affiche un sondage"""

    ctx=context(request)
    id=int(request.GET.get("poll"))
    #print request.POST
    if id:
        try:
            poll=Poll.objects.get(id=id)
        except:
            return redirect("/liste")
        if not poll.alreadyAnwsered(request.session.get('username')) and not poll.anonymous:
            return redirect('/poll/answer?poll='+str(id))

        ctx['poll'] = poll
        ctx['lesQuestions'] = poll.question_set.all()
        
        #si on a des arguments en POST c'est qu'on a une réponse, sinon on créer les formulaires.
        return render_to_response("sondages/poll.html",ctx)
    return redirect("/liste")

