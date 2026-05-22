"""
Bombay Hair Art — Flask Backend
================================
DB:      PostgreSQL (Render) / SQLite (local fallback)
Admin:   /admin/login  →  /admin/dashboard
Run:     python app.py
URL:     http://localhost:5000
"""

import os
import re
import hashlib
import secrets
from datetime import datetime
from functools import wraps
from flask import (
    Flask, request, jsonify, send_from_directory,
    session, redirect, url_for, render_template_string
)

# ─────────────────────────────────────────────
# Detect DB mode: PostgreSQL or SQLite
# ─────────────────────────────────────────────
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql://', 1)

USE_POSTGRES = bool(DATABASE_URL)

if USE_POSTGRES:
    import psycopg2
    import psycopg2.extras
    print('[DB] Mode: PostgreSQL')
else:
    import sqlite3
    print('[DB] Mode: SQLite (local)')

# ─────────────────────────────────────────────
# App Configuration
# ─────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH  = os.path.join(BASE_DIR, 'database.db')

app = Flask(__name__, static_folder=None)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(32))

# ─── Admin credentials (set via env vars in production) ───
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'BombayHairArt@2024')

PH = '%s' if USE_POSTGRES else '?'


# ─────────────────────────────────────────────
# DB Connection Helper
# ─────────────────────────────────────────────
def get_db():
    if USE_POSTGRES:
        return psycopg2.connect(DATABASE_URL, cursor_factory=psycopg2.extras.RealDictCursor)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ─────────────────────────────────────────────
# Database Initialisation
# ─────────────────────────────────────────────
def init_db():
    conn = get_db()
    c    = conn.cursor()

    if USE_POSTGRES:
        c.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id         SERIAL PRIMARY KEY,
                name       TEXT        NOT NULL,
                phone      TEXT        NOT NULL,
                email      TEXT        DEFAULT '',
                service    TEXT        NOT NULL,
                date       TEXT        NOT NULL,
                time       TEXT        NOT NULL,
                message    TEXT        DEFAULT '',
                status     TEXT        DEFAULT 'pending',
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id         SERIAL PRIMARY KEY,
                name       TEXT        NOT NULL,
                phone      TEXT        NOT NULL,
                email      TEXT        DEFAULT '',
                message    TEXT        NOT NULL,
                is_read    BOOLEAN     DEFAULT FALSE,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
        ''')
        # Add status/is_read columns if upgrading from old schema
        c.execute("ALTER TABLE appointments ADD COLUMN IF NOT EXISTS status TEXT DEFAULT 'pending'")
        c.execute("ALTER TABLE contacts    ADD COLUMN IF NOT EXISTS is_read BOOLEAN DEFAULT FALSE")
    else:
        c.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                phone      TEXT    NOT NULL,
                email      TEXT    DEFAULT '',
                service    TEXT    NOT NULL,
                date       TEXT    NOT NULL,
                time       TEXT    NOT NULL,
                message    TEXT    DEFAULT '',
                status     TEXT    DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        c.execute('''
            CREATE TABLE IF NOT EXISTS contacts (
                id         INTEGER PRIMARY KEY AUTOINCREMENT,
                name       TEXT    NOT NULL,
                phone      TEXT    NOT NULL,
                email      TEXT    DEFAULT '',
                message    TEXT    NOT NULL,
                is_read    INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # Add columns if upgrading
        try:
            c.execute("ALTER TABLE appointments ADD COLUMN status TEXT DEFAULT 'pending'")
        except Exception:
            pass
        try:
            c.execute("ALTER TABLE contacts ADD COLUMN is_read INTEGER DEFAULT 0")
        except Exception:
            pass

    conn.commit()
    conn.close()
    print('[DB] Tables ready.')


# ─────────────────────────────────────────────
# Admin Auth Decorator
# ─────────────────────────────────────────────
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return redirect('/admin/login')
        return f(*args, **kwargs)
    return decorated


# ─────────────────────────────────────────────
# Admin API Auth Decorator (returns JSON)
# ─────────────────────────────────────────────
def admin_api_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'message': 'Unauthorized. Please log in.'}), 401
        return f(*args, **kwargs)
    return decorated


