import requests
import platform

__author__ = 'Jian Xun'

INDEX_HOST = 'http://127.0.0.1:8081/'
if platform.system() == 'Darwin':
    INDEX_HOST = 'http://192.168.99.100:8081/'


def assign_batch(method):
    """
    Assign tasks to workers using one of the algorithms.
    Parameters
    ----------
    method : str
        The name of the method to use, should be on of ['geocrowdgreedy', 'geocrowdllep', 'geocrowdnnp',
         'geotrucrowdgreedy', 'geotrucrowdlo', 'rdbscdivideandconquer', 'rdbscsampling']
    current_time : int
        Current time instance, 0 means 1970-01-01 08:00:00
    """
    headers = {'content-type': 'application/json', 'accept': 'application/json'}
    matches = requests.post(
        url=INDEX_HOST + '/Index/actions/assignment/' + method + '/batch',
        headers=headers).json()
    return matches
