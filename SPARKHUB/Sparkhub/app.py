from flask import Flask, render_template, request, redirect, session
import mysql.connector
import hashlib

app = Flask(__name__)
app.secret_key = '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'

# Function to connect to the MySQL database
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="dineshbtech26@gmail.com",
        password="Dinesh@9080",
        database="sparkhub"
    )

# Function to create the database table
def create_table():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            password VARCHAR(255) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Function to insert a new user into the database
def insert_user(username, email, password):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
    ''', (username, email, password))
    conn.commit()
    conn.close()

# Function to retrieve a user by email
def get_user_by_email(email):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT * FROM users WHERE email = %s
    ''', (email,))
    user = cursor.fetchone()
    conn.close()
    return user

# Function to hash a password
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Create the database table when the application starts
create_table()

# Function to get the brand name (replace this with your actual method)
def get_brand_name():
    return "XYZ Brand"

# Function to check if the user is a brand
def is_brand(email):
    # Your logic to determine if the user is a brand
    # For now, let's assume all users with an email domain ending in '.com' are brands
    return email.endswith('.com')

@app.route('/')
def index():
    access_token = session.get('access_token')
    channel_data = session.get('channel_data')
    return render_template('index.html', channel_data=channel_data)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = hash_password(request.form['password'])
        insert_user(username, email, password)
        if is_brand(email):
            session['loggedin'] = True
            session['username'] = username
            return redirect('/influencer')
        else:
            return redirect('/login')
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = hash_password(request.form['password'])
        user = get_user_by_email(email)
        if user and user[3] == password:
            session['loggedin'] = True
            session['username'] = user[1]
            if is_brand(email):
                return redirect('/influencer')
            else:
                    return redirect('/influencer')
        else:
            return 'Invalid email/password combination'

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'loggedin' in session:
        return render_template('profile.html', username=session['username'])
    else:
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

@app.route('/influencer')
def influencer():
    if 'loggedin' in session:
        return render_template('influencer.html', username=session['username'])
    else:
        return redirect('/login')
    
@app.route('/negotiation_page')
def negotiation_page():
    return render_template('negotiation.html')

@app.route('/influencer_channels')
def influencer_channels():
    if 'loggedin' in session:
        youtube = get_authenticated_service()
        channel_data = get_channel_data(youtube)
        return render_template('influencer_channels.html', channel_data=channel_data)
    else:
        return redirect('/login')
    
@app.route('/landing_page')
def landing_page():
    # Get the brand name and logged-in user's name
    brand_name = get_brand_name()
    username = session.get('username')
    return render_template('landing_page.html', brand_name=brand_name, username=username)

@app.route('/oauth2callback')
def oauth2callback():
    access_token = request.args.get('access_token')
    if access_token:
        session['access_token'] = access_token
        return redirect('/influencer_channels')  # Redirect to influencer_channels page
    return redirect('/')

def get_authenticated_service():
    scopes = ["https://www.googleapis.com/auth/youtube.readonly"]

    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes=scopes
    )

    # Run the OAuth flow using a local server
    credentials = flow.run_local_server()

    # Build the YouTube service using the credentials
    youtube = build("youtube", "v3", credentials=credentials)

    return youtube

def get_channel_data(youtube):
    request = youtube.channels().list(
        part="snippet",
        mine=True
    )
    response = request.execute()
    if 'items' in response:
        return response['items'][0]  # Assuming only one channel is returned
    else:
        return None

@app.route('/campaigns')
def campaigns():
    return render_template('campaigns.html')

@app.route('/add_channel', methods=['GET', 'POST'])
def add_channel():
    if request.method == 'POST':
        # Process the form data
        channel_name = request.form['channel_name']
        channel_url = request.form['channel_url']
        channel_description = request.form['channel_description']
        
        # Insert the channel data into the database or perform any other necessary action
        # For now, let's just print the data
        print("Channel Name:", channel_name)
        print("Channel URL:", channel_url)
        print("Channel Description:", channel_description)
        
        # Redirect to a success page or wherever appropriate
        return redirect('/influencer_channels')

    return render_template('add_channel.html')

@app.route('/negotiation', methods=['GET', 'POST'])
def negotiation():
    if request.method == 'POST':
        # Process negotiation form submission
        influencer = request.form['influencer']
        brand = request.form['brand']
        message = request.form['message']
        
        # Store negotiation data in the database (you'll need to implement this)
        # For demonstration, let's print the data
        print(f"Influencer: {influencer}, Brand: {brand}, Message: {message}")
        
        # Redirect to the negotiation page or any other appropriate page
        return redirect('/negotiation')
    else:
        # Render the negotiation page template
        return render_template('negotiation.html')
    
if __name__ == '__main__':
    app.run(debug=True)