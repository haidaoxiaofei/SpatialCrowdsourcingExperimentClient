import subprocess
from os import listdir
from shutil import rmtree
from math import log

__author__ = 'Jian Xun'


__initial__ = False


class Worker:
    id = None
    longitude = None
    latitude = None
    capacity = 1
    activeness = 1
    min_lat = None
    min_lon = None
    max_lat = None
    max_lon = None
    reliability = 1
    velocity = None
    min_direction = None
    max_direction = None

    def from_general(self, params):
        """
        Args:
            params(list): a list of params parsed from SCAWG output file
        """
        self.id = params[0]
        self.latitude = params[1]
        self.longitude = params[2]
        self.capacity = params[3]
        self.activeness = params[4]
        # only use one parameter to generate a square region
        dis = params[5][0]
        self.max_lat = self.latitude + dis / 2
        self.max_lon = self.longitude + dis / 2
        self.min_lat = self.latitude - dis / 2
        self.min_lon = self.longitude - dis / 2
        self.reliability = params[6]


class Task:
    id = None
    longitude = None
    latitude = None
    arrival_time = None
    expire_time = None
    require_answer_count = 1
    assigned = 0
    entropy = 0.5
    confidence = 0.5

    def from_general(self, params):
        self.latitude = params[0]
        self.longitude = params[1]
        self.arrival_time = params[2]
        self.expire_time = params[3]
        self.require_answer_count = params[4]
        self.confidence = params[5]
        self.entropy = params[6]


def run_jar(params):
    print 'run params', str(params)
    subprocess.call(['java', '-jar', './GeocrowdDataGenerator.jar'] + params)


def parse_line(line):
    """
    parse the line to several parts, a part can be either a string or a list.
    Args:
        line(str):

    Returns: a list of strings or lists or both

    """
    result = []
    cur = 0
    while cur < len(line):
        if line[cur] == '[':
            last = line.index(']', cur)
            result.append(parse_line(line[cur + 1: last]))
            cur = last + 2
        else:
            try:
                last = line.index(';', cur)
                result.append(line[cur: last])
                cur = last + 1
            except ValueError:
                result.append(line[cur:])
                cur = len(line)
    for i in xrange(len(result)):
        if isinstance(result[i], str) and '.' in result[i]:
            result[i] = float(result[i])
        if isinstance(result[i], str) and '.' not in result[i]:
            result[i] = int(result[i])
    return result


def generate_instance(options=[]):
    run_jar(options)


def generate_general_task_and_worker(options=[]):
    clear_dir()
    run_jar(['general'] + options)
    dirct = 'uni'
    if 'real' in options:
        dirct = 'real'
    files = listdir('./dataset/' + dirct + '/task')
    tasks = []
    for name in files:
        temp = []
        file = open('./dataset/' + dirct + '/task/' + name, 'r')
        for line in file:
            task = Task()
            task.from_general(parse_line(line))
            temp.append(task)
        file.close()
        tasks.append(temp)
    files = listdir('./dataset/' + dirct + '/worker')
    workers = []
    for name in files:
        temp = []
        file = open('./dataset/' + dirct + '/worker/' + name, 'r')
        for line in file:
            worker = Worker()
            worker.from_general(parse_line(line))
            temp.append(worker)
        file.close()
        workers.append(temp)
    compute_entropy(tasks, workers)
    return tasks, workers


def compute_entropy(tasks, workers):
    for t_ins in xrange(len(tasks)):
        for task in tasks[t_ins]:
            # calculate entropy for this task
            total_num = 0.0
            distinct = {}
            for w_ins in xrange(t_ins + 1):
                for worker in workers[w_ins]:
                    dis_lon = worker.longitude - task.longitude if worker.longitude > task.longitude\
                        else task.longitude - worker.longitude
                    dis_lat = worker.latitude - task.latitude if worker.latitude > task.latitude\
                        else task.latitude - worker.latitude
                    if dis_lon <= 0.1 and dis_lat < 0.1:
                        w_id = str(worker.id)
                        if w_id in distinct:
                            distinct[w_id] += 1
                        else:
                            distinct[w_id] = 1
                        total_num += 1
            entropy = 0.0
            for w_id in distinct:
                pl = distinct[w_id] / total_num
                entropy -= pl * log(pl)
            task.entropy = entropy
            # print 'entropy is', entropy


def clear_dir():
    files = listdir('./dataset')
    if 'uni' in files:
        rmtree('./dataset/uni')
    files = listdir('./res')
    if 'dataset' in files:
        rmtree('./res/dataset')


if __name__ == '__main__':
    line = '598;74.16063640794154;45.10879073935417;19;0.7866654507704679;[74.16063640794154;45.10879073935417;0.0;0.0]0.3106544569620695'
    print parse_line(line)
    worker = Worker()
    worker.from_general(parse_line(line))
    print worker.min_lon, worker.min_lat, worker.max_lon, worker.max_lat
