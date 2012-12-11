#encoding=utf8
import ldap
from votingsystem.siteCfg import serveurLDAP


def rechercheLDAP(filter):
    """Fonction permettant une recherche paramétrable dans le LDAP de l'INSA de Rouen
 le retour est une liste de dictionnaires définis comme suit:
 dico={'typeDActeur':"ETUDIANT | Enseignant | Autre",'idLDAP':,'nom':,'prenom':,'eMail':,'fonction':,'telephone':,'departement':,'anneeEtude':,'adresse':}
 Pour accéder à un élément, il convient donc de faire:
 for dic in rechercheLDAP(filter):
    print "je m'appelle"+dic['nom']
 """
 
    parametresDeRecherche=("ou=people,dc=insa-rouen,dc=fr",ldap.SCOPE_SUBTREE,filter,None)
    timeout=0
    result_set = []

    l=ldap.open(serveurLDAP)
    resultat_id = l.search(*parametresDeRecherche)
    while 1:
        type, donnees = l.result(resultat_id, timeout)
        if (donnees == []):
            break
        else:
            if type == ldap.RES_SEARCH_ENTRY:
                result_set.append(donnees)  
    if len(result_set) == 0:
        return 
    for i in range(len(result_set)):
        for entree in result_set[i]:
            dico={}
            listeInstructions=["dico['nom']=entree[1]['sn'][0]",
                "dico['prenom']=entree[1]['givenName'][0]",
                "dico['idLDAP']=entree[1]['uid'][0]",
                "dico['eMail']=entree[1]['mail'][0]",
                "dico['fonction']=entree[1]['custom3'][0]",
                "dico['telephone']=entree[1]['telephoneNumber']",
                "dico['departement']=entree[1]['custom4']",
                "dico['anneeEtude']=entree[1]['insarouenAnneeEtude']",
                "dico['adresse']=entree[1]['postalAddress']"]
            for instruction in listeInstructions:
                try: exec(instruction)
                except: pass                    
            yield dico

def rechercheLDAPUid(uid):
    return iter(rechercheLDAP("uid="+uid)).next()

def rechercheLDAPDirecteur():
    return iter(rechercheLDAP("custom3=*Directeur*I.N.S.A*")).next()

def rechercheLDAPEmail(email):
    return iter(rechercheLDAP("mail="+email)).next()

def __rechercheLDAPDep__(dep):
    """Fonction permettant une recherche paramétrable dans le LDAP de l'INSA de Rouen
 le retour est une liste de dictionnaires définis comme suit:
 dico={'typeDActeur':"ETUDIANT | Enseignant | Autre",'idLDAP':,'nom':,'prenom','eMail':,'fonction':,'telephone':,'departement':,'anneeEtude':,'adresse':}
 Pour accéder à un élément, il convient donc de faire:
 for dic in rechercheLDAP(filter):
    print "je m'appelle"+dic['nom']
 """
 
    parametresDeRecherche=("ou=groups,dc=insa-rouen,dc=fr",ldap.SCOPE_SUBTREE,dep,None)
    timeout=0
    result_set = []

    l=ldap.open(serveurLDAP)
    resultat_id = l.search(*parametresDeRecherche)
    while 1:
        type, donnees = l.result(resultat_id, timeout)
        if (donnees == []):
            break
        else:
            if type == ldap.RES_SEARCH_ENTRY:
                result_set.append(donnees)  
    if len(result_set) == 0:
        return 
    for i in range(len(result_set)):
        for entree in result_set[i]:
            dico={}
            listeInstructions=["dico['departementLong']=entree[1]['description'][0].title()",
                "dico['departement']=entree[1]['cn'][0]"]
            for instruction in listeInstructions:
                try: 
                    exec(instruction)
                except: pass                    
            yield dico

def rechercheLDAPDep(dep):
    return iter(__rechercheLDAPDep__("cn="+dep)).next()

#for a in rechercheLDAP("givenName=Martin"):
#    print a

