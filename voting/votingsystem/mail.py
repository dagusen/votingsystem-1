#encoding=utf8

import smtplib
from votingsystem import siteCfg

emailSender=siteCfg.emailSender
loginSender=siteCfg.loginSender
mdpSender=siteCfg.mdpSender



def sendmail(mail,sujet,contenu):
    """Envoie un mail"""

    msg="Subject:"+sujet+"\nFrom:no-reply@insa-rouen.fr"+"\nTo:"+mail+"\n\n"+contenu+"\n"
    s=smtplib.SMTP_SSL("smtps-1.insa-rouen.fr",465)
    s.login(loginSender,mdpSender)#à enlever une fois en prod
    s.sendmail(emailSender,mail,msg.encode("UTF-8"))
    s.close()

