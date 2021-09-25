import re
from datetime import datetime

from account.models import User
from dispatcher.judge import send_judge_through_watch, response_fail_with_timestamp
from submission.utils import SubmissionStatus
from submission.models import Submission, SubmissionReport
from .models import Problem
from django.core.cache import cache


def create_submission(problem, author: User, code, contest=None, status=SubmissionStatus.WAITING, ip='',
                      visible=True):
    if len(code) > 65536:
        raise ValueError("代码不得超过 65536 字节。")
    if author.submission_set.exists() and (
            datetime.now() - author.submission_set.first().create_time).total_seconds() < 10:
        raise ValueError("10 秒内只能提交一次。")
    # if contest:
    #     if contest.submission_set.filter(author_id=author.id, problem_id=problem.id, code__exact=code).exists():
    #         raise ValueError("你之前交过完全一样的代码。")
    problem.total_count += 1
    problem.save(update_fields=['total_count'])
    return Submission.objects.create(code=code, author=author, problem=problem, contest=contest,
                                     status=status, ip=ip, visible=visible)


def judge_submission_on_problem(submission, callback=None, **kwargs):

    problem = submission.problem
    code = submission.code
    case_list = []
    file_list = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", problem.cases)))
    for filename in file_list:
        with open(filename, 'r', encoding='utf-8') as f:
            cur = ''
            row = f.readlines()
            for line in row:
                line = line.rstrip("\n")
                cur += line
            case_list.append(cur)
    table = dict()
    table['table_to_delete'] = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", problem.table_to_delete)))
    table['table_to_do'] = list(filter(lambda x: x, re.split(r"[,;\[\]' ]", problem.table_to_do)))

    def on_receive_data(data):
        judge_time = datetime.fromtimestamp(data['timestamp'])
        if submission.judge_end_time and judge_time < submission.judge_end_time:
            return True
        if data.get('status') == 'received':
            if 'message' in data:
                submission.status_message = data['message']
            else:
                submission.status_message = ''
            submission.status = data.get('verdict', SubmissionStatus.JUDGING)

            details = data.get('detail', [])
            score = 0
            for detail in details:
                score += detail.get("point", 0)
            submission.status_percent = round(score)  # 总分

            submission.running_process = 'Running on test ' + str(len(details)) + '/' + str(problem.case_total)

            display_details = details + [{}] * max(0, len(case_list) - len(details))  # 已经处理好的和未处理的(空)
            submission.status_detail = display_details

            submission.judge_server = data.get('server', 0)
            # 暂时进行更新
            submission.judge_end_time = judge_time
            message = data.get('status_message')
            if message is not None:
                submission.status_message = message
            else:
                submission.status_message = " "
            submission.save(update_fields=['status_message', 'status_detail', 'status', 'judge_end_time',
                                           'status_percent', 'judge_server', 'running_process', 'status_message'])

            if SubmissionStatus.is_judged(data.get('verdict')):
                if submission.status_percent > 99.9:
                    problem.ac_count += 1
                    problem.save(update_fields=['ac_count'])
                return True
            return False
        else:
            submission.status = SubmissionStatus.SYSTEM_ERROR
            submission.status_message = data['message']
            submission.save(update_fields=['status', 'status_message'])
            return True

    try:
        return send_judge_through_watch(code, problem.checker, case_list, table,
                                        problem.problem_type, on_receive_data)
    except:
        on_receive_data(response_fail_with_timestamp())
