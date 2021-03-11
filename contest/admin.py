from django.contrib import admin

from contest.models import Contest, ContestParticipant, ContestProblem

admin.site.register(Contest)
admin.site.register(ContestProblem)
admin.site.register(ContestParticipant)
