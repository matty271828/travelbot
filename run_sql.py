import os
import psycopg2
import psycopg2.extras as ext

# Set environment variable
# Set manually as 'dev' to run from local database
ENV = 'dev'
# Run local database
if ENV == 'dev':
    DATABASE_URL = os.environ.get('travelbot_local_database_url')
# Run production database
else:
    DATABASE_URL = os.environ.get('DATABASE_URL')

# Function to run SQL queries 
def run_sql(sql, values = None):
    conn = None
    results = []
    try:
        if ENV == 'dev':
            conn = psycopg2.connect(DATABASE_URL)
        else:
            conn = psycopg2.connect(DATABASE_URL, sslmode='require')

        cur = conn.cursor(cursor_factory=ext.DictCursor)
        cur.execute(sql, values)
        conn.commit()

        # Check for results present
        if cur.description != None:
            results = cur.fetchall()

        cur.close()

    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        return 'error occurred'
        
    finally:
        if conn is not None:
            conn.close()
    
    return results