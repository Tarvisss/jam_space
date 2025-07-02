from dotenv import load_dotenv
import os
import base64
from flask import Flask, render_template, request, flash, redirect, session, g, abort, url_for
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy.exc import IntegrityError
import requests
from forms import UserAddForm, LoginForm, PostForm, UserUpdateForm, PreSignupForm, MusicianForm, OrganizerForm, FanForm, DeleteForm
from models import db, connect_db, User, Post

# Constant for current user session key
CURRENT_USER_KEY = "curr_user"

# Initialize the Flask app
app = Flask(__name__)
#Imported to load .env file 
load_dotenv()
SUPABASE_DB_URL = os.getenv('SUPABASE_DB_URL')
LOCAL_DB = os.getenv('LOCAL_DB')
app.config['SQLALCHEMY_DATABASE_URI'] = (
    os.environ.get('SUPABASE_DB_URL', LOCAL_DB))

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = False
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = True
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')




# Push app context (needed for debugging with the toolbar)
app.app_context().push()

# Initialize the Flask Debug Toolbar
toolbar = DebugToolbarExtension(app)

# Connect the app to the database
connect_db(app)
#
##############################################################################
# User signup/login/logout routes

# Before each request, check if the user is logged in and store the user object in the global `g`
@app.before_request
def add_user_to_g():

    if CURRENT_USER_KEY in session:
        # Retrieve the user from the database based on the session user ID
        g.user = User.query.get(session[CURRENT_USER_KEY])
    else:
        g.user = None  # No user logged in


# Function to log in a user (set the user ID in the session)
def do_login(user):

    session[CURRENT_USER_KEY] = user.id

    
# Function to log out a user (remove user ID from the session)
def do_logout():

    if CURRENT_USER_KEY in session:
        del session[CURRENT_USER_KEY]

@app.route('/pre-signup', methods=["GET", "POST"])
def preSignup():
    form = PreSignupForm()
    try:
        if form.validate_on_submit():
            choice = form.choice.data  

            # Redirect to the appropriate signup page based on the user's choice
            if choice == '1':
                return redirect(url_for('signup', user_type='fan'))
            elif choice == '2':
                return redirect(url_for('signup', user_type='organizer'))
            elif choice == '3':
                return redirect(url_for('signup', user_type='musician'))

        return render_template('pre-signup-question.html', form=form)
    except Exception as err:
        flash(f"Must be one of the choices {err}")
        return render_template('pre-signup-question.html', form=form)

# Route for user signup
@app.route('/signup', methods=["GET", "POST"])
def signup():
    try:    
        user_type = request.args.get('user_type')  # Get the user type from the URL query parameter
        form = UserAddForm()

        # Adjust the form or logic based on user_type
        if user_type == 'fan':
            # Customize form for 'fan' if necessary
            form.type.data = 'fan'  # You can add a hidden field or use this to store user type in the DB
        elif user_type == 'organizer':
            # Customize form for 'organizer'
            form.type.data = 'organizer'
        elif user_type == 'musician':
            # Customize form for 'musician'
            form.type.data = 'musician'

        if form.validate_on_submit():
            try:
                # Create a new user and save it to the database with the user type
                user = User.signup(
                    username=form.username.data,
                    password=form.password.data,
                    email=form.email.data,
                    image_url=form.image_url.data or "/static/images/default-pic.png",
                    user_type=form.type.data,  # Store the user type in the DB
                )
                db.session.commit()
            except IntegrityError:
                flash("Username already taken", 'danger')
                return render_template('users/signup.html', form=form)

            # Log the user in after signing up
            do_login(user)

            # Redirect to the homepage after successful signup
            return redirect("/")

        return render_template('users/signup.html', form=form, user_type=user_type)
    except Exception as err:
        flash(f"Must be of type Musician, Organizer, fan {err}")
        return render_template('users/signup.html', form=form)



# Route for user login
@app.route('/login', methods=["GET", "POST"])
def login():
    try:   

        form = LoginForm()

        if form.validate_on_submit():
            # Try to authenticate the user
            user = User.authenticate(form.username.data, form.password.data)

            if user:
                # Log in the user if authentication is successful
                do_login(user)
                flash(f"Hello, {user.username}!", "success")
                return redirect("/")

            # Flash an error message if credentials are invalid
            flash("Invalid credentials.", 'danger')

        return render_template('users/login.html', form=form)
    except Exception as err:
        flash(f"error {err}")
        return render_template('users/login.html', form=form)

