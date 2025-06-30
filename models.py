"""SQLAlchemy models for Jam Space."""

# Import necessary libraries
from datetime import datetime
from flask_bcrypt import Bcrypt  # For hashing passwords
from flask_sqlalchemy import SQLAlchemy  # ORM for interacting with SQL databases

# Initialize bcrypt object for password hashing
bcrypt = Bcrypt()

# Initialize SQLAlchemy object for database interaction
db = SQLAlchemy()

# Model representing the relationship between users who follow each other
class Follows(db.Model):
    """Connection of a follower <-> followed_user."""
    
    __tablename__ = 'follows'  # Table name in the database

    # Foreign key pointing to the 'id' of a user who is being followed
    user_being_followed_id = db.Column(db.Integer,db.ForeignKey('users.id', ondelete="cascade"),primary_key=True,)  # This column is part of the composite primary key

    # Foreign key pointing to the 'id' of a user who is following
    user_following_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete="cascade"),
        primary_key=True,  # This column is part of the composite primary key
    )


# Model representing the relationship between users and the posts they "like"
class Likes(db.Model):
    """Mapping user likes to Posts."""
    
    __tablename__ = 'likes'  # Table name in the database

    # Primary key for the 'likes' table
    id = db.Column(
        db.Integer,
        primary_key=True
    )

    # Foreign key to the 'users' table, representing the user who liked the message
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='cascade')
    )

    # Foreign key to the 'posts' table, representing the liked message
    message_id = db.Column(
        db.Integer,
        db.ForeignKey('posts.id', ondelete='cascade'),
        unique=True  # Each message can only be liked once by the same user
    )

