# Import Flask Library
import datetime
import hashlib
import os

from flask import Flask, render_template, request, redirect, url_for, flash, session
import psycopg2

app = Flask(__name__)
app.secret_key = 'your secret key'

def get_pg_connection():
     return psycopg2.connect(database="test", user="root",
                         password="toot", host="silly.db.elephantsql.com", port="5432", options="-c search_path=public")


@app.route('/')
def main():
    # welcome page
    return render_template('welcome.html')

@app.route('/complete')
def wrap_up():
    # complete page
    return render_template('complete.html')

@app.route('/household')
def household_info_view():
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()

    data = {}

    cur.execute('''SELECT * FROM household_type''')
    data['household_types'] = cur.fetchall()

    cur.execute('''SELECT * FROM public_utilities''')
    data['public_utilities'] = cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()

    return render_template('household.html', data=data)

@app.route('/add_appliance')
def add_appliance():
    conn = get_pg_connection()
    cursor=conn.cursor()
    manufacturer_query = 'SELECT manufacturer_id, manufacturer_name FROM manufacturer'
    cursor.execute(manufacturer_query)
    manufacturers = cursor.fetchall()
    types = ['Air handler','Water heater']
    energySourceAhs = ['Electric','Gas','Thermosolar']
    energySourceWhs = ['Electric', 'Gas', 'Fuel Oil', 'Heat Pump']

    cursor.close()
    print(manufacturers)
    return render_template('add_appliance.html', types=types, manufacturers=manufacturers, energySourceAhs=energySourceAhs, energySourceWhs=energySourceWhs)

@app.route('/submit_add_appliance',methods=['POST'])
def submit_add_appliance():
    app.logger.info(request.form)
    conn = get_pg_connection()
    cursor = conn.cursor()

    # TODO: change household_id based on enter household info form
    # household_id = 2
    household_id = session['household_id']

    # get the upcoming sequential order from the current household
    sequential_order_query = 'SELECT COALESCE(max(sequential_order), 0) + 1 FROM air_handler WHERE household_id= %s'
    cursor.execute(sequential_order_query, (household_id,))
    sequential_order = cursor.fetchone()[0]
    print(f'sequential_order: {sequential_order}')

    # get data from front end form
    appliance_type = request.form['applianceType']
    btu = request.form['btu']
    manufacturer_id = request.form['manufacturerID']
    model_name = request.form['modelName']
    fan_rpm = request.form['fanRPM']

    # if user chooses air conditioner, get eer from front end
    air_conditioner = request.args.get('airConditioner', None)
    eer = request.form['EER']

    # if user chooses heater, get energy source from front end
    heater = request.args.get('heater', None)
    energy_source_ah = request.form['energySourceAh']

    # if user chooses heat pump, get seer and hspf from front end
    heat_pump = request.args.get('heatPump', None)
    seer = request.form['SEER']
    hspf = request.form['HSPF']

    tank_size = request.form['tankSize']
    # btu_rating = request.form['btuRating']
    temperature = request.form['temperature']
    # convert an empty string into a None type which can then be passed as NULL to the database.
    if temperature == '':
        temperature = None
    energy_source_wh = request.form['energySourceWh']

    if appliance_type == 'Air handler':
        add_air_handler_query = '''
            INSERT INTO air_handler (household_id, sequential_order, fan_rpm, btu, model_name, manufacturer_id)
            VALUES(%s, %s, %s, %s, %s, %s)
            '''
        cursor.execute(add_air_handler_query, (household_id, sequential_order, fan_rpm, btu, model_name, manufacturer_id))
        conn.commit()
        if air_conditioner:
            add_air_conditioner_query = 'INSERT INTO air_conditioner VALUES (%s, %s)'
            cursor.execute(add_air_conditioner_query,(household_id, eer))
            conn.commit()
        if heater:
            add_heater_query = 'INSERT INTO heater VALUES (%s, %s)'
            cursor.execute(add_heater_query,(household_id, energy_source_ah))
            conn.commit()
        if heat_pump:
            add_heat_pump_query = 'INSERT INTO heat_pump VALUES (%s, %s)'
            cursor.execute(add_heat_pump_query,(household_id, seer, hspf))
            conn.commit()
    else:
        add_water_heater_query = '''
            INSERT INTO water_heater(household_id, sequential_order_wh, energy_source, btu, tank_size, temperature, model_name, manufacturer_id)
            VALUES(%s, %s, %s, %s, %s, %s, %s, %s)
        '''
        cursor.execute(add_water_heater_query, (household_id, sequential_order, energy_source_wh, btu, tank_size, temperature, model_name, manufacturer_id))
        conn.commit()

    cursor.close()

    # TODO: return appliance_listing
    # return "success",200
    return redirect(url_for('appliance_listing', household_id=household_id))







