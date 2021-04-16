from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from django.db.models import Q

from submission.models import Submission


class GetAllSubmissionView(View):
    def post(self, request, *args, **kwargs):
        count = request.POST.get('cnt', 0)
        count = int(count)
        queryset = Submission.objects.filter(contest_id=None)[:count]
        return JsonResponse({'submission_list': queryset})


class GetOneProblemSubmissionView(View):
    def post(self, request, *args, **kwargs):
        count = request.POST.get('cnt', 0)
        count = int(count)
        user_id = self.kwargs['u_id']
        problem_id = self.kwargs['p_id']
        queryset = Submission.objects.filter(Q(author_id=user_id) & Q(problem_id=problem_id) & Q(contest_id=None))[:count]
        return JsonResponse({'submission_list': queryset})