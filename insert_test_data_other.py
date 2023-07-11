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

cur.execute("SELECT pg_get_serial_sequence('household', 'household_id')")
seq_household = cur.fetchone()[0]
cur.execute('DELETE FROM household')
cur.execute('ALTER SEQUENCE %s RESTART WITH 1' % seq_household)
sql_household = '''
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (1,1000,3,null,null,15);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (2,1000,3,null,null,132);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (3,2000,4,1,23,16);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (4,500,5,2,40,17);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values ('test005@test.com',3000,1,470,null,5);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (6,200,5,7,null,7);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (7,4040,1,null,5,18);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (8,2020,1,null,null,19);
INSERT INTO household
(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id)
values (9,2020,1,null,null,20);
'''
cur.execute(sql_household)
conn.commit()

cur.execute("SELECT pg_get_serial_sequence('air_handler', 'air_handler_id')")
seq_air_handler = cur.fetchone()[0]
cur.execute('DELETE FROM air_handler')
cur.execute('ALTER SEQUENCE %s RESTART WITH 1' % seq_air_handler)
sql_air_handler = '''
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (1,1,234,34,'testmodel1',1 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (2,1,234,34,'testmodel1',1 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id) values (2,2,234,34,'testmodel2',12);
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id) values (2,3,234,34,'testmodel31',3 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id) values (3,1,234,34,'testmodel1',2 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id) values (4,1,234,34,'testmodel1',2 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id) values (6,1,234,34,'testmodel1',21);
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (7,1,234,34,'001air',10 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (7,2,333,54,'air test',12);
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (8,1,333,54,'test Air002',23 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (8,2,333,54,'model sense',53 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (8,3,333,54,'model spring',54 );
insert into air_handler (household_id,sequential_order, fan_rpm, btu, model_name,manufacturer_id)  values (8,4,678,54,'model max',55 );
'''
cur.execute(sql_air_handler)
conn.commit()

cur.execute("SELECT pg_get_serial_sequence('water_heater', 'water_heater_id')")
seq_water_heater = cur.fetchone()[0]
cur.execute('DELETE FROM water_heater')
cur.execute('ALTER SEQUENCE %s RESTART WITH 1' % seq_water_heater)
sql_water_heater = '''
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (1,1,'Electric',4500,34.908,55,'testmodel1',1);
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (2,1,'Electric',4532,34.908,55,'testmodel1',1);
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (2,2,'Gas',4532,34.908,55,'testmodel2',2 );
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (2,3,'Fuel Oil',4532,34.908,55,'testmodel3',3 );
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id) values (3,1,'Heat Pump',4532,34.908,55,'testmodel1',2 );
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id) values (4,1,'Electric',4532,34.908,55,'testmodel1',2);
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (6,1,'Electric',4532,34.908,55,'testmodel1',2);
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (6,2,'Electric',4532,45,70,'testmodel2',4 );
insert into  water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (6,3,'Gas',50,45,70,'testmodel3',6 );
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (7,3,'Electric',4532,34.908,55,'testmodel1-max',55);
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (7,4,'Electric',4532,34.908,55,'airtestmodel2-max',55);
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (8,5,'Electric',4532,34.908,55,'testmodel1-spring',54);
insert into water_heater (household_id,sequential_order_wh, energy_source, btu,tank_size,temperature, model_name,manufacturer_id)  values (8,6,'Electric',4532,34.908,55,'testmodel1-sense',53);
'''
cur.execute(sql_water_heater)
conn.commit()

sql_house_publicutilities = '''
insert into house_publicutilities values (1,1);
insert into house_publicutilities values (2,1);
insert into house_publicutilities values (2,2);
insert into house_publicutilities values (2,3);
insert into house_publicutilities values (2,4);
insert into house_publicutilities values (5,1);
insert into house_publicutilities values (3,2);
insert into house_publicutilities values (4,3);
insert into house_publicutilities values (4,4);
'''
cur.execute(sql_house_publicutilities)
conn.commit()

sql_power_generation = '''
insert into power_generation values (1,1,'Wind-turbine',300,null);
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

sql_heating_cooling = '''
insert into air_conditioner values (1, 134);
insert into air_conditioner values (2, 2432);

insert into heater values (1, 'Gas');
insert into heater values (2, 'Electric');

insert into heat_pump values (3, 134.21,423.3434);
insert into heat_pump values (2, 2432.97867,93.97873);
'''
cur.execute(sql_heating_cooling)
conn.commit()

# close the cursor and connection
cur.close()
conn.close()

if __name__ == '__main__':
    app.run(debug=True)

