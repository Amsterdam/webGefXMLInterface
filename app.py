from flask import Flask, flash, request, redirect
from io import BytesIO
import matplotlib.pyplot as plt
import base64

from geotexxx import gefxml_reader

ALLOWED_EXTENSIONS = {'gef', 'xml'}

app = Flask(__name__)

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
            f = file.read().decode()
            if file.filename.lower().endswith('xml'):
                testType = gefxml_reader.Test().type_from_xml(f, fromFile=False)
                if testType == 'cpt':
                    test = gefxml_reader.Cpt()
                    test.load_xml(f, checkAddDepth=True, checkAddFrictionRatio=True, fromFile=False)
                elif testType == 'bore':
                    test = gefxml_reader.Bore()
                    test.load_xml(f, fromFile=False)
                pdfName = file.filename.lower().replace('.xml', '.pdf')
                pngName = file.filename.lower().replace('.xml', '.png')
                dataName = file.filename.lower().replace('.xml', '.csv')

            elif file.filename.lower().endswith('gef'):
                testType = gefxml_reader.Test().type_from_gef(f, fromFile=False)
                if testType == 'cpt':
                    test = gefxml_reader.Cpt()
                    test.load_gef(f, checkAddDepth=True, checkAddFrictionRatio=True, fromFile=False)
                elif testType == 'bore':
                    test = gefxml_reader.Bore()
                    test.load_gef(f, fromFile=False)
                pdfName = file.filename.lower().replace('.gef', '.pdf') 
                pngName = file.filename.lower().replace('.gef', '.png')
                dataName = file.filename.lower().replace('.gef', '.csv')

            fig = test.plot(saveFig=False)

            pdfBytes = BytesIO()
            plt.savefig(pdfBytes, format='pdf')
            pdfBytes.seek(0)
            pdf_url = base64.b64encode(pdfBytes.getvalue()).decode()

            img = BytesIO()
            plt.savefig(img, format='png')
            img.seek(0)
            png_url = base64.b64encode(img.getvalue()).decode()
            
            dataOut = BytesIO()

            if testType == 'cpt':
                test.data.to_csv(dataOut, sep=';')
            elif testType == 'bore':
                test.soillayers['veld'].to_csv(dataOut, sep=';')
            
            data_url = base64.b64encode(dataOut.getvalue()).decode()

            return f'''
            <a href=data:object/pdf;base64,{pdf_url} download="{pdfName}"><button>Download pdf</button></a>
            <a href=data:image/png;base64,{png_url} download="{pngName}"><button>Download png</button></a>
            <a href=data:object/csv;base64,{data_url} download="{dataName}"><button>Download data</button></a>
            <img src="data:image/png;base64,{png_url}">
            '''

    return '''
    <!doctype html>
    <title>Plot sonderingen</title>
    <h1>Upload een gef of xml van een sondering</h1>
    <p>Daarna kan je deze als pdf en png downloaden<p>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file>
      <input type=submit value=Upload>
    </form>
    '''


if __name__ == '__main__':
   app.run()