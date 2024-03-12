import base64
from datetime import datetime, timedelta
from ensta import Host, SessionHost
from flask import Flask, request, jsonify, render_template, redirect, url_for
from pymongo import MongoClient
from get_cookie import is_two_factor_required, login_v2
from Exceptions import (
    UserNotFound,
    SessionInfoIsNotValid
)
from werkzeug.exceptions import BadRequest


app = Flask(__name__)
client = MongoClient('mongodb://127.0.0.1:27017')


db = client['users']
collection_name = 'user_info'
if collection_name in db.list_collection_names():
    collection = db[collection_name]
else:
    collection = db.create_collection(collection_name)


def saveUserInformationToDatabase(username, followers, following, request_time=None, endpoint=None, session_data=None):
    user_data = collection.find_one({'username': username})

    # Kullanıcı adına ait veri yoksa, yeni bir belge oluşturun
    if user_data is None:
        byte_data = session_data.encode('utf-8')
        encoded_data = base64.b64encode(byte_data)

        user_data = {'username': username, 'followers': followers,
                     'following': following, 'session-data': encoded_data}

        if request_time:
            user_data[f'{endpoint}_request_time'] = request_time
        collection.insert_one(user_data)
    else:
        # Varolan kullanıcıya ait veriyi güncelleyin
        existing_followers = user_data.get('followers', [])
        existing_followers = list(set(existing_followers + followers))

        existing_following = user_data.get('following', [])
        existing_following = list(set(existing_following + following))

        user_data[f'{endpoint}_request_time'] = request_time

        byte_data = session_data.encode('utf-8')
        encoded_data = base64.b64encode(byte_data)

        update_data = {'followers': existing_followers, 'following': existing_following,
                       'session-data': encoded_data}
        if request_time:
            update_data[f'{endpoint}_request_time'] = request_time

        collection.update_one(
            {'username': username},
            {'$set': update_data}
        )


# Verisetinden verileri çek
def getFollowerList(host, username):
    follower_list = host.followers(username, count=0)
    return [user.username for user in follower_list]


# Verisetinden verileri çek
def getFollowingList(host, username):
    following_list = host.followings(username, count=0)
    return [user.username for user in following_list]


# Benim takip ettiğim onların beni takip etmediği kullanıcıları döndürür
def notFollowingMeBack(host, username):
    following_list = getFollowingList(host, username)
    follower_list = getFollowerList(host, username)
    not_following_back = [user for user in following_list if user not in follower_list]

    return not_following_back


# Onların beni takip ettiği benim takip etmediğim kullanıcıları döndürür
def ImNotFollowingBack(host, username):
    following_list = getFollowingList(host, username)
    follower_list = getFollowerList(host, username)
    not_following_back = [user for user in follower_list if user not in following_list]

    return not_following_back


def getUnfollowedUser(host, username):
    user_data = collection.find_one({"username": username})
    if user_data and "followers" in user_data:
        old_follower_list = user_data["followers"]
    else:
        old_follower_list = []
        return {'status': 'fail', 'error': 'user not found or user_data not found in db'}

    new_follower_list = getFollowerList(host, username)

    old_follower_set = set(old_follower_list)
    new_follower_set = set(new_follower_list)

    unfollowed_users = old_follower_set - new_follower_set

    return list(unfollowed_users)


# test_data = {'username': 'test_user', 'followers': [1, 2, 3], 'following': [4, 5, 6]}
# collection.insert_one(test_data)

def getRemainingTimeForNextFakeLogin(username):
    user_data = collection.find_one({'username': username})

    if user_data and 'login_request_time' in user_data:
        last_request_time = user_data['fake_login_request_time']
        elapsed_time = datetime.utcnow() - last_request_time
        remaining_time = timedelta(hours=12) - elapsed_time

        if remaining_time.total_seconds() > 0:
            return remaining_time
    return None


def getRemainingTimeForNextLoginRequest(username):
    user_data = collection.find_one({'username': username})

    if user_data and 'login_request_time' in user_data:
        last_request_time = user_data['login_request_time']
        elapsed_time = datetime.utcnow() - last_request_time
        remaining_time = timedelta(hours=12) - elapsed_time

        if remaining_time.total_seconds() > 0:
            return remaining_time
    return None


