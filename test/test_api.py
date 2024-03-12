import unittest
# import app
import requests
import json
from pymongo import MongoClient


class APITest(unittest.TestCase):
    def setUp(self):
        self.base_url = "http://127.0.0.1:8090"
        self.profile_data = {'username': 'fegimib190'}
        self.client = MongoClient('mongodb://127.0.0.1:27017/?directConnection=true&serverSelectionTimeoutMS=2000&appName=mongosh+2.1.0')
        self.db = self.client['users']  # test veritabanı adı
        self.collection = self.db['user_info']  # test koleksiyon adı
        self.follower_following_data = None

    # def test_follower_list_in_db(self):
    #     pass

    # def test_following_list_in_db(self):
    #     pass

    # def test_login_limit(self):
    #     pass

    # def test_using_session_host_limit(self):
    #     pass

    def test_add_user_to_db(self):
        pass

    def test_added_user_in_db(self):
        pass

    def test_delete_user_in_db(self):
        pass
    

    def test_add_user_follower_and_following_to_db_and_test_added(self):
        url = self.base_url + "/profileDetail"
        login_data = {'username': 'fegimib190'}
        profileDetail = requests.get(url, params=login_data)
        self.follower_following_data = self.collection.find_one({'username': 'fegimib190'})
        expected_follower_list = ['olgudaolgu', 'mor_ad1140']
        expected_following_list = ['scotteastwood', 'instagram', 'dinahjane', 'salicerose', '90skid4lyfe', 'cmpulisic']
        self.assertIsNotNone(self.follower_following_data)

        if self.follower_following_data:
            # print("Follower Following Data:", self.follower_following_data)

            actual_follower_list = self.follower_following_data.get('followers')
            actual_following_list = self.follower_following_data.get('following')

            # print("Actual Follower List:", actual_follower_list)
            # print("Actual Following List:", actual_following_list)

            self.assertIsNotNone(actual_follower_list)
            self.assertIsNotNone(actual_following_list)

            self.assertSetEqual(set(expected_follower_list), set(actual_follower_list))
            self.assertSetEqual(set(expected_following_list), set(actual_following_list))
        else:
            self.fail("Failed to retrieve follower_following_data from the database.")

    def test_user_login(self):
        url = self.base_url + "/login"
        login_data = {'username': 'fegimib190', 'password': 'bionluk.10'}
        login = requests.post(url, data=login_data) 
        self.assertEqual(login.status_code, 200)

    def test_profile_detail(self):
        url = self.base_url + "/profileDetail"
        response = requests.get(url, params=self.profile_data)

        self.assertEqual(response.status_code, 200)

    def test_stories(self):
        url = self.base_url + "/stories"
        response = requests.get(url, params=self.profile_data)
        sample = {'status': 'this feature coming soon!'}
        self.assertEqual(response.json(), sample)

    # def test_profile_info(self):
    #     url = self.base_url + "/profileInfo"
    #     response = requests.get(url, params=self.profile_data)
    #     sampleOutput = {
    #     'profile_picture_hd': 'https://instagram.fgye25-1.fna.fbcdn.net/v/t51.2885-19/44884218_345707102882519_2446069589734326272_n.jpg?_nc_ht=instagram.fgye25-1.fna.fbcdn.net&_nc_cat=1&_nc_ohc=usNCOR8H6Z0AX_t9JAg&edm=AAAAAAABAAAA&ccb=7-5&ig_cache_key=YW5vbnltb3VzX3Byb2ZpbGVfcGlj.2-ccb7-5&oh=00_AfCdoqnqofbpnjwBKA0SWszDJzVUj8uQ-tJUxn9nOlorWA&oe=6579138F&_nc_sid=2c5659',
    #     'unfollowed_user_lenght': 0,
    #     'unfollowed_user_usernames': []
    #     }
    #     # self.assertEqual(response.json(), {'profileInfo': sampleOutput})
    #     print(response.json())

    @unittest.skip("Not added this feature yet")
    def test_login_limitations(self):
        url = self.base_url + "/login"
        login_data = {'username': 'fegimib190', 'password': 'bionluk.10'}
        for i in range(11):
            response = requests.post(url, data=login_data)
            print(f"---Loop: {i}")
        self.assertEqual(response.status_code, 429)

    # @unittest.skip('will be look after')
    def test_follower_list_limit(self):
        url = self.base_url + "/profileDetail"
        username = {'username': 'acmilan'}
        response = requests.get(url, params=username)
        self.assertEqual(response.status_code, 200)

    # status_code
    def test_status_code_profile_detail(self):
        url = self.base_url + "/profileDetail"
        response = requests.get(url, params=self.profile_data)
        self.assertEqual(response.status_code, 200)

    def test_status_code_test_stories(self):
        url = self.base_url + "/stories"
        response = requests.get(url, params=self.profile_data)
        self.assertEqual(response.status_code, 200)

    def test_status_code_profile_info(self):
        url = self.base_url + "/profileInfo"
        response = requests.get(url, params=self.profile_data)
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()