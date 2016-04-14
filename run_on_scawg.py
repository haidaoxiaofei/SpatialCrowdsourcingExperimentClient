import math

import scawg_util
import virtual_user
import datetime
from models import UserLastPosition, WorkerDetail, HitDetail, session, Message
import encoder

__author__ = 'Jian Xun'


class DBUtil:
    @classmethod
    def move_to(cls, uid, longitude, latitude):
        position = session.query(UserLastPosition).filter_by(user_id=uid).first()
        if position is not None:
            position.longitude = longitude
            position.latitude = latitude
        else:
            position = UserLastPosition()
            position.user_id = uid
            position.longitude = longitude
            position.latitude = latitude
            session.add(position)
        session.commit()

    @classmethod
    def set_worker_attributes(cls, uid, capacity=None, reliability=None, min_direction=None, max_direction=None,
                              velocity=None, min_lon=None, min_lat=None, max_lon=None, max_lat=None, is_online=None):
        user_detail = session.query(WorkerDetail).filter_by(id=uid).first()
        if user_detail is None:
            # print uid, 'not found'
            user_detail = WorkerDetail()
            user_detail.id = uid
            session.add(user_detail)
        if capacity is not None:
            user_detail.capacity = capacity
        if reliability is not None:
            user_detail.reliability = reliability
        if min_direction is not None:
            user_detail.min_direction = min_direction
        if max_direction is not None:
            user_detail.max_direction = max_direction
        if velocity is not None:
            user_detail.velocity = velocity
        if min_lon is not None:
            user_detail.region_min_lon = min_lon
        if min_lat is not None:
            user_detail.region_min_lat = min_lat
        if max_lon is not None:
            user_detail.region_max_lon = max_lon
        if max_lat is not None:
            user_detail.region_max_lat = max_lat
        if is_online is not None:
            user_detail.is_online = is_online
        session.commit()

    @classmethod
    def set_hit_attributes(cls, hid, entropy=None, confidence=None, is_valid=None):
        hit_detail = session.query(HitDetail).filter_by(id=hid).first()
        if hit_detail is None:
            hit_detail = HitDetail()
            hit_detail.id = hid
            session.add(hit_detail)
        if entropy is not None:
            hit_detail.entropy = entropy
        if confidence is not None:
            hit_detail.confidence = confidence
        if is_valid is not None:
            hit_detail.is_valid = is_valid
        session.commit()

    @classmethod
    def clear_message(cls):
        session.query(Message).delete()
        session.commit()

    @classmethod
    def initialize_db(cls):
        session.query(WorkerDetail).update(values={WorkerDetail.is_online: False})
        session.query(HitDetail).update(values={HitDetail.is_valid: False})
        session.commit()


class Measure:
    total_assignment = None
    running_time = None
    worker_dic = None
    task_dic = None
    total_moving_dis = 0
    assigned_workers = None

    def __init__(self):
        self.total_assignment = 0
        self.finished = 0
        self.average_moving_dis = 0
        self.average_workload = 0
        self.running_time = 0
        self.task_dic = {}
        self.worker_dic = {}
        self.assigned_workers = {}

    def add_result(self, assigns, tasks, workers):
        for task in tasks:
            self.task_dic[str(task.id)] = task
        for worker in workers:
            wid = get_id(worker.id)
            self.worker_dic[str(wid)] = worker
        for assign in assigns:
            if assign['taskId'] == -1:
                self.running_time += assign['workerId']
            else:
                self.total_assignment += 1
                wid = str(assign['workerId'])
                tid = str(assign['taskId'])
                # print assign['workerId'],  wid
                if wid not in self.assigned_workers:
                    self.assigned_workers[wid] = wid
                self.task_dic[tid].assigned += 1
                self.total_moving_dis += Measure.moving_dis(self.task_dic[tid], self.worker_dic[wid])

    @staticmethod
    def moving_dis(task, worker):
        return math.sqrt((task.longitude - worker.longitude)**2 + (task.latitude - worker.latitude)**2)

    def report(self):
        finished = 0
        for tid in self.task_dic:
            if self.task_dic[tid].assigned >= self.task_dic[tid].require_answer_count:
                finished += 1
        return {
            'task_num': len(self.task_dic),
            'worker_num': len(self.worker_dic),
            'assigned_worker_num': len(self.assigned_workers),
            'finished_task_num': finished,
            'average_moving_dis':
                0 if len(self.assigned_workers) == 0 else self.total_moving_dis / len(self.assigned_workers),
            'average_workload':
                0 if len(self.assigned_workers) == 0 else self.total_assignment / len(self.assigned_workers),
            'total_assignment': self.total_assignment,
            'running_time': self.running_time / 1000.0
        }


