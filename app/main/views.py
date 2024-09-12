from datetime import datetime
from flask import render_template, session, redirect, url_for, flash, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy.testing.pickleable import User
from . import main
from .forms import Login,  ChangePasswordForm, EditInfoForm, NewStoreForm, \
     NewCaseForm, SearchCaseForm, AccountSearchForm, CaseMatchForm, Register
from .. import db
from ..models import Admin, Case
import time, datetime
from werkzeug.security import generate_password_hash
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

@main.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        user = Admin.query.filter_by(admin_id=form.account.data, password=form.password.data).first()
        if user is None:
            flash('账号或密码错误！')
            return redirect(url_for('.login'))
        else:
            login_user(user)
            session['admin_id'] = user.admin_id
            session['name'] = user.admin_name
            return redirect(url_for('.user_info', id=current_user.admin_id))
    return render_template('main/login.html', form=form)


@main.route('/register', methods=['GET', 'POST'])
def register():
    form = Register()
    if form.validate_on_submit():
        # 检查账号是否已存在
        existing_user = Admin.query.filter_by(admin_id=form.account.data).first()
        if existing_user:
            flash('该账号已存在，请使用不同的账号。')
            return redirect(url_for('main.register'))

            # 创建新管理员实例并设置密码哈希
        new_admin = Admin(
            admin_id=form.account.data,
            admin_name=form.name.data,  # 假设表单中有一个名为 name 的字段
            password_hash=generate_password_hash(form.password.data),
            # 如果有其他必填字段，也在这里设置
        )

        # 将新管理员添加到数据库会话并提交
        db.session.add(new_admin)
        db.session.commit()

        flash('注册成功！请登录。')
        return redirect(url_for('main.login'))  # 假设您的登录视图函数在 main 蓝图中，且路由名为 login

    return render_template('account-register.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经登出！')
    return redirect(url_for('.login'))

@main.route('/user/<id>')
@login_required
def user_info(id):
    user = Admin.query.filter_by(admin_id=id).first()
    return render_template('main/user-info.html', user=user, name=session.get('name'))


@main.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.password2.data != form.password.data:
        flash(u'两次密码不一致！')
    if form.validate_on_submit():
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            db.session.commit()
            flash(u'已成功修改密码！')
            return redirect(url_for('.index'))
        else:
            flash(u'原密码输入错误，修改失败！')
    return render_template("main/change-password.html", form=form)


@main.route('/change_info', methods=['GET', 'POST'])
@login_required
def change_info():
    form = EditInfoForm()
    if form.validate_on_submit():
        current_user.admin_name = form.name.data
        db.session.add(current_user)
        flash(u'已成功修改个人信息！')
        return redirect(url_for('.user_info', id=current_user.admin_id))
    form.name.data = current_user.admin_name
    id = current_user.admin_id
    right = current_user.right
    return render_template('main/change-info.html', form=form, id=id, right=right)


@main.route('/case_user', methods=['GET', 'POST'])
def case_user():
    form = SearchCaseForm()
    return render_template('main/case-user.html', form=form)

def timeStamp(timeNum):
    if timeNum is None:
        return timeNum
    else:
        timeStamp = float(float(timeNum)/1000)
        timeArray = time.localtime(timeStamp)
        print(time.strftime("%Y-%m-%d", timeArray))
        return time.strftime("%Y-%m-%d", timeArray)

#添加账户
@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    form = NewStoreForm()
    if form.validate_on_submit():
            exist = Admin.query.filter_by(admin_id=request.form.get('admin_id')).first()
            if exist is not None:
                flash(u'该用户信息已经存在。')
            else:
                admin = Admin()
                admin.admin_id = request.form.get('admin_id')
                admin.password = request.form.get('password')
                admin.right = request.form.get('right')
                admin.admin_name = request.form.get('admin_name')
                db.session.add(admin)
                db.session.commit()
                flash(u'用户添加成功！')
            return redirect(url_for('.new_store'))
    return render_template('main/new-store.html', name=session.get('name'), form=form)

#添加案例
@main.route('/case_add', methods=['GET', 'POST'])
@login_required
def case_add():
    form = NewCaseForm()
    if form.validate_on_submit():
        exist = Case.query.filter_by(title=request.form.get('title')).first()
        if exist is not None:
            flash(u'该案例信息已经存在，请核对后再录入；或者填写入库表。')
        else:
            case = Case()
            case.title = request.form.get('title')
            case.client = request.form.get('client')
            case.legal_basis = request.form.get('legal_basis')
            case.information_nature = request.form.get('information_nature')
            case.violation_mode = request.form.get('violation_mode')
            case.scale_scope = request.form.get('scale_scope')
            case.illegal_gains = request.form.get('illegal_gains')
            case.attitude_conduct = request.form.get('attitude_conduct')
            case.judical_outcome = request.form.get('judical_outcome')
            db.session.add(case)
            db.session.commit()
            flash(u'案例添加成功！')
        return redirect(url_for('.case_add'))
    return render_template('main/case-add.html', name=session.get('name'), form=form)

