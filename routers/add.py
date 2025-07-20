'''coderadi'''

# ? Importing libraries
from flask import Blueprint, redirect, url_for, flash, request
from backend.extensions import *
from datetime import datetime

# ! Building router
add = Blueprint('add', __name__, url_prefix=('/add'))

# & Add Trade Route
@add.route('/trade/', methods=['POST'])
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
    teamid = request.form.get('team')

    if not validate_result(result):
        flash("Result must be 'profit', 'loss', or 'be", "error")
        return redirect(url_for('router.dash'))
    
    if teamid:
        team = Team.query.filter_by(id=teamid).first()
        team.pnl += pnl
        update_trade_count(result, team)
        db.session.commit()
        
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
        session=session,
        team=teamid
    )

    db.session.add(new_trade)
    db.session.commit()
    current_user.win_rate = get_win_rate()
    current_user.pnl = round(current_user.pnl + pnl, 2)
    current_user.risk_reward = get_risk_reward()
    update_trade_count(result, current_user)
    db.session.commit()

    flash("New traded added successfully!", 'success')
    return redirect(url_for('router.dash'))

# & Add Team route
@add.route('/team/', methods=['POST'])
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
    return redirect(f"/teams/{new_team.id}")

# & Add Member route
@add.route('/member/', methods=['POST'])
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

# & Add Strategy route
@add.route('/strategy/', methods=['POST'])
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

    user_strategies: list = current_user.strategies.split(", ")
    user_strategies.remove("")
    user_strategies.append(title)    
    current_user.strategies = ", ".join(user_strategies)
    db.session.commit()

    flash("New strategy added successfully.", "success")
    return redirect(url_for('router.strategies'))