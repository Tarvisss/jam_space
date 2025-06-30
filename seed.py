
from app import db
from models import User


db.drop_all()
db.create_all()



def seed_users():
    users= [
        User(email="when@yahoo.com",username="tuckerdiane", image_url="https://images.pexels.com/photos/29877967/pexels-photo-29877967/free-photo-of-urban-street-scene-with-elderly-man-in-focus.jpeg?auto=compress&cs=tinysrgb&w=600",password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe", bio="Dumb as can be!", header_image_url="https://cdn.pixabay.com/photo/2016/06/02/02/33/triangles-1430105_1280.png", location="Home is where you make it", user_type="fan"),
        User(email="Where@yahoo.com",username="hehehaha", image_url="https://images.pexels.com/photos/19270854/pexels-photo-19270854/free-photo-of-redhead-model-in-coat-on-city-street.jpeg?auto=compress&cs=tinysrgb&w=600",password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe", bio="Where the party at!", header_image_url="https://cdn.pixabay.com/photo/2015/12/09/01/02/mandalas-1084082_960_720.jpg", location="Outer Space",user_type="fan"),
        User(email="Who@yahoo.com",username="Squirl Master", image_url="https://images.pexels.com/photos/27856326/pexels-photo-27856326/free-photo-of-handsome-boy.jpeg?auto=compress&cs=tinysrgb&w=600",password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe", bio="Sometimes it's not worth it", header_image_url="https://cdn.pixabay.com/photo/2022/01/28/18/32/leaves-6975462_960_720.png", location="Everywhere", user_type="fan"),
        User(email="what@yahoo.com",username="Coolio", image_url="https://images.pexels.com/photos/6034162/pexels-photo-6034162.jpeg?auto=compress&cs=tinysrgb&w=600",password="$2b$12$Q1PUFjhN/AWRQ21LbGYvjeLpZZB6lfZ1BPwifHALGO6oIbyC3CmJe", bio="Everytime sometimes.....", header_image_url="https://cdn.pixabay.com/photo/2017/06/14/08/20/map-of-the-world-2401458_1280.jpg", location="Yolo", user_type="fan")
    ]




    db.session.add_all(users)
    db.session.commit()
if __name__ == '__main__':
    seed_users()