#案例匹配
@main.route('/match', methods=['GET', 'POST'])
def match():
    form = CaseMatchForm()
    return render_template('main/matching.html', name=session.get('name'), form=form)

@main.route('/match1', methods=['GET', 'POST'])
@login_required
def match1():
    form = CaseMatchForm()
    return render_template('main/matching1.html', name=session.get('name'), form=form)

#案例查询
@main.route('/case_search', methods=['GET', 'POST'])
@login_required
def case_search():  # 这个函数里不再处理提交按钮，使用Ajax局部刷新
    form = SearchCaseForm()
    return render_template('main/case-search.html', name=session.get('name'), form=form)

#案例删除
@main.route('/case_delete',methods=['POST'])
def case_delete():
    case_id = request.form.get('case_id')

    if case_id:
        case = Case.query.get(case_id)
        if case:
            try:
                db.session.delete(case)
                db.session.commit()
                return jsonify({'status': 'success'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)})
        else:
            return jsonify({'status': 'error', 'message': '案例不存在'})
    else:
        return jsonify({'status': 'error', 'message': '无效的案例ID'})

@main.route('/cases', methods=['POST'])
def find_case():

    def find_title():
        return Case.query.filter(Case.title.like('%'+request.form.get('content')+'%')).all()

    def find_client():
        return Case.query.filter(Case.client.contains(request.form.get('content'))).all()

    def find_information_nature():
        return Case.query.filter(Case.information_nature.contains(request.form.get('content'))).all()

    def find_violation_mode():
        return Case.query.filter(Case.violation_mode.contains(request.form.get('content'))).all()

    methods = {
        'title': find_title,
        'client': find_client,
        'information_nature': find_information_nature,
        'violation_mode': find_violation_mode
    }
    cases = methods[request.form.get('method')]()
    data = []
    for case in cases:
        count = Case.query.filter_by(title=case.title).count()
        available = Case.query.filter_by(title=case.title).count()
        item = {'title': case.title, 'client': case.client, 'information_nature': case.information_nature, 'violation_mode': case.violation_mode,
                'scale_scope': case.scale_scope, 'illegal_gains': case.illegal_gains, 'attitude_conduct': case.attitude_conduct, 'judical_outcome':case.judical_outcome}
        data.append(item)
    return jsonify(data)

#账户查询
@main.route('/account_search', methods=['GET', 'POST'])
@login_required
def account_search():  # 这个函数里不再处理提交按钮，使用Ajax局部刷新
    form = AccountSearchForm()
    return render_template('main/account-search.html', name=session.get('name'), form=form)

#账号删除
@main.route('/account_delete',methods=['POST'])
def account_delete():
    admin_id = request.form.get('admin_id')

    if admin_id:
        account = Admin.query.get(admin_id)
        if account:
            try:
                db.session.delete(account)
                db.session.commit()
                return jsonify({'status': 'success'})
            except Exception as e:
                db.session.rollback()
                return jsonify({'status': 'error', 'message': str(e)})
        else:
            return jsonify({'status': 'error', 'message': '账户不存在'})
    else:
        return jsonify({'status': 'error', 'message': '无效的账户ID'})

@main.route('/accounts', methods=['POST'])
def find_account():

    def find_name():
        return Admin.query.filter(Admin.admin_name.like('%'+request.form.get('content')+'%')).all()

    def find_id():
        return Admin.query.filter(Admin.admin_id.contains(request.form.get('content'))).all()

    methods = {
        'admin_name': find_name,
        'admin_id': find_id,
    }
    accounts = methods[request.form.get('method')]()
    data = []
    for account in accounts:
        count = Admin.query.filter_by(admin_name=account.admin_name).count()
        available = Admin.query.filter_by(admin_name=account.admin_name).count()
        item = {'admin_name': account.admin_name, 'admin_id': account.admin_id, 'password': account.password, 'right': account.right}
        data.append(item)
    return jsonify(data)

def preprocess_data(df):
    df.fillna('', inplace=True)  # 将所有NaN替换为空字符串
    df['combined'] = df.apply(lambda row: ' '.join([str(row['当事人']),
                                                    str(row['法律依据']),
                                                    str(row['信息性质']),
                                                    str(row['侵犯方式']),
                                                    str(row['规模和范围']),
                                                    str(row['违法所得']),
                                                    str(row['被告态度和行为'])]), axis=1)
    return df

