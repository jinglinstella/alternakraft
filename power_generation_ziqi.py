@app.route('/add_power_gen')
def add_power_gen():
    conn = get_pg_connection()
    cursor = conn.cursor()
    power_gen_type = ['solar', 'wind-turbine']
    cursor.close()
    return render_template('add_power_gen.html', power_gen_type=power_gen_type)


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
