from flask import Flask, render_template, flash, redirect, url_for, request, session, jsonify

app = Flask(__name__)
app.secret_key = 'afajkdfadfladfjkaldkfk;52615567adfadf'

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How razorback-jumping frogs can level six piqued gymnasts!",
    "Pack my box with five dozen liquor jugs."
]


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    data = request.get_json()
    # store user info & reset sentence index
    session['email']      = data['email']
    session['firstName']  = data['firstName']
    session['lastName']   = data['lastName']
    session['region']     = data['region']
    session['sentence_i'] = 0

    return jsonify({
        'success': True,
        'next_sentence': SENTENCES[0],
        'email': data['email'],
        'firstName': data['firstName'],
        'lastName': data['lastName']
    })

@app.route('/record', methods=['POST'])
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
def next_sentence():
    i = session.get('sentence_i', 0) + 1
    session['sentence_i'] = i
    next_sentence = SENTENCES[i] if i < len(SENTENCES) else None
    return jsonify({
        'success': True,
        'next_sentence': next_sentence
    })

if __name__ == '__main__':
    app.run(debug=True)