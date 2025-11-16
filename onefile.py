# flask and HTML in one file

from flask import Flask, request, send_file, redirect, url_for, flash
import os
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
app.secret_key = ''
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # you can change this ig

os.makedirs("uploads", exist_ok=True)

# HTML Template
HTML_TEMPLATE = '''<!DOCTYPE html>
<html>
<head>
    <title>files 1.0</title>
</head>
<body>
    <h1>files 1.0</h1>
    
    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <p>{{ message }}</p>
            {% endfor %}
        {% endif %}
    {% endwith %}
    
    <h2>upload</h2>
    <form method="POST" action="/upload" enctype="multipart/form-data">
        <input type="file" name="file" required>
        <input type="submit" value="Upload">
    </form>
    
    <h2>uploaded files</h2>
    {% if files %}
        <table border="1">
            <tr>
                <th>filename</th>
                <th>size</th>
                <th>date</th>
                <th>download</th>
            </tr>
            {% for file in files %}
            <tr>
                <td>{{ file.name }}</td>
                <td>{{ file.size }}</td>
                <td>{{ file.date }}</td>
                <td>
                    <form method="GET" action="/download/{{ file.name }}" style="display: inline;">
                        <button type="submit">Download</button>
                    </form>
                </td>
            </tr>
            {% endfor %}
        </table>
    {% else %}
        <p>no files :( you should never see this, dm @pikapika12312 on disc ill fix it</p>
    {% endif %}
</body>
</html>'''

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
    from flask import render_template_string
    files = []
    for filename in os.listdir("uploads"):
        file_info = get_file_info(filename)
        if file_info:
            files.append(file_info)
    files.sort(key=lambda x: x['date'], reverse=True)
    return render_template_string(HTML_TEMPLATE, files=files)

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
    safe_filename = secure_filename(filename)
    
    if not safe_filename:
        flash('Invalid filename')
        return redirect(url_for('index'))
    
    filepath = os.path.join("uploads", safe_filename)
    
    uploads_dir = os.path.abspath("uploads")
    resolved_path = os.path.abspath(filepath)
    
    if not resolved_path.startswith(uploads_dir + os.sep):
        flash('Access denied')
        return redirect(url_for('index'))
    
    if os.path.exists(resolved_path):
        return send_file(resolved_path, as_attachment=True)
    
    flash('File not found')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=False)