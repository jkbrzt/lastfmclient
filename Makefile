build: spec code

spec:
	./generate.py spec > spec.json

code:
	./generate.py code > laastfm/api.py
