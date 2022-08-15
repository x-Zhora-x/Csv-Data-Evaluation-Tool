from contextlib import redirect_stderr
from flask import Flask, render_template, redirect
import pandas as pd
import json
from flask import Flask, render_template, request, session
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import pandas_highcharts
import matplotlib.pyplot as plt
import os
from werkzeug.utils import secure_filename
import seaborn as sns
import numpy as np 

 
# Define folder to save uploaded files to process further
UPLOAD_FOLDER = os.path.join('staticFiles', 'uploads')
 
# Define allowed files (for this example I want only csv file)
ALLOWED_EXTENSIONS = {'csv'}
 
app = Flask(__name__, static_folder='staticFiles')# Configure upload file path flask
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
 
# Define secret key to enable session
app.secret_key = 'This is your secret key to utilize session in Flask'
 
 
@app.route('/')
def index():
    return render_template('index_upload_and_show_data.html')
 
@app.route('/',  methods=("POST", "GET"))
def uploadFile():
    if request.method == 'POST':
        # upload file flask
        uploaded_df = request.files['uploaded-file']
 
        # Extracting uploaded data file name
        data_filename = secure_filename(uploaded_df.filename)
 
        # flask upload file to database (defined uploaded folder in static path)
        try:
            uploaded_df.save(os.path.join(app.config['UPLOAD_FOLDER'], data_filename))
        except:
            return redirect("/")
        # Storing uploaded file path in flask session
        session['uploaded_data_file_path'] = os.path.join(app.config['UPLOAD_FOLDER'], data_filename)
        
        data_file_path = session.get('uploaded_data_file_path', None)
        df = pd.read_csv(data_file_path)   
        if len(df) < 300:
            sample = df.sample(n = len(df)).to_html(index=False)
        else:
            sample = df.sample(n = 300).to_html(index=False)
        return render_template('index_upload_and_show_data_page2.html', theSample = sample,numCol = len(df.columns), numRow=len(df))
 
@app.route('/show_data')
def showData():
    
    # Retrieving uploaded file path from session
    data_file_path = session.get('uploaded_data_file_path', None)
    
    # read csv file in python flask (reading uploaded csv file from uploaded server location)
    try:
        df = pd.read_csv(data_file_path)
    except:
        return redirect("/")
    #Description
    data = {
        'Data Type': df.dtypes.astype(str).replace(to_replace = "object", value = "String"),
        'Number Of Null Values': [i for i in df.isna().sum()],        
        'Unique Values':[len(i) for i in [df[i].value_counts() for i in df]],

    }
    df2 = pd.DataFrame(data)
    ax_box = None
    for i in df:
        if df[i].dtype == "float64" or df[i].dtype == "int64":
            sns.set(style="darkgrid")
            f, (ax_box, ax_hist) = plt.subplots(2, sharex=True, gridspec_kw={"height_ratios": (.15, .85)})
            sns.boxplot(x=df[i], ax=ax_box)
            sns.histplot(x=df[i], bins=12, kde=True,  ax=ax_hist)

            ax_box.set(yticks=[])
            sns.despine(ax=ax_hist)
            sns.despine(ax=ax_box, left=True)
            plt.axvline(df[i].mean(), color='k', linestyle='dashed', linewidth=1)
            plt.savefig('staticFiles/images/' + i + '.png')
        '''    
        elif len(df[i].value_counts()) < 12:
            sns.set(style="darkgrid")
            plt.clf()
            df[i].value_counts().plot(kind = "barh")
            plt.savefig('staticFiles/images/' + i + '.png')
            '''
    tempDf = df.select_dtypes(include=np.number)

    try:
        listOfTables = [pd.DataFrame(tempDf.describe()[i]).transpose().to_html(index=False, table_id = "minis") for i in tempDf.describe()]
    except:
        listOfTables = []
    # pandas dataframe to html table flask
    uploaded_df_html = df2.to_html(table_id = "hello")
    strCols = df.select_dtypes(include=['object'])
    listStrs = [strCols[i].value_counts() for i in strCols if len(strCols[i].value_counts().to_dict())< 12]
    listVals = [i.to_list() for i in listStrs]
    listInds = [i.index.to_list() for i in listStrs]    


    return render_template('show_csv_data.html', data_var = uploaded_df_html, listOfTables = listOfTables, listVals = listVals, listInds = listInds)
 
if __name__=='__main__':
    app.run(debug = True)
