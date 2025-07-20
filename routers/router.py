'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from backend.extensions import *
from datetime import datetime

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
    return redirect(url_for('auth.signup'))

# & Dashboard Route
@router.route('/dashboard/')
@login_required
def dash():
    teams = Team.query.filter_by(created_by=current_user.id).all()
    allteams = Team.query.filter(
        Team.memberlist.contains(str(current_user.id))
    ).all()

    return render_template('pages/home.html', teams=teams, allteams=allteams)

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
    allteams = Team.query.filter(
        Team.memberlist.contains(str(current_user.id))
    ).all()
    
    return render_template('pages/analytics.html', 
        trades=trades,
        teams=teams,
        sessions=trade_sessions(),
        allteams=allteams
    )

# & Strategies Route
@router.route('/strategies/')
@login_required
def strategies():
    teams = Team.query.filter_by(created_by=current_user.id).all()
    allteams = Team.query.filter(
        Team.memberlist.contains(str(current_user.id))
    ).all()
    strategies = Strategy.query.filter_by(user=current_user.id).all()
    return render_template('pages/strategies.html',
        teams=teams,
        strategies=strategies, 
        allteams=allteams
    )

# & Team Route
@router.route('/teams/<int:team_id>')
@login_required
def team(team_id):
    team = Team.query.filter_by(id=team_id).first()
    teams = Team.query.filter_by(created_by=current_user.id).all()
    allteams = Team.query.filter(
        Team.memberlist.contains(str(current_user.id))
    ).all()

    if not team:
        flash("Team not found! Try refreshing the app.", "error")
        return redirect(url_for('router.dash'))
    
    members = [User.query.filter_by(id=memid).first() for memid in team.memberlist.split(", ")]
    
    return render_template('pages/team.html',
        team=team,
        teams=teams,
        members=members, 
        allteams=allteams
    )

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
    allteams = Team.query.filter(
        Team.memberlist.contains(str(current_user.id))
    ).all()
    return render_template('pages/profile.html', teams=teams, allteams=allteams)

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