def getRemainingTimeForNextProfileRequest(username):
    user_data = collection.find_one({'username': username})

    if user_data and 'profileDetail_request_time' in user_data:
        last_request_time = user_data['profileDetail_request_time']
        elapsed_time = datetime.utcnow() - last_request_time
        remaining_time = timedelta(hours=12) - elapsed_time  # Örnek olarak 24 saatlik bir limit

        if remaining_time.total_seconds() > 0:
            return remaining_time
    return None


def getRemainingTimeForNextSessionRequest(username):
    user_data = collection.find_one({'username': username})

    if user_data and 'session_request_time' in user_data:
        last_request_time = user_data['session_request_time']
        elapsed_time = datetime.utcnow() - last_request_time
        remaining_time = timedelta(hours=12) - elapsed_time  # Örnek olarak 24 saatlik bir limit

        if remaining_time.total_seconds() > 0:
            return remaining_time
    return None


def getRemainingTimeForNextProfileInfoRequest(username):
    user_data = collection.find_one({'username': username})

    if user_data and 'profileInfo_request_time' in user_data:
        last_request_time = user_data['profileInfo_request_time']
        elapsed_time = datetime.utcnow() - last_request_time
        remaining_time = timedelta(hours=12) - elapsed_time  # Örnek olarak 24 saatlik bir limit

        if remaining_time.total_seconds() > 0:
            return remaining_time
    return None


def get_session_data_from_db(username):
    user_data = collection.find_one({'username': username})
    if user_data:
        session_data = user_data.get('session-data')
        encoded_data = base64.b64decode(session_data)
        byte_data = encoded_data.decode('utf-8')
        return byte_data

    else:
        raise UserNotFound('User not found, please make sure given username is correct,'
                           ' or try to login.')

# Sunucuda bu func var
# def get_session_data_from_db(username):
#     user_data = db.collection.find_one({'username': username})
#
#     if user_data and 'session-data' in user_data:
#         session_data = user_data['session-data']
#
#         # session_data bir string mi kontrol et
#         if isinstance(session_data, str):
#             try:
#                 session_data_json = json.loads(session_data)
#                 return session_data_json
#             except json.JSONDecodeError:
#                 # JSON decode hatası olursa
#                 print(f"JSON decode hatası: {session_data}")
#         else:
#             return session_data
#
#     return None


def is_session_valid(username):
    if username is None or username == "":
        raise UserNotFound("User not found, please make sure given username is correct")

    session_data = get_session_data_from_db(username=username)
    print(session_data)
    host = SessionHost(session_data)
    private_info = host.private_info().username

    if private_info:
        return True
    else:
        return False


@app.route('/is-session-valid', methods=['GET'])
def isSessionValid():
    username = request.headers.get('username')
    print(username)
    try:
        if username is None:
            raise BadRequest("Username parameter is missing")

        return jsonify({'status': 'ok', 'is-session-valid': is_session_valid(username)})

    except SessionInfoIsNotValid as e:

        return jsonify({'status': 'fail', 'msg': str(e)})

    except BadRequest as e:

        return jsonify({'status': 'fail', 'msg': str(e)})


@app.route('/fakeLogin', methods=['POST', 'GET'])
def fakeLogin():
    if request.method == 'POST':
        data = request.json
        username = data.get('username')
        password = data.get('password')
        proxy: dict[str, str] = {}
        two_factor_bool, response_json = is_two_factor_required(user_identifier=username,
                                                                password=password, proxy=proxy)
        if two_factor_bool:
            return jsonify({'status': 'ok',
                            'is_two_factor_required': 'true',
                            'response_json': response_json})

        else:
            return jsonify({'status': 'ok',
                            'is_two_factor_required': 'false',
                            'response_json': response_json})

        # else:
            # return redirect(url_for('login'))

    else:
        return render_template('index.html')


@app.route('/fake2FA', methods=['GET', 'POST'])
def fake2FA():
    if request.method == 'POST':
        data = request.json
        verification_code = data.get('verification_code')
        username = data.get('username')
        response_json = data.get('response_json')

        try:
            remaining_time = getRemainingTimeForNextFakeLogin(username)
            if remaining_time:
                return jsonify({"status": "fail",
                                "msg": f"Lütfen başka bir giriş isteği yapmadan önce {remaining_time} bekleyin."})

            session_info = login_v2(response_json=response_json,
                                    verification_code=verification_code, user_identifier=username)

            host = SessionHost(session_info)

            followers_list = getFollowerList(host, username)
            following_list = getFollowingList(host, username)
            saveUserInformationToDatabase(username, followers_list, following_list,
                                          request_time=datetime.utcnow(), endpoint='fake_login',
                                          session_data=session_info)

            return jsonify({'status': 'ok', 'session_data': session_info})

        except Exception as e:
            return jsonify({'status': 'fail', 'msg': str(e)})

    return render_template('two_factor.html')


