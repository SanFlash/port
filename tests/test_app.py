import json
import tempfile
import unittest
from pathlib import Path
from sqlalchemy import select, func
from app import create_app
import database as db
ROOT=Path(__file__).resolve().parents[1]
class PortfolioTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory()
        self.app=create_app({'TESTING':True,'SECRET_KEY':'test','ADMIN_EMAIL':'a@example.com','ADMIN_PASSWORD':'password','DATABASE_URL':'sqlite:///'+self.tmp.name+'/test.db','SITE_URL':'https://portfolio.example.com','SESSION_COOKIE_SECURE':False})
        self.engine=self.app.extensions['portfolio_engine'];db.initialize(self.engine)
        self.client=self.app.test_client()
    def tearDown(self):
        self.engine.dispose();self.tmp.cleanup()
    def login(self):
        return self.client.post('/api/auth/login',data={'email':'a@example.com','password':'password'})
    def test_pages_content_and_assets(self):
        from html import unescape
        response=self.client.get('/');self.assertEqual(response.status_code,200)
        html=unescape(response.get_data(as_text=True))
        data=json.loads((ROOT/'data/portfolio.json').read_text())
        for value in data['profile'].values():self.assertIn(value,html)
        for key in ['skills','projects']:
            for value in data[key]:
                for part in value.split(' — '):self.assertIn(part,html)
        for role in json.loads((ROOT/'data/database_seed.json').read_text())['items']:
            if role[0]=='experience':self.assertIn(role[2]['description'],html)
        for path in ['/resume.txt','/assets/enhanced.css','/assets/portfolio.js','/assets/sculpture.js','/admin','/onboarding','/robots.txt','/sitemap.xml','/healthz','/assets/admin.js','/assets/onboarding.js']:
            with self.client.get(path) as response:self.assertEqual(response.status_code,200,path)
        with self.client.get('/assets/styles.css') as response:self.assertEqual(response.data,(ROOT/'original-nextjs/app/styles.css').read_bytes())
        self.assertEqual(self.client.get('/app.py').status_code,404)
        self.assertEqual(self.client.get('/missing').status_code,404)
    def test_auth_cms_lifecycle(self):
        for method,path in [('get','/api/cms'),('post','/api/cms'),('patch','/api/cms/x'),('delete','/api/cms/x')]:
            self.assertEqual(getattr(self.client,method)(path).status_code,401)
        self.assertEqual(self.client.post('/api/auth/login',data={'email':'a@example.com','password':'bad'}).status_code,401)
        response=self.login();self.assertEqual(response.status_code,200)
        self.assertIn('HttpOnly',response.headers['Set-Cookie']);self.assertIn('SameSite=Lax',response.headers['Set-Cookie'])
        self.assertIn('Add new',self.client.get('/admin').get_data(as_text=True))
        item=self.client.post('/api/cms',json={'collection':'projects','title':'Original title','data':{'body':'Keep exactly'}}).json['item']
        self.assertEqual(item['status'],'DRAFT')
        self.assertEqual(self.client.get('/api/cms?collection=projects').json['items'][0]['title'],'Original title')
        self.assertEqual(self.client.get('/api/cms?collection=roles').json['items'],[])
        published=self.client.patch('/api/cms/'+item['id'],json={'status':'PUBLISHED'}).json['item']
        self.assertEqual(published['status'],'PUBLISHED');self.assertEqual(published['data'],{'body':'Keep exactly'})
        self.assertEqual(self.client.delete('/api/cms/'+item['id']).status_code,200)
        self.assertEqual(self.client.get('/api/cms?collection=projects').json['items'],[])
        self.assertEqual(self.client.patch('/api/cms/'+item['id'],json={'status':'PUBLISHED'}).status_code,404)
    def test_invalid_writes(self):
        self.login()
        for body in [{},{'collection':[],'title':'X'},{'collection':'projects','title':'X','status':[]},[]]:
            self.assertEqual(self.client.post('/api/cms',json=body).status_code,400)
        self.assertEqual(self.client.post('/api/events',json=[]).status_code,400)
        self.assertEqual(self.client.post('/api/contact',data={'name':'X'}).status_code,400)
        self.assertEqual(self.client.post('/api/cms',json={'collection':'projects','title':'X'},headers={'Origin':'https://other.example'}).status_code,403)
    def test_contact_events_persistence(self):
        contact={'name':'Name','email':'name@example.com','company':'Company','message':'Original message','projectType':'Brand','budget':'100','timeline':'Month'}
        response=self.client.post('/api/contact',data=contact)
        self.assertEqual(response.status_code,303);self.assertEqual(response.headers['Location'],'/#contact')
        self.assertEqual(self.client.post('/api/events',json={'name':'view','path':'/','metadata':{'source':'test'}}).status_code,200)
        with self.engine.connect() as conn:
            row=conn.execute(select(db.contacts)).mappings().one()
            for key,value in contact.items():self.assertEqual(row[key],value)
            self.assertEqual(conn.execute(select(db.events)).mappings().one()['metadata'],{'source':'test'})
        second=create_app(dict(self.app.config));engine=second.extensions['portfolio_engine']
        with engine.connect() as conn:self.assertEqual(conn.scalar(select(func.count()).select_from(db.contacts)),1)
        engine.dispose()
    def test_seed_exact_and_idempotent(self):
        db.seed(self.engine);db.seed(self.engine)
        seed=json.loads((ROOT/'data/database_seed.json').read_text())
        with self.engine.connect() as conn:
            rows=conn.execute(select(db.items)).mappings().all();self.assertEqual(len(rows),len(seed['items']))
            for collection,title,data in seed['items']:
                self.assertTrue(any(r['collection']==collection and r['title']==title and r['data']==data for r in rows))
            profile=conn.execute(select(db.profile)).mappings().one()
            for key,value in seed['profile'].items():self.assertEqual(profile[key],value)
    def test_configured_admin_and_logout(self):
        from werkzeug.security import generate_password_hash
        configured=create_app({'TESTING':True,'DATABASE_URL':self.app.config['DATABASE_URL'],
            'ADMIN_EMAIL':'test-admin@example.com','ADMIN_PASSWORD':'',
            'ADMIN_PASSWORD_HASH':generate_password_hash('test-only-password')})
        client=configured.test_client()
        self.assertEqual(client.post('/api/auth/login',data={'email':'test-admin@example.com','password':'test-only-password'}).status_code,200)
        self.assertEqual(client.get('/api/cms').status_code,200)
        self.assertEqual(client.post('/api/auth/logout').status_code,200)
        self.assertEqual(client.get('/api/cms').status_code,401)
        configured.extensions['portfolio_engine'].dispose()
    def test_unconfigured_admin_is_disabled(self):
        configured=create_app({'TESTING':True,'DATABASE_URL':self.app.config['DATABASE_URL'],
            'ADMIN_EMAIL':'','ADMIN_PASSWORD':'','ADMIN_PASSWORD_HASH':''})
        client=configured.test_client()
        self.assertEqual(client.post('/api/auth/login',data={'email':'','password':''}).status_code,503)
        configured.extensions['portfolio_engine'].dispose()
    def test_resume_and_ajax_contact(self):
        response=self.client.get('/resume.txt')
        self.assertIn('attachment',response.headers['Content-Disposition'])
        text=response.get_data(as_text=True)
        for value in ['Falguni Chauhan','Bhuttico','Samarth Scheme','NIFT','falgunichouhan1234@gmail.com']:
            self.assertIn(value,text)
        response=self.client.post('/api/contact',data={'name':'Name','email':'test@example.com','message':'Hi'},headers={'Accept':'application/json'})
        self.assertEqual(response.json,{'ok':True})
    def test_cli_and_seo(self):
        runner=self.app.test_cli_runner()
        self.assertEqual(runner.invoke(args=['init-db']).exit_code,0)
        self.assertEqual(runner.invoke(args=['seed-db']).exit_code,0)
        self.assertIn('https://portfolio.example.com/sitemap.xml',self.client.get('/robots.txt').get_data(as_text=True))
        import xml.etree.ElementTree as ET
        root=ET.fromstring(self.client.get('/sitemap.xml').data)
        self.assertEqual(root[0][0].text,'https://portfolio.example.com')

