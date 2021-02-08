import sqlite3
from sqlite3 import Error


def create_connection(path='farmsim.sql', feedback=False):
    """
    Create connection to an sqlite database

    :param path: (str) path to the database
    :param feedback: (bool) give sql (error) feedback
    :return: connection to the sql database
    """
    connection = None
    try:
        connection = sqlite3.connect(path)
        if feedback:
            print("Connection to DB successful")
    except Error as e:
        if feedback:
            print(f"Error: '{e}'")
        else:
            pass
    return connection


def execute_query(connection, query, feedback=False):
    """
    Executes the given query on the database

    :param connection: (sqlite3.connect(path)) connection to a database to execute query on
    :param query: (str) SQL command string of the query that needs to be executed
    :param feedback: (bool) give sql (error) feedback
    :return:
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query)
        connection.commit()
        if feedback:
            print("Query executed")
    except Error as e:
        if feedback:
            print(f"Error: '{e}'")
        else:
            pass


def execute_query_v2(connection, query, args, feedback=False):
    """
    Executes the given query on the connected database and will insert the given argument tuple into the query.

    :param connection: (sqlite3.connect(path)) connection to a database to execute query on
    :param query: (str) SQL command string of the query that needs to be executed
    :param args: (tuple) of arguments that needs to be inserted into the query
    :param feedback: (bool) give sql (error) feedback
    :return:
    """
    cursor = connection.cursor()
    try:
        cursor.execute(query, args)
        connection.commit()
        if feedback:
            print("Query executed")
    except Error as e:
        if feedback:
            print(f"Error: '{e}'")
        else:
            pass


def execute_read_query(connection, query, feedback=False):
    """
    Used to execute a read query on a sql database connection

    :param connection: (sqlite3.connect(path)) connection to a database to execute query on
    :param query: SQL command string of the query that needs to be executed
    :param feedback: (bool) give sql (error) feedback
    :return:
        result (list) of tuples with the found data
    """
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
    except Error as e:
        if feedback:
            print(f"Error: '{e}'")
        else:
            pass

    return result


def execute_read_query_v2(connection, query, args, feedback=False):
    """
    Used to execute the given read query on the connected database and will insert the given argument tuple into the
    query.
    :param connection: (sqlite3.connect(path)) connection to a database to execute query on
    :param query: (str) SQL command string of the query that needs to be executed
    :param args: (tuple) of arguments that needs to be inserted into the query
    :param feedback: (bool) give sql (error) feedback
    :return:
        result (list) of tuples with the found data
    """
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query, args)
        result = cursor.fetchall()
    except Error as e:
        if feedback:
            print(f"Error: '{e}'")
        else:
            pass
    return result


def _create_veg_table():
    """
    Creates the vegetable table for the farm simulator game
    """

    conn = create_connection('farmsim.sql')
    query = """CREATE TABLE IF NOT EXISTS vegetables (
    KIND TEXT NOT NULL,
    price INTEGER,
    days_to_grow INTEGER,
    prod_value INTEGER,
    prod_number INTEGER,
    multi_grow INTEGER,
    UNIQUE(KIND, price, days_to_grow, prod_value, prod_number)
    );
    """
    execute_query(conn, query)


def _create_anm_table():
    """
    Creates the animals table for the farm simulator game
    """

    conn = create_connection('farmsim.sql')
    query = """CREATE TABLE IF NOT EXISTS animals (
        KIND TEXT NOT NULL,
        price INTEGER,
        days_to_adult INTEGER,
        age_max INTEGER,
        days_to_prod INTEGER,
        prod_value INTEGER,
        UNIQUE(KIND, price, days_to_adult, age_max, days_to_prod, prod_value)
        );
        """
    execute_query(conn, query)


def _insert_vegetable(kind, price, days_to_grow, prod_value, prod_number, multigrow):
    """
    creates a new entry in the vegetables table by inserting the given parameters
    :param kind: (str) name of the vegetable
    :param price: (int) buy price of the vegetable
    :param days_to_grow: (int) days until the crop produces
    :param prod_value: (int) base product value
    :param prod_number: (int) maximum number of yield 
    :param multigrow: (int) the times a crop can regrow
    """
    conn = create_connection('farmsim.sql')
    query = """INSERT INTO
                vegetables (KIND, price, days_to_grow, prod_value, prod_number, multi_grow)
                VALUES
                (?,?,?,?,?,?)"""
    tpl = (kind, price, days_to_grow, prod_value, prod_number, multigrow,)
    execute_query_v2(conn, query, tpl)


def _insert_animal(kind, price, days_to_adult, age_max, days_to_grow, prod_value):
    """
    creates a new entry for the animals table by inserting the given parameters
    :param kind: (str) name of the animal type
    :param price: (int) buy price of the animal
    :param days_to_adult: (int) number of days before the animal becomes an adult
    :param age_max: (int) maximum age (days) of the animal
    :param days_to_grow: (int) number of days it takes the animal to produce
    :param prod_value: (int) value of the product the animal produces
    """
    conn = create_connection('farmsim.sql')
    query = """INSERT INTO
                    animals (KIND, price, days_to_adult, age_max, days_to_prod, prod_value)
                    VALUES
                    (?,?,?,?,?,?)"""
    tpl = (kind, price, days_to_adult, age_max, days_to_grow, prod_value,)
    execute_query_v2(conn, query, tpl)


def _insert_vegs():
    """
    insert different crops into vegetables table 
    """
    _create_veg_table()
    names = ['Wheat', 'Corn', 'Melon', 'Cabbage', 'Strawberry', 'potato']
    price = [25, 100, 120, 40, 20, 50]
    dtg = [3, 6, 10, 4, 5, 6]
    val = [40, 50, 200, 60, 5, 35]
    num = [1, 2, 1, 1, 4, 3]
    mg = [0, 3, 0, 0, 4, 0]
    for i in range(len(names)):
        _insert_vegetable(names[i], price[i], dtg[i], val[i], num[i], mg[i])
    query = "SELECT * FROM vegetables"
    conn = create_connection('farmsim.sql')
    table = execute_read_query(conn, query)
    for i in table:
        print(i)


def _insert_anim():
    """
    insert different animals into the animals table 
    """
    _create_anm_table()
    names = ['Cow', 'Chicken', 'Pig', 'Sheep']
    price = [1000, 250, 500, 750]
    days = [8, 2, 5, 10]
    age = [250, 100, 150, 200]
    prod = [2, 1, 5, 10]
    val = [12, 5, 15, 50]
    for i in range(len(names)):
        _insert_animal(names[i], price[i], days[i], age[i], prod[i], val[i])
    query = "SELECT * FROM animals"
    conn = create_connection('farmsim.sql')
    table = execute_read_query(conn, query, feedback=True)
    for i in table:
        print(i)

if __name__ == '__main__':
    _insert_vegs()
    _insert_anim()
