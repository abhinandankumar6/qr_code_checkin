from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import qrcode
import random
import base64
import os
from io import BytesIO
import socket #to get ip address
import logging

logging.basicConfig(level=logging.DEBUG)
app = Flask(__name__)


@app.route('/')
def index():
    logging.debug(f'App secret key from index page{os.urandom(24)}')
    return render_template('index.html')
    #return render_template('index_test.html')

@app.route('/welcome', methods=['POST'])
def welcome():
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
            # get name and unique id
            name = user.iloc[0]['name']
            unique_id=user.iloc[0]['unique_id']
            if user.iloc[0]['count'] < 1:
                users_df.loc[users_df['unique_id'] == code, 'checkin_status'] = 'Checked-In'
                users_df.loc[users_df['unique_id'] == code, 'count'] +=1
                logging.debug('Updated checkin status and count')
            else:
                # update count
                users_df.loc[users_df['unique_id'] == code, 'count'] +=1
                logging.debug('Updated only count')
            
            # save count to csv file
            users_df.to_csv("users.csv", index=False)
            logging.debug(f"Updated count for {unique_id}: {users_df.loc[users_df['unique_id'] == code, 'count'].iloc[0]}")
            # return the success template
            return render_template('welcome.html', name=name)
        elif user.iloc[0]['count'] == 2:
            name = user.iloc[0]['name']
            message = f"You have collected both of your drinks {name}. Come back next year."
            return render_template('enjoy.html', heading=message)
    else:
        heading = 'You should not be here!'
        message = 'You are not a registered user.'
        image_url = 'https://memetemplates.in/uploads/1641347541.jpeg'
        return render_template('enjoy.html', heading=heading, message=message, image_url=image_url)
        
    
if __name__ == '__main__':
    app.run(debug=True)
