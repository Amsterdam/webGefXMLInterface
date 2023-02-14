from flask import Flask, flash, request, redirect, url_for
from io import StringIO, BytesIO
import matplotlib.pyplot as plt
import base64

from gefxml_reader import Cpt

UPLOAD_FOLDER = '/path/to/the/uploads'
ALLOWED_EXTENSIONS = {'gef', 'xml'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            cpt = Cpt()
            if file.filename.lower().endswith('xml'):
                cpt.load_xml(file.read().decode(), checkAddDepth=True, checkAddFrictionRatio=True, file=False)
            elif file.filename.lower().endswith('gef'):
                cpt.load_gef(file.read().decode(), checkAddDepth=True, checkAddFrictionRatio=True, fromFile=False)
            
            fig = cpt.plot(returnFig=True)
            fn = file.filename.replace('.xml', '.png')
            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            plot_url = base64.b64encode(img.getvalue()).decode()
            
            return '<img src="data:image/png;base64,{}">'.format(plot_url)

    return '''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
   app.run()