# ═════════════════════════════════════════════
# PUBLIC STATIC ROUTES
# ═════════════════════════════════════════════
@app.route('/')
def home():
    return send_from_directory(BASE_DIR, 'index.html')

@app.route('/about')
def about():
    return send_from_directory(BASE_DIR, 'about.html')

@app.route('/services')
def services():
    return send_from_directory(BASE_DIR, 'services.html')

@app.route('/gallery')
def gallery():
    return send_from_directory(BASE_DIR, 'gallery.html')

@app.route('/booking')
def booking():
    return send_from_directory(BASE_DIR, 'booking.html')

@app.route('/contact')
def contact_page():
    return send_from_directory(BASE_DIR, 'contact.html')


# ═════════════════════════════════════════════
# ADMIN — LOGIN / LOGOUT
# ═════════════════════════════════════════════
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['admin_logged_in'] = True
            session['admin_user']      = username
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('admin_login', error=1)), 401
    return send_from_directory(os.path.join(BASE_DIR, 'admin'), 'login.html')


@app.route('/admin/logout')
def admin_logout():
    session.clear()
    return redirect('/admin/login')


# ═════════════════════════════════════════════
# ADMIN — DASHBOARD (protected)
# ═════════════════════════════════════════════
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    return send_from_directory(os.path.join(BASE_DIR, 'admin'), 'dashboard.html')


# ═════════════════════════════════════════════
# CATCH-ALL STATIC (must be LAST)
# ═════════════════════════════════════════════
@app.route('/<path:filename>')
def serve_static(filename):
    # Never serve admin files through this route
    if filename.startswith('admin'):
        return redirect('/admin/login')
    return send_from_directory(BASE_DIR, filename)


# ═════════════════════════════════════════════
# PUBLIC API — Book Appointment
# ═════════════════════════════════════════════
@app.route('/api/book', methods=['POST'])
def book_appointment():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload.'}), 400

    required = ['name', 'phone', 'service', 'date', 'time']
    missing  = [f for f in required if not str(data.get(f, '')).strip()]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {", ".join(missing)}'}), 422

    phone = re.sub(r'\s+', '', data['phone'])
    if not re.match(r'^[6-9]\d{9}$', phone):
        return jsonify({'success': False, 'message': 'Enter a valid 10-digit Indian mobile number.'}), 422

    try:
        conn = get_db()
        c    = conn.cursor()
        vals = (
            data['name'].strip(), phone,
            data.get('email', '').strip(),
            data['service'].strip(),
            data['date'].strip(), data['time'].strip(),
            data.get('message', '').strip()
        )
        if USE_POSTGRES:
            c.execute(
                f'INSERT INTO appointments (name,phone,email,service,date,time,message) '
                f'VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH}) RETURNING id', vals
            )
            appointment_id = c.fetchone()['id']
        else:
            c.execute(
                f'INSERT INTO appointments (name,phone,email,service,date,time,message) '
                f'VALUES ({PH},{PH},{PH},{PH},{PH},{PH},{PH})', vals
            )
            appointment_id = c.lastrowid

        conn.commit()
        conn.close()
        print(f'[BOOKING] #{appointment_id} — {data["name"]} | {data["service"]} | {data["date"]} {data["time"]}')
        return jsonify({
            'success': True,
            'message': 'Appointment booked! We will confirm via WhatsApp or call within 30 minutes.',
            'appointment_id': appointment_id
        }), 201
    except Exception as e:
        print(f'[DB ERROR] {e}')
        return jsonify({'success': False, 'message': 'Database error. Please try again.'}), 500


