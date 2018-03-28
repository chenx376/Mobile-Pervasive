import os
from flask import Flask, request

app = Flask(__name__, static_url_path='')
UPLOAD_FOLDER = '/Users/jinwang/Desktop/receive'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


@app.route('/upload', methods=['POST'])
def upload_file():
    sensor_id = request.form['id']
    upload = request.files['file']
    filename = upload.filename
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], sensor_id, filename)
    upload.save(filepath)
    return ''


@app.route('/test', methods=['GET'])
def test():
    return 'success'

if __name__ == '__main__':
    app.run(threaded=True, debug=True, host='0.0.0.0', port=5000)
