import math
import scawg_util
import virtual_user
from models import *
import encoder
import sys
import logging
import config

__author__ = 'Jian Xun'

logger = logging.getLogger('default')
logger.setLevel(logging.DEBUG)
fh = logging.FileHandler('default.log')
formatter = logging.Formatter('%(asctime)s - %(module)s(%(filename)s:%(lineno)d) - %(levelname)s - %(message)s')
fh.setLevel(logging.DEBUG)
fh.setFormatter(formatter)
logger.addHandler(fh)


class DBUtil:
    def __init__(self):
        pass

    @classmethod
    def move_to(cls, uid, longitude, latitude, commit=True):
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
        if commit:
            session.commit()

    @classmethod
    def set_worker_attributes(cls, uid, capacity=None, reliability=None, min_direction=None, max_direction=None,
                              velocity=None, min_lon=None, min_lat=None, max_lon=None, max_lat=None, is_online=None,
                              commit=True):
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
        if commit:
            session.commit()

    @classmethod
    def create_hit(cls, longitude, latitude, arrival_time, expire_time, require_answer_count, entropy, confidence,
                   is_valid=None, commit=True):
        # add coordinate
        coord = Coordinate()
        coord.longitude = longitude
        coord.latitude = latitude
        coord.altitude = 0
        session.add(coord)
        session.flush()
        session.refresh(coord)
        # add location
        location = Location()
        location.coordinate_id = coord.id
        location.name = 'jianxuntest_' + str(coord.id)
        session.add(location)
        session.flush()
        session.refresh(location)
        # add hit
        hit = HIT()
        hit.type = 'text'
        hit.title = 'jianxuntest_' + str(location.id)
        hit.description = 'desc desc'
        hit.campaign_id = 1
        hit.credit = 10
        hit.status = 'open'
        hit.required_answer_count = require_answer_count
        hit.min_selection_count = 1
        hit.max_selection_count = 1
        hit.begin_time = arrival_time
        hit.end_time = expire_time
        hit.location_id = location.id
        hit.requester_id = 10001
        session.add(hit)
        session.flush()
        session.refresh(hit)
        # set attributes
        DBUtil.set_hit_attributes(hit.id, entropy, confidence, is_valid, commit)
        return hit.id

    @classmethod
    def set_hit_attributes(cls, hid, entropy=None, confidence=None, is_valid=None, commit=True):
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
        if commit:
            session.commit()

    @classmethod
    def clear_message(cls):
        session.query(Message).delete()
        session.commit()

    @classmethod
    def clear_hits(cls):
        cls.clear_message()
        session.query(HitDetail).delete()
        session.query(HIT).delete()
        session.commit()

    @classmethod
    def initialize_db(cls):
        user_num = session.query(User).count()
        if user_num < config.total_worker_num:
            for i in xrange(user_num + 1, config.total_worker_num + 1):
                u = User()
                u.email = 'jianxuntest_' + str(i) + '@test.com'
                u.username = 'jianxuntest_' + str(i)
                u.password = '$6$rounds=625784$CWH2/L8e8Oswa6Ce$D6dTtMNbX8QI0Ff37IJy/SA0wszAweLxoEeq502gYmb2Fo9' \
                             'eRlCuQQsfmKzNBRmPkulik0.YjttczfRRjsTlh/'
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
    total_moving_dis = None
    assigned_workers = None
    task_worker = None
    finished = None
    average_workload = None

    def __init__(self):
        self.total_assignment = 0
        self.finished = 0
        self.total_moving_dis = 0
        self.average_workload = 0
        self.running_time = 0
        self.task_dic = {}
        self.worker_dic = {}
        self.assigned_workers = {}
        self.task_worker = {}

    def add_result(self, assigns, tasks, workers):
        for task in tasks:
            tid = str(task.id)
            self.task_dic[tid] = task
            self.task_worker[tid] = []
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
                if wid in self.task_worker[tid]:
                    logger.error('!!!!!!! duplicate assignment !!!!!!!')
                self.task_worker[tid].append(wid)
                self.task_dic[tid].assigned += 1
                self.total_moving_dis += Measure.moving_dis(self.task_dic[tid], self.worker_dic[wid])

    @staticmethod
    def ars(workers, level, confidence, neg_count, task):
        if level == len(workers) or level - neg_count == task.require_answer_count:
            return confidence
        if level > 10 or confidence < 0.0000001:
            return confidence
        # assume this worker gives a positive answer
        answer = Measure.ars(workers, level + 1, confidence * workers[level].reliability, neg_count, task)
        if answer > task.confidence:
            return 1
        # assume this worker gives a negative answer
        if neg_count < (len(workers) - 1) / 2:
            answer += Measure.ars(workers, level + 1, confidence * (1 - workers[level].reliability), neg_count + 1,
                                  task)
        return answer

    @staticmethod
    def satisfy_conf(task, workers):
        # maximum possible worker num
        if len(workers) >= 17:
            return True
        return Measure.ars(workers, 0, 1, 0, task) >= task.confidence

    @staticmethod
    def moving_dis(task, worker):
        return math.sqrt((task.longitude - worker.longitude) ** 2 + (task.latitude - worker.latitude) ** 2)

    def report(self):
        self.finished = 0
        finished_conf = 0
        for tid in self.task_dic:
            if len(self.task_worker[tid]) >= self.task_dic[tid].require_answer_count:
                self.finished += 1
                if Measure.satisfy_conf(self.task_dic[tid], [self.worker_dic[wid] for wid in self.task_worker[tid]]):
                    finished_conf += 1
        return {
            'task_num': len(self.task_dic),
            'worker_num': len(self.worker_dic),
            'assigned_worker_num': len(self.assigned_workers),
            'finished_task_num': self.finished,
            'finished_task_num_conf': finished_conf,
            'average_moving_dis':
                0 if len(self.assigned_workers) == 0 else self.total_moving_dis / len(self.assigned_workers),
            'average_workload':
                0 if len(self.assigned_workers) == 0 else (self.total_assignment + 0.0) / len(self.assigned_workers),
            'total_assignment': self.total_assignment,
            'running_time': self.running_time / 1000.0
        }


