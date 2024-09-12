from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField
from wtforms.validators import DataRequired, EqualTo, Length


class Login(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired()])
    password = PasswordField(u'密码', validators=[DataRequired()])
    submit = SubmitField(u'登录')

class Register(FlaskForm):
    name = StringField(u'用户名', validators=[Length(1, 64)])
    account = StringField(u'账号', validators=[DataRequired(), Length(1, 12)])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(1, 18)])
    submit = SubmitField(u'提交注册')

class ChangePasswordForm(FlaskForm):
    old_password = PasswordField(u'原密码', validators=[DataRequired()])
    password = PasswordField(u'新密码', validators=[DataRequired(), EqualTo('password2', message=u'两次密码必须一致！')])
    password2 = PasswordField(u'确认新密码', validators=[DataRequired()])
    submit = SubmitField(u'确认修改')

class EditInfoForm(FlaskForm):
    name = StringField(u'用户名', validators=[Length(1, 32)])
    submit = SubmitField(u'提交')

class NewStoreForm(FlaskForm):
    admin_id = StringField(validators=[DataRequired(), Length(1, 64)])
    admin_name = StringField(validators=[DataRequired(), Length(1, 64)])
    password = StringField(validators=[DataRequired(), Length(1, 64)])
    right = StringField(validators=[DataRequired(), Length(1, 64)])
    submit = SubmitField(u'提交')

class NewCaseForm(FlaskForm):
    title = StringField(validators=[DataRequired(), Length(1,32)])
    client = StringField(validators=[DataRequired(), Length(1, 64)])
    legal_basis = StringField(validators=[DataRequired(), Length(1, 32)])
    information_nature = StringField(validators=[DataRequired(), Length(1, 64)])
    violation_mode = StringField(validators=[DataRequired(), Length(1, 64)])
    scale_scope = StringField(validators=[DataRequired(), Length(1, 64)])
    illegal_gains = StringField(validators=[DataRequired(), Length(1, 256)])
    attitude_conduct = StringField(validators=[DataRequired(), Length(1, 512)])
    judical_outcome = StringField(validators=[DataRequired(), Length(1, 1024)])
    submit = SubmitField(u'提交')

class CaseMatchForm(FlaskForm):
    client = StringField(validators=[DataRequired(), Length(1, 64)])
    legal_basis = StringField(validators=[DataRequired(), Length(1, 32)])
    information_nature = StringField(validators=[DataRequired(), Length(1, 64)])
    violation_mode = StringField(validators=[DataRequired(), Length(1, 64)])
    scale_scope = StringField(validators=[DataRequired(), Length(1, 64)])
    illegal_gains = StringField(validators=[DataRequired(), Length(1, 256)])
    attitude_conduct = StringField(validators=[DataRequired(), Length(1, 512)])
    submit = SubmitField(u'匹配')

class SearchCaseForm(FlaskForm):
    methods = [('title', '案例标题'), ('client', '当事人'), ('information_nature', '侵犯信息性质'), ('violation_mode', '侵犯方式')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')

#账户查询
class AccountSearchForm(FlaskForm):
    methods = [('admin_name', '用户名'), ('admin_id', '账号')]
    method = SelectField(choices=methods, validators=[DataRequired()], coerce=str)
    content = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')
