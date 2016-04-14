import scawg_util
import virtual_user
import datetime
import models

import run_on_scawg

__author__ = 'Jian Xun'


def prepare_workers():
    # prepare the workers
    total_worker_num = 1000
    vworkers = []
    # maps scawg id to gmission id (the same as index of vworkers)
    worker_dic = {}
    # print initial workers
    for i in xrange(total_worker_num):
        print 'worker ' + str(i)
        username = 'jianxuntest_' + str(i)
        password = 'PaSSwoRd'
        email = 'jianxuntest_%s@%s.com' % (i, 'test')
        vworker = virtual_user.Worker(username, password, email)


def test_modify_hit_detail():
    boss = virtual_user.Boss('jianxuntest_boss', 'PaSSwoRd', 'jianxuntest_boss@test.com')
    hit_id = 369
    boss.set_hit_attributes(hit_id=hit_id)

if __name__ == '__main__':
    run_on_scawg.DBUtil.clear_message()
