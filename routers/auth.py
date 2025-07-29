'''coderadi'''

# ? Importing libraries
from flask import Blueprint, render_template, redirect, url_for, flash, request
from backend.extensions import *
from werkzeug.security import generate_password_hash, check_password_hash

# ! Building auth
auth = Blueprint('auth', __name__, url_prefix='/auth')

# & Signup Route
@auth.route('/signup/', methods=['GET', 'POST'])
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
        return redirect(url_for('auth.signup'))
    
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
@auth.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated: return redirect(url_for('router.dash'))
    if request.method == 'GET': return render_template('auth/login.html')

    email = request.form.get('email')
    password = request.form.get('password')
    user = User.query.filter_by(email=email).first()

    if not user:
        flash("Email not found! Try signin instead.", 'error')
        return redirect(url_for('auth.login'))
    
    if not check_password_hash(user.password, password):
        flash("Invalid password!", 'error')
        return redirect(url_for('auth.login'))
    
    login_user(user)
    flash("You're logged in successfully!", "success")
    return redirect(url_for('router.dash'))

# & Google login route
@auth.route('/login/google')
def google_login():
    if current_user.is_authenticated:
        return redirect(url_for('router.dash'))
    redirect_uri = url_for('auth.google_authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

# & Google login callback route
@auth.route('/login/google/callback')
def google_authorize():
    try:
        # Get the token
        token = oauth.google.authorize_access_token()
        
        # Get user info directly from the token response
        user_info = token.get('userinfo')
        if not user_info:
            # Fallback to API request if not in token
            user_info = oauth.google.get('userinfo').json()
        
        # Ensure we have required fields
        if not user_info.get('email'):
            flash('Google login failed: No email provided', 'error')
            return redirect(url_for('auth.login'))
        
        # Find or create user
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            user = User(
                google_id=user_info.get('sub'),
                name=user_info.get('name', ''),
                email=user_info['email'],
            )
            db.session.add(user)
        else:
            # Update existing user if needed
            if not user.google_id:
                user.google_id = user_info.get('sub')
        
        db.session.commit()
        login_user(user)
        flash('Logged in successfully with Google.', 'success')
        return redirect(url_for('router.index'))
        
    except Exception as e:
        flash('Failed to log in with Google. Please try again.', 'error')
        print(f"Google OAuth error: {str(e)}")
        return redirect(url_for('auth.login'))

# & Logout Route
@auth.route('/logout/')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))