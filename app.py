import os
import requests
from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_wtf import FlaskForm
from flask_debugtoolbar import DebugToolbarExtension
from flask_bcrypt import Bcrypt
from forms import RegistrationForm, LoginForm
from models import connect_db, User, SavedCocktail, db 



app = Flask(__name__)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', "it's a secret")
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL', 'postgresql:///cocktails')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True

toolbar = DebugToolbarExtension(app)
bcrypt = Bcrypt()

connect_db(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/search', methods=['GET', 'POST'])
def search_form():
    return render_template('search_form.html')

@app.route('/search_cocktail', methods=['GET'])
def search_cocktail():
    search_query = request.args.get('q') 
    api_url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={search_query}'
    response = requests.get(api_url)

    if response.status_code == 200:
        data = response.json()
        if data['drinks']:  
            
            cocktail_id = data['drinks'][0]['idDrink']
            return get_cocktail_details(cocktail_id)
        else:
            return jsonify({'error': 'Cocktail not found'}), 404
    else:
        return jsonify({'error': 'Failed to fetch data'}), 500

def get_cocktail_details(cocktail_id):
    details_url = f'https://www.thecocktaildb.com/api/json/v1/1/lookup.php?i={cocktail_id}'
    details_response = requests.get(details_url)

    if details_response.status_code == 200:
        details_data = details_response.json()

        return render_template('search_results.html', drinks=[details_data['drinks'][0]])
    else:
        return jsonify({'error': 'Failed to fetch cocktail details'}), 500
    
@app.route('/search_results', methods=['POST'])
def search_results():
    if request.method == 'POST':
        search_query = request.form['search_query']
        api_url = f'https://www.thecocktaildb.com/api/json/v1/1/search.php?s={search_query}'
        response = requests.get(api_url)

        if response.status_code == 200:
            data = response.json()
            drinks = data['drinks'] if 'drinks' in data else []
            return render_template('search_results.html', drinks=drinks, search_query=search_query)
        else:
            return 'Error fetching search results'
    else:
        return 'Invalid request method'
    
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        # Assuming you have a User model with a unique user ID field
        user = User.query.filter_by(username=form.username.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            session['user_id'] = user.id  # Set user ID in session
            flash('Login successful!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('Invalid username or password', 'danger')

    return render_template('profile.html', form=form)

@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Clear user ID from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        return redirect(url_for('login'))
    return render_template('signup.html', form=form)

@app.route('/profile')
def profile():
    # Retrieve saved cocktails for the current user
    saved_cocktails = current_user.saved_cocktails.all()

    return render_template('profile.html', saved_cocktails=saved_cocktails)

@app.route('/save_cocktail', methods=['POST'])
def save_cocktail():
    if 'user_id' in session:
        user_id = session['user_id']
        cocktail_id = request.form['cocktail_id']
        name = request.form['name']
        ingredients = request.form['ingredients']

        saved_cocktail = SavedCocktail(user_id=user_id, cocktail_id=cocktail_id, name=name, ingredients=ingredients)
        db.session.add(saved_cocktail)
        db.session.commit()

        flash('Cocktail saved successfully!', 'success')
        return redirect(url_for('profile'))
    else:
        flash('Please log in to save cocktails.', 'danger')
        return redirect(url_for('login'))



if __name__ == '__main__':
    app.run(debug=True)
