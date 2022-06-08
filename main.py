from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
import requests

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
    kode_saham = db.Column(db.String(4), db.ForeignKey('saham.kode'), nullable=False)

    def __repr__(self):
        return '<Berita %r>' % self.judul
db.create_all()


@app.route('/')
def index():
    all_saham = Saham.query.all()
    return render_template('index.html', saham=all_saham)

@app.route('/saham/')
@app.route('/saham/<kode_saham>')
def saham(kode_saham):
    saham_relevan = Saham.query.filter_by(kode=kode_saham).one()
    berita_relevan = Berita.query.filter_by(kode_saham=kode_saham).order_by(Berita.tanggal_publish.desc()).limit(5)
    return render_template('saham.html', berita_rel=berita_relevan, saham_rel=saham_relevan)

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

if __name__ == '__main__':
    app.run(debug=True)