@app.route('/appliance_listing/<int:household_id>')
def appliance_listing(household_id):
    # Connect to the database
    conn = get_pg_connection()

    # Create a cursor
    cur = conn.cursor()

    # Fetch the list of appliances for the specified household ID
    cur.execute('''
        SELECT ah.air_handler_id, ah.sequential_order, 'Air handler' AS type, m.manufacturer_name, ah.model_name
        FROM Air_Handler AS ah
        JOIN Manufacturer AS m ON ah.manufacturer_id = m.manufacturer_id
        WHERE ah.household_id = %s
        UNION ALL
        SELECT wh.water_heater_id, wh.sequential_order_wh, 'Water heater' AS type, m.manufacturer_name, wh.model_name
        FROM Water_Heater AS wh
        JOIN Manufacturer AS m ON wh.manufacturer_id = m.manufacturer_id
        WHERE wh.household_id = %s
        ORDER BY type, sequential_order
    ''', (household_id, household_id))
    appliances = cur.fetchall()

    # Close the cursor and connection
    cur.close()
    conn.close()

    return render_template('appliance_listing.html', appliances=appliances, household_id=household_id)



@app.route('/add_power_generation/<int:household_id>')
def add_power_generation(household_id):

        conn = get_pg_connection()
        cursor = conn.cursor()
        power_gen_type = ['solar', 'wind-turbine']
        cursor.close()
        return render_template('add_power_generation.html', power_gen_type=power_gen_type,household_id=household_id)







@app.route('/submit_add_power_gen', methods=['POST'])
def submit_add_power_gen():
    app.logger.info(request.form)
    conn = get_pg_connection()
    cursor = conn.cursor()

    # TODO: change household_id based on enter household info form
    # household_id = 2
    household_id = session['household_id']

    # get the upcoming sequential order from the current household
    sequential_order_query = 'SELECT COALESCE(max(sequential_order), 0) + 1 FROM power_generation WHERE household_id= %s'
    cursor.execute(sequential_order_query, (household_id,))
    sequential_order = cursor.fetchone()[0]
    print(f'sequential_order: {sequential_order}')

    # get data from front end form
    power_gen_type = request.form['powerGenType']
    monthly_kwh = request.form['monthlyKwh']
    battery_storage_capacity_kwh = request.form['batteryStorageCapacityKwh']

    add_power_gen_query = '''
        INSERT INTO power_generation(household_id, sequential_order, power_gen_type, monthly_kwh, battery_storage_capacity_kwh)
        VALUES(%s, %s, %s, %s, %s)
    '''
    cursor.execute(add_power_gen_query, (household_id, sequential_order, power_gen_type, monthly_kwh, battery_storage_capacity_kwh))
    conn.commit()

    cursor.close()

    # TODO: return power_gen_listing
    # return "success",200
    return redirect(url_for('power_gen_listing', household_id=household_id))