# Route for logging out a user
@app.route('/logout')
def logout():
    
    flash(f"logged out!", "success")
    do_logout()
    return redirect("/login")


##############################################################################
# General user routes:

# Route to list all users or search users by username
@app.route('/users')
def list_users():
    try:    

        search = request.args.get('q')

        if not search:
            users = User.query.all()  # Get all users
        else:
            # Filter users by matching username
            users = User.query.filter(User.username.like(f"%{search}%")).all()

        return render_template('users/index.html', users=users, user_type=g.user.user_type)
    except Exception as err:
        flash(f"error {err}")
        return redirect("/")


# Route to show a user's profile
@app.route('/users/<int:user_id>')
def users_show(user_id):
    try:
        user = User.query.get_or_404(user_id)

        # Fetching the necessary data from the User model
        header_image_url = user.header_image_url
        bio = user.bio
        location = user.location
        user_type = user.user_type

        # Fetch the user's posts
        posts = (Post
                    .query
                    .filter(Post.user_id == user_id)
                    .order_by(Post.timestamp.desc())
                    .limit(100)
                    .all())

        # Render the template with the necessary data
        return render_template('users/show.html', 
                               user=user, 
                               posts=posts,
                               location=location,
                               bio=bio,
                               header_image_url=header_image_url, 
                               user_type=user_type)
    
    except Exception as err:
        flash(f"error {err}")
        return redirect("/")

