from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from werkzeug.utils import secure_filename
from wtforms.validators import InputRequired
from give_me_the_odds import get_the_odds
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = '4axFalcon_Giskard89x    '
app.config['UPLOAD_FOLDER'] = 'static/files'

class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()], render_kw={'style': 'width: 400px; font-size: 30px; cursor: pointer;'})
    submit = SubmitField("Upload empire JSON", render_kw={'style': 'width: 300px; font-size: 30px; cursor: pointer;'})

@app.route('/', methods=['GET', "POST"])
@app.route('/home', methods=['GET', "POST"])
def home():
    form = UploadFileForm()
    best_odds = ""
    best_route = ""
    if form.validate_on_submit():
        file = form.file.data
        if file.filename.split(".")[-1] == "json":
            file.save(os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config['UPLOAD_FOLDER'], secure_filename(file.filename)))
            odds, best_route = get_the_odds(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))
            best_odds = "Your survival odds: " + str(odds) + "%"
        else:
            best_odds = "Error: Not a JSON file. Please upload a JSON file."
    return render_template('index.html', form=form, best_odds=best_odds, best_route=best_route)

if __name__ == '__main__':
    app.run(debug=True)