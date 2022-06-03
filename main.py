from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/saham')
def saham():
    return render_template('saham.html')

@app.route('/berita')
def berita():
    return render_template('berita.html')

if __name__ == '__main__':
    app.run(debug=True)