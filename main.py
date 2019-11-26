"""
Report Generator
Author: Lena Zhao
Date: Nov 19, 2019
TO DO:
This application read a csv file...
"""
import pandas as pd
import sqlite3
from DatabaseManager import DatabaseManager
from app import app
from flask import Flask, flash, request, redirect, render_template, url_for
import os

__author__ = 'Lena Zhao'

# database name
sqlite_name = 'payroll_db.sqlite'

# application root path
APP_ROOT = os.path.dirname(os.path.abspath(__file__))

# file extensions allowed
ALLOWED_EXTENSIONS = set(['csv'])


# check if input file name is the allowed file type
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


'''
Main web page for upload files
'''
@app.route("/")
def index():
    return render_template('upload.html')


'''
Upload files from user and save them to input_files folder
'''
@app.route("/upload", methods=['POST'])
def upload():
    target = os.path.join(APP_ROOT, 'input_files/')
    print(target)

    # check if input file direction exists, if not create one
    if not os.path.isdir(target):
        os.mkdir(target)

    files = []
    print(request.files.getlist("input-files"))
    for file in request.files.getlist("input-files"):
        # print('file: ', file)
        filename = file.filename
        files.append(filename)
        destination = "/".join([target, filename])
        # print("Destination: ", destination)
        if file and allowed_file(filename):
            file.save(destination)
        else:
            flash(u'ERROR: Invalid file type. Please provide file type: csv', 'error')
            return redirect(url_for('index'))

    # print('files:', files)
    # read and save input files to database
    if save_input_files(files, sqlite_name):
        flash('Input files successfully saved to database')
    else:
        flash(u"ERROR: Cannot upload file with the same 'report id'", 'error')
        return redirect(url_for('index'))

    return render_template("complete.html")


'''
Display the Payroll Report
'''
@app.route('/report')
def report():
    # generates the output report
    rows = generate_output_report(sqlite_name)
    print(type(rows))
    # render in the UI
    return render_template('report.html', len=len(rows), title='Payroll Report', rows=rows)


'''
Main Function
'''
def main() -> None:

    # setup db
    db_setup(sqlite_name)
    print("------ Finish Database Setup -------")

    app.run(debug=True)


def save_input_files(file_names: list, db_name: str) -> bool:
    # fixed header names from csv file
    column_names = ['date', 'hours worked', 'employee id', 'job group']

    # get all the previous uploaded report ids
    report_ids = get_report_id_from_db(db_name)

    try:
        # read input files
        for file in file_names:

            # read csv files
            input_df = read_input_file(file, column_names)

            # get and remove report id from df
            report_number = get_report_id(input_df)
            # drop last row (report id)
            input_df = input_df.head(-1)

            # set column types for the df
            set_df_column_type(input_df, column_names)

            # check for unique report id, if report id exists, print error message and exit
            if report_number in report_ids:
                return False;
                # raise ValueError("--- ERROR: Cannot upload file with the same 'report id'---")
                # exit main()
                # sys.exit(0)
            else:
                report_ids.append(report_number)

            # add input report to db
            save_input_report(input_df, db_name)

        # add report id to db
        save_report_id(db_name, report_ids)
        return True

    except ValueError as e:
        print("main() Error: %s" % e.args[0])


def db_setup(db_name: str) -> None:
    try:
        # access db
        with DatabaseManager(db_name) as db:
            # create a table for input files archives
            db.execute("""CREATE TABLE IF NOT EXISTS input_reports(
                        pk INTEGER NOT NULL PRIMARY KEY,
                        date TEXT, 
                        hours_worked REAL, 
                        employee_id INTEGER, 
                        job_group TEXT)""")

            # create a table for storing unique report ids
            db.execute("""CREATE TABLE IF NOT EXISTS report_ids(
                       id INTEGER,
                       PRIMARY KEY (id))""")

            # create a table for job groups
            db.execute("""CREATE TABLE IF NOT EXISTS job_group(
                       job_group TEXT,
                       rate REAL,
                       PRIMARY KEY (job_group))""")

            # insert data for job group table
            db.execute("""INSERT OR IGNORE INTO job_group VALUES('A', 20), ('B', 30)""")

    except sqlite3.Error as e:
        print("db_setup Error: %s" % e.args[0])
        db.__exit__()


