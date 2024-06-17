![MongoDB](https://img.shields.io/badge/MongoDB-%234ea94b.svg?style=for-the-badge&logo=mongodb&logoColor=white)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

# Instagram API

A great backend service for applications. 
Provides database to register users and track their activity.

It allows you to use session data for back-to-back or intermittent transactions without the need to log in again, and with a 12-hour cooldown when making requests to each endpoint, it allows you to avoid instagram knowing you're acting suspiciously.

![Flowchart](https://github.com/OlguD/inst-api/blob/main/flowchart.png)


I look forward to you contributing to this repository, there's a lot to do.



## API Reference

#### Checks if the session still valid

```http
  GET /is-session-valid
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `username` | `string` | **Required**.Useraname for checking session is still valid|

---

### Login v2
This endpoint checks if the user have 2FA. If enabled returns:
It gives an information about if the user have 2FA.
```python
return jsonify({'status': 'ok',
                'is_two_factor_required': 'true',
                'response_json': response_json})
```

```http
  POST /fakeLogin
```
```http
  GET /fakeLogin
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `username, password`      | `string` | **Required** for login |

---

### If user enabled 2FA this endpoint makes user login.

This endpoint saves user information (followers, followings, etc.).

```http
  POST /fake2FA
```
```http
  GET /fake2FA
```

| Parameter | Type     | 
| :-------- | :------- |
| `verification_code, username, response_json`      | `string` |


---

### Login.

If user doesn't enabled 2FA you can directly use this endpoint. It does the same job with /fake2FA endpoint but /login endpoint takes only username, password informations.

```http
  POST /login
```

| Parameter | Type     | 
| :-------- | :------- |
| `username, password, proxy`      | `string` |

---

### Profile Detail.

This endpoint provides follower lists, following lists and the informations below:

```python
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

```

```http
  GET /profileDetail
```

| Parameter | Type     | 
| :-------- | :------- |
| `username`      | `string` |


---

### Profile Information.

This endpoint provides follower and following activities.

```python
profileInfo = {
    'profile_picture_hd': profile.profile_picture_url_hd,
    'unfollowed_user_lenght': len(unfollowed_list),
    'unfollowed_user_usernames': unfollowed_list,
    'not_following_me_back': notFollowingMeBack,
    'Im_not_following_back': ImNotFollowingBack
}
```

```http
  GET /profileInfo
```

| Parameter | Type     | 
| :-------- | :------- |
| `username`      | `string` |


---

### Session Cookie.

This endpoint provides getting user profile informations, followings, followers without login if the session informations still valid.

```python
informations = {
    'full_name': profile.full_name,
    'biography': profile.biography,
    'biography_link': profile.biography_links,
    'follower': profile.follower_count,
    'following': profile.following_count,
    'profile_picture_url_hd': profile.profile_picture_url_hd,
    'post_info': posts_url,
    'total_post_count': profile.total_post_count,
    'unfollowed_users': getUnfollowedUser(host, username)
}
```

```http
  GET /useSessionCookie
```

| Parameter | Type     | 
| :-------- | :------- |
| `username`      | `string` |


---

### Profile Picture HD.

```python
return jsonify({'status': 'ok',
                'profile_pic_hd': profile_pic_hd})
```

```http
  GET /getProfilePicHD
```

| Parameter | Type     | 
| :-------- | :------- |
| `username`      | `string` |


---

### Unfollow user.

```python
return jsonify({'status': 'ok', 'msg': 'User unfollowed'})
```

```http
  POST /unfollow-user
```

| Parameter | Type     | 
| :-------- | :------- |
| `username, target_username`      | `string` |



---
## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/OlguD/inst-api/blob/main/LICENSE) file for details.

## Acknowledgements

This project uses code from [ENSTA](https://github.com/diezo/Ensta), which is licensed under the MIT License.
