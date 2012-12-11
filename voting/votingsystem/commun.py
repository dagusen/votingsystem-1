#encoding=utf8

from votingsystem.siteCfg import urlReturnCAS


def context(request):
    """Préremplit le dictionnaire qui sera envoyé aux templates en fonctions des informations contenues dans la session"""

    username = request.session.get("username", None)
    ctx = {"urlReturnCAS": urlReturnCAS, "connected": False}
    ctx["tabs"] = {1:{"Liste":"/liste"}}
    if username:
        ctx["connected"] = True
        ctx["username"] = username
        ctx["fullname"] = request.session.get("fullname",None)
        ctx["tabs"][2] = {"Proposer un sondage":"/add"}
        #ctx["tabs"][3] = {"Recherche":"/recherche"}
    else:
        ctx["connected"] = False

    return ctx