def read_input_file(csv: str, col_names: list) -> pd.DataFrame:
    input_df = pd.read_csv(csv, header=0, names=col_names)
    return input_df


def get_report_id(df: pd.DataFrame) -> int:
    report_num = df.iloc[-1]['hours worked'].astype(int)

    # return a int type instead of numpy.int32
    return report_num.item()


def get_report_id_from_db(db_name: str) -> list:
    with DatabaseManager(db_name) as db:
        db.execute("SELECT * FROM report_ids")
        tup = db.fetchall()
        # convert tuples to a list
        result = list(sum(tup, ()))
        return result


def save_report_id(db_name: str, id_list: list) -> None:
    with DatabaseManager(db_name) as db:
        # insert data for job group table
        for item in id_list:
            db.execute("INSERT OR IGNORE INTO report_ids VALUES(?)", (item,))


def set_df_column_type(df: pd.DataFrame, names: list) -> None:
    df[names[0]] = pd.to_datetime(df[names[0]], format='%d/%m/%Y')
    # assume hours worked is always positive
    df['hours worked'] = pd.to_numeric(df['hours worked'], downcast='unsigned')
    df['employee id'] = df['employee id'].astype(int)
    df['job group'] = df['job group'].astype(str)

    # rename df columns
    df.rename(columns={'hours worked': 'hours_worked', 'employee id': 'employee_id',
                       'job group': 'job_group'}, inplace=True)


def save_input_report(df: pd.DataFrame, db: str) -> None:
    # set an index for the df
    df.set_index(['date', 'employee_id', 'job_group'])

    try:
        # save input file to db
        df.to_sql(name='input_reports', con=sqlite3.connect(db), if_exists='append', index=True, index_label='pk')
    except sqlite3.Error as e:
        print("Saving to database error: %s" % e.args[0])


def generate_output_report(db: str) -> list:
    try:
        with DatabaseManager(db) as db:
            db.execute("""
                    SELECT employee_id, pay_period, amount_paid
                    FROM (
                        SELECT r.employee_id , SUM(r.amount_paid) as amount_paid,
                            CASE
                                WHEN strftime('%d',r.date) < '16' 
                                THEN strftime('%m-%Y', Date(r.date,'start of month')) || ' - ' 
                                     || strftime('%m-%Y', Date(r.date,'start of month','+14 day'))
                                ELSE strftime('%m-%Y', Date(r.date,'start of month','+15 day')) || ' - ' 
                                     || strftime('%m-%Y', Date(r.date,'start of month','+1 month','-1 day'))
                            END month_year_key,
                            CASE
                                WHEN strftime('%d',r.date) < '16' 
                                THEN strftime('%d/%m/%Y', Date(r.date,'start of month')) || ' - ' 
                                     || strftime('%d/%m/%Y', Date(r.date,'start of month','+14 day'))
                                ELSE strftime('%d/%m/%Y', Date(r.date,'start of month','+15 day')) || ' - ' 
                                     || strftime('%d/%m/%Y', Date(r.date,'start of month','+1 month','-1 day'))
                            END pay_period
                            FROM (
                                SELECT i.date, i.employee_id, i.hours_worked*j.rate AS amount_paid 
                                FROM input_reports i
                                JOIN job_group j 
                                ON i.job_group = j.job_group 
                                ORDER BY i.employee_id, i.date ASC) r
                            GROUP BY pay_period, employee_id
                            ORDER BY employee_id, month_year_key, pay_period ASC)"""
                       )

            output_report = db.fetchall()

        return output_report

    except sqlite3.Error as e:
        print("db_setup Error: %s" % e.args[0])
        db.__exit__()


if __name__ == '__main__':
    main()
