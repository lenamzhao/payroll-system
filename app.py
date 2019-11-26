import os
from flask import Flask, flash, request, redirect, render_template

__author__ = 'Lena Zhao'


app = Flask(__name__)


app.secret_key = "secret_key"


# database name
# sqlite_name = 'payroll_db.sqlite'

# # check if input file name is the allowed file type
# def allowed_file(filename):
#     return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# @app.route("/")
# def index():
#     return render_template('upload.html')
#
#
# @app.route("/upload", methods=['POST'])
# def upload():
#     target = os.path.join(APP_ROOT, 'input_files/')
#     print(target)
#
#     # check if input file direction exists, if not create one
#     if not os.path.isdir(target):
#         os.mkdir(target)
#
#     for file in request.files.getlist("input-files"):
#         # print('file: ', file)
#         filename = file.filename
#         destination = "/".join([target, filename])
#         # print("Destination: ", destination)
#         if file and allowed_file(filename):
#             file.save(destination)
#             flash('File successfully uploaded!')
#             return render_template("complete.html")
#         else:
#             flash('Allowed file types is: csv')
#             return redirect(request.url)
#
#     return render_template("report.html")