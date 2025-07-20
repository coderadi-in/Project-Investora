'''coderadi'''

# ? Importing libraries
from flask import Blueprint, jsonify, request
from sqlalchemy import extract, and_
from datetime import datetime, timedelta
from backend.extensions import *

# ! Building router
api = Blueprint('api', __name__, url_prefix=('/api'))

# & Trades route
@api.route('/trades/')
def trades():
    timeframe = request.args.get('timeframe')
    current_year = datetime.now().year
    current_month = datetime.now().month
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)          

    if timeframe == 'yearly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(extract('year', Trade.date) == current_year).all()

    elif timeframe == 'monthly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(
            and_(
                extract('year', Trade.date) == current_year,
                extract('month', Trade.date) == current_month
            )
        ).all()

    elif timeframe == 'weekly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(
            Trade.date >= start_of_week,
            Trade.date <= end_of_week
        ).all()

    elif timeframe == 'daily':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(Trade.date == today).all()


    else: trades:list = Trade.query.filter_by(user=current_user.id).all()


    winning: list = [trade for trade in trades if trade.result == 'profit']
    losing: list = [trade for trade in trades if trade.result == 'loss']
    breakevens: list = [trade for trade in trades if trade.result == 'be']

    return jsonify({
        'winning': len(winning),
        'losing': len(losing),
        'be': len(breakevens)
    })

# & History route
@api.route('/history/')
def history():
    timeframe = request.args.get('timeframe')
    current_year = datetime.now().year
    current_month = datetime.now().month
    today = datetime.now().date()
    start_of_week = today - timedelta(days=today.weekday())
    end_of_week = start_of_week + timedelta(days=6)          

    if timeframe == 'yearly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(extract('year', Trade.date) == current_year).all()

    elif timeframe == 'monthly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(
            and_(
                extract('year', Trade.date) == current_year,
                extract('month', Trade.date) == current_month
            )
        ).all()

    elif timeframe == 'weekly':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(
            Trade.date >= start_of_week,
            Trade.date <= end_of_week
        ).all()

    elif timeframe == 'daily':
        trades: list = Trade.query.filter_by(
            user=current_user.id
        ).filter(Trade.date == today).all()


    else: trades:list = Trade.query.filter_by(user=current_user.id).all()

    pnl_history: list = [trade.pnl for trade in trades]
    pnl_history[0] += current_user.starting_bal
    pnl = update_to_cumulative(pnl_history)

    return jsonify({
        'pnl': pnl
    })

# & Team trades route
@api.route('/team/<int:team_id>/trades/')
def team_trades(team_id):
    team = Team.query.filter_by(id=team_id).first()
    trades = Trade.query.filter_by(team=team.id).all()

    winning: list = [trade for trade in trades if trade.result == 'profit']
    losing: list = [trade for trade in trades if trade.result == 'loss']
    breakevens: list = [trade for trade in trades if trade.result == 'be']

    return jsonify({
        'winning': len(winning),
        'losing': len(losing),
        'be': len(breakevens)
    })

@api.route('/team/<int:team_id>/history/')
def team_history(team_id):
    team = Team.query.filter_by(id=team_id).first()
    trades = Trade.query.filter_by(team=team.id).all()

    pnl: list = [trade.pnl for trade in trades]

    return jsonify({'pnl': pnl})
