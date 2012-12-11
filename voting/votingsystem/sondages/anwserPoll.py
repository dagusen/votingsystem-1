#encoding=utf8

from votingsystem.sondages.models import *
from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
from votingsystem.commun import context
from votingsystem import ldapINSA
from votingsystem.sondages.forms import *



def answerPoll(request):
    
    return redirect("/")




