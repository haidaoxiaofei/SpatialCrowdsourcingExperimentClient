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

total_worker_num = 10000
distribution = ['skew', 'gaus', 'real']
worker_per_instance = [150, 200, 250, 300, 400, 500]
worker_per_instance_worker_select = [300, 400, 500]
task_per_instance = [150, 200, 250, 300, 400, 500]
task_per_instance_worker_select = [300, 400, 500]
task_duration = [(1, 2), (2, 4), (4, 6), (6, 8)]
task_requirement = [(1, 3), (3, 5), (5, 7), (7, 9)]
task_confidence = [(0.65, 0.7), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
worker_capacity = [(1, 3), (3, 5), (5, 7), (7, 9)]
worker_reliability = [(0.65, 0.7), (0.7, 0.75), (0.75, 0.8), (0.8, 0.85), (0.85, 0.9)]
working_side_length = [(0.05, 0.1), (0.1, 0.15), (0.15, 0.2), (0.2, 0.25)]

default_instance_num = 20
default_worker_per_instance = 150
default_worker_per_instance_worker_select = 300
default_task_per_instance = 150
default_task_per_instance_worker_select = 300


def change_to(category):
    if category == 'worker_select':
        global output_order
        output_order = output_order_worker_select
        global worker_per_instance
        worker_per_instance = worker_per_instance_worker_select
        global task_per_instance
        task_per_instance = task_per_instance_worker_select
        global default_task_per_instance
        default_task_per_instance = default_task_per_instance_worker_select
        global default_worker_per_instance
        default_worker_per_instance = default_worker_per_instance_worker_select
