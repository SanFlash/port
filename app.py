"""Flask entrypoint for local Python, Render/Gunicorn, and Vercel."""
import hmac
import json
import os
import secrets
from datetime import timedelta
from functools import wraps
from pathlib import Path
from urllib.parse import urlsplit
from xml.sax.saxutils import escape

import click
from dotenv import load_dotenv
from flask import Flask, jsonify, redirect, render_template, request, session, Response
from werkzeug.security import check_password_hash
from sqlalchemy import create_engine, delete, insert, select, update
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.pool import NullPool
import database as db

ROOT = Path(__file__).resolve().parent
load_dotenv(ROOT / '.env')
NAV = ['About','Expertise','Work','Case Studies','Research','Marketing','Content','YouTube','Resume','Contact']
SECTIONS = ['Profile','Roles','Experience','Education','Skills','Projects','Case Studies','Research','Marketing','SEO','Meta Ads','Content','YouTube','Social Links','Resume','Media','Contact submissions','Analytics','Settings']
STATUSES = {'DRAFT','PUBLISHED','PRIVATE','ARCHIVED'}

def create_app(config=None):
    app = Flask(__name__, static_folder='public', static_url_path='')
    hosted = bool(os.getenv('VERCEL') or os.getenv('RENDER') or os.getenv('APP_ENV') == 'production')
    app.config.update(SECRET_KEY=os.getenv('AUTH_SECRET') or (None if hosted else secrets.token_hex(32)),
        ADMIN_EMAIL=os.getenv('ADMIN_EMAIL', ''), ADMIN_PASSWORD=os.getenv('ADMIN_PASSWORD', ''),
        ADMIN_PASSWORD_HASH=os.getenv('ADMIN_PASSWORD_HASH', ''),
        DATABASE_URL=os.getenv('DATABASE_URL', ''), SITE_URL=os.getenv('SITE_URL') or os.getenv('NEXT_PUBLIC_SITE_URL'),
        SESSION_COOKIE_NAME='portfolio_admin', SESSION_COOKIE_HTTPONLY=True,
        SESSION_COOKIE_SECURE=hosted, SESSION_COOKIE_SAMESITE='Lax',
        PERMANENT_SESSION_LIFETIME=timedelta(hours=8), MAX_CONTENT_LENGTH=1024*1024)
    if config:
        app.config.update(config)
    if hosted and not app.config['SECRET_KEY']:
        raise RuntimeError('Set AUTH_SECRET before deployment.')
    url = app.config['DATABASE_URL']
    if not url and not hosted:
        (ROOT / 'instance').mkdir(exist_ok=True)
        url = 'sqlite:///' + str(ROOT / 'instance/portfolio.db')
    if url.startswith(('postgres://', 'postgresql://')):
        url = 'postgresql+psycopg://' + url.split('://', 1)[1]
    if hosted and url and not url.startswith('postgresql+psycopg://'):
        raise RuntimeError('Use a PostgreSQL DATABASE_URL for persistent hosted storage.')
    options = {'pool_pre_ping': True}
    if url.startswith('postgresql+psycopg://'):
        options.update(poolclass=NullPool, connect_args={'connect_timeout': 10})
    engine = create_engine(url, **options) if url else None
    app.extensions['portfolio_engine'] = engine
    content = json.loads((ROOT / 'data/portfolio.json').read_text())
    seed_content = json.loads((ROOT / 'data/database_seed.json').read_text())
    showcase = json.loads((ROOT / 'data/showcase.json').read_text())

    def require_engine():
        if engine is None:
            raise SQLAlchemyError('Database not configured')
        return engine

    def admin_only(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            if session.get('role') != 'admin':
                return jsonify(error='Unauthorized'), 401
            return fn(*args, **kwargs)
        return wrapped

    def payload():
        body = request.get_json(silent=True)
        return body if isinstance(body, dict) else {}

    def serialize(row):
        return {k: v.isoformat(timespec='milliseconds')+'Z' if hasattr(v, 'isoformat') else v
                for k, v in row.items()}

    @app.before_request
    def origin_check():
        if request.method in {'POST','PATCH','DELETE'}:
            origin = request.headers.get('Origin')
            if origin and urlsplit(origin).netloc != request.host:
                return jsonify(error='Unauthorized'), 403
            if request.headers.get('Sec-Fetch-Site') == 'cross-site':
                return jsonify(error='Unauthorized'), 403

    @app.after_request
    def private_cache(response):
        if request.path.startswith(('/admin','/api/cms','/api/auth')):
            response.headers['Cache-Control'] = 'no-store'
        response.headers['X-Content-Type-Options'] = 'nosniff'
        return response

    @app.errorhandler(SQLAlchemyError)
    def database_error(error):
        # Do not return connection credentials or SQL parameters to callers.
        app.logger.error('Database operation failed (%s)', type(error).__name__)
        return jsonify(error='Database unavailable'), 503

    @app.errorhandler(IntegrityError)
    def conflict(error):
        return jsonify(error='Item conflicts with existing content'), 409

    @app.get('/')
    def home():
        json_ld = {'@context':'https://schema.org','@type':'Person',
            'name':content['profile']['name'],'jobTitle':content['profile']['headline'],
            'address':content['profile']['location']}
        if app.config['SITE_URL']:
            json_ld['url'] = app.config['SITE_URL']
        return render_template('home.html', **content, nav=NAV, year=db.now().year, json_ld=json_ld,
            showcase=showcase, contact_profile=seed_content['profile'],
            career=[{'title':t, **d} for c,t,d in seed_content['items'] if c=='experience'],
            education=[{'title':t, **d} for c,t,d in seed_content['items'] if c=='education'])

    @app.get('/admin')
    def admin():
        return render_template('admin.html', authenticated=session.get('role') == 'admin', sections=SECTIONS)

    @app.post('/api/auth/logout')
    def logout():
        session.clear()
        return jsonify(ok=True)

    @app.get('/resume.txt')
    def resume_download():
        profile = seed_content['profile']
        lines = [profile['name'], profile['headline'], profile['location'],
                 profile['email'] + ' | ' + profile['phone'], '', content['profile']['summary'], '', 'EXPERIENCE']
        for collection, title, details in seed_content['items']:
            if collection == 'experience':
                lines += [title, details['organization'] + ' | ' + details['dates'], details['description'], '']
        for collection_name in ['education', 'project']:
            lines += ['', collection_name.upper()]
            for collection, title, details in seed_content['items']:
                if collection == collection_name:
                    lines += [title, *[str(value) for value in details.values()], '']
        lines += ['SKILLS', ', '.join(content['skills']), '', 'LINKS']
        lines += [title + ': ' + details['url'] for collection,title,details in seed_content['items'] if 'url' in details]
        return Response('\n'.join(lines), mimetype='text/plain', headers={'Content-Disposition':'attachment; filename=Falguni-Chauhan-Resume.txt'})

    @app.get('/onboarding')
    def onboarding():
        return render_template('onboarding.html')

    @app.post('/api/auth/login')
    def login():
        email, password = request.form.get('email',''), request.form.get('password','')
        password_ok = (hmac.compare_digest(password.encode(), app.config['ADMIN_PASSWORD'].encode())
            if app.config['ADMIN_PASSWORD'] else bool(app.config['ADMIN_PASSWORD_HASH']) and check_password_hash(app.config['ADMIN_PASSWORD_HASH'], password))
        if not (app.config['ADMIN_EMAIL'] and hmac.compare_digest(email.encode(), app.config['ADMIN_EMAIL'].encode()) and password_ok):
            return jsonify(error='Invalid credentials'), 401
        session.clear()
        session.permanent = True
        session['role'] = 'admin'
        return jsonify(ok=True)

    @app.route('/api/cms', methods=['GET','POST'])
    @admin_only
    def cms():
        with require_engine().begin() as conn:
            if request.method == 'GET':
                rows = conn.execute(select(db.items).where(db.items.c.collection == request.args.get('collection',''))
                                    .order_by(db.items.c.updatedAt.desc())).mappings()
                return jsonify(items=[serialize(r) for r in rows])
            body = payload()
            if not all(isinstance(body.get(k), str) and body[k].strip() for k in ('collection','title')):
                return jsonify(error='collection and title required'), 400
            status = body.get('status', 'DRAFT')
            if not isinstance(status, str) or status not in STATUSES:
                return jsonify(error='Invalid status'), 400
            row = conn.execute(insert(db.items).values(collection=body['collection'],title=body['title'],
                status=status,data=body.get('data') or {},source='manual').returning(db.items)).mappings().one()
            return jsonify(item=serialize(row))

    @app.route('/api/cms/<item_id>', methods=['PATCH','DELETE'])
    @admin_only
    def item(item_id):
        with require_engine().begin() as conn:
            if not conn.execute(select(db.items.c.id).where(db.items.c.id == item_id)).first():
                return jsonify(error='Not found'), 404
            if request.method == 'DELETE':
                conn.execute(delete(db.items).where(db.items.c.id == item_id))
                return jsonify(ok=True)
            body = payload()
            allowed = {'collection','title','slug','status','featured','position','data','source'}
            changes = {k:v for k,v in body.items() if k in allowed}
            for k in ('collection','title','source'):
                if k in changes and (not isinstance(changes[k],str) or not changes[k].strip()):
                    return jsonify(error='Invalid item'), 400
            if 'status' in changes and (not isinstance(changes['status'],str) or changes['status'] not in STATUSES):
                return jsonify(error='Invalid status'), 400
            if 'featured' in changes and type(changes['featured']) is not bool:
                return jsonify(error='Invalid item'), 400
            if 'position' in changes and type(changes['position']) is not int:
                return jsonify(error='Invalid item'), 400
            if 'slug' in changes and changes['slug'] is not None and not isinstance(changes['slug'],str):
                return jsonify(error='Invalid item'), 400
            if 'data' in changes and changes['data'] is None:
                return jsonify(error='Invalid item'), 400
            changes['updatedAt'] = db.now()
            row = conn.execute(update(db.items).where(db.items.c.id == item_id).values(**changes)
                .returning(db.items)).mappings().one()
            return jsonify(item=serialize(row))

    @app.post('/api/contact')
    def contact():
        values = {k:request.form.get(k,'').strip() for k in ('name','email','message')}
        if not all(values.values()):
            return jsonify(error='Name, email and message are required'), 400
        values.update({k:request.form.get(k) or None for k in ('company','projectType','budget','timeline')})
        with require_engine().begin() as conn:
            conn.execute(insert(db.contacts).values(**values))
        if request.accept_mimetypes.best == 'application/json':
            return jsonify(ok=True)
        return redirect('/#contact', code=303)

    @app.post('/api/events')
    def event():
        body = payload()
        if not isinstance(body.get('name'),str) or not isinstance(body.get('path'),str):
            return jsonify(error='Invalid event'), 400
        with require_engine().begin() as conn:
            conn.execute(insert(db.events).values(name=body['name'],path=body['path'],metadata=body.get('metadata')))
        return jsonify(ok=True)

    @app.get('/robots.txt')
    def robots():
        site = (app.config['SITE_URL'] or request.url_root).rstrip('/')
        return f'User-Agent: *\nAllow: /\nDisallow: /admin\n\nSitemap: {site}/sitemap.xml\n', 200, {'Content-Type':'text/plain; charset=utf-8'}

    @app.get('/sitemap.xml')
    def sitemap():
        site = escape((app.config['SITE_URL'] or request.url_root).rstrip('/'))
        return (f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">'
                f'<url><loc>{site}</loc><lastmod>{db.now().isoformat()}Z</lastmod>'
                '<changefreq>weekly</changefreq><priority>1</priority></url></urlset>'), 200, {'Content-Type':'application/xml'}

    @app.get('/healthz')
    def health():
        return jsonify(status='ok')

    @app.cli.command('init-db')
    def init_db():
        db.initialize(require_engine())
        click.echo('Database tables initialized.')

    @app.cli.command('seed-db')
    def seed_db():
        db.seed(require_engine())
        click.echo('Original seed content loaded; existing records preserved.')

    return app

app = create_app()
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT','5000')))
