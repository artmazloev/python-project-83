# page_analyzer/app.py

import os
import requests
from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
import atexit

import page_analyzer.utils as utils
# Импортируем наш новый модуль как db
import page_analyzer.db as db

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Регистрируем функцию для закрытия пула соединений при выходе из приложения
atexit.register(db.close_pool)


@app.route('/')
def index_get() -> str:
    return render_template('index.html')


@app.post('/urls')
def index_post():
    address = request.form.get('url', '')
    clean_url = utils.normalize_url(address)
    try:
        utils.check_url(clean_url)
    except (utils.URLTooLong, utils.URLNotValid) as e:
        flash(f'Некорректный URL: {e}', 'danger')
        return render_template(
            'index.html',
            search=address), 422

    # Используем новые функции напрямую
    id_url = db.find_url_name(clean_url)
    if id_url:
        flash('Страница уже существует', 'info')
    else:
        id_url = db.save_url(clean_url)
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id_url), code=302)


@app.route('/urls')
def urls():
    # Используем новые функции напрямую
    addresses = db.get_content()
    return render_template(
        'urls.html',
        addresses=addresses
    )


@app.route('/urls/<int:id>')
def url(id):
    # Используем новые функции напрямую
    address = db.exist_url_id(id)
    if not address:
        return render_template('not_found.html'), 404
    
    urls_check = db.get_content_check(id)
    return render_template(
        'url.html',
        address=address,
        urls_check=urls_check
    )


@app.post('/urls/<int:id>/check')
def check_url(id):
    address = db.exist_url_id(id)
    if not address:
        return render_template('not_found.html'), 404
    
    url_name = address['name']
    
    try:
        content = utils.get_content(url_name)
        content['url_id'] = id
        # Используем новые функции напрямую
        db.save_url_check(content)
        flash('Страница успешно проверена', 'success')
    except requests.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
        
    return redirect(url_for('url', id=id))
