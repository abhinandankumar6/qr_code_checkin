from flask import Flask, render_template, request, redirect, url_for, session
import pandas as pd
import logging
import os

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)
app.secret_key = os.urandom(24)  # Needed for session management

@app.route('/')
def index():
    return render_template('index.html')
logging.debug('this is after index function. After this welcome function starts.')
@app.route('/welcome', methods=['POST'])
def welcome():
    # Check if the user has already been welcomed
    if session.get('welcomed'):
        session['welcomed'] = False
        logging.debug('Session redirecting to index page')
        return redirect(url_for('index'))
        
    logging.debug('Session going to welcome page')
    
    # Get the code from the form
    code = request.form.get('code')
    if not code:
        return redirect(url_for('index'))
    
    # Load the user data from CSV into a DataFrame
    users_df = pd.read_csv("users.csv")
    
    # Search for the user in the DataFrame
    user = users_df[users_df['unique_id'] == code]
    
    logging.debug(f"Found user: {user['name']}")
    
    if not user.empty:
        if user.iloc[0]['count'] < 2:
            # Get name and unique id
            name = user.iloc[0]['name']
            unique_id = user.iloc[0]['unique_id']
            if user.iloc[0]['count'] < 1:
                users_df.loc[users_df['unique_id'] == code, 'checkin_status'] = 'Checked-In'
                users_df.loc[users_df['unique_id'] == code, 'count'] += 1
                logging.debug('Updated checkin status and count')
            else:
                # Update count
                users_df.loc[users_df['unique_id'] == code, 'count'] += 1
                logging.debug('Updated only count')
            
            # Save count to CSV file
            users_df.to_csv("users.csv", index=False)
            logging.debug(f"Updated count for {unique_id}: {users_df.loc[users_df['unique_id'] == code, 'count'].iloc[0]}")
            
            # Set the session variable
            session['welcomed'] = True
            
            # Return the success template
            return render_template('welcome.html', name=name)
        elif user.iloc[0]['count'] == 2:
            name = user.iloc[0]['name']
            message = f"You have collected both of your drinks {name}. Come back next year."
            image_url = 'https://memetemplates.in/uploads/1641347541.jpeg'
            return render_template('enjoy.html', heading=message, image_url=image_url)
    else:
        heading = 'You should not be here!'
        message = 'You are not a registered user.'
        image_url = 'https://memetemplates.in/uploads/1641347541.jpeg'
        return render_template('enjoy.html', heading=heading, message=message, image_url=image_url)

if __name__ == '__main__':
    app.run(debug=True)