# ═════════════════════════════════════════════
# PUBLIC API — Contact Form
# ═════════════════════════════════════════════
@app.route('/api/contact', methods=['POST'])
def contact():
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid JSON payload.'}), 400

    required = ['name', 'phone', 'message']
    missing  = [f for f in required if not str(data.get(f, '')).strip()]
    if missing:
        return jsonify({'success': False, 'message': f'Missing fields: {", ".join(missing)}'}), 422

    try:
        conn = get_db()
        c    = conn.cursor()
        vals = (
            data['name'].strip(), data['phone'].strip(),
            data.get('email', '').strip(), data['message'].strip()
        )
        if USE_POSTGRES:
            c.execute(
                f'INSERT INTO contacts (name,phone,email,message) VALUES ({PH},{PH},{PH},{PH}) RETURNING id', vals
            )
            contact_id = c.fetchone()['id']
        else:
            c.execute(
                f'INSERT INTO contacts (name,phone,email,message) VALUES ({PH},{PH},{PH},{PH})', vals
            )
            contact_id = c.lastrowid

        conn.commit()
        conn.close()
        print(f'[CONTACT] #{contact_id} from {data["name"]} ({data["phone"]})')
        return jsonify({
            'success': True,
            'message': 'Message sent! We will get back to you within 24 hours.',
            'contact_id': contact_id
        }), 201
    except Exception as e:
        print(f'[DB ERROR] {e}')
        return jsonify({'success': False, 'message': 'Database error. Please try again.'}), 500


