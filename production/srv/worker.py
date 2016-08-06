import psycopg2
import sys

# config: database and user
d = 'sweater'
u = d

con = None

try:
     
    con = psycopg2.connect(database = d, user = u)
    cur = con.cursor()
    cur.execute('SELECT endpoint FROM quotas WHERE quota > 0')
    #cur.execute('SELECT endpoint, payload FROM requests ORDER BY endpoint, priority DESC')
    ver = cur.fetchall()
    print(ver)
    

except:
	print('hui')
	sys.exit(1)
    
    
finally:
    
    if con:
        con.close()
