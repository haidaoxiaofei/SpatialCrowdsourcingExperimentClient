import math
import scawg_util
import virtual_user
import datetime
from models import User, UserLastPosition, WorkerDetail, HitDetail, session, Message
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
        user_num = session.query(User).count()
        if user_num < 10000:
            for i in xrange(user_num + 1, 10001):
                u = User()
                u.email = 'jianxuntest_' + str(i) + '@test.com'
                u.username = 'jianxuntest_' + str(i)
                u.password = '$6$rounds=625784$CWH2/L8e8Oswa6Ce$D6dTtMNbX8QI0Ff37IJy/SA0wszAweLxoEeq502gYmb2Fo9eRlCuQQsfmKzNBRmPkulik0.YjttczfRRjsTlh/'
                u.credit = 0
                u.active = 1
                session.add(u)
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
total_worker_num = 10000
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


def run_exp(distribution, instance_num=20, worker_per_instance=25, task_per_instance=25, task_duration=(4, 8),
            task_requirement=(5, 7), task_confidence=(0.85, 0.9), worker_capacity=(5, 7),
            worker_reliability=(0.75, 0.8), working_side_length=(0.15, 0.2)):
    """
    run experiment and return the result
    Parameters
    ----------
    distribution : str
    instance_num : int
    worker_per_instance : int
    task_per_instance : int
    task_duration : tuple
    task_requirement : tuple
    task_confidence : tuple
    worker_capacity : tuple
    worker_reliability : tuple
    working_side_length : tuple

    Returns
    -------

    """
    DBUtil.initialize_db()
    DBUtil.clear_message()
    print 'db initialized'

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
        'rdbscdivideandconquer': Measure(),
        'rdbscsampling': Measure()
    }

    tasks, workers = scawg_util.generate_general_task_and_worker([
        distribution,
        'general',
        'instance=' + str(instance_num),
        'worker_num_per_instance=' + str(worker_per_instance),
        'task_num_per_instance=' + str(task_per_instance),
        'min_task_duration=' + str(task_duration[0]),
        'max_task_duration=' + str(task_duration[1]),
        'min_task_requirement=' + str(task_requirement[0]),
        'max_task_requirement=' + str(task_requirement[1]),
        'min_task_confidence=' + str(task_confidence[0]),
        'max_task_confidence=' + str(task_confidence[1]),
        'min_worker_capacity=' + str(worker_capacity[0]),
        'max_worker_capacity=' + str(worker_capacity[1]),
        'min_worker_reliability=' + str(worker_reliability[0]),
        'max_worker_reliability=' + str(worker_reliability[1]),
        'min_working_side_length=' + str(working_side_length[0]),
        'max_working_side_length=' + str(working_side_length[1])
    ])
    print 'data generated'

    # test on each method in result
    for method in result:
        print method
        for i in xrange(instance_num):
            worker_ins = workers[i]
            task_ins = tasks[i]
            set_worker_attributes_batch(worker_ins)
            set_task_attributes_batch(task_ins, boss)

            assign = encoder.encode(boss.assign(method, i))['result']
            # print isinstance(assign, list), isinstance(assign, dict), isinstance(assign, str)
            # print assign
            result[method].add_result(assign, task_ins, worker_ins)
            offline_workers_batch(worker_ins)
        for i in xrange(instance_num):
            invalid_tasks_batch(tasks[i])
        DBUtil.clear_message()

    return result


def run_on_variable(distribution, variable_name, values):
    measures = []
    for value in values:
        temp = eval('run_exp(\'' + distribution + '\', ' + variable_name + '=' + str(value) + ')')
        for method in temp:
            if method not in results:
                results[method] = {}
            results[method][str(value)] = temp[method].report()
            if len(measures) == 0:
                measures = [x for x in results[method][str(value)]]

    ofile = open(distribution + '_' + variable_name + '.csv', 'w')
    for measure in measures:
        ofile.write(measure + '\n')
        ofile.write('method')
        for value in values:
            ofile.write('\t' + str(value))
        ofile.write('\n')
        for method in results:
            ofile.write(method)
            for value in values:
                ofile.write('\t' + str(results[method][str(value)][measure]))
            ofile.write('\n')
    ofile.close()

if __name__ == '__main__':
    results = {}
    distribution = ['unif', 'gaus', 'skew', 'zipf', 'real']
    worker_per_instance = [25, 50, 125, 200, 250]
    task_per_instance = [25, 50, 125, 200, 250]
    task_duration = [(1, 2), (2, 4), (4, 8), (8, 12), (12, 16)]
    task_requirement = [(1, 3), (3, 5), (5, 7), (7, 9)]
    task_confidence = [(0.75, 0.8), (0.8, 0.85), (0.85, 0.9), (0.9, 0.95)]
    worker_capacity = [(1, 3), (3, 5), (5, 7), (7, 9)]
    worker_reliability = [(0.65, 0.7), (0.7, 0.75), (0.75, 0.8), (0.8, 0.85)]
    working_side_length = [(0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25)]
    measures = []
    for dist in distribution:
        if dist != 'real':
            run_on_variable(dist, 'worker_per_instance', worker_per_instance)
        run_on_variable(dist, 'task_per_instance', task_per_instance)
        run_on_variable(dist, 'task_duration', task_duration)
        run_on_variable(dist, 'task_requirement', task_requirement)
        run_on_variable(dist, 'task_confidence', task_confidence)
        run_on_variable(dist, 'worker_capacity', worker_capacity)
        run_on_variable(dist, 'worker_reliability', worker_reliability)
        run_on_variable(dist, 'working_side_length', working_side_length)
