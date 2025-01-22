from flask import Flask, render_template, request, redirect, url_for
from flask_migrate import Migrate
from models import db, Survey, Response
import os

app = Flask(__name__)
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'database/surveys.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializa la base de datos
db.init_app(app)

# Configura Flask-Migrate
migrate = Migrate(app, db)

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
        if answer:  # Asegúrate de que haya un valor en la respuesta
            new_response = Response(survey_id=survey.id, answer=answer)
            db.session.add(new_response)
            db.session.commit()
        return redirect(url_for("results", survey_id=survey.id))
    return render_template("survey.html", survey=survey)


@app.route("/results/<int:survey_id>")
def results(survey_id):
    survey = Survey.query.get_or_404(survey_id)
    responses = Response.query.filter_by(survey_id=survey.id).all()

    # Si no hay respuestas, retornamos la plantilla con datos vacíos
    if not responses:
        return render_template("results.html", survey=survey, labels=[], data=[], responses=[])

    # Contar las frecuencias de las respuestas
    frequencies = {}
    for response in responses:
        answer = response.answer
        frequencies[answer] = frequencies.get(answer, 0) + 1

    # Convertir las claves y valores del diccionario a listas
    labels = list(frequencies.keys())
    data = list(frequencies.values())

    # Retornar la plantilla con las respuestas y los datos del gráfico
    return render_template("results.html", survey=survey, labels=labels, data=data, responses=responses)


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
