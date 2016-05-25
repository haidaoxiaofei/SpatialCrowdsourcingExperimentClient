__author__ = 'Jian Xun'

output_order = ['geotrucrowdgreedy',
                'geotrucrowdhgr',
                'geocrowdgreedy',
                'geocrowdllep',
                'geocrowdnnp',
                'rdbscdivideandconquer',
                'rdbscsampling'
                ]

output_order_worker_select = ['workerselectprogressive',
                              'workerselectdp',
                              'workerselectbb',
                              'workerselectha'
                              ]

output_order_worker_select = ['geotrucrowdgreedy',
                              'geotrucrowdhgr',
                              'geocrowdgreedy',
                              'geocrowdllep',
                              'geocrowdnnp',
                              'rdbscdivideandconquer',
                              'rdbscsampling'
                              ]

# total_worker_num = 100000
distribution = ['skew', 'gaus']  # , 'real']
worker_per_instance = [150, 200, 250, 300, 400, 500]
task_per_instance = [150, 200, 250, 300, 400, 500]
task_duration = [(1, 2), (2, 4), (4, 6), (6, 8)]
task_requirement = [(1, 3), (3, 5), (5, 7), (7, 9)]
task_confidence = [(0.65, 0.7), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
worker_capacity = [(1, 3), (3, 5), (5, 7), (7, 9)]
worker_reliability = [(0.65, 0.7), (0.7, 0.75), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
working_side_length = [(0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25)]

default_setting = {
    'instance_num': 20,
    'worker_per_instance': 150,
    'task_per_instance': 150,
    'task_duration': (1, 2),
    'task_requirement': (1, 3),
    'task_confidence': (0.75, 0.8),
    'worker_capacity': (1, 3),
    'worker_reliability': (0.75, 0.8),
    'working_side_length': (0.05, 0.1)
}

worker_per_instance_worker_select = [150, 200, 250, 300, 350]
task_per_instance_worker_select = [150, 200, 250, 300, 350]
task_duration_worker_select = [(1, 2), (2, 3), (3, 4), (4, 5)]
worker_capacity_worker_select = [(2, 3), (3, 4), (4, 5), (5, 6)]

default_setting_worker_select = {
    'instance_num': 100,
    'worker_per_instance': 150,
    'task_per_instance': 150,
    'task_duration': (1, 2),
    'task_requirement': (3, 5),
    'task_confidence': (0.75, 0.8),
    'worker_capacity': (2, 3),
    'worker_reliability': (0.75, 0.8),
    'working_side_length': (0.1, 0.15)
}


def change_to(category):
    if category == 'worker_select':
        global output_order
        output_order = output_order_worker_select
        global default_setting
        default_setting = default_setting_worker_select
        global worker_per_instance
        worker_per_instance = worker_per_instance_worker_select
        global task_per_instance
        task_per_instance = task_per_instance_worker_select
        global task_duration
        task_duration = task_duration_worker_select
        global worker_capacity
        worker_capacity = worker_capacity_worker_select


def get_default():
    return default_setting.copy()
