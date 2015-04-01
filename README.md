optbot
==
Tools for evaluating options investments.

Build
--
Install virtualenv, virtualenvwrapper and autoenv as specified [here](http://docs.python-guide.org/en/latest/dev/virtualenvs/).
Then, from the current directory:

    $ mkvirtualenv optbot
    $ cp requirements.txt $WORKON_HOME/optbot/
    $ pushd $WORKON_HOME/optbot
    $ pip install -r requirements.txt
    $ popd
    $ source .env

Notes
--
If you need to change local configurations of the service, modify the contents of
`service/_locconst.py`. Then run:

    $ git update-index --assume-unchanged service/_locconst.py

optbot/service
--
Service to download daily options quotes and push to a MongoDB instance.

Before starting the service, you should populate MongoDB with stocks to
observe. To add stocks to the local observation list:

    $ cd service
    $ python observe.py --add tsla nflx spwr

Start the service with:

    $ cd service
    $ python quotes.py --start &