@app.route('/delete_appliance/<int:appliance_id>/<int:household_id>')
def delete_appliance(appliance_id, household_id):
    # Connect to the database
    conn = get_pg_connection()

    # Create a cursor
    cur = conn.cursor()

    # Get the type of the appliance
    cur.execute('SELECT air_handler_id FROM Air_Handler WHERE air_handler_id = %s', (appliance_id,))
    air_handler_id = cur.fetchone()

    # Check if the appliance is an Air Handler
    if air_handler_id:
        # Delete the subtypes (Air Conditioner, Heater, and Heat Pump)
        cur.execute('DELETE FROM Air_Conditioner WHERE air_handler_id = %s', (air_handler_id,))
        cur.execute('DELETE FROM Heater WHERE air_handler_id = %s', (air_handler_id,))
        cur.execute('DELETE FROM Heat_Pump WHERE air_handler_id = %s', (air_handler_id,))
        # Delete the Air Handler
        cur.execute('DELETE FROM Air_Handler WHERE air_handler_id = %s', (air_handler_id,))
    else:
        # Delete the Water Heater
        cur.execute('DELETE FROM Water_Heater WHERE water_heater_id = %s', (appliance_id,))

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Redirect back to the appliance listing page
    return redirect(url_for('appliance_listing', household_id=household_id))

@app.route('/reports/manu_model_search')
def manu_model_search():
    conn = get_pg_connection()
    cursor = conn.cursor()
    search_term = "%air%"
    manu_model_search_query = '''
        SELECT DISTINCT manufacturer_name, model_name FROM air_handler 
        NATURAL JOIN
        manufacturer WHERE manufacturer_name ILIKE %s OR model_name ILIKE %s
        UNION
        SELECT DISTINCT manufacturer_name, model_name FROM water_heater 
        NATURAL JOIN
        manufacturer WHERE manufacturer_name ILIKE %s OR model_name ILIKE %s
        ORDER BY manufacturer_name ASC, model_name DESC;
    '''
    cursor.execute(manu_model_search_query, (search_term, search_term, search_term, search_term))
    results = cursor.fetchall()

    # check which cells match the search term and store them in a list of tuples
    highlights_manu = []
    highlights_model = []
    for result in results:
        if search_term[1:-1].lower() in result[0].lower():
            highlights_manu.append(result[0])
        if search_term[1:-1].lower() in result[1].lower():
            highlights_model.append(result[1])

    return render_template('manu_model_search.html', results=results, highlights_manu=highlights_manu,highlights_model=highlights_model)

@app.route('/add_household', methods=['POST'])
def add_household():
    conn = get_pg_connection()
    cur = conn.cursor()
    form_data = request.form
    print(form_data)
    cur.execute('''SELECT * FROM household where email=%s''', (form_data['email'],))
    if cur.rowcount > 0:
        error = "email already exist in our system"
        return render_template('error.html', data=error)


    cur.execute('''SELECT * FROM postal_code where zip=%s''', (form_data['postal_code'],))
    if cur.rowcount  == 0:
        error = "postal code {} doesn't exist in the system".format(form_data['postal_code'])
        return render_template('error.html', data=error)


    try:
        sql_statement = '''INSERT INTO household(email, square_footage, household_type_id, thermostat_setting_heating, thermostat_setting_cooling, postal_code_id) 
        SELECT '{}', {}, {}, {}, {}, postal_code_id FROM postal_code WHERE zip = '{}' RETURNING household_id;'''.format(form_data['email'], int(form_data['square_footage']), int(form_data['home_type']),
                                                               'NULL' if 'no_heat' in form_data  else int(form_data['heat_thermostat']),
                                                               'NULL' if 'no_cooling' in form_data else int(form_data['cool_thermostat']),
                                                               form_data['postal_code'])

        cur.execute(sql_statement)

        household_id = cur.fetchone()[0]
        session['household_id']=household_id

        if 'Electric' in form_data:
            utility_sql_statement = """INSERT INTO House_PublicUtilities(household_id, public_utilities_id) values ({}, {})""".format(household_id, form_data['Electric'])
            cur.execute(utility_sql_statement)

        if 'Gas' in form_data:
            utility_sql_statement = """INSERT INTO House_PublicUtilities(household_id, public_utilities_id) values ({}, {})""".format(household_id, form_data['Gas'])
            cur.execute(utility_sql_statement)

        if 'Steam' in form_data:
            utility_sql_statement = """INSERT INTO House_PublicUtilities(household_id, public_utilities_id) values ({}, {})""".format(household_id, form_data['Steam'])
            cur.execute(utility_sql_statement)

        if 'Liquid Fuel' in form_data:
            utility_sql_statement = """INSERT INTO House_PublicUtilities(household_id, public_utilities_id) values ({}, {})""".format(household_id, form_data['Liquid Fuel'])
            cur.execute(utility_sql_statement)

        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        error = "Failed to save the household info: {}".format(str(e))
        return render_template('error.html', data=error)
    finally:
        cur.close()
        conn.close()
    return redirect(url_for('add_appliance'))


