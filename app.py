from flask import Flask,render_template,session,request,redirect,flash
from wtforms import StringField,SubmitField,validators,TextAreaField
from flask_wtf import FlaskForm
import sqlite3
import os


app = Flask(__name__)
app.config["SECRET_KEY"]="key"
db = sqlite3.connect("flash.db")
cur = db.cursor()
cur.execute("CREATE table if not exists flash(id INTEGER PRIMARY KEY,name text,email text,password text)")
cur.execute("CREATE table if not exists cards(id INTEGER PRIMARY KEY,title text,question text,answer text,toid integer)")
SIGNED=False
db.commit()
db.close()

class Form(FlaskForm):
    name = StringField("name")
    email = StringField("email",validators=[validators.DataRequired()])
    password = StringField("password",validators=[validators.DataRequired()])
    submit = SubmitField("submit")

class FlashForm(FlaskForm):
    title=StringField("FLashcard Title",validators=[validators.DataRequired()])
    question =TextAreaField("Question",validators=[validators.DataRequired()]) 
    answer = TextAreaField("Answer",validators=[validators.DataRequired()])
    sub = SubmitField("submit")
class Adminform(FlaskForm):
    name = StringField("name",validators={validators.DataRequired()})
    password = StringField("Password")
    sub = SubmitField("Log in")

@app.route('/',methods=["POST","GET"])
def index():
    form = Form()
    if form.validate_on_submit():
        session['email']=form.email.data
        session['password']=form.password.data
        return redirect('/profile')
    return render_template("index.html",form=form,signed=SIGNED)

@app.route("/register",methods=["POST","GET"])
def register():
    global SIGNED
    name = request.form.get("name")
    email = request.form.get("email")
    password=request.form.get("password")
    db = sqlite3.connect("flash.db")
    cur = db.cursor()
    cur.execute("INSERT into flash(name,email,password)VALUES(?,?,?)",(name,email,password))
    db.commit()
    db.close()
    SIGNED = True
    flash("You Signed Up !,Login Now !")
    return redirect("/")

@app.route("/profile")
def profile():
    email=session['email']
    password=session['password']
    db = sqlite3.connect("flash.db")
    cur = db.cursor()
    cur.execute("SELECT * from flash WHERE email=? and password=?",(email,password))
    fet = cur.fetchall()
    form = FlashForm()
    session['code']=fet[0][0]
    if fet:
        return render_template("profile.html",fet=fet,form=form)
    else:
        return "Account Not Valid"
@app.route("/saveflash",methods=['POST',"GET"])
def saveflashcard():
    cardform = FlashForm()
    title = cardform.title.data
    question = cardform.question.data
    answer = cardform.answer.data
    code = session['code']
    db = sqlite3.connect("flash.db")
    cur = db.cursor()
    cur.execute("INSERT into cards(title,question,answer,toid)VALUES(?,?,?,?)",(title,question,answer,code))
    db.commit()
    db.close()
    return redirect("/yourcards")

@app.route("/yourcards")
def yourcards():
    email=session['email']
    password=session['password']
    db = sqlite3.connect("flash.db")
    cur = db.cursor()
    cur.execute("SELECT * from flash WHERE email=? and password=?",(email,password))
    fet = cur.fetchall()
    cur.execute("SELECT * from cards WHERE toid=?",(fet[0][0],))
    yourcards = cur.fetchall()
    db.close()
    if fet:
        return render_template("yourcards.html",fet=fet,cards=yourcards)
    else:
        return "Account Not Valid Try login"

@app.route("/admin",methods=["POST","GET"])
def admin():
    ad = Adminform()

    if ad.validate_on_submit():
        if ad.name.data=="admin" and ad.password.data=='ad123':
            db = sqlite3.connect("flash.db")
            cur = db.cursor()
            cur.execute("SELECT * from flash")
            users = cur.fetchall()
            db.close()
            return users 
        elif ad.name.data=="ad" and ad.password.data=="bad":
            db = sqlite3.connect("flash.db")
            cur = db.cursor()
            cur.execute("SELECT * from cards")
            cards = cur.fetchall()
            db.close()
            return cards
                            
    return render_template("loginadmin.html",ad=ad)


@app.errorhandler(404)
def er(r):
    return render_template("error.html")    
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

