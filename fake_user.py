__author__ = 'JIAN Xun'

import sys
import MySQLdb
import generate

HOST='192.168.99.100'

PORT=3308
USER='csp_team'
PASSWORD='csp2014hkust'
DB='gmission_hkust'

db = MySQLdb.connect(host=HOST, port=PORT, user=USER, passwd=PASSWORD, db=DB)
c = db.cursor()
c.execute('select max(id) from user')
uid = int(c.fetchone()[0])
c.execute('select username, email, password, iat from user where id=%s', (uid,))
uinfo = c.fetchone()
password = uinfo[2]
iat = int(uinfo[3])

if (len(sys.argv)) > 1:
    number = int(sys.argv[1])
else:
    number = 1

for i in xrange(number):
    email = 'jianxuntest_%s@%s.com' % (generate.randstr(), generate.randstr())
    username = 'jianxuntest_' + generate.randstr()
    c.execute('insert into user(username, email, password, credit, active, iat) values (%s, %s, %s, %s, %s, %s)',
              (username + '_' + str(i), '_' + email, password, 0, 0, iat + 1,))
    new_id = c.lastrowid
    print new_id
    pos = generate.randpos()
    c.execute('insert into user_last_position(longitude, latitude, z, user_id) values (%s, %s, %s, %s)',
              (pos['longitude'], pos['latitude'], 0, new_id))
    db.commit()
