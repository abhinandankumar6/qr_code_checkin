from flask import Flask, render_template, request, session
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

class UserCheckin:
    def __init__(self, code):
        self.code = code
        self.users_df = pd.read_csv("users.csv")
        self.user = self.users_df[self.users_df['unique_id'] == self.code]
        logging.debug('User checkin done at line 16 ')

    def check_user(self):
        if not self.user.empty:
            if self.user.iloc[0]['count'] < 2:
                logging.debug('processing checkin line 21')
                return self.process_checkin()
            elif self.user.iloc[0]['count'] == 2:
                logging.debug('already collected line 24')
                return self.already_collected()
        else:
            return self.not_registered()

    def process_checkin(self):
        if not session['checked_in']:
            session['checked_in'] = True
            name = self.user.iloc[0]['name']
            unique_id = self.user.iloc[0]['unique_id']
            logging.debug('processing checkin line 34')
            if self.user.iloc[0]['count'] < 1:
                self.users_df.loc[self.users_df['unique_id'] == self.code, 'checkin_status'] = 'Checked-In'
                self.users_df.loc[self.users_df['unique_id'] == self.code, 'count'] += 1
                logging.debug('Updated checkin status and count line 38')
            else:
                self.users_df.loc[self.users_df['unique_id'] == self.code, 'count'] += 1
                logging.debug('Updated only count line 41')
            self.users_df.to_csv("users.csv", index=False)
            logging.debug('Updated count at line 43')
            return render_template('welcome.html', name=name)
        else:
            logging.debug('processing checkin line 46')
            return render_template('welcome.html')

    def already_collected(self):
        name = self.user.iloc[0]['name']
        message = f"You have collected both of your drinks {name}. Come back next year."
        logging.debug('processing checkin line 52')
        return render_template('enjoy.html', heading=message)

    def not_registered(self):
        heading = 'You should not be here!'
        message = 'You are not a registered user.'
        image_url = 'https://memetemplates.in/uploads/1641347541.jpeg'
        logging.debug('processing checkin line 59')
        return render_template('enjoy.html', heading=heading, message=message, image_url=image_url)

@app.route('/')
def index():
    session['checked_in'] = False
    logging.debug('Reached index page line 65')
    return render_template('index.html')

@app.route('/welcome', methods=['POST'])
def checkin():
    code = request.form['code']
    user_checkin = UserCheckin(code)
    logging.debug('Reached checkin welcome page line 72')
    return user_checkin.check_user()

if __name__ == '__main__':
    app.run(debug=True)