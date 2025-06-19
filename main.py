from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify
from spectree import SpecTree, Response
from dtos import UserInfo, NextQueryResponse

app = Flask(__name__)
app.secret_key = 'afajkdfadfladfjkaldkfk;52615567adfadf'

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How razorback-jumping frogs can level six piqued gymnasts!",
    "Pack my box with five dozen liquor jugs."
]

spec = SpecTree("flask")
@app.route("/")
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
@spec.validate(
    json=UserInfo, resp=Response(HTTP_200=NextQueryResponse), tags=["api"]
)
def submit():
    data = request.json
        # store user info & reset sentence index
    print(data)
    session['email']      = data['email']
    session['firstName']  = data['first_name']
    session['lastName']   = data['last_name']
    session['region']     = data['country']
    session['sentence_i'] = 0

    return jsonify(
        next_sentence= SENTENCES[0],
    )

@app.route('/record', methods=['POSnext_sentenceT'])
def record():
    # pretend to “save” the blob
    audio = request.files.get('audio')   # blob from frontend
    # increment index
    i = session.get('sentence_i', 0) + 1
    session['sentence_i'] = i
    next_sentence = SENTENCES[i] if i < len(SENTENCES) else None

    return jsonify({
        'success': True,
        'next_sentence': next_sentence
    })

@app.route('/next-sentence', methods=['GET'])
@spec.validate(
    resp=Response(HTTP_200=NextQueryResponse), tags=["api"]
)
def next_sentence():
    i = session.get('sentence_i', 0) + 1
    session['sentence_i'] = i
    next_sentence = SENTENCES[i] if i < len(SENTENCES) else None
    return NextQueryResponse(
        next_sentence= next_sentence,
    )

if __name__ == '__main__':
    spec.register(app)
    app.run(debug=True)