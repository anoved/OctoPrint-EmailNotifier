# OctoPrint-EmailNotifier

Recieve email notifications when OctoPrint jobs are complete.

![Settings tab and email screenshot](extras/emailnotifier.png)

## Installation

Install via the OctoPrint [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) or manually using this [archive URL](https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip):

	https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip

## Configuration

One manual configuration step is required. Your outgoing email account password is not stored with OctoPrint's settings. It is retrieved from your system [keyring](https://pypi.python.org/pypi/keyring#what-is-python-keyring-lib). Store your password from a Python prompt on your OctoPrint system using [`yagmail.register`](https://github.com/kootenpv/yagmail#username-and-password): 

	$ ~/oprint/bin/python
	>>> import yagmail
	>>> yagmail.register("SMTP username", "SMTP password")

For some accounts, your SMTP username may be your complete `username@domain.com` address.

## Acknowledgements

Loosely based on [OctoPrint-Pushbullet](https://github.com/OctoPrint/OctoPrint-Pushbullet). 

Uses [yagmail](https://github.com/kootenpv/yagmail) to send email.

## License

Licensed under the terms of the [AGPLv3](http://opensource.org/licenses/AGPL-3.0).
