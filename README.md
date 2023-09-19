#Project 1: Sockets Simple Server

* Run the simple server with
```shell
python3 ./simpleserver.py
```

This will automatically bind to a random port between 1000 and 5000. You'll see output like:

```
[shaddi@cottonwood ~]$ python3 simpleserver.py
Running on host: cottonwood.rlogin
listening at port 4882
```

If you want to specify a port to listen on, you can use the `-p` option.

Note: If you're running the server on rlogin, your client will also need to be running on the rlogin cluster. Be sure to kill your server when you're done using it to avoid making our TechStaff folks very sad.

The username is hard-coded to be "hokiebird". Feel free to modify the simple server as you see fit to test your client. As noted in the project specification, you may not share modifications to this script outside your team (just like your solution code).
