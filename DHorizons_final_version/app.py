from flask import Flask, render_template, request, redirect, url_for, session, flash  #session e flash sono per login (chiave di sessione)
from flask_sqlalchemy import SQLAlchemy    
from werkzeug.utils import secure_filename
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "u1@#Pz9k$!mL7eWx3^Rt5gJ&vA2Q"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///database.db"
app.config["UPLOAD_FOLDER"] = "static/uploads"
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)   #nullable = campo obbligatorio
    contenuto = db.Column(db.Text, nullable=False)
    immagine = db.Column(db.String(200))

class Eventi(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    contenuto = db.Column(db.Text, nullable=False)
    immagine = db.Column(db.String(200))
    data = db.Column(db.Date, nullable=False)   #salvata come date e non come stringa (gg/mm/aaa)

class Lezioni(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titolo = db.Column(db.String(100), nullable=False)
    link = db.Column(db.String(300), nullable=False)

# HOME
@app.route("/")
def home():
    post = Post.query.order_by(Post.id.desc()).limit(3).all() #.query() è una SELECT
    eventi = Eventi.query.order_by(Eventi.id.desc()).limit(3).all() #queste variavili sono delle liste
    lezioni = Lezioni.query.order_by(Lezioni.id.desc()).limit(3).all()

    ultimi_post = post + eventi + lezioni #unisce le liste
    ultimi_post.sort(key=lambda x: x.id, reverse=True)  #lambda = funzione senza nome. sintassi= argomento: risultato(return)

    return render_template("index.html", ultimi_post=ultimi_post)


# PAGINE VISIBILI
@app.route("/post")
def post():
    posts = Post.query.all()
    return render_template("post.html", posts=posts)

@app.route("/eventi")
def eventi():
    eventi = Eventi.query.order_by(Eventi.data.desc()).all()
    return render_template("eventi.html", eventi=eventi)

@app.route("/lezioni")
def lezioni():
    lezioni = Lezioni.query.all()
    return render_template("lezioni.html", lezioni=lezioni)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        # Username e password fissi (puoi cambiarli ovviamente)
        if username == "admin" and password == "1234":
            session["admin_logged_in"] = True
            return redirect("/admin")
        else:
            flash("Credenziali errate")

    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect("/login")

# ADMIN - MOSTRA FORM + LISTE
@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect("/login")
    posts = Post.query.all()
    eventi = Eventi.query.all()
    lezioni = Lezioni.query.all()
    return render_template("admin.html", posts=posts, eventi=eventi, lezioni=lezioni)

# AGGIUNGI POST
@app.route("/admin/post", methods=["POST"])
def aggiungi_post():
    titolo = request.form["titolo"]
    contenuto = request.form["contenuto"]
    file = request.files.get("immagine")
    filename = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    nuovo_post = Post(titolo=titolo, contenuto=contenuto, immagine=filename)
    db.session.add(nuovo_post)  #prepara per l'aggiunta: INSERT INTO
    db.session.commit()         #finalizza/salva l'aggiunta o il delete. .commit() è usato come UPDATE. 
    return redirect("/admin")

# AGGIUNGI EVENTO
@app.route("/admin/event", methods=["POST"])
def aggiungi_evento():
    titolo = request.form["titolo"]
    contenuto = request.form["contenuto"]
    data_str = request.form["data"]        #input type="date" nel'HTML > Flask lo riceve come stringa
    data = datetime.strptime(data_str, "%Y-%m-%d").date()  #strptime = "string parse time" > converte stringa in oggetto date se rispetta "%Y-%m-%d"
    file = request.files.get("immagine")
    filename = None
    if file and file.filename:
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["UPLOAD_FOLDER"], filename))
    nuovo_evento = Eventi(titolo=titolo, contenuto=contenuto, data=data, immagine=filename)
    db.session.add(nuovo_evento)
    db.session.commit()
    return redirect("/admin")

# AGGIUNGI LEZIONE
@app.route("/admin/lesson", methods=["POST"])
def aggiungi_lezione():
    titolo = request.form["titolo"]
    link = request.form["link"]
    nuova_lezione = Lezioni(titolo=titolo, link=link)
    db.session.add(nuova_lezione)
    db.session.commit()
    return redirect("/admin")

# ESTRAZIONE YOUTUBE_ID
@app.template_filter('youtube_id') #Questo crea un filtro personalizzato di Jinja (il motore di template di Flask), che puoi usare nei tuoi template HTML con la sintassi
def youtube_id(link):
    # supporta sia link lunghi che corti
    import re
    match = re.search(r"(?:v=|be/)([A-Za-z0-9_-]{11})", link) #Cerca l’ID del video, che è sempre una stringa di 11 caratteri alfanumerici (più trattini e underscore).
    return match.group(1) if match else ''

# ELIMINA POST
@app.route("/admin/delete/post/<int:id>", methods=["POST"])
def elimina_post(id):
    post = Post.query.get(id)
    if post:
        db.session.delete(post)
        db.session.commit()
    return redirect("/admin")

# ELIMINA EVENTO
@app.route("/admin/delete/event/<int:id>", methods=["POST"])
def elimina_evento(id):
    evento = Eventi.query.get(id)
    if evento:
        db.session.delete(evento)
        db.session.commit()
    return redirect("/admin")

# ELIMINA LEZIONE
@app.route("/admin/delete/lesson/<int:id>", methods=["POST"])
def elimina_lezione(id):
    lezione = Lezioni.query.get(id)
    if lezione:
        db.session.delete(lezione)
        db.session.commit()
    return redirect("/admin")

# BARRA DI RICERCA
@app.route("/search")
def search():
    query = request.args.get("query", "").lower()
    if not query:                            #valutare messaggio con flash("Inserisci un termine di ricerca valido.", "warning")
        return redirect(request.referrer)    #Riporta alla pagina dove è stata fatta la request    
    # Cerca nei titoli e contenuti di Post, Eventi, Lezioni
    post_risultati = Post.query.filter(Post.titolo.ilike(f"%{query}%") | Post.contenuto.ilike(f"%{query}%")).all()
    eventi_risultati = Eventi.query.filter(Eventi.titolo.ilike(f"%{query}%") | Eventi.contenuto.ilike(f"%{query}%")).all()
    lezioni_risultati = Lezioni.query.filter(Lezioni.titolo.ilike(f"%{query}%")).all()

    return render_template("search_results.html", 
                           query=query, 
                           post_risultati=post_risultati, 
                           eventi_risultati=eventi_risultati, 
                           lezioni_risultati=lezioni_risultati)

# RUN
if __name__ == '__main__':
    app.run(debug=True)