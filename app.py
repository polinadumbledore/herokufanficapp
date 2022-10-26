from flask import Flask, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.form['message']
        return render_template('result.html')
        
@app.route('/')

def index():
    return render_template('index.html')

@app.route('/tags')
def tags():
    return render_template('tags.html')


@app.route('/rules')
def rules():
    return render_template('rules.html')

if __name__ == "__main__":
    app.run(debug=True)
