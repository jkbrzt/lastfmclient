import argparse
import json

import tornado.web
import tornado.gen
import tornado.ioloop

from lastfmclient.async import AsyncLastfmClient


class settings:
    API_KEY = None
    API_SECRET = None


class LastfmHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        if not self.get_argument('token', None):
            self.redirect_to_lastfm()
        else:
            yield self.back_from_lastfm()
            self.finish()

    def redirect_to_lastfm(self):
        client = AsyncLastfmClient(
            api_key=settings.API_KEY,
            api_secret=settings.API_SECRET,
        )

        auth_url = client.get_auth_url(callback_url='%s://%s/' % (
            self.request.protocol,
            self.request.host
        ))

        self.redirect(auth_url)

    @tornado.gen.coroutine
    def back_from_lastfm(self):

        client = AsyncLastfmClient(
            api_key=settings.API_KEY,
            api_secret=settings.API_SECRET,
        )
        token = self.get_argument('token')

        print('Fetching session...')
        session = yield client.auth.get_session(token)

        client.session_key = session['key']

        print('Fetching user info...')
        user = yield client.user.get_info()

        print('Fetching tracks and friends simultaneously...')
        tracks, friends = yield [
            client.user.get_recent_tracks(user=user['name'], limit=3),
            client.user.get_friends(user=user['name'], limit=3)
        ]

        print('Finishing.')

        self.set_header('Content-Type', 'text/plain')
        self.write('You:\n\n')
        self.write(json.dumps(user, sort_keys=True, indent=4))
        self.write('\n\n\nRecent Tracks:\n\n')
        self.write(json.dumps(tracks, sort_keys=True, indent=4))
        self.write('\n\n\nFriends:\n\n')
        self.write(json.dumps(friends, sort_keys=True, indent=4))


if __name__ == '__main__':

    # Parse API key and secret from the command line:
    parser = argparse.ArgumentParser()
    parser.add_argument('--api-key', required=True)
    parser.add_argument('--api-secret', required=True)
    args = parser.parse_args()
    settings.API_KEY = args.api_key
    settings.API_SECRET = args.api_secret

    # Start our app:
    app = tornado.web.Application(
        handlers=[('/', LastfmHandler)],
        debug=True,
    )
    app.listen(8888)
    tornado.ioloop.IOLoop.instance().start()
