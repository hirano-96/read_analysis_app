from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('author', __name__, url_prefix='/author')

@bp.route('/')
def index():
    db = get_db()
    authors = db.execute(
        'SELECT a.id, a.name, a.created, u.username as created_by'
        ' FROM author a JOIN user u ON a.created_by = u.id'
        ' ORDER BY a.name ASC'
    ).fetchall()
    return render_template('author/index.html', authors=authors)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        name = request.form['name']
        error = None

        if not name:
            error = 'Author name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            try:
                db.execute(
                    'INSERT INTO author (name, created_by) VALUES (?, ?)',
                    (name, g.user['id'])
                )
                db.commit()
            except db.IntegrityError:
                error = f"Author {name} is already registered."
                flash(error)
            else:
                return redirect(url_for('author.index'))

    return render_template('author/create.html') 