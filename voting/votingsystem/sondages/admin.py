from votingsystem.sondages.models import *
from django.contrib import admin

mdls = [
    INSAUser,
    INSAGroup,
    Poll,
    UserAuthorization,
    GroupAuthorization,
    FullAuthorization,
    MCQuestion,
    TextualChoice,
    ImageChoice,
    FileChoice,
    TextualQuestion,
    MCQAnswer,
    TextualAnswer,
    Signature
]

for m in mdls:
    admin.site.register(m)

