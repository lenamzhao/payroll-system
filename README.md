# wave-challenge

#### Pre-requisites:
- python 3
- read and write permission on the application folder: 'wave-challenge'

To check your python 3 version:

`python3 --version`

### To run web application:

If you are in python terminal, run the following command:

`./main.py`

If you are in any command terminal, run the following command: 

`python main.py`

Once the server is up and running, go to `http://127.0.0.1:5000/`


## Description

This web application built with `Python` as back-end, `Flask` as front-end and `Sqlite3`as a local relational 
database. Pandas dataframe is used to read input csv save to database. I created a `DatabaseManager` class manage all 
database related tasks. I chose to let most of the data processing and manipulation handled by the database since 
this time series data could potentially grow to be a very large. This will optimize the performance since database queries 
are much faster than dataframe performance. I've also included a 'upload complete' page to let the user know that files 
were uploaded successfully without any issues/errors. It also give the user the ability to go back to the upload page 
if they wish to do so. I've added some simple styling to give a better user experience which allows the users to read 
the data easily.
