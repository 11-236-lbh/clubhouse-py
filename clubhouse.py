#/usr/bin/python -u
#-*- coding: utf-8 -*-

"""
clubhouse.py

API for Clubhouse (v297 / 0.1.27)
Developed for education purposes only.

Please know what you're doing!
Modifying a bit of header could result a permanent block on your account.
"""

import uuid
import random
import secrets
import functools
import requests

class Clubhouse:
    """
    Clubhouse Class
    """

    # App/API Information
    API_URL = "https://www.clubhouseapi.com/api"
    API_BUILD_ID = "297"
    API_BUILD_VERSION = "0.1.27"
    API_UA = "clubhouse/297 (iPhone; iOS 13.5.1; Scale/3.00)"

    # Some useful information for commmunication
    PUBNUB_PUB_KEY = "pub-c-6878d382-5ae6-4494-9099-f930f938868b"
    PUBNUB_SUB_KEY = "sub-c-a4abea84-9ca3-11ea-8e71-f2b83ac9263d"

    TWITTER_ID = "NyJhARWVYU1X3qJZtC2154xSI"
    TWITTER_SECRET = "ylFImLBFaOE362uwr4jut8S8gXGWh93S1TUKbkfh7jDIPse02o"

    AGORA_KEY = "938de3e8055e42b281bb8c6f69c21f78"
    SENTRY_KEY = "5374a416cd2d4009a781b49d1bd9ef44@o325556.ingest.sentry.io/5245095"
    INSTABUG_KEY = "4e53155da9b00728caa5249f2e35d6b3"
    AMPLITUDE_KEY = "9098a21a950e7cb0933fb5b30affe5be"

    # Useful header information
    HEADERS = {
        "CH-Languages": "en-JP,ja-JP",
        "CH-Locale": "en_JP",
        "Accept": "application/json",
        "Accept-Language": "en-JP;q=1, ja-JP;q=0.9",
        "Accept-Encoding": "gzip, deflate",
        "CH-AppBuild": f"{API_BUILD_ID}",
        "CH-AppVersion": f"{API_BUILD_VERSION}",
        "User-Agent": f"{API_UA}",
        "Connection": "close",
        "Content-Type": "application/json; charset=utf-8",
        "Cookie": f"__cfduid={secrets.token_hex(21)}{random.randint(1, 9)}"
    }


    def require_authentication(func):
        """ Simple decorator to check for the authentication """
        @functools.wraps(func)
        def wrap(self, *args, **kwargs):
            if not (self.HEADERS.get("CH-UserID") and
                    self.HEADERS.get("CH-DeviceId") and
                    self.HEADERS.get("Authorization")):
                raise Exception('Not Authenticated')
            return func(self, *args, **kwargs)
        return wrap


    def __init__(self, user_id='', user_token='', user_device=''):
        """ (Clubhouse, str, str, str) -> NoneType

        Set authenticated information
        """
        self.HEADERS['CH-UserID'] = user_id if user_id else "(null)"
        if user_token:
            self.HEADERS['Authorization'] = f"Token {user_token}"
        self.HEADERS['CH-DeviceId'] = user_device.upper() if user_device else str(uuid.uuid4()).upper()

    def __str__(self):
        """ (Clubhouse) -> str

        Get information about the given class.

        >>> clubhouse = Clubhouse()
        >>> str(clubhouse)
        Clubhouse(user_id=(null), user_token=None, user_device=31525f52-6b67-40de-83c0-8f9fe0f6f409)
        """
        return "Clubhouse(user_Id={}, user_token={}, user_device={}".format(
            self.HEADERS.get('CH-UserID'),
            self.HEADERS.get('Authorization'),
            self.HEADERS.get('CH-DeviceId')
        )

    def start_phone_number_auth(self, phone_number):
        """ (Clubhouse, str) -> dict

        Begin phone number authentication.
        Some examples for the phone number.

        >>> clubhouse = Clubhouse()
        >>> clubhouse.start_phone_number_auth("+821012341337")
        ...
        >>> clubhouse.start_phone_number_auth("+818013371221")
        ...
        """
        if self.HEADERS.get("Authorization"):
            raise Exception('Already Authenticatied')
        data = {
            "phone_number": phone_number
        }
        req = requests.post(f"{self.API_URL}/start_phone_number_auth", headers=self.HEADERS, json=data)
        return req.json()


    def complete_phone_number_auth(self, phone_number, verification_code):
        """ (Clubhouse, str, str) -> dict

        Complete phone number authentication.
        This should return `auth_token`, `access_token`, `refresh_token`, is_waitlisted, ...

        Please note that output may be different depending on the status of the authenticated user
        """
        if self.HEADERS.get("Authorization"):
            raise Exception('Already Authenticatied')
        data = {
            "phone_number": phone_number,
            "verification_code": verification_code
        }
        req = requests.post(f"{self.API_URL}/complete_phone_number_auth", headers=self.HEADERS, json=data)
        # find out how userId is taken
        return req.json()


    def check_for_update(self, is_testflight=False):
        """ (Clubhouse, bool) -> dict

        Check for app updates.

        >>> clubhouse = Clubhouse()
        >>> clubhouse.check_for_update(False)
        {'has_update': False, 'success': True}
        """
        query = f"is_testflight={int(is_testflight)}"
        req = requests.get(f"{self.API_URL}/check_for_update?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def add_email(self, email):
        """ (Clubhouse, str) -> dict

        Request for email verification.
        You only need to do this once.
        """
        data = {
            "email": email
        }
        req = requests.post(f"{self.API_URL}/add_email", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def update_photo(self, photo_filename):
        """ (Clubhouse, str) -> dict

        Update photo. Please make sure to upload a JPG format.
        """
        files = {
            "file": ("image.jpg", open(photo_filename, "rb"), "image/jpeg"),
        }
        tmp = self.HEADERS['Content-Type']
        self.HEADERS.pop("Content-Type")
        req = requests.post(f"{self.API_URL}/update_photo", headers=self.HEADERS, files=files)
        self.HEADERS['Content-Type'] = tmp
        return req.json()


    @require_authentication
    def unfollow(self, user_id):
        """ (Clubhouse, int) -> dict

        Unfollow a user.
        """
        data = {
            "user_id": int(user_id)
        }
        req = requests.post(f"{self.API_URL}/unfollow", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def follow(self, user_id, user_ids=None, source=4, source_topic_id=None):
        """ (Clubhouse, int, list, int, int) -> dict

        Follow a user.
        Different value for `source` may require different parameters to be set
        """
        data = {
            "source_topic_id": source_topic_id,
            "user_ids": user_ids,
            "user_id": int(user_id),
            "source": source
        }
        req = requests.post(f"{self.API_URL}/follow", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def follow_club(self, club_id, source_topic_id=None):
        """ (Clubhouse, int, int) -> dict

        Follow a club
        """
        data = {
            "club_id": int(club_id),
            "source_topic_id": source_topic_id
        }
        req = requests.post(f"{self.API_URL}/follow_club", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def unfollow_club(self, club_id, source_topic_id=None):
        """ (Clubhouse, int, int) -> dict

        Unfollow a club
        """
        data = {
            "club_id": int(club_id),
            "source_topic_id": source_topic_id
        }
        req = requests.post(f"{self.API_URL}/unfollow_club", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def update_follow_notifications(self, user_id, notification_type=2):
        """ (Clubhouse, str, int) -> dict

        Update notification frequency for the given user.
        1 = Always notify, 2 = Sometimes, 3 = Never
        """
        data = {
            "user_id": int(user_id),
            "notification_type": int(notification_type)
        }
        req = requests.post(f"{self.API_URL}/update_follow_notifications", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_suggested_follows_similar(self, user_id):
        """ (Clubhouse, int) -> dict

        Get similar users based on the given user.
        """
        data = {
            "user_id": int(user_id),
        }
        req = requests.post(f"{self.API_URL}/get_suggested_follows_similar", headers=self.HEADERS, json=data)
        return req.json()

    @require_authentication
    def get_events(self, is_filtered=True, page_size=25, page=1):
        """ (Clubhouse, bool, int, int) -> dict

        Get list of upcoming events with details.
        """
        _is_filtered = "true" if is_filtered else "false"
        query = f"is_filtered={_is_filtered}&page_size={page_size}&page={page}"
        req = requests.get(f"{self.API_URL}/get_events?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def get_club(self, club_id, source_topic_id=None):
        """ (Clubhouse, int, int) -> dict

        Get the information about the given club_id.
        """
        data = {
            "club_id": int(club_id),
            "source_topic_id": source_topic_id
        }
        req = requests.post(f"{self.API_URL}/get_club", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_club_members(self, club_id, return_followers=False, return_members=True, page_size=50, page=1):
        """ (Clubhouse, int, bool, bool, int, int) -> dict

        Get list of members on the given club_id.
        """
        query = "club_id={}&return_followers={}&return_members={}&page_size={}&page={}".format(
            club_id,
            int(return_followers),
            int(return_members),
            page_size,
            page
        )
        req = requests.get(f"{self.API_URL}/get_club_members?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def join_channel(self, channel, attribution_source="feed"):
        """ (Clubhouse, str, str) -> dict

        Join the given channel
        """
        # Join channel
        data = {
            "channel": channel,
            "attribution_source": attribution_source,
            "attribution_details": "eyJpc19leHBsb3JlIjpmYWxzZSwicmFuayI6MX0=",
        }
        req = requests.post(f"{self.API_URL}/join_channel", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def leave_channel(self, channel):
        """ (Clubhouse, str) -> dict

        Leave the given channel
        """
        data = {
            "channel": channel,
            "channel_id": None
        }
        req = requests.post(f"{self.API_URL}/leave_channel", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_profile(self, user_id):
        """ (Clubhouse, str) -> dict

        Get someone else's profile
        """
        data = {
            "user_id": int(user_id)
        }
        req = requests.post(f"{self.API_URL}/get_profile", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_profile_self(self, return_blocked_ids=False, timezone_identifier="Asia/Tokyo", return_following_ids=False):
        """ (Clubhouse, bool, str, bool) -> dict

        Get my information
        """
        # Get myself
        data = {
            "return_blocked_ids": return_blocked_ids,
            "timezone_identifier": timezone_identifier,
            "return_following_ids": return_following_ids
        }
        req = requests.post(f"{self.API_URL}/me", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_profile_following(self, user_id):
        """ (Clubhouse, str) -> dict

        Get list of users
        """
        data = {
            "user_id": int(user_id)
        }
        req = requests.post(f"{self.API_URL}/get_following", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_all_topics(self):
        """ (Clubhouse) -> dict

        Get list of topics, based on the server's channel selection algorithm
        """
        req = requests.get(f"{self.API_URL}/get_all_topics", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def get_channels(self):
        """ (Clubhouse) -> dict

        Get list of channels, based on the server's channel selection algorithm
        """
        req = requests.get(f"{self.API_URL}/get_channels", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def active_ping(self, channel):
        """ (Clubhouse, str) -> dict

        Keeping the user active while being in a chatroom
        """
        data = {
            "channel": channel,
            "chanel_id": None
        }
        req = requests.post(f"{self.API_URL}/active_ping", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def audience_reply(self, channel, raise_hands=True, unraise_hands=False):
        """ (Clubhouse, str, bool, bool) -> bool

        Request for raise_hands.
        """
        data = {
            "channel": channel,
            "raise_hands": raise_hands,
            "unraise_hands": unraise_hands
        }
        req = requests.post(f"{self.API_URL}/audience_reply", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def update_skintone(self, skintone=1):
        """ (Clubhouse, int) -> dict

        Updating skinetone for raising hands, etc.
        """
        skintone = int(skintone)
        if not 1 <= skintone <= 5:
            return False

        data = {
            "skintone": skintone
        }
        req = requests.post(f"{self.API_URL}/update_skintone", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_notifications(self, page_size=20, page=1):
        """ (Clubhouse, int, int) -> dict

        Get my notifications.
        """
        query = f"page_size={page_size}&page={page}"
        req = requests.get(f"{self.API_URL}/get_notifications?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def get_online_friends(self):
        """ (Clubhouse) -> dict

        List all online friends.
        """
        req = requests.post(f"{self.API_URL}/get_online_friends", headers=self.HEADERS, json={})
        return req.json()


    @require_authentication
    def accept_speaker_invite(self, channel, user_id):
        """ (Clubhouse, str, int) -> dict

        Accept speaker's invitation, based on the (channel, invited_moderator)
        `raise_hands` needs to be called first, prior to the invitation.
        """
        data = {
            "channel": channel,
            "user_id": int(user_id)
        }
        req = requests.post(f"{self.API_URL}/accept_speaker_invite", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_suggested_speakers(self, channel):
        """ (Clubhouse, str) -> dict

        Get suggested speakers from the given channel
        """
        data = {
            "channel": channel
        }
        req = requests.post(f"{self.API_URL}/get_suggested_speakers", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def create_channel(self, topic="", user_ids=(), is_private=False, is_social_mode=False):
        """ (Clubhouse, str, list, bool, bool) -> dict

        Create a new channel. Type of the room can be changed.
        """
        data = {
            "is_social_mode": is_social_mode,
            "is_private": is_private,
            "club_id": None,
            "user_ids": user_ids,
            "event_id": None,
            "topic": topic
        }
        req = requests.post(f"{self.API_URL}/create_channel", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_create_channel_targets(self):
        """ (Clubhouse) -> dict

        Not sure what this does.
        """
        data = {}
        req = requests.post(f"{self.API_URL}/get_create_channel_targets", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_suggested_invites(self, club_id=None, upload_contacts=True, contacts=()):
        """ (Clubhouse, int, bool, list) -> dict

        Get number of invitations and list of invitations.
        """
        data = {
            "club_id": club_id,
            "upload_contacts": upload_contacts,
            "contacts": contacts
        }
        req = requests.post(f"{self.API_URL}/get_suggested_invites", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def search_users(self, query, followers_only=False, following_only=False, cofollows_only=False):
        """ (Clubhouse, str, bool, bool, bool) -> dict

        Search users based on the given query.
        """
        data = {
            "cofollows_only": cofollows_only,
            "following_only": following_only,
            "followers_only": followers_only,
            "query": query
        }
        req = requests.post(f"{self.API_URL}/search_users", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def search_clubs(self, query, followers_only=False, following_only=False, cofollows_only=False):
        """ (Clubhouse, str, bool, bool, bool) -> dict

        Search clubs based on the given query.
        """
        data = {
            "cofollows_only": cofollows_only,
            "following_only": following_only,
            "followers_only": followers_only,
            "query": query
        }
        req = requests.post(f"{self.API_URL}/search_clubs", headers=self.HEADERS, json=data)
        return req.json()


    @require_authentication
    def get_clubs_for_topic(self, topic_id, page_size=25, page=1):
        """ (Clubhouse, int, int, int) -> dict

        Get list of clubs based on the given topic id.
        """
        query = "topic_id={}&page_size={}&page={}".format(
            topic_id,
            page_size,
            page
        )
        req = requests.get(f"{self.API_URL}/get_clubs_for_topic?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def get_users_for_topic(self, topic_id, page_size=25, page=1):
        """ (Clubhouse, int, int, int) -> dict

        Get list of users based on the given topic id.
        """
        query = "topic_id={}&page_size={}&page={}".format(
            topic_id,
            page_size,
            page
        )
        req = requests.get(f"{self.API_URL}/get_users_for_topic?{query}", headers=self.HEADERS)
        return req.json()


    @require_authentication
    def invite_to_existing_channel(self, channel, user_id):
        """ (Clubhouse, str, int) -> dict

        Invite someone to a currently joined channel.
        It will send a ping notification to the given user_id.
        """
        data = {
            "channel": channel,
            "user_id": int(user_id)
        }
        req = requests.post(f"{self.API_URL}/invite_to_existing_channel", headers=self.HEADERS, json=data)
        return req.json()


if __name__ == "__main__":
    # 1. Confirm that the CLubhouse class is working properly.
    '''
    CLUBHOUSE = Clubhouse()
    print(CLUBHOUSE)
    exit(0)
    '''

    # Copy uuid from step (1).
    # 2. Authenticate user by using phone number
    USER_DEVICE = "8c4190fe-34c1-485c-9ec0-c0f552049f85"
    USER_PHONE = "+818012341234"
    VERIFY_CODE = "1234"
    '''
    CLUBHOUSE = Clubhouse(user_device=USER_DEVICE)
    # 2-1. Request for SMS
    print(CLUBHOUSE.start_phone_number_auth(phone_number=USER_PHONE)
    # 2-2. Get response from SMS
    print(CLUBHOUSE.complete_phone_number_auth(phone_number=USER_PHONE, verification_code=VERIFY_CODE))
    # 2-3. Get `user_id` and `auth_token` from the response..
    exit(0)
    '''

    # 3. Try to login as a normal user and get list of channels.
    '''
    USER_ID = str(13371337)
    USER_TOKEN = "CHANGE_ME"
    CLUBHOUSE = Clubhouse(user_device=USER_DEVICE, user_id=USER_ID, user_token=USER_TOKEN)
    print(CLUBHOUSE.get_channels())
    '''

    # 4. Join Channel. continue to be active.
    '''
    import time
    MY_CHANNEL = "ABCD12345"
    print(CLUBHOUSE.join_channel(MY_CHANNEL))
    time.sleep(3)
    # 4-1. You need to continuously ping yourself to keep yourself in the channel
    print(CLUBHOUSE.active_ping(MY_CHANNEL))
    time.sleep(2)
    print(CLUBHOUSE.leave_channel(MY_CHANNEL))
    '''
