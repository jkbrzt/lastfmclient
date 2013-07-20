build: spec code

spec:
	./generate.py spec > api.json

code:
	./generate.py code > lastfmclient/api.py