class AdminConfigurationTests(unittest.TestCase):
    def app(self, **overrides):
        return create_app({'TESTING':True,'SECRET_KEY':'test-only-secret',
            'DATABASE_URL':'sqlite:///:memory:', 'ADMIN_EMAIL':' Owner@Example.com ',
            'ADMIN_PASSWORD':'test-only-password','ADMIN_PASSWORD_HASH':'',**overrides})
    def test_email_normalization(self):
        app=self.app()
        client=app.test_client()
        self.assertEqual(client.post('/api/auth/login',data={'email':' OWNER@example.COM ','password':'test-only-password'}).status_code,200)
        self.assertIn('Add new',client.get('/admin').get_data(as_text=True))
    def test_password_is_exact(self):
        client=self.app().test_client()
        self.assertEqual(client.post('/api/auth/login',data={'email':'owner@example.com','password':' test-only-password'}).status_code,401)
    def test_missing_configuration_has_specific_error(self):
        for values in [{'ADMIN_EMAIL':''},{'ADMIN_PASSWORD':'','ADMIN_PASSWORD_HASH':''}]:
            response=self.app(**values).test_client().post('/api/auth/login',data={})
            self.assertEqual(response.status_code,503)
            self.assertEqual(response.json['code'],'admin_not_configured')
    def test_bad_hash_is_not_server_crash(self):
        response=self.app(ADMIN_PASSWORD='',ADMIN_PASSWORD_HASH='unsupported$bad$hash').test_client().post('/api/auth/login',data={'email':'owner@example.com','password':'x'})
        self.assertEqual(response.status_code,503)
        self.assertEqual(response.json['code'],'admin_configuration_invalid')
    def test_local_setup_roundtrip_and_preservation(self):
        from configure_admin import configure
        from dotenv import dotenv_values
        with tempfile.TemporaryDirectory() as folder:
            path=Path(folder)/'.env'
            path.write_text('DATABASE_URL=sqlite:///existing.db\nAUTH_SECRET=existing-private-secret\nADMIN_PASSWORD=old-test-password\n')
            configure(path,' Owner@Example.com ','test-only-password')
            values=dotenv_values(path)
            self.assertEqual(values['DATABASE_URL'],'sqlite:///existing.db')
            self.assertEqual(values['AUTH_SECRET'],'existing-private-secret')
            self.assertEqual(values['ADMIN_PASSWORD'],'')
            self.assertNotIn('test-only-password',path.read_text())
            client=self.app(ADMIN_EMAIL=values['ADMIN_EMAIL'],ADMIN_PASSWORD='',ADMIN_PASSWORD_HASH=values['ADMIN_PASSWORD_HASH']).test_client()
            self.assertEqual(client.post('/api/auth/login',data={'email':'owner@example.com','password':'test-only-password'}).status_code,200)

if __name__=='__main__':unittest.main()
