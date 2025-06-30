# Jam Space
## Link to Jam Space website: [Jam Space](https://jam-space.onrender.com)

### Jam Space is a music lovers hub where organizers, musicians and fans can connect and share their musical journey.
 

 ## how to set up app locally:
 - clone repo to your machine 
 ```
git clone <your-repo-url>
cd <your-project-directory>

 ```
 - install and set up postgresQL on your machine
 - Set a username and password during installation or use your system's user account.
 - create a database.
 ```
 createdb name_of_database

 ```
 - inside of the root of the project create an env file 
 - inside of the env file create a local db varible called LOCAL_DB
 ``` 
 LOCAL_DB=postgresql://postgressUsername:[yourPostgressPassword]@localhost:5432/nameOfDatabase
 ```
 - install the denpendicies with the the following code in the terminal console.
 ```
pip install -r requirements.txt
 ```
 - if any requirements fail to install, attempt to start the server using the command. then manually install the missing dependicies as they appear in the console
 ```
flask run

pip install package-name

 ```


#### Jam Space:
![Image of Jam Space.](static/images/Jam_Space1.png "Profile View")

#### The focus here isn't to create another social media app, but to cater to those who see music as essentail to life as water
#### Every user has access to a search form where they can look up and view details about their favorite artists using the Spotify API
![Image of the spotify API being used to search for an artist.](static/images/Jam_Space2.png "API in use.")

#### App Features Include:
* upon registering for Jam Space a user will be asked which type of account they would like to create. This will change the users experience depending on thier choice.

### Image of one of the possible options given to a user
![one of the possible options](static/images/Jam_Space3.png "Sign up Page")

* The profile of a user will contain different fields including:
	* \# Favorite genre - Fan profile
	* \# Most memorable concert experience - Fan profile
	* \# Venue capacity - Organizer profile
	* \# Organization name - Organizer profile
	* \# Band members - Musician profile
	* \# Latest release - Musician profile
    * \# Just to name a few.

* Fans, musicians and Organizers can interact with one another just as you would expect from any social media platform:
	* Secure login 
	* Make posts 
	* like posts
	* follow others
	* User friendly UI



#### Resources Used:

* Spotify API: [https://developer.spotify.com/documentation/web-api](https://developer.spotify.com/documentation/web-api)

#### Technology Used:
* Flask
* Python
* BeautifulSoup
* Bootstrap
* Jinja
# jam_space
