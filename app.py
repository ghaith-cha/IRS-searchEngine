from flask import Flask, render_template, request
from inde import indexer
import json

app = Flask(__name__)
c = indexer()
c.Loadinde()


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/', methods=['POST'])
def getvalues():
    text = request.form['input']
    view = c.findWord(text)
    if type(view) is set:
        return render_template("searchresult.html", search=map(json.dumps,view), value=text,didumean="")
    else:
        thekey = list(view.keys())[0]
        toprint = view[thekey]
        return render_template("searchresult.html", search=map(json.dumps,toprint), value=text,didumean=thekey)


@app.route('/<string:did>')
def go_to(did):
    view = c.findWord(did)
    if type(view) is set:
        return render_template("searchresult.html", search=map(json.dumps,view), value=did,didumean="")
    else:
        thekey = list(view.keys())[0]
        toprint = view[thekey]
        return render_template("searchresult.html", search=map(json.dumps,toprint), value=did,didumean=thekey)


if __name__ == "__main__":
    app.run(debug=True)