@app.route('/login', methods=['POST'])
def login():
    """
    this function takes "username" & "password", and returns session_data which is used to perform authenticated requests
    """
    data = request.json
    username = data.get('username')
    password = data.get('password')
    two_factor = data.get('two_factor')
    proxy = data.get('proxy')

    try:
        remaining_time = getRemainingTimeForNextLoginRequest(username)
        if remaining_time:
            return jsonify({"status": "fail",
                            "message": f"Lütfen başka bir giriş isteği yapmadan önce {remaining_time} bekleyin."})

        # if is_session_valid(username):
        #    host = SessionHost()
        host = Host(username, password, totp_token=two_factor, proxy=proxy)

        followers_list = getFollowerList(host, username)
        following_list = getFollowingList(host, username)
        saveUserInformationToDatabase(username, followers_list, following_list,
                                      request_time=datetime.utcnow(), endpoint='login',
                                      session_data=host.session_data)

        return jsonify({"status": "ok",
                        "session_data": host.session_data})

    except Exception as e:
        # login failed
        return {"status": "fail", "message": str(e)}


@app.route('/profileDetail', methods=['GET'])
def profileDetail():
    username = request.headers.get('username')
    session_data = get_session_data_from_db(username=username)
    # Loads session data from database

    remaining_time = getRemainingTimeForNextProfileRequest(username)
    if remaining_time:
        return {"status": "fail", "message": f"Lütfen başka bir profil isteği yapmadan önce {remaining_time} bekleyin."}

    host = SessionHost(session_data=session_data)
    profile = host.profile(username)

    followers_list = getFollowerList(host, username)
    following_list = getFollowingList(host, username)
    saveUserInformationToDatabase(username, followers_list, following_list,
                                  request_time=datetime.utcnow(), endpoint='profileDetail',
                                  session_data=session_data)

    profileDetail = {
        'profile_pic_hd': profile.profile_picture_url_hd,
        'username': username,
        'full_name': profile.full_name,
        'biography': profile.biography,
        'follower_count': profile.follower_count,
        'follower_list': followers_list,
        'following_list': following_list,
        'following_count': profile.following_count,
        'post_count': profile.total_post_count
    }

    return {'status': 'ok', 'profileDetail': profileDetail}


@app.route('/stories', methods=['GET'])
def stories():
    # remaining_time = getRemainingTimeForNextRequest(username)
    # if remaining_time:
    #     return {"status": "fail", "message": f"Please wait {remaining_time} before making another request."}

    return {'status': 'this feature coming soon!'}


@app.route('/profileInfo', methods=['GET'])
def profileInfo():
    username = request.headers.get('username')
    session_data = get_session_data_from_db(username=username)
    remaining_time = getRemainingTimeForNextProfileInfoRequest(username)
    if remaining_time:
        return {"status": "fail", "message": f"Please wait {remaining_time} before making another request."}

    host = SessionHost(session_data=session_data)
    profile = host.profile(username)

    followers_list = getFollowerList(host, username)
    following_list = getFollowingList(host, username)
    saveUserInformationToDatabase(username, followers_list, following_list,
                                  request_time=datetime.utcnow(), endpoint='profileInfo',
                                  session_data=session_data)

    unfollowed_list = getUnfollowedUser(host, username)
    # notFollowingMeBack = notFollowingMeBack(host, username)
    # ImNotFollowingBack = ImNotFollowingBack(host, username)
    profileInfo = {
        'profile_picture_hd': profile.profile_picture_url_hd,
        'unfollowed_user_lenght': len(unfollowed_list),
        'unfollowed_user_usernames': unfollowed_list,
        'not_following_me_back': notFollowingMeBack,
        'Im_not_following_back': ImNotFollowingBack
    }

    return jsonify({'status': 'ok', 'profileInfo': profileInfo})


