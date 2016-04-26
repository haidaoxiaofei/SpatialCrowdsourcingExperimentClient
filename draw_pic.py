import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.pyplot import savefig
from os import listdir, path, mkdir

__author__ = 'Jian Xun'

LABEL = {
    'geocrowdgreedy': 'G-greedy',
    'geocrowdnnp': 'G-nnp',
    'geocrowdllep': 'G-llep',
    'geotrucrowdgreedy': 'GT-greedy',
    'geotrucrowdlo': 'GT-lo',
    'rdbscsampling': 'RDB-sam',
    'rdbscdivideandconquer': 'RDB-d&c'
}


def read_file(file_path):
    datas = []
    variable = file_path.split('/')[-1].split('_', 1)[1].split('.')[0]
    dist = file_path.split('/')[-1].split('_', 1)[0]
    with open(file_path, 'r') as infile:
        line = infile.readline().strip()
        while line != '':
            data = {
                'distribution': dist,
                'y_label': line,
                'x_label': variable,
                'x_series': infile.readline().split('\t')[1:],
                'lines': {}
            }
            line = infile.readline().strip()
            while '\t' in line:
                sp = line.split('\t')
                data['lines'][sp[0]] = sp[1:]
                line = infile.readline().strip()
            datas.append(data)
    return datas


def draw(data, suffix):
    line_width = 2
    markers = [
        {
            'marker': 's',
            'mew': 1,
            'markerSize': 14
        }, {
            'marker': '^',
            'mew': 1,
            'markerSize': 14
        }, {
            'marker': 'd',
            'mew': 1,
            'markerSize': 14
        }, {
            'marker': '*',
            'mew': 1,
            'markerSize': 16
        }, {
            'marker': '.',
            'mew': 1,
            'markerSize': 16
        }, {
            'marker': '+',
            'mew': 2,
            'markerSize': 14
        }, {
            'marker': 'x',
            'mew': 2,
            'markerSize': 14
        }]
    legend_text_size = 18

    plots = []
    marker = 0
    plt.figure(figsize=(9, 9))
    for label in data['lines']:
        p, = plt.plot(data['lines'][label], color='k', label=LABEL[label],
                      markerfacecolor='w', lineWidth=line_width, **markers[marker])
        plots.append(p)
        marker += 1
    plt.xticks(range(len(data['x_series'])), data['x_series'], size='medium')
    plt.xlabel(data['x_label'], fontsize=legend_text_size)
    plt.ylabel(data['y_label'], fontsize=legend_text_size)
    plt.legend(handles=plots)

    # save picture into 'pics' directory
    if not path.isdir('./pics'):
        mkdir('./pics')
    savefig('./pics/' + data['distribution'] + '_' + data['x_label'] + '_' + data['y_label'] + '.' + suffix)

if __name__ == '__main__':
    files = listdir('.')
    for file_name in files:
        if '.csv' in file_name:
            datas = read_file(file_name)
            for data in datas:
                if data['y_label'] != 'worker_num' and data['y_label'] != 'task_num':
                    draw(data, 'eps')
