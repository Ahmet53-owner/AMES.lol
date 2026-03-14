from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

# ayarlar
app.secret_key = 'guns_lol_projesi_cok_gizli'  # Oturum güvenliği için
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///veritabani.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


# veritabanı modeli
class Kullanici(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    kullanici_adi = db.Column(db.String(50), unique=True, nullable=False)
    sifre = db.Column(db.String(200), nullable=False)
    bio = db.Column(db.String(200), default="Henüz bir biyografi yazılmadı.")
    discord = db.Column(db.String(100), default="")


# veritabanı
with app.app_context():
    if not os.path.exists('instance'):
        os.makedirs('instance')
    db.create_all()

# anasayfa
@app.route('/')
def ana_sayfa():
    return render_template('index.html')


# kayıtişlemi
@app.route('/kayit', methods=['POST'])
def kayit_ol():
    adi = request.form.get('kullanici_adi').lower()
    sifre = request.form.get('sifre')

    mevcut_user = Kullanici.query.filter_by(kullanici_adi=adi).first()
    if mevcut_user:
        return "<h1>Hata!</h1><p>Bu isim zaten alınmış.</p><a href='/'>Geri dön</a>"

    yeni_user = Kullanici(
        kullanici_adi=adi,
        sifre=generate_password_hash(sifre)
    )

    db.session.add(yeni_user)
    db.session.commit()
    return redirect(url_for('login'))


# girissayfası
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        adi = request.form.get('kullanici_adi').lower()
        sifre = request.form.get('sifre')

        user = Kullanici.query.filter_by(kullanici_adi=adi).first()

        if user and check_password_hash(user.sifre, sifre):
            session['user_id'] = user.id
            return redirect(url_for('panel'))
        else:
            return "<h1>Hata!</h1><p>Bilgiler yanlış.</p><a href='/login'>Tekrar dene</a>"

    return render_template('login.html')


# panel
@app.route('/panel')
def panel():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = Kullanici.query.get(session['user_id'])
    return render_template('panel.html', user=user)


# güncelleme
@app.route('/guncelle', methods=['POST'])
def guncelle():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user = Kullanici.query.get(session['user_id'])
    user.bio = request.form.get('yeni_bio')
    user.discord = request.form.get('yeni_discord')

    db.session.commit()
    return redirect(url_for('panel'))


# profildençık
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('ana_sayfa'))


# dinamikprofil
@app.route('/<username>')
def profil_sayfasi(username):
    user = Kullanici.query.filter_by(kullanici_adi=username.lower()).first()
    if user:
        return render_template('profil.html', user=user)
    return "<h1>404</h1><p>Kullanıcı bulunamadı!</p>", 404
if __name__ == '__main__':
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
