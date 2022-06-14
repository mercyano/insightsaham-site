from flask import Flask, redirect, request, render_template
from flask_sqlalchemy import SQLAlchemy
import pandas as pd
import pandas_datareader as web
import numpy as np
import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from tensorflow import keras
import io
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

app = Flask(__name__)

# CREATE DATABASE
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///insightsaham.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# CREATE TABLE
class Saham(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(250), unique=True, nullable=False)
    kode = db.Column(db.String(4), unique=True, nullable=False)
    profil = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return '<Saham %r>' % self.kode


db.create_all()


class Berita(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(250), unique=True, nullable=False)
    link_url = db.Column(db.String(2048), unique=True, nullable=False)
    sumber = db.Column(db.String(250), nullable=False)
    tanggal_publish = db.Column(db.Date, nullable=False)
    teras = db.Column(db.String(500), nullable=False)
    kode_saham = db.Column(db.String(4), db.ForeignKey(
        'saham.kode'), nullable=False)

    def __repr__(self):
        return '<Berita %r>' % self.judul


db.create_all()


@app.route('/')
def index():
    all_saham = Saham.query.all()
    rand_saham = Saham.query.order_by(db.func.random()).first()
    return render_template('index.html', saham=all_saham, rand_saham=rand_saham)


@app.route('/saham/')
@app.route('/saham/<kode_saham>', methods=['GET'])
def saham(kode_saham):
    saham_relevan = Saham.query.filter_by(kode=kode_saham).one()
    berita_relevan = Berita.query.filter_by(kode_saham=kode_saham).order_by(
        Berita.tanggal_publish.desc()).limit(5)
    rand_saham = Saham.query.order_by(db.func.random()).first()

    today = datetime.datetime.now().strftime('%d-%m-%Y')
    df = web.DataReader(
        kode_saham+".JK", data_source='yahoo', start='01-01-2022', end=today)
    df = df.filter(['Close'])
    df = df.reset_index(drop=False)
    scaler = joblib.load("model-development\Stock.pkl")
    best_model = keras.models.load_model('model-development\model.h5')
    
    y_test = scaler.transform(df[['Close']])
    n_future = 2*7
    future = [[y_test[-1, 0]]]
    X_new = y_test[-1:, 0].tolist()

    for i in range(n_future):
        y_future = best_model.predict(np.array([X_new]).reshape(1, 1, 1))
        future.append([y_future[0, 0]])
        X_new = X_new[1:]
        X_new.append(y_future[0, 0])

    future = scaler.inverse_transform(np.array(future))
    date_future = pd.date_range(
        start = df['Date'].values[-1], periods=n_future+1, freq='D')
    # Plot Data sebulan terakhir dan seminggu ke depan
    fig = plt.figure(figsize=(15, 8))
    sns.lineplot(
        data=df[-1*30:], x='Date', y='Close', label='data sebelumnya')
    sns.lineplot(x=date_future, y=future[:, 0], label='future')
    plt.ylabel('Close')
    
    pngImage = io.BytesIO()
    FigureCanvas(fig).print_png(pngImage)
    
    # Encode PNG image to base64 string
    pngImageB64String = "data:image/png;base64,"
    pngImageB64String += base64.b64encode(pngImage.getvalue()).decode('utf8')


    return render_template('saham.html', berita_rel=berita_relevan, saham_rel=saham_relevan, rand_saham=rand_saham, image_prediction=pngImageB64String)


@app.route('/berita')
def berita():
    all_berita = Berita.query.order_by(Berita.tanggal_publish.desc()).all()
    return render_template('berita.html', berita=all_berita)


@app.route('/tentang')
def tentang():
    return render_template('tentang.html')


@app.route('/peringatan-resiko')
def peringatan_resiko():
    return render_template('peringatan_resiko.html')


@app.route("/cari", methods=['POST'])
def cari():
    kode_saham = request.form['cari']
    return redirect('/saham/' + kode_saham)


if __name__ == '__main__':
    app.run(debug=True)
