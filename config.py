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

# output_order_worker_select = ['geotrucrowdgreedy',
#                               'geotrucrowdhgr',
#                               'geocrowdgreedy',
#                               'geocrowdllep',
#                               'geocrowdnnp',
#                               'rdbscdivideandconquer',
#                               'rdbscsampling'
#                               ]

# total_worker_num = 100000
distribution = ['real', 'skew', 'gaus', 'unif']
worker_per_instance = [150, 200, 250, 300, 350]
task_per_instance = [150, 200, 250, 300, 350]
task_duration = [(1, 2), (2, 3), (3, 4), (4, 5)]
task_requirement = [(1, 3), (3, 5), (5, 7), (7, 9)]
task_confidence = [(0.65, 0.7), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
worker_capacity = [(2, 3), (3, 4), (4, 5), (5, 6)]
worker_reliability = [(0.65, 0.7), (0.7, 0.75), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
working_side_length = [(0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25)]

default_setting = {
    'instance_num': 50,
    'worker_per_instance': 150,
    'task_per_instance': 150,
    'task_duration': (1, 2),
    'task_requirement': (3, 5),
    'task_confidence': (0.75, 0.8),
    'worker_capacity': (2, 3),
    'worker_reliability': (0.75, 0.8),
    'working_side_length': (0.05, 0.1)
}

default_setting_worker_select = {
    'instance_num': 50,
    'worker_per_instance': 150,
    'task_per_instance': 150,
    'task_duration': (1, 2),
    'task_requirement': (3, 5),
    'task_confidence': (0.75, 0.8),
    'worker_capacity': (2, 3),
    'worker_reliability': (0.75, 0.8),
    'working_side_length': (0.05, 0.1)
}


def change_to(category):
    if category == 'worker_select':
        global output_order
        output_order = output_order_worker_select


def get_default():
    return default_setting.copy()
