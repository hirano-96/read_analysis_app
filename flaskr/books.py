from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from datetime import datetime

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint('books', __name__)

@bp.route('/')
def index():
    db = get_db()
    # 読書記録と本の情報を結合して取得
    records = db.execute(
        'SELECT r.id, r.start_date, r.end_date, r.impression, r.created as record_created,'
        ' b.title, b.publisher,'
        ' a.name as author_name,'
        ' g.name as genre_name,'
        ' u.username'
        ' FROM reading_record r'
        ' JOIN book_info b ON r.book_id = b.id'
        ' JOIN author a ON b.author_id = a.id'
        ' JOIN genre g ON b.genre_id = g.id'
        ' JOIN user u ON r.reader_id = u.id'
        ' ORDER BY r.created DESC'
    ).fetchall()
    return render_template('books/index.html', records=records)

@bp.route('/books')
def book_list():
    db = get_db()
    books = db.execute(
        'SELECT b.id, b.title, b.publisher, b.created,'
        ' a.name as author_name,'
        ' g.name as genre_name,'
        ' u.username as registered_by'
        ' FROM book_info b'
        ' JOIN author a ON b.author_id = a.id'
        ' JOIN genre g ON b.genre_id = g.id'
        ' JOIN user u ON b.created_by = u.id'
        ' ORDER BY b.created DESC'
    ).fetchall()
    return render_template('books/book_list.html', books=books)

@bp.route('/books/create', methods=('GET', 'POST'))
@login_required
def create_book():
    db = get_db()
    authors = db.execute('SELECT id, name FROM author ORDER BY name ASC').fetchall()
    genres = db.execute('SELECT id, name FROM genre ORDER BY name ASC').fetchall()

    if request.method == 'POST':
        title = request.form['title']
        author_id = request.form['author_id']
        genre_id = request.form['genre_id']
        publisher = request.form['publisher']
        error = None

        if not title:
            error = 'Title is required.'
        elif not author_id:
            error = 'Author is required.'
        elif not genre_id:
            error = 'Genre is required.'
        elif not publisher:
            error = 'Publisher is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO book_info (title, author_id, genre_id, publisher, created_by)'
                ' VALUES (?, ?, ?, ?, ?)',
                (title, author_id, genre_id, publisher, g.user['id'])
            )
            db.commit()
            return redirect(url_for('books.book_list'))

    return render_template('books/create_book.html', authors=authors, genres=genres)

@bp.route('/record/create/<int:book_id>', methods=('GET', 'POST'))
@login_required
def create_record(book_id):
    db = get_db()
    book = db.execute(
        'SELECT b.id, b.title, b.publisher,'
        ' a.name as author_name,'
        ' g.name as genre_name'
        ' FROM book_info b'
        ' JOIN author a ON b.author_id = a.id'
        ' JOIN genre g ON b.genre_id = g.id'
        ' WHERE b.id = ?',
        (book_id,)
    ).fetchone()
    
    if book is None:
        abort(404, f"Book id {book_id} doesn't exist.")

    if request.method == 'POST':
        start_date = request.form['start_date'] or None
        end_date = request.form['end_date'] or None
        impression = request.form['impression']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO reading_record (book_id, reader_id, start_date, end_date, impression)'
                ' VALUES (?, ?, ?, ?, ?)',
                (book_id, g.user['id'], start_date, end_date, impression)
            )
            db.commit()
            return redirect(url_for('books.index'))

    return render_template('books/create_record.html', book=book)

def get_record(id, check_reader=True):
    record = get_db().execute(
        'SELECT r.id, book_id, reader_id, start_date, end_date, impression,'
        ' b.title, b.publisher,'
        ' a.name as author_name,'
        ' g.name as genre_name,'
        ' u.username'
        ' FROM reading_record r'
        ' JOIN book_info b ON r.book_id = b.id'
        ' JOIN author a ON b.author_id = a.id'
        ' JOIN genre g ON b.genre_id = g.id'
        ' JOIN user u ON r.reader_id = u.id'
        ' WHERE r.id = ?',
        (id,)
    ).fetchone()

    if record is None:
        abort(404, f"Record id {id} doesn't exist.")

    if check_reader and record['reader_id'] != g.user['id']:
        abort(403)

    return record

@bp.route('/record/<int:id>/update', methods=('GET', 'POST'))
@login_required
def update_record(id):
    record = get_record(id)

    if request.method == 'POST':
        start_date = request.form['start_date'] or None
        end_date = request.form['end_date'] or None
        impression = request.form['impression']
        error = None

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE reading_record SET start_date = ?, end_date = ?, impression = ?'
                ' WHERE id = ?',
                (start_date, end_date, impression, id)
            )
            db.commit()
            return redirect(url_for('books.index'))

    return render_template('books/update_record.html', record=record)

@bp.route('/record/<int:id>/delete', methods=('POST',))
@login_required
def delete_record(id):
    get_record(id)
    db = get_db()
    db.execute('DELETE FROM reading_record WHERE id = ?', (id,))
    db.commit()
    return redirect(url_for('books.index')) 