@app.route('/reports')
def reports_list():
    return render_template('reports.html')


@app.route('/reports/top_manufacturer')
def top_manufacturer():
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()

    data = {}
    sql_statement = """
        WITH manu AS (
            SELECT 'water heater' AS appliance_type, household_id,
            sequential_order_wh AS seq, manufacturer_id
            FROM water_heater
            UNION
            SELECT 'air handler' AS appliance_type, household_id, sequential_order
            AS seq, manufacturer_id
            FROM air_handler
        )
        SELECT mn.manufacturer_id, mn.manufacturer_name, count(1) AS appliance_count
        FROM manu m
        JOIN manufacturer mn
        ON m.manufacturer_id=mn.manufacturer_id
        GROUP BY mn.manufacturer_id, manufacturer_name
        ORDER BY appliance_count DESC
        LIMIT 25
        ;"""
    cur.execute(sql_statement)
    data= cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()
    return render_template('top25manufacturer.html', data=data)



@app.route('/reports/top_manufacturer/<id>')
def top_manufacturer_drilldown(id):
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()

    data = {}
    sql_statement = """
        WITH raw AS (
            SELECT 'wh' AS appliance_type, water_heater_id AS ap_id, manufacturer_id
            FROM water_heater
            UNION ALL
            SELECT 'ah' AS appliance_type, air_handler_id AS ap_id, manufacturer_id
            FROM air_handler
            UNION ALL
            SELECT 'ah-ac' AS appliance_type, ac.air_handler_id AS ap_id,
            ah1.manufacturer_id
            FROM air_handler ah1
            JOIN air_conditioner ac
            ON ah1.air_handler_id=ac.air_handler_id
            UNION ALL
            SELECT 'ah-h' AS appliance_type, h.air_handler_id AS ap_id,
            ah2.manufacturer_id
            FROM air_handler ah2
            JOIN heater h
            ON ah2.air_handler_id=h.air_handler_id
            UNION ALL
            SELECT 'ah-hp' AS appliance_type, hp.air_handler_id AS ap_id,
            ah3.manufacturer_id
            FROM air_handler ah3
            JOIN heat_pump hp
            ON ah3.air_handler_id=hp.air_handler_id
        ),
        tall AS (
            SELECT m.manufacturer_name,m.manufacturer_id, r.appliance_type, count(r.ap_id) AS count
            FROM manufacturer m
            LEFT JOIN raw r
            ON r.manufacturer_id=m.manufacturer_id
            GROUP BY 1,2,3
        ),
        wide AS (
            SELECT r.manufacturer_name, r.manufacturer_id,
            CASE WHEN r.appliance_type='wh' THEN count ELSE NULL END AS
            water_heater_count,
            CASE WHEN r.appliance_type='ah' THEN count ELSE NULL END AS
            air_handler_count,
            CASE WHEN r.appliance_type='ah-ac' THEN count ELSE NULL END AS
            air_handler_air_conditioner_count,
            CASE WHEN r.appliance_type='ah-h' THEN count ELSE NULL END AS
            air_handler_heater_count,
            CASE WHEN r.appliance_type='ah-hp' THEN count ELSE NULL END AS
            air_handler_heat_pum_count
            FROM tall r
        )
            SELECT w.manufacturer_name,
            max(w.water_heater_count) AS water_heater_count,
            max(w.air_handler_count) AS air_handler_count,
            max(w.air_handler_air_conditioner_count) AS
            air_handler_air_conditioner_count,
            max(w.air_handler_heater_count) AS air_handler_heater_count,
            max(w.air_handler_heat_pum_count) AS air_handler_heat_pum_count
            FROM wide w
            Where w.manufacturer_id={}
            GROUP BY 1
            ORDER BY 1
            ;
    """.format(id)
    cur.execute(sql_statement)
    data= cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()
    return render_template('top25manufacturer_drilldown.html', data=data)


