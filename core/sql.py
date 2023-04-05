"""
Creates entries in an SQL database

Modules:
    3rd Party: pyodbc, termcolor
    Internal: config, core

Classes:

    Sql
        Write to and read from a database

Functions

    None

Exceptions:

    None

Misc Variables:

    None

Author:
    Luke Robertson - April 2023
"""

import pyodbc
from config import GLOBAL, GRAPH
from core import teamschat
import termcolor


class Sql():
    """Connect to an SQL server/database to read and write

    Attributes
    ----------
    None

    Methods
    -------
    add()
        Adds an entry to the database
    read_last()
        Reads the last entry in a database
    read_since()
        Reads all entries since a particular time
    """

    # Initialise the class
    def __init__(self):
        """Class constructor

        Reads the database server and name from the config file

        Parameters
        ----------
        None

        Raises
        ------
        None

        Returns
        -------
        None
        """

        self.server = GLOBAL['db_server']
        self.db = GLOBAL['db_name']

    # Add an entry to the SQL server
    def add(self, table, fields):
        """Add an entry to the database

        This is often instantiated when loading a plugin

        Parameters
        ----------
        table : str
            The database table to write to
        fields : dict
            A dictionary that includes named fields and values to write

        Raises
        ------
        Exception
            If there were errors writing to the database

        Returns
        -------
        True : boolean
            If the write was successful
        False : boolean
            If the write failed
        """

        # We need columns and values
        #   Both are strings, a comma separates each entry
        # Create empty strings for columns and corresponding values
        columns = ''
        values = ''

        # Populate the columns and values (comma after each entry)
        for field in fields:
            columns += field + ', '
            values += str(fields[field]) + ', '

        # Clean up the trailing comma, to make this valid
        columns = columns.strip(", ")
        values = values.strip(", ")

        # Build the SQL command as a string
        sql_string = f'INSERT INTO {table} ('
        sql_string += columns
        sql_string += ')'

        sql_string += '\nVALUES '
        sql_string += f'({values});'

        # Optionally, we can debug this to the terminal
        if GLOBAL['flask_debug']:
            print(termcolor.colored(
                f"DEBUG (sql.py): {sql_string}",
                "magenta"
            ))

        # Connect to db, run the SQL command, commit the transaction
        try:
            with pyodbc.connect(
                    'Driver={SQL Server};'
                    'Server=%s;'
                    'Database=%s;'
                    'Trusted_Connection=yes;'
                    % (self.server, self.db)) as self.conn:

                # The cursor is a pointer to an area in the database
                self.cursor = self.conn.cursor()

                # Try to execute the SQL command (add rows)
                try:
                    self.cursor.execute(sql_string)
                except Exception as err:
                    print(termcolor.colored(
                        f"SQL execution error: {err}",
                        "red"
                    ))

                    teamschat.send_chat(
                        "An error has occurred while writing to SQL",
                        GRAPH['chat_id']
                    )

                    return False

                # Commit the transaction
                try:
                    self.conn.commit()
                except Exception as err:
                    print(termcolor.colored(
                        f"SQL commit error: {err}",
                        "red"
                    ))

                    teamschat.send_chat(
                        "An error has occurred while committing\
                            the SQL transaction",
                        GRAPH['chat_id']
                    )

                    return False

        # If the SQL server connection failed
        except Exception as err:
            print(termcolor.colored(
                f"Error {err} connecting to the SQL database",
                "red"
            ))

            teamschat.send_chat(
                "Could not connect to the SQL server",
                GRAPH['chat_id']
            )

            return False

        # If all was good, return True
        return True

    # Read the last entry from the SQL server
    def read_last(self, table):
        """Read the last entry in a table

        Parameters
        ----------
        table : str
            The database table to write to

        Raises
        ------
        Exception
            If there were errors connecting to the server
        Exception
            If there were errors reading

        Returns
        -------
        entry : str
            The entry retrieved from the SQL server
        False : boolean
            If the read failed
        """

        # Connect to the SQL database
        try:
            with pyodbc.connect(
                    'Driver={SQL Server};'
                    'Server=%s;'
                    'Database=%s;'
                    'Trusted_Connection=yes;'
                    % (self.server, self.db)) as self.conn:
                self.cursor = self.conn.cursor()

                # Send the SQL command to the server and execute
                try:
                    self.cursor.execute(
                        f"SELECT TOP 1 * \
                        FROM [NetworkAssistant_Alerts].[dbo].[{table}] \
                        ORDER BY id DESC"
                    )
                    for row in self.cursor:
                        entry = row

                # If there was a problem reading
                except Exception as err:
                    print(termcolor.colored(
                        f"SQL read error: {err}",
                        "red"
                    ))

                    teamschat.send_chat(
                        "An error has occurred while reading from the\
                            SQL database",
                        GRAPH['chat_id']
                    )

                    return False

        # If there was a problem connecting to the server
        except Exception as err:
            print(termcolor.colored(
                f"Error {err} connecting to the SQL database",
                "red"
            ))

            teamschat.send_chat(
                "Could not connect to the SQL server",
                GRAPH['chat_id']
            )

            return False

        # If it all worked, return the entry
        return entry

    # Read entries between date/times
    def read_since(self, table, start_date, start_time, end_date, end_time):
        """Read entries between particular date/times

        Parameters
        ----------
        table : str
            The database table to write to
        start_date : datetime
            The starting date
        start_time : datetime
            The starting time
        end_date : datetime
            The ending date
        end_time : datetime
            The ending time

        Raises
        ------
        Exception
            If there were errors connecting to the server
        Exception
            If there were errors reading

        Returns
        -------
        entry : list
            A list of entries retrieved from the SQL server
        False : boolean
            If the read failed
        """

        # A list of entries
        entry = []

        # Connect to db
        try:
            with pyodbc.connect(
                    'Driver={SQL Server};'
                    'Server=%s;'
                    'Database=%s;'
                    'Trusted_Connection=yes;'
                    % (self.server, self.db)) as self.conn:
                self.cursor = self.conn.cursor()

                # Send the SQL command
                try:
                    self.cursor.execute(
                        f"SELECT * \
                        FROM [NetworkAssistant_Alerts].[dbo].[{table}] \
                        WHERE \
                        (logdate = '{start_date}' \
                            AND logtime between '{start_time}' \
                            AND '23:59:59') OR \
                        (logdate = '{end_date}' \
                            AND logtime between '00:00:00' \
                            AND '{end_time}') OR \
                        (logdate between '{start_date}' AND '{end_date}') AND \
                        (message NOT LIKE '' AND message NOT LIKE '0')"
                    )

                    # Add the results to the list to return
                    for row in self.cursor:
                        entry.append(row)

                # If there was a problem reading
                except Exception as err:
                    print(termcolor.colored(
                        f"SQL read error: {err}",
                        "red"
                    ))

                    teamschat.send_chat(
                        "An error has occurred while reading from the\
                            SQL database",
                        GRAPH['chat_id']
                    )

                    return False

        # If there was a problem connecting to the DB
        except Exception as err:
            print(termcolor.colored(
                f"Error {err} connecting to the SQL database",
                "red"
            ))

            teamschat.send_chat(
                "Could not connect to the SQL server",
                GRAPH['chat_id']
            )

            return False

        # If all worked, return the entries
        return entry
