# OctoPrint-EmailNotifier

Recieve email notifications when print jobs are done.

## Installation

Install via the OctoPrint [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) or manually using this archive/URL:

	[https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip](https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip)

## Configuration



One manual configuration step is required. Your outgoing email account password is not stored with OctoPrint's settings. It is retrieved from your system [keyring](https://pypi.python.org/pypi/keyring#what-is-python-keyring-lib). Once this plugin and its prerequisites are installed, you can add your password to the keyring using this bit of interactive Python: 

	$ ~/oprint/bin/python
	>>> import yagmail
	>>> yagmail.register("SMTP username", "SMTP password")

For Gmail addresses, the SMTP username is your complete `username@gmail.com` address.

## Limitations

Not yet tested with non-Gmail SMTP servers. Some additional settings or keyring management may be required.

## Acknowledgements

Loosely based on [OctoPrint-Pushbullet](https://github.com/OctoPrint/OctoPrint-Pushbullet). 

Uses [yagmail](https://github.com/kootenpv/yagmail) to send email.

## License

Licensed under the terms of the [AGPLv3](http://opensource.org/licenses/AGPL-3.0).
