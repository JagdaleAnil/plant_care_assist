from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate  # Import Migrate
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///plants.db'  # Update as needed
app.config['SECRET_KEY'] = 'your_secret_key'
db = SQLAlchemy(app)
migrate = Migrate(app, db)  # Initialize Migrate

class Plant(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    diseases = db.relationship('Disease', backref='plant', lazy=True)

class Disease(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plant_id = db.Column(db.Integer, db.ForeignKey('plant.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    stage = db.Column(db.String(50), nullable=False)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    mobile_number = db.Column(db.String(15), nullable=False)  # New mobile number field
    password_hash = db.Column(db.String(128), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)  # Admin flag

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/features')
def features():
    return render_template('features.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('plant_selection'))
        else:
            flash('Invalid username or password')
    return render_template('login.html')

@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, is_admin=True).first()
        if user and user.check_password(password):
            session['user_id'] = user.id
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid admin username or password')
    return render_template('admin_login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        mobile_number = request.form['mobile_number']  # Capture mobile number
        password = request.form['password']
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            flash('User already exists')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email, mobile_number=mobile_number)
        new_user.set_password(password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/plant_selection')
def plant_selection():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    plants = Plant.query.all()
    return render_template('plant_selection.html', plants=plants)

@app.route('/disease_management/<int:plant_id>', methods=['GET'])
def disease_management(plant_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    plant = Plant.query.get_or_404(plant_id)
    diseases = Disease.query.filter_by(plant_id=plant_id).all()
    return render_template('disease_management.html', plant=plant, diseases=diseases)

@app.route('/disease_info/<int:disease_id>', methods=['GET'])
def disease_info(disease_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    disease = Disease.query.get_or_404(disease_id)
    return render_template('disease_info.html', disease=disease)

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out')
    return redirect(url_for('login'))

@app.route('/admin')
def admin_dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('plant_selection'))

    users = User.query.all()
    return render_template('admin_dashboard.html', users=users)

@app.route('/admin/edit_user/<int:user_id>', methods=['GET', 'POST'])
def edit_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('plant_selection'))

    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.mobile_number = request.form['mobile_number']  # Update mobile number
        password = request.form['password']
        if password:
            user.set_password(password)
        db.session.commit()
        flash('User updated successfully')
        return redirect(url_for('admin_dashboard'))

    return render_template('edit_user.html', user=user)

@app.route('/admin/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    current_user = User.query.get(session['user_id'])
    if not current_user.is_admin:
        flash('Access denied!')
        return redirect(url_for('plant_selection'))

    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully')
    return redirect(url_for('admin_dashboard'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create an admin user if not already created
        if not User.query.filter_by(username='admin').first():
            admin_user = User(username='admin', email='admin@example.com', mobile_number='1234567890', is_admin=True)
            admin_user.set_password('adminpassword')
            db.session.add(admin_user)
            db.session.commit()
    app.run(debug=True)
