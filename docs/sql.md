# SQL Database
Events are written to a database as they are received 
This is intended to be queried by a future module to find patterns, etc 
Currently tested with MSSQL only

&nbsp;<br>
## DB design
This can vary per plugin, but most will follow a design similar to this

Table Fields
------------

Event ID (primary key)  
* A unique ID to associate with each event  
* Type: char(12)  
* Allow null: no  

Device  
* The name of the device, if applicable, that generated the event  
* Type: text  
* Allow null: yes  

Site  
* The name of the site, if applicable, that the event was raised in  
* Type: text  
* Allow null: yes  

Event  
* The event itself, eg 'SW_CONNECTED'  
* Type: text  
* Allow null: no  

Description  
* A more detailed description of what happened (not all events will have these)  
* Type: text  
* Allow null: yes  

LogDate  
* The date of the event  
* Type: date  
* Allow null: no  

LogTime  
* The time of the event  
* Type: time  
* Allow null: no  

Source IP (only supports v4 for now)  
* The IP address that sent the alert  
* Type: binary(4)  
* Allow null: no  

Chat message ID  
* The ID, as set by the Graph API of the message sent to teams (not all will have a message sent)  
* Type: text  
* Allow null: yes  


&nbsp;<br>
- - - -
## sql.py
  Contains the Sql class, for writing events to the database.
  The methods are outlined below

&nbsp;<br>
### __init__()
  Gets the server name and DB name from the config file

### add()
Arguments:  
* table: The table to write to  
* fields: The entries to write  
Returns:  True if successful, False if not
Purpose:  
  Connect to the SQL server/database  
  Write entries to the database
  Gracefully close the connection
  
### read_last()
Arguments:
* table: The table to read from
Returns: The entry that has been read from the table
Purpose:
  Connects to the SQL datanase
  Reads the last entry in the table

### read_since()
Arguments:
* table: The table to read from
* start_date: The starting date to read entries from
* start_time: The starting time (within the start date)
* end_date: The ending date to read entries to
* end_time: The ending time (within the end date)
Returns: A list of entries that have been retrieved from the database
Purpose:
  Connects to the SQL datanase
  Retrieves all entries between the start and end times