# Model representing a user in the system
class User(db.Model):
    """User in the system."""
    
    __tablename__ = 'users'  # Table name in the database

    # Primary key for the 'users' table
    id = db.Column(db.Integer,primary_key=True,)

    # The user's email address (must be unique)
    email = db.Column(db.Text,nullable=False,unique=True,)

    # The user's username (must be unique)
    username = db.Column(db.Text,nullable=False,unique=True,)

    # Profile picture URL (defaults to a placeholder image if not provided)
    image_url = db.Column(db.String(256), default='/static/images/default-pic.png')

    # Header image URL (defaults to a placeholder image if not provided)
    header_image_url = db.Column(db.Text,default="/static/images/pexels-mitja-juraja-357365-970517.jpg")

    # The user's bio (defaults to "Introverted" if not provided)
    bio = db.Column(db.Text,default="Introverted.")

    # The user's location (defaults to "You can't find me." if not provided)
    location = db.Column(db.Text,default="You can't find me.")

    # The user's hashed password (mandatory field)
    password = db.Column(db.Text,nullable=False,)

    # The users selected account type
    user_type = db.Column(db.Text, nullable=False)

    # Add these fields for fan-specific data
    favorite_genre = db.Column(db.String(100))

    favorite_band = db.Column(db.String(100))

    favorite_song = db.Column(db.String(100))

    concert_ex = db.Column(db.Text)

    overplayed_song = db.Column(db.Text)

    # Add these fields for organizer-specific data
    organization_name = db.Column(db.Text)

    event_description = db.Column(db.String(100))

    venue_locations = db.Column(db.String(100))

    dates_unavailable = db.Column(db.Text)

    venue_capacity = db.Column(db.Text)

    # Add these fields for musician-specific data
    members = db.Column(db.String(100))

    music_style = db.Column(db.String(100))

    band_name = db.Column(db.String(100))

    latest_release= db.Column(db.Text)

    music_achievments = db.Column(db.Text)




    # Relationship for a user to have many posts
    posts = db.relationship('Post')

    # Relationship for a user to have many followers (through the 'follows' table)
    followers = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_being_followed_id == id),
        secondaryjoin=(Follows.user_following_id == id)
    )

    # Relationship for a user to follow many other users (through the 'follows' table)
    following = db.relationship(
        "User",
        secondary="follows",
        primaryjoin=(Follows.user_following_id == id),
        secondaryjoin=(Follows.user_being_followed_id == id)
    )

    # Relationship for a user to like many posts (through the 'likes' table)
    likes = db.relationship(
        'Post',
        secondary="likes"
    )

    # String representation of the User object (used for debugging/logging)
    def __repr__(self):
        return f"<User #{self.id}: {self.username}, {self.email}>"

    # Method to check if the user is followed by another user
    def is_followed_by(self, other_user):
        """Is this user followed by `other_user`?"""

        # Check if the user exists in the followers list
        found_user_list = [user for user in self.followers if user == other_user]
        return len(found_user_list) == 1

    # Method to check if the user is following another user
    def is_following(self, other_user):
        """Is this user following `other_user`?"""

        # Check if the user exists in the following list
        found_user_list = [user for user in self.following if user == other_user]
        return len(found_user_list) == 1

    # Class method to create and sign up a new user
    @classmethod
    def signup(cls, username, email, password, image_url, user_type):
       

        # Hash the password using bcrypt
        hashed_pwd = bcrypt.generate_password_hash(password).decode('UTF-8')

        # Create a new user instance
        user = User(
            username=username,
            email=email,
            password=hashed_pwd,
            image_url=image_url,
            user_type=user_type,
        )

        # Add the user to the database session
        db.session.add(user)
        return user
    
    # Class method to update an existing user's information
    @classmethod
    def update_user(cls, user_id, username, email, image_url, bio, header_image_url, location):
        
        # Find the user by their ID
        user = cls.query.get(user_id)

        if user:
            # Update user attributes with the provided values
            user.username = username
            user.email = email
            user.bio = bio
            user.header_image_url = header_image_url
            user.image_url = image_url
            user.location = location

            # Commit the changes to persist them in the database
            db.session.commit()
            return True
        else:
            return False

    @classmethod
    def update_user_fan(cls, user_id, favorite_genre, favorite_band, favorite_song, concert_ex, overplayed_song):
        
        # Find the user by their ID
        user = cls.query.get(user_id)

        if user:
            # Update user attributes with the provided values
            user.favorite_genre = favorite_genre
            user.favorite_band = favorite_band
            user.favorite_song = favorite_song
            user.concert_ex = concert_ex
            user.overplayed_song = overplayed_song

            # Commit the changes to persist them in the database
            db.session.commit()
            return True
        else:
            return False
    
    @classmethod
    def update_user_organizer(cls, user_id, organization_name, event_description, venue_locations, dates_unavailable, venue_capacity):

        
        # Find the user by their ID
        user = cls.query.get(user_id)

        if user:
            # Update user attributes with the provided values
            user.organization_name = organization_name
            user.event_description = event_description
            user.venue_locations = venue_locations
            user.dates_unavailable = dates_unavailable
            user.venue_capacity = venue_capacity

            # Commit the changes to persist them in the database
            db.session.commit()
            return True
        else:
            return False
        

    @classmethod
    def update_user_musician(cls, user_id, members, music_style, band_name, latest_release, music_achievments):
        
        # Find the user by their ID
        user = cls.query.get(user_id)

        if user:
            # Update user attributes with the provided values
            user.members = members
            user.music_style = music_style
            user.band_name = band_name
            user.latest_release = latest_release
            user.music_achievments = music_achievments

            # Commit the changes to persist them in the database
            db.session.commit()
            return True
        else:
            return False
    # Class method to authenticate a user by checking their username and password
    @classmethod
    def authenticate(cls, username, password):
        """Find user with `username` and `password`.

        This is a class method (call it on the class, not an individual user.)
        It searches for a user whose password hash matches this password
        and, if it finds such a user, returns that user object.

        If can't find matching user (or if password is wrong), returns False.
        """

        # Find the user by their username
        user = cls.query.filter_by(username=username).first()

        if user:
            # Check if the provided password matches the stored hashed password
            is_auth = bcrypt.check_password_hash(user.password, password)
            if is_auth:
                return user

        return False


# Model representing a message ("warble")
class Post(db.Model):
    """An individual post."""

    __tablename__ = 'posts'  # Table name in the database

    # Primary key for the 'posts' table
    id = db.Column(
        db.Integer,
        primary_key=True,
    )

    # The text content of the message (max 140 characters)
    text = db.Column(
        db.Text,
        nullable=False,
    )

    # Timestamp of when the message was created (defaults to the current date and time)
    timestamp = db.Column(
        db.DateTime,
        nullable=False,
        default=datetime.now(),  # Sets the default value as the current date and time
    )

    # Foreign key to the 'users' table (who created this message)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id', ondelete='CASCADE'),
        nullable=False,
    )

    # Relationship to the 'User' table (creator of the message)
    user = db.relationship('User')


# Function to connect the database to the Flask app
def connect_db(app):

    db.app = app  # Assign the Flask app to the db object
    db.init_app(app)  # Initialize the db with the Flask app
