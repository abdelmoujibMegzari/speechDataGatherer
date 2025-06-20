import os
from flask import Flask, render_template, flash, request, session, jsonify
from spectree import SpecTree, Response
from dtos import UserInfo, NextQueryResponse
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, User

engine = create_engine("sqlite:///udb.db", echo=True)

RECORDS_FOLDER_PATH = "./recordings/"
app = Flask(__name__)
app.secret_key = 'afajkdfadfladfjkaldkfk;52615567adfadf'
app.config['UPLOAD_FOLDER'] = RECORDS_FOLDER_PATH
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
    with Session(engine) as s:
        userSelect = select(User).where(User.email == data['email']).limit(1)
        user = s.scalar(userSelect)
        print(user)
        if not user:
            user = User(
                email = data['email'],
                first_name= data['first_name'],
                last_name= data['last_name'],
                country = data['country'],
                current_sentence= 0,
                permutation_number=0
            )
        s.add(user)
        s.commit()
        session['id'] = user.id
        session['email']      = data['email']
        session['firstName']  = user.first_name
        session['lastName']   = user.last_name
        session['region']     = user.country
        session['sentence_i'] = user.current_sentence
        session['sentences_permutation'] = user.permutation_number

    return jsonify(
        next_sentence= SENTENCES[0],
    )

ALLOWED_EXTENSIONS = set('webm')
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/record', methods=['POST'])
def record():
    # pretend to “save” the blob
    if 'audio' not in request.files:
        flash("No audio found")
        return 403
    audio = request.files.get('audio')   # blob from frontend
    # if audio and allowed_file(audio.filename):
    filename = secure_filename(audio.filename)
    newpath = os.path.join(app.config['UPLOAD_FOLDER']+filename)
    print(newpath)
    audio.save(newpath)

    # increment index
    i = session.get('sentence_i', 0) + 1
    session['sentence_i'] = i
    next_sentence = SENTENCES[i] if i < len(SENTENCES) else None

    return jsonify({
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
    Base.metadata.create_all(engine)
    spec.register(app)
    app.run(debug=True)
