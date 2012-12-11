#encoding=utf8

from django.shortcuts import render_to_response,redirect
from votingsystem.siteCfg import urlReturnCAS,urlSite
import urllib2
import xml.dom.minidom as dom


from votingsystem.commun import context
from votingsystem import ldapINSA,mail
#from votingsystem.sondages import newPoll


def index(request):
    """Affiche la page d'index"""

    ctx = context(request)
    #sendmail("mathieu.chataigner@insa-rouen.fr","test2","prout")
    return render_to_response("sondages/index.html", ctx)

def aide(request):
    """Affiche la page d'aide"""

    return render_to_response("sondages/aide.html",context(request))

def connectFromCAS(request):
    """Appelée en retour du CAS de l'INSA. Ouvre une session"""

    ticket = request.GET["ticket"]
    resp = urllib2.urlopen("https://cas.insa-rouen.fr/cas/serviceValidate?service="+urlReturnCAS+"&ticket="+ticket)
    xmlDoc = dom.parse(resp)
    auth = xmlDoc.getElementsByTagName("cas:authenticationSuccess")
    if len(auth) > 0:
        username = auth[0].getElementsByTagName("cas:user")[0].firstChild.data
        try:
            user = iter(ldapINSA.rechercheLDAP("uid="+username)).next()
        except StopIteration:
            pass
        request.session["username"] = username  # C'est tout !
        fullname=user['prenom']+" "+user['nom']
        request.session["fullname"] = fullname
        #user = ActeurINSA(nom="",prenom="",email="",fonction="",idLDAP="")
    return redirect("/")#index(request)

def disconnect(request):
    """Ferme la session et déconnecte du CAS"""
    request.session.flush()
    return redirect("/")#redirect("https://cas.insa-rouen.fr/cas/logout?service="+urlSite)#index(request)


