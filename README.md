optbot
==
Tools for evaluating options investments.

optbot/service
--
Service to download daily options quotes and push to a MongoDB instance.

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
