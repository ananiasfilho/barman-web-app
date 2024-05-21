import json, datetime, subprocess
import random, string
from flask import Flask, render_template, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_user import current_user, login_required, roles_required, UserManager, UserMixin
from flask_caching import Cache

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('config.py')
    cache = Cache(app)

    db = SQLAlchemy(app)

    class User(db.Model, UserMixin):
        __tablename__ = 'users'
        id = db.Column(db.Integer, primary_key=True)
        active = db.Column('is_active', db.Boolean(), nullable=False, server_default='1')
        username = db.Column(db.String(100, collation='NOCASE'), nullable=False, unique=True)
        password = db.Column(db.String(255), nullable=False, server_default='')
        email_confirmed_at = db.Column(db.DateTime())
        first_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        last_name = db.Column(db.String(100, collation='NOCASE'), nullable=False, server_default='')
        roles = db.relationship('Role', secondary='user_roles')

    class Role(db.Model):
        __tablename__ = 'roles'
        id = db.Column(db.Integer(), primary_key=True)
        name = db.Column(db.String(50), unique=True)

    class UserRoles(db.Model):
        __tablename__ = 'user_roles'
        id = db.Column(db.Integer(), primary_key=True)
        user_id = db.Column(db.Integer(), db.ForeignKey('users.id', ondelete='CASCADE'))
        role_id = db.Column(db.Integer(), db.ForeignKey('roles.id', ondelete='CASCADE'))

    user_manager = UserManager(app, db, User)

    # Create all database tables within the application context
    with app.app_context():
        db.create_all()

        appconf = app.config.get_namespace("APP_CONF_", False)

        if not User.query.filter(User.username == appconf["ADMIN_USERNAME"]).first():
            user = User(
                username=appconf["ADMIN_USERNAME"],
                email_confirmed_at=datetime.datetime.utcnow(),
                password=user_manager.hash_password(appconf["ADMIN_PASSWORD"]),
            )
            user.roles.append(Role(name='SuperAdmin'))
            db.session.add(user)
            db.session.commit()

    def run_barman_command(*args):
        command_barman = ("barman", "-f", "json", *args)
        if appconf["USE_PREFIX_COMMAND"]:
            command_barman = appconf["PREFIX_COMMAND"] + command_barman
        result = json.loads(subprocess.run(list(command_barman), stdout=subprocess.PIPE).stdout.decode("utf-8"))
        return result

    @cache.cached(key_prefix='server_list')
    def get_servers_list():
        global tab_menu
        tab_menu = run_barman_command("list-server")
        return tab_menu

    @app.route('/')
    @login_required
    def home_page():
        tab_menu = get_servers_list()
        return render_template("index_template.html", tab_menu=tab_menu)

    @app.route('/refreshlist')
    @roles_required('SuperAdmin')
    def refresh_list():
        cache.clear()
        return redirect(url_for('home_page'))

    @app.route('/listservers')
    @roles_required('SuperAdmin')
    def barman_list_servers():
        result_status = run_barman_command("list-server")
        return render_template("list_servers.html", tab=result_status, tab_menu=tab_menu)

    @app.route('/statusserver/<server>')
    @roles_required('SuperAdmin')
    def barman_status_server(server):
        result_status = run_barman_command("status", server)
        return render_template("status_server.html", tab=result_status, tab_menu=tab_menu)

    @app.route('/checkserver/<server>')
    @roles_required('SuperAdmin')
    def barman_check_server(server):
        result_status = run_barman_command("check", server)
        return render_template("check_server.html", tab=result_status, tab_menu=tab_menu)

    @app.route('/listbackupsserver/<server>')
    @roles_required('SuperAdmin')
    def barman_listbackup_server(server):
        result_status = run_barman_command("list-backup", server)
        datejour = datetime.date.today().strftime('%Y%m%d')
        return render_template("list_backup.html", tab=result_status, tab_menu=tab_menu, datejour=datejour)

    @app.route('/showserver/<server>')
    @roles_required('SuperAdmin')
    def barman_show_server(server):
        result_status = run_barman_command("show-server", server)
        return render_template("show_server.html", tab=result_status, tab_menu=tab_menu)

    @app.route('/showbackup/<server>/<backupid>')
    @roles_required('SuperAdmin')
    def barman_show_backup(server, backupid):
        result_status = run_barman_command("show-backup", server, backupid)
        return render_template("show_backup.html", tab=result_status, tab_menu=tab_menu)

    @app.route('/deletebackup/<server>/<backupid>')
    @roles_required('SuperAdmin')
    def barman_delete_backup(server, backupid):
        result_status = run_barman_command("delete", server, backupid)
        return render_template("delete_backup.html", tab=result_status, tab_menu=tab_menu, server=server)

    @app.route('/prelaunchbackup/<server>')
    @roles_required('SuperAdmin')
    def barman_prelaunch_backup(server):
        return render_template("pre_launch_backup.html", tab_menu=tab_menu, server=server)

    @app.route('/launchbackup/<server>')
    @roles_required('SuperAdmin')
    def barman_launch_backup(server):
        result_status = run_barman_command("backup", server)
        return render_template("launch_backup.html", tab=result_status, tab_menu=tab_menu, server=server)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(host='127.0.0.1', port=5555, debug=True)
