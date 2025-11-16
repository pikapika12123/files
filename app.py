from flask import Flask, render_template, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__, template_folder='.', static_folder='.')
app.secret_key = ''
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # you can change this ig

os.makedirs("uploads", exist_ok=True)

def format_size(size):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"

def get_file_info(filename):
    filepath = os.path.join("uploads", filename)
    if os.path.isfile(filepath):
        stat = os.stat(filepath)
        return {
            'name': filename,
            'size': format_size(stat.st_size),
            'date': datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
        }
    return None

@app.route('/')
def index():
    files = []
    for filename in os.listdir("uploads"):
        file_info = get_file_info(filename)
        if file_info:
            files.append(file_info)
    files.sort(key=lambda x: x['date'], reverse=True)
    return render_template('index.html', files=files)

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        flash('no file selected')
        return redirect(url_for('index'))
    
    file = request.files['file']
    
    if file.filename == '':
        flash('no file selected')
        return redirect(url_for('index'))
    
    if file:
        filename = secure_filename(file.filename)
        file.save(os.path.join("uploads", filename))
        flash(f'file "{filename}" uploaded successfully')
        return redirect(url_for('index'))

@app.route('/download/<filename>')
def download(filename):
    filepath = os.path.join("uploads", filename)
    if os.path.exists(filepath):
        return send_file(filepath, as_attachment=True)
    flash('File not found')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)