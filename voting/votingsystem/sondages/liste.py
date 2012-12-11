#encoding=utf8
from votingsystem.sondages.models import *
from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
from votingsystem.commun import context
from votingsystem import ldapINSA
from votingsystem.sondages.forms import *



def liste(request):
    """Affiche la liste des sondages en filtrant les sondages non visibles.
    Un utilisateur non connecté ne verra pas les sondages non anonymes.
    Un utilisateur ne verra pas les sondages auxquels il n'a pas le droit de répondre (NON IMPLEMENTE)"""

    ctx=context(request)
    if ctx["connected"]:
        ctx['polls']=Poll.objects.all()
    else:
        ctx['polls']=Poll.objects.filter(anonymous=True)
    return render_to_response("sondages/liste.html",ctx)

