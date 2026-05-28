from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_sqlalchemy import SQLAlchemy
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'sinilai-secret-key-2025')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql://admin:admin123@db:5432/nilaidb')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─── Model ─────────────────────────────────────────────────────────────────────

class Mahasiswa(db.Model):
    __tablename__ = 'mahasiswa'
    id   = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    nim  = db.Column(db.String(20),  nullable=False, unique=True)
    clo1 = db.Column(db.Float, default=0)
    clo2 = db.Column(db.Float, default=0)
    clo3 = db.Column(db.Float, default=0)
    clo4 = db.Column(db.Float, default=0)

    def nilai_akhir(self):
        return round((self.clo1 + self.clo2 + self.clo3 + self.clo4) / 4, 2)

    def grade(self):
        na = self.nilai_akhir()
        if na >= 85: return 'A'
        elif na >= 75: return 'B'
        elif na >= 65: return 'C'
        elif na >= 55: return 'D'
        else: return 'E'

# ─── Hardcoded Dosen ───────────────────────────────────────────────────────────
DOSEN = {
    'username': 'dosen',
    'password': 'dosen123',
    'nama':     'Dr. Budi Santoso, M.Kom',
    'matkul':   'Rekayasa Perangkat Lunak'
}

# ─── Init DB ───────────────────────────────────────────────────────────────────
def init_db():
    with app.app_context():
        db.create_all()
        if Mahasiswa.query.count() == 0:
            contoh = [
                Mahasiswa(nama='Andi Prasetyo',  nim='2021001', clo1=85, clo2=78, clo3=90, clo4=82),
                Mahasiswa(nama='Siti Rahayu',    nim='2021002', clo1=72, clo2=80, clo3=75, clo4=88),
                Mahasiswa(nama='Budi Kurniawan', nim='2021003', clo1=60, clo2=65, clo3=70, clo4=68),
            ]
            db.session.add_all(contoh)
            db.session.commit()

# ─── Routes Umum ───────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        role = request.form.get('role')

        if role == 'dosen':
            username = request.form.get('username', '').strip()
            password = request.form.get('password', '').strip()
            if username == DOSEN['username'] and password == DOSEN['password']:
                session.clear()
                session['role']       = 'dosen'
                session['nama_dosen'] = DOSEN['nama']
                return redirect(url_for('dashboard_dosen'))
            flash('Username atau password dosen salah.', 'error')

        elif role == 'mahasiswa':
            nama = request.form.get('nama', '').strip()
            nim  = request.form.get('nim', '').strip()
            mhs  = Mahasiswa.query.filter_by(nim=nim).first()
            if mhs and mhs.nama.lower() == nama.lower():
                session.clear()
                session['role']     = 'mahasiswa'
                session['mhs_id']   = mhs.id
                session['mhs_nim']  = mhs.nim
                session['mhs_nama'] = mhs.nama
                return redirect(url_for('dashboard_mahasiswa'))
            flash('Nama atau NIM tidak ditemukan. Hubungi dosen Anda.', 'error')

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── Routes Dosen ──────────────────────────────────────────────────────────────

@app.route('/dosen')
def dashboard_dosen():
    if session.get('role') != 'dosen':
        return redirect(url_for('login'))
    mahasiswa  = Mahasiswa.query.order_by(Mahasiswa.nim).all()
    nilai_list = [m.nilai_akhir() for m in mahasiswa]
    stats = {
        'total':     len(mahasiswa),
        'tertinggi': round(max(nilai_list), 1) if nilai_list else 0,
        'rata_rata': round(sum(nilai_list) / len(nilai_list), 1) if nilai_list else 0,
        'lulus':     sum(1 for n in nilai_list if n >= 55),
    }
    return render_template('dosen.html', mahasiswa=mahasiswa, dosen=DOSEN, stats=stats)

@app.route('/dosen/tambah', methods=['POST'])
def tambah_mahasiswa():
    if session.get('role') != 'dosen':
        return redirect(url_for('login'))
    nama = request.form.get('nama', '').strip()
    nim  = request.form.get('nim', '').strip()
    if not nama or not nim:
        flash('Nama dan NIM wajib diisi.', 'error')
        return redirect(url_for('dashboard_dosen'))
    if Mahasiswa.query.filter_by(nim=nim).first():
        flash(f'NIM {nim} sudah terdaftar.', 'error')
        return redirect(url_for('dashboard_dosen'))

    def parse(key):
        try: return max(0.0, min(100.0, float(request.form.get(key, 0))))
        except: return 0.0

    db.session.add(Mahasiswa(nama=nama, nim=nim,
        clo1=parse('clo1'), clo2=parse('clo2'),
        clo3=parse('clo3'), clo4=parse('clo4')))
    db.session.commit()
    flash(f'Mahasiswa {nama} berhasil ditambahkan.', 'success')
    return redirect(url_for('dashboard_dosen'))

@app.route('/dosen/edit/<int:id>', methods=['POST'])
def edit_mahasiswa(id):
    if session.get('role') != 'dosen':
        return redirect(url_for('login'))
    mhs = db.session.get(Mahasiswa, id)
    if not mhs:
        flash('Data tidak ditemukan.', 'error')
        return redirect(url_for('dashboard_dosen'))

    def parse(key):
        try: return max(0.0, min(100.0, float(request.form.get(key, 0))))
        except: return 0.0

    mhs.clo1 = parse('clo1')
    mhs.clo2 = parse('clo2')
    mhs.clo3 = parse('clo3')
    mhs.clo4 = parse('clo4')
    db.session.commit()
    flash(f'Nilai {mhs.nama} berhasil diperbarui.', 'success')
    return redirect(url_for('dashboard_dosen'))

@app.route('/dosen/hapus/<int:id>', methods=['POST'])
def hapus_mahasiswa(id):
    if session.get('role') != 'dosen':
        return redirect(url_for('login'))
    mhs = db.session.get(Mahasiswa, id)
    if not mhs:
        return redirect(url_for('dashboard_dosen'))
    nama = mhs.nama
    db.session.delete(mhs)
    db.session.commit()
    flash(f'Data {nama} berhasil dihapus.', 'success')
    return redirect(url_for('dashboard_dosen'))

# ─── Routes Mahasiswa ──────────────────────────────────────────────────────────

@app.route('/mahasiswa')
def dashboard_mahasiswa():
    if session.get('role') != 'mahasiswa':
        return redirect(url_for('login'))
    mhs = db.session.get(Mahasiswa, session['mhs_id'])
    if not mhs:
        return redirect(url_for('login'))
    return render_template('mahasiswa.html', mhs=mhs, matkul=DOSEN['matkul'])

# ─── Run ───────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=False)
