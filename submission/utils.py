class SubmissionStatus(object):
    SUBMITTED = -3
    WAITING = -2
    JUDGING = -1
    ACCEPTED = 0
    SCORED = 1
    COMPILE_ERROR = 2
    SYSTEM_ERROR = 3
    WRONG_ANSWER = 4


    @staticmethod
    def is_judged(status):
        return status >= SubmissionStatus.ACCEPTED

    @staticmethod
    def is_penalty(status):
        return SubmissionStatus.is_judged(status) and status != SubmissionStatus.COMPILE_ERROR

    @staticmethod
    def is_accepted(status):
        return status == SubmissionStatus.ACCEPTED

    @staticmethod
    def is_scored(status):
        return status == SubmissionStatus.SCORED


STATUS_CHOICE = (
    (-3, 'Submitted'),
    (-2, 'In queue'),
    (-1, 'Running'),
    (0, 'Accepted'),
    (1, 'Partial score'),
    (2, 'Compilation error'),
    (3, 'System error'),
)