# ═════════════════════════════════════════════
# ADMIN API — Appointments (protected)
# ═════════════════════════════════════════════
@app.route('/api/admin/appointments', methods=['GET'])
@admin_api_required
def admin_list_appointments():
    try:
        conn = get_db()
        c    = conn.cursor()
        c.execute('SELECT * FROM appointments ORDER BY created_at DESC')
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        # Serialize datetime objects
        for r in rows:
            if isinstance(r.get('created_at'), datetime):
                r['created_at'] = r['created_at'].isoformat()
        return jsonify({'success': True, 'count': len(rows), 'appointments': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/appointments/<int:appt_id>', methods=['PUT'])
@admin_api_required
def admin_update_appointment(appt_id):
    data = request.get_json(silent=True)
    if not data:
        return jsonify({'success': False, 'message': 'Invalid payload.'}), 400

    allowed = {'name', 'phone', 'email', 'service', 'date', 'time', 'message', 'status'}
    updates = {k: v for k, v in data.items() if k in allowed}
    if not updates:
        return jsonify({'success': False, 'message': 'No valid fields to update.'}), 422

    try:
        conn = get_db()
        c    = conn.cursor()
        set_clause = ', '.join(f'{k} = {PH}' for k in updates)
        values     = list(updates.values()) + [appt_id]
        c.execute(f'UPDATE appointments SET {set_clause} WHERE id = {PH}', values)
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Appointment updated.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/appointments/<int:appt_id>', methods=['DELETE'])
@admin_api_required
def admin_delete_appointment(appt_id):
    try:
        conn = get_db()
        c    = conn.cursor()
        c.execute(f'DELETE FROM appointments WHERE id = {PH}', (appt_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Appointment deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ═════════════════════════════════════════════
# ADMIN API — Messages (protected)
# ═════════════════════════════════════════════
@app.route('/api/admin/messages', methods=['GET'])
@admin_api_required
def admin_list_messages():
    try:
        conn = get_db()
        c    = conn.cursor()
        c.execute('SELECT * FROM contacts ORDER BY created_at DESC')
        rows = [dict(r) for r in c.fetchall()]
        conn.close()
        for r in rows:
            if isinstance(r.get('created_at'), datetime):
                r['created_at'] = r['created_at'].isoformat()
        return jsonify({'success': True, 'count': len(rows), 'messages': rows})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/messages/<int:msg_id>/read', methods=['PUT'])
@admin_api_required
def admin_mark_read(msg_id):
    try:
        conn = get_db()
        c    = conn.cursor()
        val  = True if USE_POSTGRES else 1
        c.execute(f'UPDATE contacts SET is_read = {PH} WHERE id = {PH}', (val, msg_id))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Marked as read.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


@app.route('/api/admin/messages/<int:msg_id>', methods=['DELETE'])
@admin_api_required
def admin_delete_message(msg_id):
    try:
        conn = get_db()
        c    = conn.cursor()
        c.execute(f'DELETE FROM contacts WHERE id = {PH}', (msg_id,))
        conn.commit()
        conn.close()
        return jsonify({'success': True, 'message': 'Message deleted.'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ═════════════════════════════════════════════
# ADMIN API — Stats
# ═════════════════════════════════════════════
@app.route('/api/admin/stats', methods=['GET'])
@admin_api_required
def admin_stats():
    try:
        conn = get_db()
        c    = conn.cursor()
        c.execute('SELECT COUNT(*) as total FROM appointments')
        total_appts = c.fetchone()

        c.execute("SELECT COUNT(*) as total FROM appointments WHERE status = %s" if USE_POSTGRES
                  else "SELECT COUNT(*) as total FROM appointments WHERE status = ?", ('pending',))
        pending = c.fetchone()

        c.execute("SELECT COUNT(*) as total FROM appointments WHERE status = %s" if USE_POSTGRES
                  else "SELECT COUNT(*) as total FROM appointments WHERE status = ?", ('confirmed',))
        confirmed = c.fetchone()

        c.execute('SELECT COUNT(*) as total FROM contacts')
        total_msgs = c.fetchone()

        c.execute("SELECT COUNT(*) as total FROM contacts WHERE is_read = %s" if USE_POSTGRES
                  else "SELECT COUNT(*) as total FROM contacts WHERE is_read = 0", (False,) if USE_POSTGRES else ())
        unread = c.fetchone()

        conn.close()
        return jsonify({
            'success': True,
            'stats': {
                'total_appointments': dict(total_appts)['total'],
                'pending':            dict(pending)['total'],
                'confirmed':          dict(confirmed)['total'],
                'total_messages':     dict(total_msgs)['total'],
                'unread_messages':    dict(unread)['total'],
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)}), 500


# ═════════════════════════════════════════════
# ADMIN API — Check session
# ═════════════════════════════════════════════
@app.route('/api/admin/check', methods=['GET'])
def admin_check():
    return jsonify({'logged_in': bool(session.get('admin_logged_in'))})


# ═════════════════════════════════════════════
# Health Check (public)
# ═════════════════════════════════════════════
@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status':    'ok',
        'db':        'postgresql' if USE_POSTGRES else 'sqlite',
        'service':   'Bombay Hair Art API',
        'timestamp': datetime.utcnow().isoformat() + 'Z'
    })


# ═════════════════════════════════════════════
# Error Handlers
# ═════════════════════════════════════════════
@app.errorhandler(404)
def not_found(e):
    return jsonify({'success': False, 'message': 'Not found.'}), 404

@app.errorhandler(405)
def method_not_allowed(e):
    return jsonify({'success': False, 'message': 'Method not allowed.'}), 405

@app.errorhandler(500)
def internal_error(e):
    return jsonify({'success': False, 'message': 'Internal server error.'}), 500


# ═════════════════════════════════════════════
# Entry Point
# ═════════════════════════════════════════════
if __name__ == '__main__':
    init_db()
    print('=' * 55)
    print('  Bombay Hair Art — Server Starting')
    print(f'  DB  : {"PostgreSQL" if USE_POSTGRES else "SQLite (local)"}')
    print('  URL : http://localhost:5000')
    print('  Admin: http://localhost:5000/admin/login')
    print('  User : admin  |  Pass: BombayHairArt@2024')
    print('=' * 55)
    app.run(debug=True, port=5000, host='0.0.0.0')