@app.route('/reports/search_by_radius')
def search_by_radius():
    return render_template('searchbyradius.html', data={})

@app.route('/report/heating_cooling_details')
def heating_cooling_details():
    # Connect to the database
    conn = get_pg_connection()

    # Create a cursor
    cur = conn.cursor()

    # Run the queries to fetch the statistics
    cur.execute('SELECT COUNT(Air_Handler.air_handler_id) AS air_conditioner_count, '
                'AVG(Air_Handler.btu)::integer AS avg_air_conditioner_btu, '
                'AVG(Air_Handler.fan_rpm)::decimal(10, 1) AS avg_air_conditioner_rpm, '
                'AVG(Air_Conditioner.eer)::decimal(10, 1) AS avg_air_conditioner_eer '
                'FROM Air_Handler '
                'JOIN Air_Conditioner ON Air_Handler.air_handler_id = Air_Conditioner.air_handler_id')

    air_conditioners = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    cur.execute('SELECT COUNT(Air_Handler.air_handler_id) AS heater_count, '
                'AVG(Air_Handler.btu)::integer AS avg_heater_btu, '
                'AVG(Air_Handler.fan_rpm)::decimal(10, 1) AS avg_heater_rpm, '
                'mode() WITHIN GROUP (ORDER BY Heater.energy_source) AS common_energy_source '
                'FROM Air_Handler '
                'JOIN Heater ON Air_Handler.air_handler_id = Heater.air_handler_id')

    heaters = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    cur.execute('SELECT COUNT(Air_Handler.air_handler_id) AS heat_pump_count, '
                'AVG(Air_Handler.btu)::integer AS avg_heat_pump_btu, '
                'AVG(Air_Handler.fan_rpm)::decimal(10, 1) AS avg_heat_pump_rpm, '
                'AVG(Heat_Pump.seer)::decimal(10, 1) AS avg_heat_pump_seer, '
                'AVG(Heat_Pump.hspf)::decimal(10, 1) AS avg_heat_pump_hspf '
                'FROM Air_Handler '
                'JOIN Heat_Pump ON Air_Handler.air_handler_id = Heat_Pump.air_handler_id')

    heat_pumps = dict(zip([desc[0] for desc in cur.description], cur.fetchone()))

    # Close the cursor and connection
    cur.close()
    conn.close()

    # Render the report template with the fetched statistics
    return render_template('heating_cooling_method_details.html',
                           air_conditioners=air_conditioners,
                           heaters=heaters,
                           heat_pumps=heat_pumps)