# Route to show users a list of people they are following
@app.route('/users/<int:user_id>/following')
def show_following(user_id):
    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        user = User.query.get_or_404(user_id)
        return render_template('users/following.html', user=user, user_type=g.user.user_type)
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to show users a list of followers
@app.route('/users/<int:user_id>/followers')
def users_followers(user_id):
    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        user = User.query.get_or_404(user_id)
        return render_template('users/followers.html', user=user, user_type=g.user.user_type)
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to add a follow relationship for the logged-in user
@app.route('/users/follow/<int:follow_id>', methods=['POST'])
def add_follow(follow_id):
    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        followed_user = User.query.get_or_404(follow_id)
        g.user.following.append(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to stop following a user
@app.route('/users/stop-following/<int:follow_id>', methods=['POST'])
def stop_following(follow_id):
    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        followed_user = User.query.get(follow_id)
        g.user.following.remove(followed_user)
        db.session.commit()

        return redirect(f"/users/{g.user.id}/following")
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to show a user's liked posts
@app.route('/users/<int:user_id>/likes', methods=["GET"])
def show_likes(user_id):
    try:   
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        user = User.query.get_or_404(user_id)
        return render_template('users/likes.html', user=user, likes=user.likes, user_type=g.user.user_type)
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to add or remove a like for a message
@app.route('/posts/<int:message_id>/like', methods=['POST'])
def add_like(message_id):

    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")
        # Prevent the user from liking their own message
        liked_message = Post.query.get_or_404(message_id)
        if liked_message.user_id == g.user.id:
            return abort(403)  

        # Toggle like status for the message
        if liked_message in g.user.likes:
            g.user.likes.remove(liked_message)
        else:
            g.user.likes.append(liked_message)

        db.session.commit()

        return redirect("/")
    
    except Exception as err:
        flash(f"error: {err}")
        return redirect("/")

# Route to update the logged-in user's profile
@app.route('/users/profile', methods=["GET", "POST"])
def profile():
    
    try:
        if not g.user:
            flash("Access unauthorized.", "danger")
            return redirect("/")

        # Common form (UserUpdateForm) for all user types
        form = UserUpdateForm()
        user_type = g.user.user_type  # Get the user type

        # Initialize user type specific forms
        fan_form = None
        organizer_form = None
        musician_form = None

        if user_type == 'fan':
            fan_form = FanForm()
        elif user_type == 'organizer':
            organizer_form = OrganizerForm()
        elif user_type == 'musician':
            musician_form = MusicianForm()

        if form.validate_on_submit():
            # Authenticate user (confirm password) before making changes
            user = User.authenticate(username=g.user.username, password=form.password.data)
            if not user:
                flash("Access Denied.", "danger")
                return redirect("/")

            # Update common fields
            try:
                User.update_user(
                    username=form.username.data or user.username,
                    email=form.email.data,
                    image_url=form.image_url.data or user.image_url,
                    header_image_url=form.header_image_url.data or user.header_image_url,
                    bio=form.bio.data or user.bio,
                    location=form.location.data or user.location,
                    user_id=user.id
                )

                # Handle user type-specific form submissions
                if user_type == 'fan' and fan_form and fan_form.validate_on_submit():

                    # Update fan-specific data
                    favorite_genre = fan_form.favorite_genre.data
                    favorite_band = fan_form.favorite_band.data
                    favorite_song = fan_form.favorite_song.data
                    concert_ex = fan_form.concert_ex.data
                    overplayed_song = fan_form.overplayed_song.data  
                  # Add logic for updating fan fields
                    success = User.update_user_fan(
                        g.user.id, 
                        favorite_genre, 
                        favorite_band, 
                        favorite_song, 
                        concert_ex, 
                        overplayed_song
                    )

                    if success:
                        flash("Your fan profile has been updated!", "success")
                        return redirect(url_for('users_show', user_id=g.user.id))

                    else:
                        flash("There was an error updating your profile. Please try again.", "danger")
                        return redirect(url_for("profile"))


                elif user_type == 'organizer' and organizer_form and organizer_form.validate_on_submit():

                    # Update fan-specific data
                    organization_name = organizer_form.organization_name.data
                    event_description = organizer_form.event_description.data
                    venue_locations = organizer_form.venue_locations.data
                    dates_unavailable = organizer_form.dates_unavailable.data
                    venue_capacity = organizer_form.venue_capacity.data  
                  # Add logic for updating fan fields
                    success = User.update_user_organizer(
                        g.user.id, 
                        organization_name, 
                        event_description, 
                        venue_locations,
                        dates_unavailable, 
                        venue_capacity 

                    )

                    if success:
                        flash("Your fan profile has been updated!", "success")
                        return redirect(url_for('users_show', user_id=g.user.id))
                    else:
                        flash("There was an error updating your profile. Please try again.", "danger")
                        return redirect(url_for("profile"))

                elif user_type == 'musician' and musician_form and musician_form.validate_on_submit():

                    # Update fan-specific data
                    members = musician_form.members.data
                    music_style= musician_form.music_style.data
                    band_name = musician_form.band_name.data
                    latest_release = musician_form.latest_release.data
                    music_achievments = musician_form.music_achievements.data  


                  # Add logic for updating fan fields
                    success = User.update_user_musician(
                        g.user.id, 
                        members, 
                        music_style, 
                        band_name, 
                        latest_release, 
                        music_achievments
                    )

                    if success:
                        flash("Your fan profile has been updated!", "success")
                        return redirect(url_for('users_show', user_id=g.user.id))
                    else:
                        flash("There was an error updating your profile. Please try again.", "danger")
                        return redirect(url_for("profile"))

            except IntegrityError:
                flash("Username already taken", 'danger')
                return render_template('users/edit.html', form=form, user_type=user_type)

            return redirect(f"/users/{g.user.id}")
    except Exception as err:
        flash(f"error: {err}")
        return render_template('users/edit.html', form=form, user_type=user_type)

    # Pre-fill the form with current user data if GET request
    form.username.data = g.user.username
    form.email.data = g.user.email
    form.image_url.data = g.user.image_url
    form.header_image_url.data = g.user.header_image_url
    form.bio.data = g.user.bio
    form.location.data = g.user.location
    delete_form = DeleteForm()


    return render_template('users/edit.html', form=form, user_type=user_type, 
                           fan_form=fan_form, organizer_form=organizer_form, musician_form=musician_form, delete_form=delete_form)


# Route to delete a user's account
@app.route('/users/delete', methods=["POST"])
def delete_user():

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    Post.query.filter_by(user_id=g.user.id).delete()
    

    db.session.delete(g.user)
    db.session.commit()
    do_logout()

    return redirect("/signup")

##############################################################################
# posts routes


# Get all a single users posts
def get_user_posts(user_id=None):
    if user_id is None:
        user_id = g.user.id

    posts = Post.query.filter_by(user_id=user_id).all()
    return posts


# Route to create a new message
@app.route('/posts/new', methods=["GET", "POST"])
def posts_add():
   
    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    form = PostForm()

    if form.validate_on_submit():
        post = Post(text=form.text.data)
        g.user.posts.append(post)
        db.session.commit()

        return redirect(f"/users/{g.user.id}")

    return render_template('posts/new.html', form=form)


# Route to show a specific message
@app.route('/posts/<int:message_id>', methods=["GET"])
def posts_show(message_id):
    """Display a specific message."""

    post = Post.query.get(message_id)
    return render_template('posts/show.html', message=post)


# Route to delete a specific message
@app.route('/posts/<int:message_id>/delete', methods=["POST"])
def posts_destroy(message_id):
    """Delete a message."""

    if not g.user:
        flash("Access unauthorized.", "danger")
        return redirect("/")

    post = Post.query.get(message_id)
    db.session.delete(post)
    db.session.commit()

    return redirect(f"/users/{g.user.id}")


##############################################################################
# Homepage and error pages

# Route for the homepage
@app.route('/')
def homepage():
    
    try:
        if g.user:
            # Fetch posts from users the logged-in user is following
            following_ids = [following.id for following in g.user.following] + [g.user.id]
            posts = (Post
                        .query.filter(Post.user_id.in_(following_ids))
                        .order_by(Post.timestamp.desc())
                        .limit(100)
                        .all())
            liked_post_ids = [post.id for post in g.user.likes]

            return render_template('home.html', posts=posts, likes=liked_post_ids, user_type=g.user.user_type)

        else:
            return render_template('home-anon.html')
    
    except Exception as err:
        flash(f"Error: {err}")
        return render_template('home-anon.html')


#%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
# Artist search via Spotify API

def get_spotify_token():
    url = 'https://accounts.spotify.com/api/token'
    
    # Ensure CLIENT_ID and CLIENT_SECRET are loaded from .env file
    
    
    if not CLIENT_ID or not CLIENT_SECRET:
        print("CLIENT_ID or CLIENT_SECRET is missing!")
        return None
    
    # Base64 encoding of CLIENT_ID:CLIENT_SECRET
    credentials = f"{CLIENT_ID}:{CLIENT_SECRET}".encode('utf-8')
    encoded_credentials = base64.b64encode(credentials).decode('utf-8')

    headers = {
        'Authorization': f'Basic {encoded_credentials}'
    }
    
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(url, headers=headers, data=data)

    if response.status_code == 200:
        token = response.json()['access_token']
        print("Access Token:", token)
        return token
    else:
        print("Error fetching token:", response.status_code)
        print(response.text)  # Print the response text for more details
        return None

def search_artists_by_name(artist_name):
    token = get_spotify_token()  # Get the token
    # if not token:
    #     print("Failed to get Spotify access token.")
    #     return []  # Return empty if no token is found
    
    url = f"https://api.spotify.com/v1/search?q={artist_name}&type=artist"
    headers = {
        'Authorization': f'Bearer {token}'
    }
    
    print(f"Requesting Spotify API with artist name: {artist_name}")
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        try:
            data = response.json()
            print("API response:", data)  # Print the API response to debug
            return data['artists']['items']  # Return the list of artists
        except KeyError:
            print("Error: Unexpected JSON structure. Response:", response.json())
            return []
    else:
        print(f"Error: Failed to fetch data from Spotify. Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return []



@app.route('/search', methods=['GET', 'POST'])
def search():
    artists = []  # Initialize an empty list to store artist results
    query = None  # Store the query to show on the page if needed
    
    posts = get_user_posts()
    
    if request.method == 'POST':
        artist_name = request.form.get('artist_name')  # Get artist name from the form
        if not artist_name:
            return "No artist name provided.", 400  # Return error if no name is provided

        artists = search_artists_by_name(artist_name)  # Fetch artist data based on the search query
        query = artist_name  # Store the query for rendering in the template

        if not artists:
            return "No artists found.", 404  
 
    # Ensure `user_type` is passed to the template along with other context variables
    return render_template(
        'users/show.html', 
        artists=artists, 
        query=query, 
        user=g.user,  
        user_type=g.user.user_type,  
        posts=posts
    )



@app.route('/artist/<artist_id>')
def artist(artist_id):
    artist_data = get_artist_data(artist_id)  # Get the artist data
    
    posts = get_user_posts()
    if not artist_data:
        flash("Artist not found", "danger")
        return redirect('users/show.html')  # Or handle the error more appropriately
    
    return render_template('users/show.html', artist=artist_data, user=g.user, posts=posts, user_type=g.user.user_type)  # Pass artist_data as artist

def get_artist_data(artist_id):
    token = get_spotify_token()
    url = f'https://api.spotify.com/v1/artists/{artist_id}'
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(url, headers=headers)
    return response.json()

##############################################################################
# Disable caching for the app (useful during development)
@app.after_request
def add_header(req):
    
    req.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    req.headers["Pragma"] = "no-cache"
    req.headers["Expires"] = "0"
    req.headers['Cache-Control'] = 'public, max-age=0'
    return req
if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        print("✅ Tables created in Supabase!")