@app.route('/useSessionCookie', methods=['GET'])
def profile_data():
    username = request.headers.get('username')
    session_data = get_session_data_from_db(username=username)
    remaining_time = getRemainingTimeForNextSessionRequest(username)

    if remaining_time:
        return {"status": "fail", "message": f"Please wait {remaining_time} before making another request."}

    host = SessionHost(session_data=session_data)
    profile = host.profile(username)

    posts_url = []
    posts = profile.raw

    for post_key, post_value in posts.items():
        if post_key == 'edge_owner_to_timeline_media':
            for node in posts[post_key]['edges']:
                # for döngüsü içinde node değerine sahibiz
                post_id = host.get_post_id(f"https://www.instagram.com/p/{node['node']['shortcode']}")
                likers = host.likers(post_id)
                post_info = {
                    'url': node['node']['display_url'],
                    'comment_count': node['node']['edge_media_to_comment']['count'],
                    'likers': [{'username': user.username, 'profile_picture_url': user.profile_picture_url} for user in
                               likers.users],
                    'caption': [texts['node']['text'] for texts in node['node']['edge_media_to_caption']['edges']]
                }
                posts_url.append(post_info)

    wanted_informations = {
        'full_name': profile.full_name,
        'biography': profile.biography,
        'biography_link': profile.biography_links,
        'follower': profile.follower_count,
        'following': profile.following_count,
        'profile_picture_url_hd': profile.profile_picture_url_hd,
        'post_info': posts_url,  # Gives post_link, post_comment_count, post_likers, post_caption
        'total_post_count': profile.total_post_count,
        'unfollowed_users': getUnfollowedUser(host, username)
    }

    return jsonify({'status': 'ok', 'profile': wanted_informations})
    # else:
    #     return {"status": "fail", "message": "Invalid username"}


@app.route('/getProfilePicHD', methods=['GET'])
def getProfilePicHD():
    username = request.headers.get('username')
    session_data = get_session_data_from_db(username=username)

    try:
        host = SessionHost(session_data=session_data)
        profile = host.profile(username=username)
        profile_pic_hd = profile.profile_picture_url_hd

        return jsonify({'status': 'ok',
                        'profile_pic_hd': profile_pic_hd})

    except Exception as e:
        return jsonify({'status': 'fail',
                        'msg': str(e)})


@app.route('/unfollow-user', methods=['POST'])
def unfollowUser():
    data = request.json
    username = data.get('username')
    target_username = data.get("target_username")
    # TODO target username verisini kullanıcıları unfollow ederken,
    # TODO random saniyelerle beklet

    if username is None:
        return jsonify({'status': 'fail',
                        'msg': UserNotFound('User not found, please make sure given username is correct,'
                                            ' or try to login.')})

    if target_username is None:
        return jsonify({'status': 'fail',
                        'msg': UserNotFound('Please make sure given username is correct.')})

    try:
        session_data = get_session_data_from_db(username)
        host = SessionHost(session_data)
        host.unfollow(target_username)

        return jsonify({'status': 'ok', 'msg': 'User unfollowed'})

    except Exception as e:
        return jsonify({'status': 'fail', 'msg': str(e)})


@app.route('/get-username-pp-follower', methods=['GET'])
def getUsernamePPFollower():
    username = request.headers.get('username')
    user_information = collection.find_one({'username': username})
    user_follower = user_information.get('followers')
    user_inf = []
    user_following = None

    session_data = get_session_data_from_db(username)
    host = SessionHost(session_data)

    try:
        for user_follower_iterated in user_follower:
            profile = host.profile(user_follower_iterated)
            user_inf.append((user_follower_iterated, profile.profile_picture_url_hd))

        return jsonify({'status': 'ok',
                        'response': user_inf})

    except Exception as e:
        return jsonify({'status': 'fail',
                        'msg': str(e)})


@app.route('/get-username-pp-following', methods=['GET'])
def getUsernamePPFollowing():
    username = request.headers.get('username')
    user_information = collection.find_one({'username': username})
    user_following = user_information.get('following')
    user_inf = []

    session_data = get_session_data_from_db(username)
    host = SessionHost(session_data)

    try:

        for user_following_iterated in user_following:
            profile = host.profile(user_following_iterated)
            user_inf.append((user_following_iterated, profile.profile_picture_url_hd))

        return jsonify({'status': 'ok',
                        'response': user_inf})

    except Exception as e:
        return jsonify({'status': 'fail',
                        'msg': str(e)})


if __name__ == '__main__':
    app.run(debug=True, port=8090)
