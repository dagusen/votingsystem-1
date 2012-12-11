#encoding=utf8

from django.conf.urls.defaults import *


urlpatterns = patterns('',
    (r"^$", "votingsystem.sondages.views.index"),
    (r"^add$", "votingsystem.sondages.newPoll.newpoll"),
    (r"^liste$", "votingsystem.sondages.liste.liste"),
    (r"^poll/answer$", "votingsystem.sondages.votePoll.poll"),
    (r"^poll$", "votingsystem.sondages.viewPoll.poll"),
    (r"^recherche$", "votingsystem.sondages.recherche.recherche"),
    (r"^aide$", "votingsystem.sondages.views.aide"),
    (r"^connectfromcas$", "votingsystem.sondages.views.connectFromCAS"),
    (r"^disconnect$", "votingsystem.sondages.views.disconnect"),     
)

