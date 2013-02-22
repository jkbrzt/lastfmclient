``laastfm``
###########

*Warning: pre-alpha quality, lack of tests and documentation.*

Python client for `Last.fm API <http://www.last.fm/api>`_  that
provides a pythonic interface to all the API's method, including OAuth, etc.
An async, Tornado-based version of the client is included as well.

The client methods code and their docstrings are generated from the online API
documentation (see ``./generate.py``, ``./spec.json`` and
``./laastfm/generated.py``).

.. code-block:: python

    # http://ws.audioscrobbler.com/2.0/?method=track.updateNowPlaying&api_key=[…]
    # ==>
    api.track.update_now_playing(
        track='Paranoid Android',
        artist='Radiohead',
        album='OK Computer',
    )


Usage
=====


Regular
-------

.. code-block:: python

    from laastfm import LastfmClient

    api = LastfmClient(
        api_key=KEY,
        api_secret=SECRET,
        session_key=session_key
    )

    resp = api.track.update_now_playing(
        track='Paranoid Android',
        artist='Radiohead',
        album='OK Computer',
    )

    print resp


Asynchronous (uses ``tornado.httpclient.AsyncHTTPClient``)
----------------------------------------------------------

.. code-block:: python

    from laastfm import AsyncLastfmClient

    def callback(resp):
        print resp

    api = AsyncLastfmClient(
        api_key=KEY,
        api_secret=SECRET,
        session_key=session_key
    )

    api.track.update_now_playing(
        track='Paranoid Android',
        artist='Radiohead',
        album='OK Computer',
        callback=callback,
    )

Updating the generated client methods code
==========================================

.. code-block:: bash

    pip install -r requirements.txt

    # 1. Generate fresh spec.json from docs at http://www.last.fm/api:
    $ make spec

    # 2. Generate `lastfm/generated.py` from `spec.json`:
    $ make code

    # Or, the above in one step:
    $ make
