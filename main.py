import os
from flask import (
    Flask,
    render_template,
    flash,
    request,
    session,
    jsonify,
    Response as r,
)
from spectree import SpecTree, Response
from dtos import UserInfo, NextQueryResponse
from werkzeug.utils import secure_filename
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from models import Base, User
from numpy import random

engine = create_engine("sqlite:///udb.db", echo=True)

RECORDS_FOLDER_PATH = "./recordings/"
app = Flask(__name__)
app.secret_key = "afajkdfadfladfjkaldkfk;52615567adfadf"
app.config["UPLOAD_FOLDER"] = RECORDS_FOLDER_PATH
SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "She sells seashells by the seashore.",
    "How razorback-jumping frogs can level six piqued gymnasts!",
    "Pack my box with five dozen liquor jugs.",
]
L = len(SENTENCES)
random.seed(15765)

NUMBER_OF_PERMUTATIONS = 10
PRMUTATIONS = [random.permutation(L) for _ in range(NUMBER_OF_PERMUTATIONS)]


spec = SpecTree("flask")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/submit", methods=["POST"])
@spec.validate(json=UserInfo, resp=Response(HTTP_200=NextQueryResponse), tags=["api"])
def submit():
    data = request.json
    # store user info & reset sentence index
    print(data)
    with Session(engine) as s:
        userSelect = select(User).where(User.email == data["email"]).limit(1)
        user = s.scalar(userSelect)
        print(user)
        if not user:
            user = User(
                email=data["email"],
                first_name=data["first_name"],
                last_name=data["last_name"],
                country=data["country"],
                current_sentence=0,
            )
        s.add(user)
        s.commit()
        session["id"] = user.id
        session["email"] = data["email"]
        session["firstName"] = user.first_name
        session["lastName"] = user.last_name
        session["region"] = user.country
        session["sentence_i"] = user.current_sentence
        session["sentences_permutation"] = user.id % NUMBER_OF_PERMUTATIONS
        permutation_index = session.get("id") % NUMBER_OF_PERMUTATIONS
        next_sentence = (
            SENTENCES[PRMUTATIONS[permutation_index][session["sentence_i"]]]
            if session["sentence_i"] < L
            else None
        )
        session["current_sentence"] = next_sentence
    return jsonify(
        next_sentence=next_sentence,
    )


ALLOWED_EXTENSIONS = {"webm"}


def allowed_file(filename):
    print(ALLOWED_EXTENSIONS)
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/record", methods=["POST"])
def record():
    # pretend to “save” the blob
    if "audio" not in request.files:
        flash("No audio found")
        return 403
    audio = request.files.get("audio")  # blob from frontend
    # if audio and allowed_file(audio.filename):
    filename = secure_filename(audio.filename)
    print(filename)
    if not allowed_file(filename):
        return r(status=415)
    if not session.get("id"):
        return r(status=401)
    permutation_index = session.get("id") % NUMBER_OF_PERMUTATIONS
    newpath = os.path.join(
        app.config["UPLOAD_FOLDER"]
        + str(session.get("id"))
        + "_"
        + str(PRMUTATIONS[permutation_index][session.get("sentence_i")])
        + ".webm"
    )
    audio.save(newpath)

    # increment index
    i = session.get("sentence_i", 0) + 1
    with Session(engine) as s:
        userSelect = select(User).where(User.id == session["id"]).limit(1)
        user = s.scalar(userSelect)
        if not user:
            return r(status=500)
        user.current_sentence = i
        s.commit()
        session["sentence_i"] = i
    permutation_index = session.get("id") % NUMBER_OF_PERMUTATIONS
    next_sentence = SENTENCES[PRMUTATIONS[permutation_index][i]] if i < L else None
    session["current_sentence"] = next_sentence
    return jsonify({"next_sentence": next_sentence})


@app.route("/next-sentence", methods=["GET"])
@spec.validate(resp=Response(HTTP_200=NextQueryResponse), tags=["api"])
def next_sentence():
    i = session.get("sentence_i", 0) + 1
    with Session(engine) as s:
        userSelect = select(User).where(User.id == session["id"]).limit(1)
        user = s.scalar(userSelect)
        if not user:
            return r(status=500)
        user.current_sentence = i
        s.commit()
        session["sentence_i"] = i
    permutation_index = session.get("id") % NUMBER_OF_PERMUTATIONS
    next_sentence = SENTENCES[PRMUTATIONS[permutation_index][i]] if i < L else None
    session["current_sentence"] = next_sentence
    return NextQueryResponse(
        next_sentence=next_sentence,
    )


@app.route("/logout", methods=["post"])
def logout():
    session.clear()
    return r(status=204)


if __name__ == "__main__":
    Base.metadata.create_all(engine)
    spec.register(app)
    app.run(debug=True)
