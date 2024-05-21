# barman-web-app

A Python Flask web app to use as an UI for pgbarman.
This is a really small and simple project using the python Flask framework.

# Installation

- create a virtualenv
```shell
virtualenv barman-web-app
cd barman-web-app
source bin/activate
```
- clone this projet
```shell
git clone https://github.com/clmntpllr/barman-web-app.git
```
- then install requirements
```shell
cd barman-web-app
python -m pip install pip --upgrade
```

- Since flask-users is EOF (End Of Life), we need clone and install it on our environment.
```
git clone https://github.com/lingthio/Flask-User.git
cd Flask-User/
python -m pip install --upgrade build
python -m build
cd dist/
python -m pip install Flask_User-1.0.2.3-py2.py3-none-any.whl 
# back to main folder
cd ../../
```
- Then install requirements
```
python -m pip install -r requirements.txt
```
- config the app by editing config.py to suits your needs
- to generate a new secret key :
```python
import secrets; 
print(secrets.token_hex())
```
- try the app by launching it as a test server
```shell
python barman-web-app.py
```
- or deploy with gunicorn
```shell
gunicorn "barman_app:create_app()"
# or
gunicorn -w 4 -b 0.0.0.0:4000 "barman_app:create_app()"
```
- or use a uwsgi server with nginx
```shell
uwsgi -s /tmp/barman-web-app.sock  --virtualenv /yourvenvdir --manage-script-name --mount /barman_app=wsgi:app
```
