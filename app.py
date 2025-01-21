from flask import Flask, render_template, request, redirect, url_for
from models import db, Survey, Response
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database/surveys.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route("/")
def home():
    surveys = Survey.query.all()
    return render_template("index.html", surveys=surveys)

@app.route("/create", methods=["GET", "POST"])
def create_survey():
    if request.method == "POST":
        title = request.form["title"]
        description = request.form.get("description")
        new_survey = Survey(title=title, description=description)
        db.session.add(new_survey)
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("create_survey.html")

@app.route("/survey/<int:survey_id>", methods=["GET", "POST"])
def survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == "POST":
        answer = request.form["answer"]
        new_response = Response(survey_id=survey.id, answer=answer)
        db.session.add(new_response)
        db.session.commit()
        return redirect(url_for("results", survey_id=survey.id))
    return render_template("survey.html", survey=survey)

@app.route("/results/<int:survey_id>")
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey.id).all()
    return render_template("results.html", survey=survey, responses=responses)

@app.route("/edit/<int:survey_id>", methods=["GET", "POST"])
def edit_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    if request.method == "POST":
        survey.title = request.form["title"]
        survey.description = request.form.get("description")
        db.session.commit()
        return redirect(url_for("home"))
    return render_template("edit_survey.html", survey=survey)

@app.route("/delete/<int:survey_id>", methods=["POST"])
def delete_survey(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    db.session.delete(survey)
    db.session.commit()
    return redirect(url_for("home"))

if __name__ == "__main__":
    app.run(debug=True)
