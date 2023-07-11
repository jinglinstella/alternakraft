# create tables, only need to run once
from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)
def get_pg_connection():
    # return psycopg2.connect(database="aatpbpuf", user="aatpbpuf",
    #                      password="svSXNOMQ1gThOVclKsLMFYNJzbxfe3px", host="silly.db.elephantsql.com", port="5432", options="-c search_path=public") #change schema

    return psycopg2.connect(database="cs6400", user="postgres",
                             password="testuser", host="localhost", port="5432", options="-c search_path=public")

# table schema DDL
sql = '''
--postgreSQL

-- Tables 
Drop table  if exists Postal_Code cascade ;
CREATE TABLE Postal_Code (
  postal_code_id integer primary key generated always as identity,
  zip varchar(5) NOT NULL,
  city varchar(100) NOT NULL,
  state varchar(100) NOT NULL,
  latitude DOUBLE precision not null,
  longtitude Double precision not null,
  unique (zip)
);

Drop table  if exists Household_Type cascade;
CREATE TABLE Household_Type (
  household_type_id integer primary key generated always as identity,
  name varchar(100) NOT null,
  unique (name)
);

--updated
Drop table  if exists Household cascade;
CREATE TABLE Household (
  household_id integer primary key generated always as identity,
  email varchar(100) NOT NULL,
  square_footage integer NOT NULL,
  household_type_id integer NOT NULL,
  thermostat_setting_heating integer,
  thermostat_setting_cooling integer,
  postal_code_id integer NOT null,
  unique (email),
  constraint fk_postal_code
	  foreign key (postal_code_id)
	  	references Postal_Code(postal_code_id)
	  	on delete cascade,
  constraint fk_house_type
	  foreign key (household_type_id)
	  	references Household_Type(household_type_id)
	  	on delete cascade
);


Drop table  if exists Public_Utilities cascade;
CREATE TABLE Public_Utilities (
  public_utilities_id integer primary key generated always as identity,
  name varchar(100) NOT null,
  unique (name)
);


Drop table  if exists House_PublicUtilities cascade;
CREATE TABLE House_PublicUtilities (
  household_id integer NOT NULL,
  public_utilities_id integer NOT null,
  constraint email_publicutilities primary key (household_id,public_utilities_id),
  constraint fk_household
	  foreign key (household_id)
	  	references Household(household_id)
	  	on delete cascade,
	constraint fk_pu
	  foreign key (public_utilities_id)
	  	references Public_Utilities(public_utilities_id)
	  	on delete cascade	
);

Drop table  if exists Power_Generation_Type cascade;
CREATE TABLE Power_Generation_Type (
  power_gen_type_name varchar(100) not null primary key
);

Drop table  if exists Power_Generation cascade;
CREATE TABLE Power_Generation (
  household_id integer NOT NULL,
  sequential_order integer NOT null,
  power_gen_type_name varchar(100) NOT NULL,
  monthly_kwh integer not null,
  battery_storage_capacity_kwh integer,
  constraint email_seq primary key (household_id,sequential_order),
  constraint fk_household_pg
	  foreign key (household_id)
	  	references Household(household_id)
	  	on delete cascade,
   constraint fk_pgt
	  foreign key (power_gen_type_name)
	  	references Power_Generation_Type(power_gen_type_name)
	  	on delete cascade
);


Drop table  if exists Manufacturer cascade;
CREATE TABLE Manufacturer (
manufacturer_id integer primary key generated always as identity,
manufacturer_name varchar(100) not null
);



Drop table  if exists Air_Handler cascade;
CREATE TABLE Air_Handler (
  air_handler_id integer primary key generated always as identity,
  household_id integer NOT NULL,
  sequential_order integer NOT null,
  fan_rpm integer NOT NULL,
  btu integer not null,
  model_name varchar(100),
  manufacturer_id integer not null,
  unique (household_id,sequential_order),
  constraint fk_household_ah
	  foreign key (household_id)
	  	references Household(household_id)
	  	on delete cascade,
	constraint fk_manu
	  foreign key (manufacturer_id)
	  	references Manufacturer(manufacturer_id)
	  	on delete cascade  	
);



Drop table  if exists Air_Conditioner cascade;
CREATE TABLE Air_Conditioner (
  air_handler_id integer NOT null primary key,
  eer decimal(100,10) NOT null,
  constraint fk_air_handler
	  foreign key (air_handler_id)
	  	references Air_Handler(air_handler_id)
	  	on delete cascade
);


Drop table  if exists Heater cascade;
CREATE TABLE Heater (
  air_handler_id integer NOT NULL primary key,
  energy_source Varchar(100) NOT null,
  constraint fk_air_handler
	  foreign key (air_handler_id)
	  	references Air_Handler(air_handler_id)
	  	on delete cascade
);

Drop table  if exists Heat_Pump cascade;
CREATE TABLE Heat_Pump (
  air_handler_id integer NOT NULL primary key,
  seer  decimal(100,10) NOT null,
  hspf  decimal(100,10) NOT null,
  constraint fk_air_handler
	  foreign key (air_handler_id)
	  	references Air_Handler(air_handler_id)
	  	on delete cascade
);



Drop table  if exists Water_Heater cascade;
CREATE TABLE Water_Heater (
 water_heater_id integer  NOT NULL primary key generated always as identity,
  household_id integer NOT NULL,
  sequential_order_wh integer NOT null,
  energy_source Varchar(100) NOT NULL,
  btu integer not null,
  tank_size decimal(100,10) NOT null,
  temperature integer,
  model_name varchar(100),
  manufacturer_id integer not null,
  unique(household_id,sequential_order_wh),
  constraint fk_household_wh
	  foreign key (household_id)
	  	references Household(household_id)
	  	on delete cascade,
	constraint fk_manu
	  foreign key (manufacturer_id)
	  	references Manufacturer(manufacturer_id)
	  	on delete cascade  	
);

'''


conn = get_pg_connection()
# create a cursor
cur = conn.cursor()
cur.execute(sql)

conn.commit()

# close the cursor and connection
cur.close()
conn.close()

