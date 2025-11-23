from flask import Flask, render_template, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc 

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///mnarega.db'
db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Mnarega(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    financial_year = db.Column(db.String(20), nullable=False)
    state = db.Column(db.String(50), nullable=False)
    district = db.Column(db.String(50), nullable=False)
    total_allocation = db.Column(db.Float, nullable=False)
    total_expenditure = db.Column(db.Float, nullable=False)
    total_person_days = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f'<Mnarega {self.financial_year} - {self.state} - {self.district}>'



@app.route('/')
def home():
    year_query = db.session.query(Mnarega.financial_year.distinct()).order_by(desc(Mnarega.financial_year)).all()
    state_query = db.session.query(Mnarega.state.distinct()).order_by(Mnarega.state).all()

    all_years = [year[0] for year in year_query]
    all_states = [state[0] for state in state_query]
    

    print(f"DEBUG: Found {len(all_years)} years and {len(all_states)} states.")
   
    return render_template('index.html', years=all_years, all_states=all_states)

@app.route('/report') 
def show_report():
   
    selected_year = request.args.get('financial_year')
    selected_state = request.args.get('state_name')
    
    
    results = Mnarega.query.filter_by(
        financial_year=selected_year,
        state=selected_state
    ).order_by(Mnarega.district).all()
    
    return render_template(
        'report.html', 
        results=results, 
        year=selected_year, 
        state=selected_state
    )
@app.route('/users')
def users():
    all_users = User.query.all()
    return render_template('users.html', users=all_users)


if __name__ == '__main__':
    
    with app.app_context():
        db.create_all()
        
    app.run(debug=True ,port=5001)