@app.route('/search_by_radius', methods=['POST'])
def household_average_by_radius():
    conn = get_pg_connection()
    cur = conn.cursor()
    form_data = request.form

    cur.execute('''SELECT * FROM postal_code where zip=%s''', (form_data['postal_code'],))
    if cur.rowcount  == 0:
        error = "postal code {} doesn't exist in the system".format(form_data['postal_code'])
        return render_template('error.html', data=error)

    data = {}
    sql_statement1 = """
    WITH
        selected_postal_code AS (
            SELECT latitude AS selected_lad, longtitude AS selecetd_long FROM postal_code WHERE zip = '{}'
        ),
        target_households AS (
            SELECT b.household_id
            FROM postal_code AS a
            JOIN household AS b ON a.postal_code_id = b.postal_code_id
            JOIN selected_postal_code ON 1 = 1
            WHERE 2*atan2(sqrt(sin((latitude-selected_lad)/2)*sin((latitude-selected_lad)/2) + cos(selected_lad)*cos(latitude)*
            sin((longtitude-selecetd_long)/2)*sin((longtitude-selecetd_long)/2)), sqrt(1-(sin((latitude-selected_lad)/2)*sin((latitude-selected_lad)/2) + cos(selected_lad)*cos(latitude)* sin((longtitude-selecetd_long)/2)*sin((longtitude-selecetd_long)/2)))) * 3958.75 <= {}
        )
        SELECT '{}' AS search_zip, '{}' AS search_radius, c.name AS household_type, count(household_id)
            AS household_count, sum(count(household_id)) OVER () AS total_household_count,
            Round(avg(square_footage)) AS avg_square_footage, round(avg(thermostat_setting_heating),1) AS avg_heat_setting,
            round(avg(thermostat_setting_cooling),1) AS avg_cool_setting
        FROM household AS a
        JOIN postal_code AS b ON a.postal_code_id = b.postal_code_id
        JOIN household_type AS c ON c.household_type_id = a.household_type_id
        WHERE 
            a.household_id IN (SELECT household_id FROM target_households)
        GROUP BY c.name;""".format(form_data['postal_code'], form_data['radius'],form_data['postal_code'], form_data['radius'])
    cur.execute(sql_statement1)
    data['aggregate1'] = cur.fetchall()

    sql_statement2 = """
        WITH
        selected_postal_code AS (
            SELECT latitude AS selected_lad, longtitude AS selecetd_long FROM postal_code WHERE zip = '{}'
        ),
        target_households AS (
            SELECT b.household_id
            FROM postal_code AS a
            JOIN household AS b ON a.postal_code_id = b.postal_code_id
            JOIN selected_postal_code ON 1 = 1
            WHERE 2*atan2(sqrt(sin((latitude-selected_lad)/2)*sin((latitude-selected_lad)/2) + cos(selected_lad)*cos(latitude)*
            sin((longtitude-selecetd_long)/2)*sin((longtitude-selecetd_long)/2)), sqrt(1-(sin((latitude-selected_lad)/2)*sin((latitude-selected_lad)/2) + cos(selected_lad)*cos(latitude)* sin((longtitude-selecetd_long)/2)*sin((longtitude-selecetd_long)/2)))) * 3958.75 <= {}
        ), 
        utility_data AS (
            SELECT STRING_AGG(DISTINCT d.name, ',') AS utilities FROM
            household AS a
            JOIN house_publicutilities AS b ON a.household_id = b.household_id
            JOIN postal_code AS c ON a.postal_code_id = c.postal_code_id
            JOIN public_utilities AS d ON b.public_utilities_id = d.public_utilities_id
            WHERE a.household_id IN (SELECT household_id FROM target_households)
        ), 
        off_grid_data AS (
            SELECT count(a.household_id) AS off_the_grid_count FROM
            household AS a
            JOIN postal_code AS b ON a.postal_code_id = b.postal_code_id
            LEFT JOIN house_publicutilities AS c ON a.household_id = c.household_id
            WHERE c.public_utilities_id IS NULL AND a.household_id IN (SELECT household_id FROM target_households)
        ), powergen_data AS (
            SELECT count(DISTINCT a.household_id) AS off_the_grid_count,
            round(avg(monthly_kwh)) AS avg_monthly_kwh
            from
            household AS a
            JOIN postal_code AS b ON a.postal_code_id = b.postal_code_id
            JOIN power_generation AS c ON c.household_id = a.household_id
            WHERE a.household_id IN (SELECT household_id FROM target_households)
        ), 
        most_common_powergen AS (
            SELECT c.power_gen_type_name, count(*) AS counts FROM
            household AS a
            JOIN postal_code AS b ON a.postal_code_id = b.postal_code_id
            JOIN power_generation AS c ON c.household_id = a.household_id
            WHERE a.household_id IN (SELECT household_id FROM target_households)
            GROUP BY 1
            ORDER BY 2 DESC
            FETCH FIRST 1 ROW WITH TIES
        ), 
        battery_data AS (
            SELECT count(DISTINCT a.household_id) AS count_of_household_with_battery_storage
            from
            household AS a
            JOIN postal_code AS b ON a.postal_code_id = b.postal_code_id
            JOIN power_generation AS c ON c.household_id = a.household_id
            WHERE c.battery_storage_capacity_kwh IS NOT NULL AND a.household_id IN (SELECT household_id FROM
            target_households)
        )
        SELECT '{}' as search_zip , '{}' as search_radius, * FROM utility_data
        full join off_grid_data on 1 = 1
        full join powergen_data on 1 = 1
        full join most_common_powergen on 1 = 1
        full join battery_data on 1 = 1;""".format(form_data['postal_code'], form_data['radius'],form_data['postal_code'], form_data['radius'])
    cur.execute(sql_statement2)
    data['aggregate2'] = cur.fetchall()
    print("?????", sql_statement2)
    return render_template('searchbyradius.html', data=data)



