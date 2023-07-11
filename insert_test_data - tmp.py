# test data load
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
def get_pg_connection():
    return psycopg2.connect(database="aatpbpuf", user="aatpbpuf",
                        password="svSXNOMQ1gThOVclKsLMFYNJzbxfe3px", host="silly.db.elephantsql.com", port="5432", options="-c search_path=public") #change schema

conn = get_pg_connection()
# create a cursor
cur = conn.cursor()


sql_power_generation = '''
insert into power_generation values (1,5,'Wind-turbine',300,null);
insert into power_generation values (2,1,'Solar',3222,null);
insert into power_generation values (2,2,'Wind-turbine',200,null);
insert into power_generation values (3,1,'Solar',235,40);
insert into power_generation values (6,1,'Solar',10,null);
insert into power_generation values (7,1,'Solar',40,40);
insert into power_generation values (8,1,'Solar',400,404);
insert into power_generation values (8,2,'Wind-turbine',400,65);
'''

cur.execute(sql_power_generation)
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

if __name__ == '__main__':
    app.run(debug=True)

