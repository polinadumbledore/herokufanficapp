from flask import Flask, render_template, url_for, request
from flask_sqlalchemy import SQLAlchemy
import json
import spacy
import pandas as pd
import sys

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id

def to_str(df):
  a = list(df)
  return a[0]

def find_ids(s, st):
  i = 0
  j = 0
  while i < len(st):
    while s[i] == st[j]:
      j += 1
      i += 1
      if j == len(st):
        return [i - len(st), i - 1]
    else:
      j = 0
      i += 1

def parse_inquiry(q):
  q = q.split(' ')
  new_q = []
  for i in q:
    new_q.append(i.split('+'))
  return new_q

def lemmatize(w):
  nlp = spacy.load("ru_core_news_sm")
  doc = nlp(w)
  for t in doc:
    return t.lemma_


def search(q, tokens):
    pos_tags = ['ADJ', 'ADP', 'ADV', 'AUX', 'CCONJ', 'DET', 'INTJ', 'NOUN', 'NUM', 'PART', 'PRON', 'PROPN', 'PUNCT',
                'SCONJ', 'SYM', 'VERB']

    k = len(q)
    for j in range(k):
        if not q[j][0].startswith('"') and q[j][0].upper() not in pos_tags:
            q[j][0] = lemmatize(q[j][0].lower())
    sss = []
    ids = []
    for i in range(len(tokens) - k + 1):
        # if tokens[i]['id_sent'] == tokens[i + min(1, k)]['id_sent'] and tokens[i + min(1, k)]['id_sent'] == tokens[i + min(k, min(2, k))]['id_sent']:
        sents = []
        s_searched = ''
        for j in range(k):

            if q[j][0].startswith('"'):
                s = q[j][0][1:(len(q[j][0]) - 1)].lower()
                if tokens[i + j]['token'].lower() == s:
                    if len(q[j]) == 2 and q[j][len(q[j]) - 1].upper() == tokens[i + j]['POS']:
                        sents.append([tokens[i + j]['id_ff'], tokens[i + j]['id_sent']])
                        s_searched += tokens[i + j]['token'] + ' '
                    elif len(q[j]) == 1:
                        sents.append([tokens[i + j]['id_ff'], tokens[i + j]['id_sent']])
                        s_searched += tokens[i + j]['token'] + ' '

            else:
                if len(q[j]) == 1:
                    if q[j][0].upper() == tokens[i + j]['POS']:
                        sents.append([tokens[i + j]['id_ff'], tokens[i + j]['id_sent']])
                        s_searched += tokens[i + j]['token'] + ' '
                    elif q[j][0].upper() not in pos_tags:
                        s = q[j][0]
                        if tokens[i + j]['lemma'].lower() == s:
                            sents.append([tokens[i + j]['id_ff'], tokens[i + j]['id_sent']])
                            s_searched += tokens[i + j]['token'] + ' '
                else:
                    s = q[j][0].lower()
                    if tokens[i + j]['lemma'].lower() == s and q[j][1].upper() == tokens[i + j]['POS']:
                        sents.append([tokens[i + j]['id_ff'], tokens[i + j]['id_sent']])
                        s_searched += tokens[i + j]['token'] + ' '

        plus = 0
        if len(sents) != 0:
            for m in range(len(sents) - 1):
                if sents[m] == sents[m + 1]:
                    plus += 1
            if plus == len(q) - 1:
                ids.append(sents[0])
                sss.append(s_searched[:(len(s_searched) - 1)])

    return ids, sss


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        data = request.form['message']
        with open('tokens.json', 'r', encoding='utf-8') as f:
            tokens = json.load(f)
        with open('sentences.json', 'r', encoding='utf-8') as sent:
            sentences = json.load(sent)
        with open('texts.json', 'r', encoding='utf-8') as tf:
            texts = json.load(tf)
        ffs = pd.read_csv('ffs.tsv', delimiter="\t")

        ans_ids, s = search(parse_inquiry(data), tokens)
        res = []
        for i in range(len(ans_ids)):
            id = ans_ids[i]
            dds = ffs[ffs['id_ff'] == id[0]]
            st = sentences[int(id[0])][int(id[1])]
            aaa = find_ids(st, s[i])
            to_add = [st, to_str(dds['ff_link'])]
            res.append(to_add)
        return render_template('result.html', res=res)


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