# maps scawg id to gmission id (the same as index of vworkers)
worker_dic = {}
worker_used = 0


def get_id(scawg_id):
    global worker_dic
    global worker_used
    if str(scawg_id) in worker_dic:
        return worker_dic[str(scawg_id)]
    elif worker_used < config.total_worker_num:
        worker_used += 1
        worker_dic[str(scawg_id)] = worker_used
        return worker_used
    else:
        logger.error('too many users!')
        return None


def set_worker_attributes_batch(workers):
    for worker in workers:
        real_id = get_id(worker.id)
        DBUtil.move_to(real_id, worker.longitude, worker.latitude, commit=False)
        DBUtil.set_worker_attributes(uid=real_id, capacity=worker.capacity, reliability=worker.reliability,
                                     min_lon=worker.min_lon, min_lat=worker.min_lat, max_lon=worker.max_lon,
                                     max_lat=worker.max_lat, velocity=worker.velocity,
                                     min_direction=worker.min_direction, max_direction=worker.max_direction,
                                     is_online=True, commit=False)
    session.commit()


def offline_workers_batch(workers):
    for worker in workers:
        real_id = get_id(worker.id)
        DBUtil.set_worker_attributes(uid=real_id, is_online=False, commit=False)
    session.commit()


def set_task_attributes_batch(tasks):
    for task in tasks:
        # print 'task ' + str(i)
        # location_id = boss.create_location(task.longitude, task.latitude)
        arrival_time = datetime.datetime.fromtimestamp(task.arrival_time).isoformat()
        expire_time = datetime.datetime.fromtimestamp(task.expire_time).isoformat()
        # hit_id = boss.create_hit(location_id, required_answer_count=task.require_answer_count,
        #                          arrival_time=arrival_time, expire_time=expire_time)
        # DBUtil.set_hit_attributes(hid=hit_id, entropy=task.entropy, confidence=task.confidence, is_valid=True)
        hit_id = DBUtil.create_hit(task.longitude, task.latitude, arrival_time, expire_time, task.require_answer_count,
                                   task.entropy, task.confidence, is_valid=True, commit=False)
        task.id = hit_id


