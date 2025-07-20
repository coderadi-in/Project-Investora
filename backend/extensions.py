'''coderadi'''

# ? Importing flask extensions
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from flask_migrate import Migrate

# ? Importing llibraries
from sqlalchemy import extract, and_
from datetime import datetime, timedelta

# ! Building extensions
db = SQLAlchemy()
migrate = Migrate()
logger = LoginManager()

# | User database model
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    password = db.Column(db.String, nullable=False)
    trades = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    be = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.00)
    risk_reward = db.Column(db.String, default='0:0')
    pnl = db.Column(db.Float, default=0.00)
    strategies = db.Column(db.String, default="Model 1, ")
    teams = db.Column(db.String, default="")
    starting_bal = db.Column(db.Float, default=0.00)

# | Team datbase model
class Team(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    created_by = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String, default='Trading team')
    members = db.Column(db.Integer, default=1)
    memberlist = db.Column(db.String, default="")
    trades = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    be = db.Column(db.Integer, default=0)
    win_rate = db.Column(db.Float, default=0.00)
    risk_reward = db.Column(db.String, default='0:0')
    pnl = db.Column(db.Float, default=0.00)

# | Trade database model
class Trade(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, nullable=False)
    date = db.Column(db.Date, nullable=False)
    pair = db.Column(db.String, nullable=False)
    side = db.Column(db.String, nullable=False)
    entry = db.Column(db.Float, nullable=False)
    sl = db.Column(db.Float, nullable=False)
    take_profit = db.Column(db.Float, nullable=False)
    lot_size = db.Column(db.Float, nullable=False)
    pips = db.Column(db.Float, nullable=False)
    risk_reward = db.Column(db.String, nullable=False)
    result = db.Column(db.String, nullable=False)
    pnl = db.Column(db.Float, nullable=False)
    strategy = db.Column(db.String, nullable=False, default="Model 1")
    session = db.Column(db.String, nullable=False)
    team = db.Column(db.Integer, default=0)

# | Strategy database model
class Strategy(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user = db.Column(db.Integer, nullable=False)
    title = db.Column(db.String)
    desc = db.Column(db.String)

# & Auxiliaries
def trade_sessions() -> list:
    return list(
        set([trade.session for trade in Trade.query.filter_by(user=current_user.id).all()])
    )

# * Function to validate result
def validate_result(result: str):
    if result.lower() in ['profit', 'loss', 'be']:
        return True
    return False

# * Function to calculate win rate
def get_win_rate() -> float:
    trades = Trade.query.filter_by(user=current_user.id).all()
    
    if len(trades) == 0:
        return 0.0
    
    wins = [trade for trade in trades if trade.result == 'profit']
    return round(float((len(wins) / len(trades)) * 100), 2)

# * Function to get risk-reward
def get_risk_reward() -> str:
    try:
        trades = Trade.query.filter_by(user=current_user.id).all()
        targets = [float(rr.risk_reward.split(":")[-1]) for rr in trades]
        total_targets = sum(targets)
        total_trades = len(trades)

        avg_rr = round(total_targets / total_trades, 2)
        avg_rr = f"1:{avg_rr}"
        return avg_rr

    except:
        return '0:0'
    
# * Function to update trades count
def update_trade_count(result: str, model) -> None:
    if result not in ['profit', 'loss', 'be']: return
    
    model.trades += 1
    if result == 'profit': model.wins += 1
    if result == 'loss': model.losses += 1
    if result == 'be': model.be += 1

# * Function to update the pnl history list
def update_to_cumulative(data: list) -> list:
    """
    Transforms a list into its cumulative sum version.
    
    Args:
        data (list): Input list of numbers
        
    Returns:
        list: New list where each element is the sum of all previous elements + itself
    """
    cumulative = 0
    result:list = []
    for num in data:
        cumulative += num
        result.append(cumulative)
    return result

current_year = datetime.now().year
current_month = datetime.now().month
today = datetime.now().date()
start_of_week = today - timedelta(days=today.weekday())
end_of_week = start_of_week + timedelta(days=6)

# * function to return trades data according to timeframe
def time_trades() -> dict[str: list[Trade]]:
    return {
        'yearly': Trade.query.filter_by(user=current_user.id)
                   .filter(extract('year', Trade.date) == current_year).all(),
        'monthly': Trade.query.filter_by(user=current_user.id)
                    .filter(and_(
                        extract('year', Trade.date) == current_year,
                        extract('month', Trade.date) == current_month
                    )).all(),
        'weekly': Trade.query.filter_by(user=current_user.id)
                   .filter(Trade.date >= start_of_week, Trade.date <= end_of_week).all(),
        'daily': Trade.query.filter_by(user=current_user.id)
                  .filter(Trade.date == today).all(),
        'all': Trade.query.filter_by(user=current_user.id).all()  # Changed from '' to 'all'
    }

# * function to return trades data according to session
def session_trades() -> dict[str: list[Trade]]:
    '''
    Returns a dictionary containing sessions as keys and trades history as values
    '''

    trades_data = {
        '': Trade.query.filter_by(user=current_user.id).all()
    }
    for session in trade_sessions():
        trades_data[session] = Trade.query.filter_by(
            user=current_user.id,
            session=session
        ).all()

    return trades_data

# * function to return trades data according to results
def result_trades() -> dict[str: list[Trade]]:
    '''
    Returns a dictionary containing sessions as keys and trades history as values
    '''

    return {
        'profit': Trade.query.filter_by(
            user=current_user.id,
            result='profit'
        ).all(),

        'loss': Trade.query.filter_by(
            user=current_user.id,
            result='loss'
        ).all(),

        'be': Trade.query.filter_by(
            user=current_user.id,
            result='be'
        ).all(),

        '': Trade.query.filter_by(user=current_user.id).all()
    }

# * function to return trades data according to strategy
def strategy_trades() -> dict[str: list[Trade]]:
    '''
    Returns a dictionary containing strategies as keys and trades history as values
    '''

    args = {
        '': Trade.query.filter_by(user=current_user.id).all()
    }
    strategies = current_user.strategies.split(", ")
    for strategy in strategies:
        args[strategy] = Trade.query.filter_by(
            user=current_user.id,
            strategy=strategy
        ).all()

    return args

# * function to return filtered trades history
def filtered_trades(
    timeframe: str|None = None,
    session: str|None = None,
    result: str|None = None,
    strategy: str|None = None
) -> list:
    # Start with all trades
    filtered = set(Trade.query.filter_by(user=current_user.id).all())
    
    # Apply timeframe filter if provided
    if timeframe:
        timeframe_trades = set(time_trades().get(timeframe, []))
        filtered = filtered.intersection(timeframe_trades)
    
    # Apply session filter if provided
    if session:
        session_trades_set = set(session_trades().get(session, []))
        filtered = filtered.intersection(session_trades_set)
    
    # Apply result filter if provided
    if result:
        result_trades_set = set(result_trades().get(result, []))
        filtered = filtered.intersection(result_trades_set)
    
    # Apply strategy filter if provided
    if strategy:
        strategy_trades_set = set(strategy_trades().get(strategy, []))
        filtered = filtered.intersection(strategy_trades_set)
    
    return list(filtered)