# worker id is from 1 to 1000
total_worker_num = 1000
# maps scawg id to gmission id (the same as index of vworkers)
worker_dic = {}
worker_used = 0


def get_id(scawg_id):
    global total_worker_num
    global worker_dic
    global worker_used
    if str(scawg_id) in worker_dic:
        return worker_dic[str(scawg_id)]
    elif worker_used < total_worker_num:
        worker_used += 1
        worker_dic[str(scawg_id)] = worker_used
        return worker_used
    else:
        print 'too many users!'
        return None


def set_worker_attributes_batch(workers):
    for worker in workers:
        real_id = get_id(worker.id)
        DBUtil.move_to(real_id, worker.longitude, worker.latitude)
        DBUtil.set_worker_attributes(uid=real_id, capacity=worker.capacity, reliability=1, min_lon=worker.min_lon,
                                     min_lat=worker.min_lat, max_lon=worker.max_lon, max_lat=worker.max_lat,
                                     velocity=worker.velocity, min_direction=worker.min_direction,
                                     max_direction=worker.max_direction, is_online=True)


def offline_workers_batch(workers):
    for worker in workers:
        real_id = get_id(worker.id)
        DBUtil.set_worker_attributes(uid=real_id, is_online=False)


def set_task_attributes_batch(tasks, boss):
    for task in tasks:
        # print 'task ' + str(i)
        location_id = boss.create_location(task.longitude, task.latitude)
        arrival_time = datetime.datetime.fromtimestamp(task.arrival_time).isoformat()
        expire_time = datetime.datetime.fromtimestamp(task.expire_time).isoformat()
        hit_id = boss.create_hit(location_id, required_answer_count=task.require_answer_count,
                                 arrival_time=arrival_time, expire_time=expire_time)
        # print hit_id
        DBUtil.set_hit_attributes(hid=hit_id, entropy=task.entropy, confidence=task.confidence, is_valid=True)
        task.id = hit_id


def invalid_tasks_batch(tasks):
    for task in tasks:
        DBUtil.set_hit_attributes(hid=task.id, is_valid=False)

def run_exp(instance_num):
    # initial boss
    boss = virtual_user.Boss('jianxuntest_boss', 'PaSSwoRd', 'jianxuntest_boss@test.com')

    # instance_num = 2

    # statistics including number of assigned(finished) tasks, average moving distance, average workload, running time
    result = {
        'geocrowdgreedy': Measure(),
        'geocrowdllep': Measure(),
        'geocrowdnnp': Measure(),
        'geotrucrowdgreedy': Measure(),
        'geotrucrowdlo': Measure(),
        #'rdbscdivideandconquer': Measure(),
        #'rdbscsampling': Measure()
    }

    DBUtil.initialize_db()
    DBUtil.clear_message()
    print 'db initialized'

    scawg_util.generate_instance(['instance=' + str(instance_num)])
    tasks, workers = scawg_util.generate_general_task_and_worker()
    print 'data generated'

    # test on each method in result
    for method in result:
        print method
        for i in xrange(instance_num):
            print 'instance ', i
            worker_ins = workers[i]
            task_ins = tasks[i]
            set_worker_attributes_batch(worker_ins)
            print 'workers done'
            set_task_attributes_batch(task_ins, boss)
            print 'tasks done'

            assign = encoder.encode(boss.assign(method, i))['result']
            # print isinstance(assign, list), isinstance(assign, dict), isinstance(assign, str)
            # print assign
            result[method].add_result(assign, task_ins, worker_ins)
            print 'offline workers'
            offline_workers_batch(worker_ins)
        print 'clean tasks'
        for i in xrange(instance_num):
            invalid_tasks_batch(tasks[i])
        DBUtil.clear_message()

    return result

if __name__ == '__main__':
    results = {}
    instances = [2, 5, 10, 20]#, 50, 100]
    measures = []
    for ins in instances:
        temp = run_exp(ins)
        for method in temp:
            if method not in results:
                results[method] = {}
            results[method][str(ins)] = temp[method].report()
            if len(measures) == 0:
                measures = [x for x in results[method][str(ins)]]

    ofile = open('report.csv', 'w')
    for measure in measures:
        ofile.write(measure + '\n')
        ofile.write('method')
        for ins in instances:
            ofile.write(',' + str(ins * 200))
        ofile.write('\n')
        for method in results:
            ofile.write(method)
            for ins in instances:
                ofile.write(',' + str(results[method][str(ins)][measure]))
            ofile.write('\n')
    ofile.close()
