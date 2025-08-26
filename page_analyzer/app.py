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

import page_analyzer.utils as utils
from page_analyzer.db import Database

app = Flask(__name__)

load_dotenv()
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')
DB = Database(DATABASE_URL)


@app.route('/')
def index_get() -> str:
    return render_template(
        'index.html',
    )


@app.post('/urls')
def index_post():
    address = request.form.get('url', '')
    clean_url = utils.normalize_url(address)
    try:
        utils.check_url(clean_url)
    except (utils.URLTooLong, utils.URLNotValid):
        flash('Некорректный URL', 'danger')
        return render_template(
            'index.html',
            search=address), 422

    id_url = DB.find_url_name(clean_url)
    if id_url:
        flash('Страница уже существует', 'success')
    else:
        id_url = DB.save_url(clean_url)
        flash('Страница успешно добавлена', 'success')
    return redirect(url_for('url', id=id_url), code=302)


@app.route('/urls')
def urls():
    addresses = DB.get_content()
    return render_template(
        'urls.html',
        addresses=addresses
    )


@app.route('/urls/<int:id>')
def url(id):
    address = DB.exist_url_id(id)
    if not address:
        return render_template('not_found.html'), 404
    urls_check = DB.get_content_check(id)
    return render_template(
        'url.html',
        address=address,
        urls_check=urls_check
    )


@app.post('/urls/<int:id>/check')
def check_url(id):
    url_name = DB.exist_url_id(id)['name']
    try:
        content = utils.get_content(url_name)
        content['url_id'] = id
        DB.save_url_check(content)
        flash('Страница успешно проверена', 'success')
    except (requests.exceptions.HTTPError,
            requests.exceptions.ConnectionError,
            requests.ReadTimeout,):
        flash('Произошла ошибка при проверке', 'danger')
    return redirect(url_for('url', id=id))
