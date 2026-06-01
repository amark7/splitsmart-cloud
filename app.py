from flask import Flask, render_template, request, redirect, url_for
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user

app = Flask(__name__)
app.secret_key = "splitsmart_secret"

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Temporary user storage
users = {}
groups = []
expenses = []
class User(UserMixin):
    def __init__(self, id):
        self.id = id

@login_manager.user_loader
def load_user(user_id):
    if user_id in users:
        return User(user_id)
    return None 

def calculate_settlements():

    settlements = []

    for expense in expenses:

        amount = float(expense['amount'])

        paid_by = expense['paid_by']

        participants = expense['participants']

        share = amount / len(participants)

        for person in participants:

            if person != paid_by:

                settlements.append(
                    f"{person} owes {paid_by} ₹{share:.2f}"
                )

    return settlements
@app.route('/')
def home():
    return render_template('index.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        users[email] = password

        return redirect(url_for('login'))

    return render_template('signup.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':

        email = request.form['email']
        password = request.form['password']

        if email in users and users[email] == password:
            user = User(email)
            login_user(user)

            return redirect(url_for('dashboard'))

    return render_template('login.html')

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html',
                           user=current_user.id)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups_page():

    if request.method == 'POST':

        group_name = request.form['group_name']

        groups.append({
            'name': group_name,
            'owner': current_user.id,
            'members': [current_user.id]
        })

    return render_template(
        'groups.html',
        groups=groups
    )

@app.route('/expenses', methods=['GET', 'POST'])
@login_required
def expenses_page():

    if request.method == 'POST':

        amount = request.form['amount']
        description = request.form['description']
        paid_by = request.form['paid_by']

        participants = request.form.getlist('participants')

        expenses.append({
            'amount': amount,
            'description': description,
            'paid_by': paid_by,
            'participants': participants
        })

    return render_template(
        'expenses.html',
        expenses=expenses,
        current_user=current_user.id
    )

@app.route('/settlements')
@login_required
def settlements_page():

    settlements = calculate_settlements()

    return render_template(
        'settlements.html',
        settlements=settlements
    )
@app.route('/group/<int:group_id>', methods=['GET', 'POST'])
@login_required
def group_details(group_id):

    group = groups[group_id]

    if request.method == 'POST':

        member_name = request.form['member_name']

        group['members'].append(member_name)

    return render_template(
        'group_details.html',
        group=group,
        group_id=group_id
    )
if __name__ == '__main__':
    app.run(debug=True)