def find_most_similar_case(new_case, case_data):
    vectorizer = TfidfVectorizer()
    all_cases = pd.concat([case_data['combined'], pd.Series([' '.join(new_case)])], ignore_index=True)
    tfidf_matrix = vectorizer.fit_transform(all_cases)
    cosine_sim = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1])
    most_similar_index = cosine_sim.argmax()
    return case_data.iloc[most_similar_index], cosine_sim[0][most_similar_index]

def infer_judgment(new_case, most_similar_case):
    judgment = most_similar_case['审判结果']
    judgment = judgment.replace(most_similar_case['当事人'], new_case['当事人'])
    judgment = judgment.replace(str(most_similar_case['违法所得']), str(new_case['违法所得']))
    return judgment

def extract_penalty_info(judgment):
    sentence_pattern = re.compile(r'判处(.*?)并')
    imprisonment_match = sentence_pattern.search(judgment)
    imprisonment = extract_imprisonment_time(imprisonment_match.group(1)) if imprisonment_match else None
    fine_pattern = re.compile(r'并处罚金(?:人民币)?(.*?)元')
    fine_match = fine_pattern.search(judgment)
    fine = extract_fine(fine_match.group(1)) if fine_match else None
    return imprisonment, fine

def extract_imprisonment_time(imprisonment_text):
    months = 0
    if '拘役' in imprisonment_text:
        months_match = re.search(r'拘役\s*(\d+|零|一|二|三|四|五|六|七|八|九|十)个月', imprisonment_text)
        if months_match:
            extracted_value = months_match.group(1)
            if extracted_value.isdigit():
                months = int(extracted_value)
            else:
                months = chinese_to_number(extracted_value)
    elif '有期徒刑' in imprisonment_text:
        years_match = re.search(r'有期徒刑\s*(\d+|零|一|二|三|四|五|六|七|八|九|十)年', imprisonment_text)
        if years_match:
            extracted_value = years_match.group(1)
            if extracted_value.isdigit():
                years = int(extracted_value)
            else:
                years = chinese_to_number(extracted_value)
            months += years * 12
    return months

def extract_fine(fine_text):
    try:
        fine_value = int(fine_text)
    except ValueError:
        fine_value = chinese_to_number(fine_text)
    return fine_value

def chinese_to_number(chinese_str):
    chinese_numerals = {
        "零": 0, "一": 1, "二": 2, "三": 3, "四": 4, "五": 5,
        "六": 6, "七": 7, "八": 8, "九": 9, "十": 10,
        "百": 100, "千": 1000, "万": 10000, "亿": 100000000
    }
    total = 0
    current_number = 0
    unit = 1
    for char in reversed(chinese_str):
        if char in chinese_numerals:
            value = chinese_numerals[char]
            if value >= 10:
                if current_number == 0:
                    current_number = 1
                unit = value
            else:
                current_number += value * unit
    total += current_number * unit
    return total

def assess_risk(imprisonment, fine):
    if imprisonment is None or fine is None:
        return "无法评估"
    if imprisonment < 12 or fine < 10000:
        return "低"
    elif (12 <= imprisonment < 24) or (10000 <= fine < 30000):
        return "中"
    else:
        return "高"

@main.route('/case_match', methods=['POST'])
def case_match():
    data = request.get_json()
    new_case_info = {
        '当事人': data.get('client'),
        '法律依据': data.get('legal_basis'),
        '信息性质': data.get('information_nature'),
        '侵犯方式': data.get('violation_mode'),
        '规模和范围': data.get('scale_scope'),
        '违法所得': data.get('illegal_gains'),
        '被告态度和行为': data.get('attitude_conduct')
    }

    cases = Case.query.all()
    case_data = pd.DataFrame([{
        '标题': case.title,
        '当事人': case.client,
        '法律依据': case.legal_basis,
        '信息性质': case.information_nature,
        '侵犯方式': case.violation_mode,
        '规模和范围': case.scale_scope,
        '违法所得': case.illegal_gains,
        '被告态度和行为': case.attitude_conduct,
        '审判结果': case.judical_outcome
    } for case in cases])

    case_data = preprocess_data(case_data)
    most_similar_case, similarity = find_most_similar_case(new_case_info.values(), case_data)
    inferred_result = infer_judgment(new_case_info, most_similar_case)
    imprisonment, fine = extract_penalty_info(inferred_result)
    risk_level = assess_risk(imprisonment, fine)

    return jsonify({
        'inferred_result': inferred_result,
        'risk_level': risk_level,
    })