import platform

USERNAME = 'csp_team'
PASSWORD = 'csp2014hkust'
HOST = '127.0.0.1'
if platform.system() == 'Darwin':
    HOST = '192.168.99.100'
PORT = '3308'
DB = 'gmission_hkust'
