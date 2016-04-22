import scawg_util
import matplotlib.pyplot as plt


def check_task_position(tasks):
    x = []
    y = []
    for task in tasks:
        x.append(task.longitude)
        y.append(task.latitude)
    plt.plot(x, y, 'ro')
    plt.title('location distribution')
    # plt.axis([0, 6, 0, 20])
    plt.show()


def check_task_confidence(tasks):
    x = []
    for task in tasks:
        x.append(task.confidence)
    plt.hist(x, 50, normed=1, facecolor='b', alpha=0.75)
    plt.title('confidence distribution')
    plt.show()

if __name__ == '__main__':
    tasks, workers = scawg_util.generate_general_task_and_worker(['zipf', 'general', 'instance=2', 'task_num_per_instance=1000'])
    check_task_confidence(tasks[0])
    check_task_position(tasks[0])