@app.route('/reports/off_grid')
def off_grid():
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()

    data1 = {}
    sql_og_1 = """
        with ogh as ( 
        select distinct h.email, pc.state 
        from household h  
        join postal_code pc  
        on h.postal_code_id=pc.postal_code_id 
        where not exists (  
        select * from house_publicutilities hp where h.household_id=hp.household_id  
        ) 
        ) 
        
        select o.state, count(1) as count_state 
        from ogh o  
        group by 1 
        order by count_state desc ,1 
        limit 1 
        ;  
        """
    cur.execute(sql_og_1)
    data_og_1 = cur.fetchall()

    data2 = {}
    sql_og_2 = """
         select round(avg(t.battery_storage_capacity_kwh),0) as avg_battery 
         from 
        (
        select distinct h.email,pg.sequential_order, 
        pg.battery_storage_capacity_kwh
        from household h 
        join power_generation pg
        on h.household_id=pg.household_id
        where not exists ( 
        select * from house_publicutilities hp where h.household_id=hp.household_id 
        )
        )t
        ;
        """
    cur.execute(sql_og_2)
    data_og_2 = cur.fetchall()

    data3 = {}
    sql_og_3 = """
        with raw as (
            select distinct h.email,pg.sequential_order, pg.power_gen_type_name
            from household h 
            join power_generation pg
            on h.household_id=pg.household_id
            where not exists ( 
            select * from house_publicutilities hp where h.household_id=hp.household_id 
            )
        )
        
        select power_gen_type_name, trim_scale(count(offgridhouse) / (sum(count(1)) over ())) as pct_type_offgridhouse
        from (
        select distinct pgt.power_gen_type_name , (r.email||r.sequential_order) as offgridhouse
        from power_generation_type pgt
        left join raw r
        on pgt.power_gen_type_name=r.power_gen_type_name
        )t
        group by 1
        ;
        """
    cur.execute(sql_og_3)
    data_og_3 = cur.fetchall()

    data4 = {}
    sql_og_4 = """
        WITH raw AS (
            SELECT DISTINCT h.email, ht.name
            FROM household h
            JOIN household_type ht ON h.household_type_id = ht.household_type_id
            WHERE NOT EXISTS (
                SELECT * FROM house_publicutilities hp WHERE h.household_id = hp.household_id
            )
        )
        SELECT t1.household_type, house_count / SUM(house_count) OVER () AS pct_household_type
        FROM (
            SELECT household_type, COUNT(email) AS house_count
            FROM (
                SELECT DISTINCT ht.name AS household_type, r.email
                FROM household_type ht
                LEFT JOIN raw r ON ht.name = r.name
            ) t
            GROUP BY 1
        ) t1;
        """
    cur.execute(sql_og_4)
    data_og_4 = cur.fetchall()


    data5 = {}
    sql_og_5 = """
        
        SELECT round(avg(t.tank_size), 1) AS avg_tanksize_offgrid
        FROM (
            SELECT DISTINCT h.email, wh.sequential_order_wh, wh.tank_size
            FROM household h
            JOIN water_heater wh ON h.household_id = wh.household_id
            WHERE NOT EXISTS (
                SELECT * FROM house_publicutilities hp WHERE h.household_id = hp.household_id
            )
        ) t;

        -- On the grid
        SELECT round(avg(t.tank_size), 1) AS avg_tanksize_ongrid
        FROM (
            SELECT DISTINCT h.email, wh.sequential_order_wh, wh.tank_size
            FROM household h
            JOIN water_heater wh ON h.household_id = wh.household_id
            WHERE EXISTS (
                SELECT * FROM house_publicutilities hp WHERE h.household_id = hp.household_id
            )
        ) t;
        """
    cur.execute(sql_og_5)
    data_og_5 = cur.fetchall()

    data6 = {}
    sql_og_6 = """
        WITH raw AS (
            SELECT appliance_type, min(t.btu) AS min_btu, max(t.btu) AS max_btu, round(avg(t.btu), 0) AS avg_btu
            FROM (
                SELECT 'air handler' AS appliance_type, ah.household_id, ah.sequential_order, btu
                FROM air_handler ah
                UNION ALL
                SELECT 'water heater' AS appliance_type, wh.household_id, wh.sequential_order_wh AS sequential_order, wh.btu
                FROM water_heater wh
            ) t
            WHERE NOT EXISTS (
                SELECT * FROM house_publicutilities hp WHERE t.household_id = hp.household_id
            )
            GROUP BY 1
        ),
        at AS (
            SELECT 'air handler' AS appliance_type
            UNION ALL
            SELECT 'water heater' AS appliance_type
        )
        SELECT at.appliance_type, COALESCE(raw.min_btu, 0) AS min_btu, COALESCE(raw.max_btu, 0) AS max_btu, COALESCE(raw.avg_btu, 0) AS avg_btu
        FROM at
        LEFT JOIN raw ON at.appliance_type = raw.appliance_type;
        """
    cur.execute(sql_og_6)
    data_og_6 = cur.fetchall()


    # close the cursor and connection
    cur.close()
    conn.close()
    return render_template('off_grid_report.html', data1=data_og_1, data2=data_og_2, data3=data_og_3,data4 = data_og_4,data5 = data_og_5,data6 = data_og_6)


@app.route('/power_gen_list')
def power_gen_list():
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()
    household_id = session['household_id']
    data = {}
    sql_pg = """
        SELECT household_id, sequential_order, power_gen_type_name, monthly_kwh, battery_storage_capacity_kwh 
        FROM power_generation
        where household_id=%s; 
        """
    #TO DO -- pass household ID?
    cur.execute(sql_pg, (household_id,))
    data_pg = cur.fetchall()

    # close the cursor and connection
    cur.close()
    conn.close()
    return render_template('power_gen_list.html', data=data_pg)



@app.route('/delete_power_gen/pid<int:pid>/seq<int:seq>', methods=['POST','GET'])
def delete_power_gen(pid, seq):
    # Connect to the database
    conn = get_pg_connection()

    # create a cursor
    cur = conn.cursor()
    sql_delete_pg = """
        DELETE FROM power_generation 
        WHERE household_id=%s and sequential_order=%s; 
        """
    tuple = (pid, seq)
    cur.execute(sql_delete_pg, tuple)
    conn.commit()
    # close the cursor and connection
    cur.close()
    conn.close()
    return redirect(url_for('power_gen_list'))

if __name__ == '__main__':
    app.secret_key = 'super secret key'
    app.run(debug=True)