import psycopg2
import sys

def main():
    # config: database and user
    d = 'sweater'
    u = d

    con = None

    try:
         
        con = psycopg2.connect(database = d, user = u)
        cur = con.cursor()
        cur.execute('SELECT endpoint FROM quotas WHERE quota > 0')
        endpoints = cur.fetchall()
        #cur.execute('SELECT endpoint, payload FROM requests ORDER BY endpoint, priority DESC')
        print(ver)
        

    except:
        print('hui')
        sys.exit(1)
        
        
    finally:
        
        if con:
            con.close()

if __name__ == '__main__':
    main()
