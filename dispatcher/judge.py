import logging
import time
import traceback
from datetime import datetime

import requests
from shortuuid import ShortUUID
from django_redis import get_redis_connection

from dispatcher.models import Server
from dispatcher.semaphore import Semaphore

DEFAULT_USERNAME = 'qust_judge'
logger = logging.getLogger(__name__)

random_gen = ShortUUID()


def random_string(length=24):
    return random_gen.random(length)


def add_timestamp_to_reply(data):
    data.update(timestamp=datetime.now().timestamp())
    return data


def response_fail_with_timestamp():
    return add_timestamp_to_reply({'status': 'reject', 'message': traceback.format_exc()})


def send_judge_through_watch(code, checker, cases, table, problem_type, callback, timeout=900):
    redis_server = get_redis_connection("default")
    with Semaphore(redis_server, stale_client_timeout=60) as (sem, token):
        try:
            server = Server.objects.get(pk=int(token.decode().split(":")[0]))
            data = _prepare_judge_json_data(code, checker, problem_type, cases, table)
            judge_url = server.http_address + '/judge'
            watch_url = server.http_address + '/query'
            timeout_count = 0

            # 加上时间戳
            response = add_timestamp_to_reply(requests.post(judge_url, json=data, auth=(DEFAULT_USERNAME, server.token),
                                                            timeout=timeout).json())
            if response.get('status') != 'received':
                callback(response)
            while timeout_count < timeout:
                interval = 1
                time.sleep(interval)
                response = add_timestamp_to_reply(requests.get(watch_url, json={'fingerprint': data['fingerprint']},
                                                               auth=(DEFAULT_USERNAME, server.token),
                                                               timeout=timeout).json())
                if callback(response):
                    # report_instance.content = requests.get(watch_report, json={'fingerprint': data['fingerprint']},
                    #                                     auth=(DEFAULT_USERNAME, server.token), timeout=timeout).text
                    # report_instance.save()
                    break
                timeout_count += interval
                interval += interval
            if timeout_count >= timeout:
                raise RuntimeError("Send judge through socketio timed out.")
        except:
            msg = "Time: %s\n%s" % (datetime.now(), traceback.format_exc())
            logger.error(msg)
            # send_mail(subject="Submit fail notice", message=msg, from_email=None,
            #           recipient_list=settings.ADMIN_EMAIL_LIST,
            #           fail_silently=True)
            callback(add_timestamp_to_reply({"status": "reject", "message": msg}))


def _prepare_judge_json_data(code, checker, problem_type, cases, table):
    all_params = locals().copy()
    all_params['fingerprint'] = random_string()
    return all_params
