from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-ganti-di-production')

# Database config
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL',
    'postgresql://admin:admin123@db:5432/nilaidb'
)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ─────────────────────────────────────────
# MODELS
# ─────────────────────────────────────────

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    nama = db.Column(db.String(100), nullable=False)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'dosen' or 'mahasiswa'
    nim_nip = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    nilai = db.relationship('Nilai', backref='mahasiswa', lazy=True,
                            foreign_keys='Nilai.mahasiswa_id')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class MataKuliah(db.Model):
    __tablename__ = 'mata_kuliah'
    id = db.Column(db.Integer, primary_key=True)
    kode = db.Column(db.String(10), unique=True, nullable=False)
    nama = db.Column(db.String(100), nullable=False)
    sks = db.Column(db.Integer, nullable=False)
    semester = db.Column(db.Integer, nullable=False)

    nilai = db.relationship('Nilai', backref='mata_kuliah', lazy=True)


class Nilai(db.Model):
    __tablename__ = 'nilai'
    id = db.Column(db.Integer, primary_key=True)
    mahasiswa_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    matkul_id = db.Column(db.Integer, db.ForeignKey('mata_kuliah.id'), nullable=False)
    dosen_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    nilai_angka = db.Column(db.Float, nullable=False)
    nilai_huruf = db.Column(db.String(2), nullable=False)
    semester = db.Column(db.String(10), nullable=False)
    tahun_ajaran = db.Column(db.String(10), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    dosen = db.relationship('User', foreign_keys=[dosen_id])


# ─────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────

def angka_to_huruf(nilai):
    if nilai >= 85: return 'A'
    elif nilai >= 80: return 'A-'
    elif nilai >= 75: return 'B+'
    elif nilai >= 70: return 'B'
    elif nilai >= 65: return 'B-'
    elif nilai >= 60: return 'C+'
    elif nilai >= 55: return 'C'
    elif nilai >= 50: return 'C-'
    elif nilai >= 45: return 'D'
    else: return 'E'

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            flash('Silakan login terlebih dahulu.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def dosen_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        if session.get('role') != 'dosen':
            flash('Akses ditolak. Hanya untuk dosen.', 'error')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

def seed_data():
    """Seed initial data jika database kosong"""
    if User.query.count() > 0:
        return

    # Dosen
    dosen1 = User(nama='Dr. Ahmad Fauzi, M.Kom', username='dosen1',
                  nim_nip='197501012005011001', role='dosen')
    dosen1.set_password('dosen123')

    dosen2 = User(nama='Dr. Siti Rahayu, M.T', username='dosen2',
                  nim_nip='198003152008012002', role='dosen')
    dosen2.set_password('dosen123')

    # Mahasiswa
    mhs_list = [
        ('Budi Santoso', 'budi', '2021001', 'mhs123'),
        ('Ani Wijaya', 'ani', '2021002', 'mhs123'),
        ('Reza Pratama', 'reza', '2021003', 'mhs123'),
        ('Dewi Lestari', 'dewi', '2021004', 'mhs123'),
        ('Fajar Nugroho', 'fajar', '2021005', 'mhs123'),
    ]
    mahasiswa_objs = []
    for nama, uname, nim, pwd in mhs_list:
        m = User(nama=nama, username=uname, nim_nip=nim, role='mahasiswa')
        m.set_password(pwd)
        mahasiswa_objs.append(m)

    # Mata Kuliah
    matkul_list = [
        MataKuliah(kode='IF101', nama='Algoritma & Pemrograman', sks=3, semester=1),
        MataKuliah(kode='IF201', nama='Struktur Data', sks=3, semester=2),
        MataKuliah(kode='IF301', nama='Basis Data', sks=3, semester=3),
        MataKuliah(kode='IF401', nama='Jaringan Komputer', sks=3, semester=4),
        MataKuliah(kode='IF501', nama='Cloud Computing', sks=3, semester=5),
        MataKuliah(kode='IF601', nama='Keamanan Sistem', sks=2, semester=6),
    ]

    db.session.add_all([dosen1, dosen2] + mahasiswa_objs + matkul_list)
    db.session.commit()

    # Sample nilai
    import random
    sample_nilai = [
        (85, '2024/2025'), (78, '2024/2025'), (92, '2024/2025'),
        (70, '2024/2025'), (88, '2024/2025'), (65, '2024/2025'),
    ]
    for i, mhs in enumerate(mahasiswa_objs):
        for j, mk in enumerate(matkul_list):
            if (i + j) % 3 != 0:  # tidak semua dapat nilai biar realistis
                angka = random.randint(55, 95)
                n = Nilai(
                    mahasiswa_id=mhs.id,
                    matkul_id=mk.id,
                    dosen_id=dosen1.id,
                    nilai_angka=angka,
                    nilai_huruf=angka_to_huruf(angka),
                    semester='Ganjil',
                    tahun_ajaran='2024/2025'
                )
                db.session.add(n)
    db.session.commit()
    print("✅ Seed data berhasil!")


# ─────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            session['nama'] = user.nama
            session['role'] = user.role
            session['nim_nip'] = user.nim_nip
            flash(f'Selamat datang, {user.nama}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Username atau password salah.', 'error')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Anda telah berhasil logout.', 'success')
    return redirect(url_for('login'))


@app.route('/dashboard')
@login_required
def dashboard():
    if session['role'] == 'dosen':
        return redirect(url_for('dosen_dashboard'))
    return redirect(url_for('mahasiswa_dashboard'))


# ── DOSEN ──────────────────────────────

@app.route('/dosen')
@dosen_required
def dosen_dashboard():
    # Stats
    total_mhs = User.query.filter_by(role='mahasiswa').count()
    total_matkul = MataKuliah.query.count()
    total_nilai = Nilai.query.filter_by(dosen_id=session['user_id']).count()

    # Recent nilai
    recent = db.session.query(Nilai).filter_by(
        dosen_id=session['user_id']
    ).order_by(Nilai.updated_at.desc()).limit(5).all()

    return render_template('dosen_dashboard.html',
                           total_mhs=total_mhs,
                           total_matkul=total_matkul,
                           total_nilai=total_nilai,
                           recent=recent)


@app.route('/dosen/nilai')
@dosen_required
def dosen_nilai():
    search = request.args.get('search', '').strip()
    matkul_filter = request.args.get('matkul', '')
    semester_filter = request.args.get('semester', '')

    query = db.session.query(Nilai).join(
        User, Nilai.mahasiswa_id == User.id
    ).join(MataKuliah, Nilai.matkul_id == MataKuliah.id)

    if search:
        query = query.filter(
            db.or_(
                User.nama.ilike(f'%{search}%'),
                User.nim_nip.ilike(f'%{search}%')
            )
        )
    if matkul_filter:
        query = query.filter(Nilai.matkul_id == matkul_filter)
    if semester_filter:
        query = query.filter(Nilai.semester == semester_filter)

    nilai_list = query.order_by(User.nama).all()
    mahasiswa_list = User.query.filter_by(role='mahasiswa').order_by(User.nama).all()
    matkul_list = MataKuliah.query.order_by(MataKuliah.nama).all()

    return render_template('dosen_nilai.html',
                           nilai_list=nilai_list,
                           mahasiswa_list=mahasiswa_list,
                           matkul_list=matkul_list,
                           search=search,
                           matkul_filter=matkul_filter,
                           semester_filter=semester_filter)


@app.route('/dosen/nilai/tambah', methods=['GET', 'POST'])
@dosen_required
def tambah_nilai():
    if request.method == 'POST':
        mahasiswa_id = request.form.get('mahasiswa_id')
        matkul_id = request.form.get('matkul_id')
        nilai_angka = float(request.form.get('nilai_angka'))
        semester = request.form.get('semester')
        tahun_ajaran = request.form.get('tahun_ajaran')

        # Cek apakah sudah ada
        existing = Nilai.query.filter_by(
            mahasiswa_id=mahasiswa_id,
            matkul_id=matkul_id,
            semester=semester,
            tahun_ajaran=tahun_ajaran
        ).first()

        if existing:
            flash('Nilai untuk mahasiswa ini di matkul ini sudah ada. Gunakan fitur edit.', 'error')
        else:
            nilai = Nilai(
                mahasiswa_id=mahasiswa_id,
                matkul_id=matkul_id,
                dosen_id=session['user_id'],
                nilai_angka=nilai_angka,
                nilai_huruf=angka_to_huruf(nilai_angka),
                semester=semester,
                tahun_ajaran=tahun_ajaran
            )
            db.session.add(nilai)
            db.session.commit()
            flash('Nilai berhasil ditambahkan!', 'success')
            return redirect(url_for('dosen_nilai'))

    mahasiswa_list = User.query.filter_by(role='mahasiswa').order_by(User.nama).all()
    matkul_list = MataKuliah.query.order_by(MataKuliah.nama).all()
    return render_template('tambah_nilai.html',
                           mahasiswa_list=mahasiswa_list,
                           matkul_list=matkul_list)


@app.route('/dosen/nilai/edit/<int:nilai_id>', methods=['GET', 'POST'])
@dosen_required
def edit_nilai(nilai_id):
    nilai = Nilai.query.get_or_404(nilai_id)

    if request.method == 'POST':
        nilai.nilai_angka = float(request.form.get('nilai_angka'))
        nilai.nilai_huruf = angka_to_huruf(nilai.nilai_angka)
        nilai.semester = request.form.get('semester')
        nilai.tahun_ajaran = request.form.get('tahun_ajaran')
        nilai.dosen_id = session['user_id']
        nilai.updated_at = datetime.utcnow()
        db.session.commit()
        flash('Nilai berhasil diperbarui!', 'success')
        return redirect(url_for('dosen_nilai'))

    mahasiswa_list = User.query.filter_by(role='mahasiswa').order_by(User.nama).all()
    matkul_list = MataKuliah.query.order_by(MataKuliah.nama).all()
    return render_template('edit_nilai.html', nilai=nilai,
                           mahasiswa_list=mahasiswa_list,
                           matkul_list=matkul_list)


@app.route('/dosen/nilai/hapus/<int:nilai_id>', methods=['POST'])
@dosen_required
def hapus_nilai(nilai_id):
    nilai = Nilai.query.get_or_404(nilai_id)
    db.session.delete(nilai)
    db.session.commit()
    flash('Nilai berhasil dihapus.', 'success')
    return redirect(url_for('dosen_nilai'))


@app.route('/dosen/mahasiswa')
@dosen_required
def dosen_mahasiswa():
    search = request.args.get('search', '').strip()
    query = User.query.filter_by(role='mahasiswa')
    if search:
        query = query.filter(
            db.or_(
                User.nama.ilike(f'%{search}%'),
                User.nim_nip.ilike(f'%{search}%')
            )
        )
    mahasiswa_list = query.order_by(User.nama).all()
    return render_template('dosen_mahasiswa.html',
                           mahasiswa_list=mahasiswa_list, search=search)


# ── MAHASISWA ──────────────────────────

@app.route('/mahasiswa')
@login_required
def mahasiswa_dashboard():
    if session['role'] != 'mahasiswa':
        return redirect(url_for('dosen_dashboard'))

    user_id = session['user_id']

    # Semua nilai
    nilai_list = db.session.query(Nilai).filter_by(
        mahasiswa_id=user_id
    ).order_by(Nilai.tahun_ajaran.desc(), Nilai.semester).all()

    # Hitung IPK
    total_bobot = 0
    total_sks = 0
    huruf_to_bobot = {'A': 4.0, 'A-': 3.7, 'B+': 3.3, 'B': 3.0,
                      'B-': 2.7, 'C+': 2.3, 'C': 2.0, 'C-': 1.7,
                      'D': 1.0, 'E': 0.0}
    for n in nilai_list:
        bobot = huruf_to_bobot.get(n.nilai_huruf, 0)
        total_bobot += bobot * n.mata_kuliah.sks
        total_sks += n.mata_kuliah.sks

    ipk = round(total_bobot / total_sks, 2) if total_sks > 0 else 0

    return render_template('mahasiswa_dashboard.html',
                           nilai_list=nilai_list,
                           ipk=ipk,
                           total_sks=total_sks,
                           total_matkul=len(nilai_list))


@app.route('/mahasiswa/transkrip')
@login_required
def mahasiswa_transkrip():
    if session['role'] != 'mahasiswa':
        return redirect(url_for('dosen_dashboard'))

    user_id = session['user_id']
    search = request.args.get('search', '').strip()
    semester_filter = request.args.get('semester', '')

    query = db.session.query(Nilai).join(
        MataKuliah, Nilai.matkul_id == MataKuliah.id
    ).filter(Nilai.mahasiswa_id == user_id)

    if search:
        query = query.filter(MataKuliah.nama.ilike(f'%{search}%'))
    if semester_filter:
        query = query.filter(Nilai.semester == semester_filter)

    nilai_list = query.order_by(MataKuliah.nama).all()

    return render_template('mahasiswa_transkrip.html',
                           nilai_list=nilai_list,
                           search=search,
                           semester_filter=semester_filter)


# ── API ────────────────────────────────

@app.route('/api/konversi-nilai')
@login_required
def api_konversi():
    angka = request.args.get('angka', 0, type=float)
    return jsonify({'huruf': angka_to_huruf(angka), 'angka': angka})


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_data()
    app.run(host='0.0.0.0', port=5000, debug=True)
