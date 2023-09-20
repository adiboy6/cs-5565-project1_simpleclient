all: simpleclient simpleclient_gai
simpleclient: simpleclient.py
	cp simpleclient.py simpleclient
	chmod +x simpleclient
simpleclient_gai: simpleclient_gai.c
	gcc simpleclient_gai.c -o simpleclient_gai
