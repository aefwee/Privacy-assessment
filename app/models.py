from flask_login import UserMixin
from . import db, login_manager


class Admin(UserMixin, db.Model):
    __tablename__ = 'admin'
    admin_id = db.Column(db.String(32), primary_key=True)
    admin_name = db.Column(db.String(32))
    password = db.Column(db.String(24))
    right = db.Column(db.String(32))

    def get_id(self):
        return self.admin_id

    def verify_password(self, password):
        if password == self.password:
            return True
        else:
            return False

    def __repr__(self):
        return '<Admin %r>' % self.admin_name

class Case(db.Model):
    __tablename__ = 'Case'
    case_id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    title = db.Column(db.String(64))
    client = db.Column(db.String(32))
    legal_basis = db.Column(db.String(512))
    information_nature = db.Column(db.String(32))
    violation_mode = db.Column(db.String(32))
    scale_scope = db.Column(db.String(128))
    illegal_gains = db.Column(db.String(256))
    attitude_conduct = db.Column(db.String(64))
    judical_outcome = db.Column(db.String(1024))
    def __repr__(self):
        return '<Case %r>' % self.title

@login_manager.user_loader
def load_user(admin_id):
    return Admin.query.get(int(admin_id))