def invalid_tasks_batch(tasks):
    for task in tasks:
        DBUtil.set_hit_attributes(hid=task.id, is_valid=False)


def run_exp(distribution, instance_num=None, worker_per_instance=None, task_per_instance=None,
            task_duration=(1, 2), task_requirement=(1, 3), task_confidence=(0.75, 0.8), worker_capacity=(1, 3),
            worker_reliability=(0.75, 0.8), working_side_length=(0.05, 0.1)):
    """
    run experiment and return the result
    :type distribution: str
    :type instance_num: int
    :type worker_per_instance: int
    :type task_per_instance: int
    :type task_duration: tuple
    :type task_requirement: tuple
    :type task_confidence: tuple
    :type worker_capacity: tuple
    :type worker_reliability: tuple
    :type working_side_length: tuple
    :return:
    """

    DBUtil.initialize_db()
    DBUtil.clear_hits()
    logger.info('db initialized')

    # initial boss
    boss = virtual_user.Boss('jianxuntest_boss', 'PaSSwoRd', 'jianxuntest_boss@test.com')

    # instance_num = 2

    # statistics including number of assigned(finished) tasks, average moving distance, average workload, running time
    result = {}
    for method in config.output_order:
        result[method] = Measure()

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
    logger.info('data generated')

    # test on each method in result
    for method in result:
        logger.info('starting run ' + method)
        for i in xrange(instance_num):
            worker_ins = workers[i]
            task_ins = tasks[i]
            logger.info('set worker attributes')
            set_worker_attributes_batch(worker_ins)
            logger.info('set task attributes')
            set_task_attributes_batch(task_ins)
            logger.info('assign ' + method)
            assign = encoder.encode(boss.assign(method, i))['result']
            # print isinstance(assign, list), isinstance(assign, dict), isinstance(assign, str)
            logger.info('add result of ' + method)
            result[method].add_result(assign, task_ins, worker_ins)
            logger.info('finished adding result, starting offline workers')
            offline_workers_batch(worker_ins)
            logger.info('finished offline workers')
        logger.info(method + ' done, clearing')
        for i in xrange(instance_num):
            invalid_tasks_batch(tasks[i])
        DBUtil.clear_hits()

    return result


def run_on_variable(distribution, variable_name, values):
    measures = []
    results = {}
    for value in values:
        kwargs = {
            'instance_num': config.default_instance_num,
            'worker_per_instance': config.default_worker_per_instance,
            'task_per_instance': config.default_task_per_instance
        }
        kwargs[variable_name] = value
        temp = run_exp(distribution, **kwargs)
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
        for method in config.output_order:
            ofile.write(method)
            for value in values:
                ofile.write('\t' + str(results[method][str(value)][measure]))
            ofile.write('\n')
    ofile.close()


def test():
    config.change_to('worker_select')
    # print config.output_order
    # print config.default_instance_num
    # print config.default_task_per_instance
    # print config.default_worker_per_instance
    # worker should be at least 2 times more than task
    run_on_variable('skew', 'worker_per_instance', config.worker_per_instance)
    run_on_variable('skew', 'task_per_instance', config.task_per_instance)


if __name__ == '__main__':
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg == 'test':
            logger.info('test mode')
            test()
            exit()
        elif arg == 'worker_select':
            logger.info('worker-selected mode')
            config.change_to('worker_select')
        elif arg == 'server_assign':
            logger.info('server-assigned mode')
        else:
            exit()

    for dist in config.distribution:
        if dist != 'real':
            run_on_variable(dist, 'worker_per_instance', config.worker_per_instance)
            run_on_variable(dist, 'task_per_instance', config.task_per_instance)
        run_on_variable(dist, 'task_duration', config.task_duration)
        run_on_variable(dist, 'task_requirement', config.task_requirement)
        run_on_variable(dist, 'task_confidence', config.task_confidence)
        run_on_variable(dist, 'worker_capacity', config.worker_capacity)
        run_on_variable(dist, 'worker_reliability', config.worker_reliability)
        run_on_variable(dist, 'working_side_length', config.working_side_length)
