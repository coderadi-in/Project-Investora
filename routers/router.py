'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request, get_flashed_messages
from backend.extensions import *
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import extract, and_
from datetime import datetime, timedelta

# ! Buiding router
router = Blueprint('router', __name__)

# | logger route
@logger.user_loader
def load_user(userid):
    return User.query.get(userid)

# & Base Route
@router.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('router.dash'))
    return redirect(url_for('router.signup'))

# & Signup Route
@router.route('/signup/', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated: return redirect(url_for('router.dash'))
    if request.method == 'GET': return render_template('auth/signup.html')

    name = request.form.get('name')
    email = request.form.get('email')
    password = generate_password_hash(
        request.form.get('password')
    )

    if User.query.filter_by(email=email).first():
        flash("Email already exists! Try logging in.", "error")
        return redirect(url_for('router.signup'))
    
    new_user = User(
        name=name,
        email=email,
        password=password
    )

    db.session.add(new_user)
    db.session.commit()
    db.session.add(Strategy(
        user=new_user.id,
        title="Model 1",
        desc="This is default strategy."
    ))
    db.session.commit()
    login_user(new_user)
    flash("You're signed up successfully!", "success")
    flash("Update your initial balance in 'starting balance' section", 'warning')
    return redirect(url_for('router.profile'))

# & Login Route
@router.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('router.dash'))
    if request.method == 'GET': return render_template('auth/login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email not found! Try signin instead.", 'error')
        return redirect(url_for('router.login'))
    
    if not check_password_hash(user.password, password):
        flash("Invalid password!", 'error')
        return redirect(url_for('router.login'))
    
    login_user(user)
    flash("You're logged in successfully!", "success")
    return redirect(url_for('router.dash'))

# & Logout Route
@router.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('router.login'))

# & Dashboard Route
@router.route('/dashboard/')
@login_required
def dash():
    teams = Team.query.filter_by(created_by=current_user.id).all()
    return render_template('pages/home.html', teams=teams)

# & Analytics Route
@router.route('/analytics/')
@login_required
def analytics():
    trades = filtered_trades(
        timeframe=request.args.get('timeframe'),
        session=request.args.get('session'),
        result=request.args.get('result'),
        strategy=request.args.get('strategy')
    )
    teams = Team.query.filter_by(created_by=current_user.id).all()
    
    return render_template('pages/analytics.html', 
        trades=trades,
        teams=teams,
        sessions=trade_sessions()
    )

# & Strategies Route
@router.route('/strategies/')
@login_required
def strategies():
    teams = Team.query.filter_by(created_by=current_user.id).all()
    strategies = Strategy.query.filter_by(user=current_user.id).all()
    return render_template('pages/strategies.html',
        teams=teams,
        strategies=strategies
    )

# | Add trade Route
@router.route('/add-trade/', methods=['POST'])
@login_required
def add_trade():
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d').date()
    pair = request.form.get('pair')
    side = request.form.get('side')
    entry = float(request.form.get('entry'))
    sl = float(request.form.get('sl'))
    take_profit = float(request.form.get('take_profit'))
    lot_size = float(request.form.get('lot'))
    pips = float(request.form.get('pips'))
    risk_reward = request.form.get('risk_reward')
    result = request.form.get('result').lower()
    pnl = float(request.form.get('pnl'))
    strategy = request.form.get('strategy')
    session = request.form.get('session')

    if not validate_result(result):
        flash("Result must be 'profit', 'loss', or 'be", "error")
        return redirect(url_for('router.dash'))

    new_trade = Trade(
        user=current_user.id,
        date=date,
        pair=pair,
        side=side,
        entry=entry,
        sl=sl,
        take_profit=take_profit,
        lot_size=lot_size,
        pips=pips,
        risk_reward=risk_reward,
        result=result,
        pnl=pnl,
        strategy=strategy,
        session=session
    )

    db.session.add(new_trade)
    db.session.commit()
    current_user.win_rate = get_win_rate()
    current_user.pnl = round(current_user.pnl + pnl, 2)
    current_user.risk_reward = get_risk_reward()
    update_trade_count(result)
    db.session.commit()

    flash("New traded added successfully!", 'success')
    return redirect(url_for('router.dash'))

# | Add Team route
@router.route('/add-team/', methods=['POST'])
@login_required
def add_team():
    name = request.form.get('name')
    new_team = Team(
        created_by=current_user.id,
        title=name,
        memberlist=f"{current_user.id}, "
    )

    db.session.add(new_team)
    db.session.commit()
    flash(f"Team '{name}' is created!", "success")
    # return redirect(f"/teams/{new_team.id}")
    return redirect(url_for('router.dash'))

# | Add Member route
@router.route('/add-member/', methods=['POST'])
@login_required
def add_member():
    email = request.form.get('email')
    team_id = request.form.get('team')
    team = Team.query.filter_by(id=team_id, created_by=current_user.id).first()
    user = User.query.filter_by(email=email).first()

    if not team:
        flash("Team not found! Try relaunching the app.", "error")
        return redirect(url_for('router.dash'))
    
    if not user:
        flash("User not found! Make sure the email is correct.", "error")
        return redirect(url_for('router.dash'))
    
    members: list = team.memberlist.split(", ")
    members.append(str(user.id))

    team.memberlist = ", ".join(members)
    team.members += 1

    db.session.commit()
    flash(f"New member '{user.name}' added.", "success")
    return redirect(f"/teams/{team.id}")

# | Add Strategy route
@router.route('/add-strategy/', methods=['POST'])
@login_required
def add_strategy():
    title = request.form.get('title')
    desc = request.form.get('desc')

    db.session.add(Strategy(
        user=current_user.id,
        title=title,
        desc=desc
    ))
    db.session.commit()
    flash("New strategy added successfully.", "success")
    return redirect(url_for('router.strategies'))

# & Delete route
@router.route('/delete/<section>/<id>')
@login_required
def delete(section, id):
    if section == 'team':
        team = Team.query.filter_by(id=id, created_by=current_user.id).first()
        
        if not section:
            flash("Team not found! Try relaunching the app.", "error")
            return redirect(url_for('router.dash'))
        
        db.session.delete(team)
        db.session.commit()
        flash(f"Team '{team.title}' deleted.", "warning")
        return redirect(url_for('router.dash'))
    
# & Profile route
@router.route('/profile/')
@login_required
def profile():
    teams = Team.query.filter_by(created_by=current_user.id).all()
    return render_template('pages/profile.html', teams=teams)

# | Update profile route
@router.route('/profile/update', methods=['POST'])
@login_required
def update_profile():
    name = request.form.get('name', current_user.name)
    email = request.form.get('email', current_user.email)
    starting_bal = float(request.form.get('stbal'))

    current_user.name = name
    current_user.email = email

    if starting_bal:
        current_user.starting_bal = starting_bal
        current_user.pnl += starting_bal

    db.session.commit()
    flash("Profile updated successfully.", "success")
    return redirect(url_for('router.profile'))