# https://stackoverflow.com/questions/72442371/deploying-streamlit-app-in-azure-without-using-docker
# let op! werkt niet met Python 3.9.7

import streamlit as st
from io import StringIO, BytesIO
import matplotlib.pyplot as plt

st.title('Visualiseer geotechnisch grondonderzoek')

from gefxml_reader import Cpt
uploaded_file = st.file_uploader("Choose a file")

if uploaded_file is not None:
    # To read file as bytes:
    bytes_data = uploaded_file.getvalue()

    # To convert to a string based IO:
    stringio = StringIO(uploaded_file.getvalue().decode("utf-8"))

    # To read file as string:
    string_data = stringio.read()

    cpt = Cpt()
    if uploaded_file.name.lower().endswith('xml'):
        cpt.load_xml(string_data, checkAddDepth=True, checkAddFrictionRatio=True, file=False)
    elif uploaded_file.name.lower().endswith('gef'):
        cpt.load_gef(string_data, checkAddDepth=True, checkAddFrictionRatio=True, fromFile=False)

    fig = cpt.plot(returnFig=True)

    fn = uploaded_file.name.replace('.xml', '.png')
    img = BytesIO()
    plt.savefig(img, format='png')
    
    btn = st.download_button(
    label="Download image",
    data=img,
    file_name=fn,
    mime="image/png"
    )



    st.pyplot(fig)
