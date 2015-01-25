import os
import math
from flask import Flask, render_template, request, redirect, send_from_directory, url_for
from werkzeug import secure_filename

UPLOAD_DIRECTORY = 'upload'
AJAX_FILEPATH = 'ajax_progress.txt'

app = Flask(__name__)


def prepare_directory(dirname):
    if not os.path.isdir(dirname):
        os.makedirs(dirname)


def write_ajax_info(uploaded_filepath, info):
    with open(AJAX_FILEPATH, 'w') as ajax_progress_file:
        ajax_progress_file.write("{0}/n{1}".format(uploaded_filepath, info))


def get_file_size(file):
    file.seek(os.SEEK_SET, os.SEEK_END)
    size = file.tell()
    file.seek(os.SEEK_SET)
    return float(size)


def proceed_file_uploading(file_stream, uploaded_filepath):
    size = get_file_size(file_stream)
    chunk = 1000
    n = int(math.ceil(size/chunk))
    for _ in xrange(n):
        with open(uploaded_filepath, 'a') as file_result:
            file_result.write(file_stream.read(chunk))
        current_status = int((file_stream.tell()/size)*100)
        write_ajax_info(uploaded_filepath, current_status)


@app.route('/', methods=['GET'])
def show_form():
    return render_template('form_template.html')


@app.route('/', methods=['POST'])
def get_file():
    write_ajax_info('', 0)
    file_stream = request.files["upload"]
    file_name = secure_filename(request.files["upload"].filename)
    uploaded_filepath = os.path.join(UPLOAD_DIRECTORY, file_name)
    proceed_file_uploading(file_stream, uploaded_filepath)
    return redirect("/")


@app.route('/progress', methods=['GET'])
def get_progress():
    with open(AJAX_FILEPATH, 'r') as ajax_progress_file:
        return ajax_progress_file.read()


@app.route('/upload/<path:filename>')
def download_file(filename):
    return send_from_directory(UPLOAD_DIRECTORY,
                               filename, as_attachment=True)


if __name__ == '__main__':
    prepare_directory(UPLOAD_DIRECTORY)
    app.run(threaded=True)
