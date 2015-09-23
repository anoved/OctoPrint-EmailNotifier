# OctoPrint-EmailNotifier

Recieve email notifications when OctoPrint jobs are complete.

## Installation

Install via the OctoPrint [Plugin Manager](https://github.com/foosel/OctoPrint/wiki/Plugin:-Plugin-Manager) or manually using this [archive URL](https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip):

	https://github.com/anoved/OctoPrint-EmailNotifier/archive/master.zip

## Configuration

![Email Notifier settings tab](http://i.imgur.com/5okAwT5.png)

(Consider using an [SMS gateway](https://en.wikipedia.org/wiki/SMS_gateway#Use_with_email_clients) to send notifications to a mobile phone.)

One manual configuration step is required. Your outgoing email account password is not stored with OctoPrint's settings. It is retrieved from your system [keyring](https://pypi.python.org/pypi/keyring#what-is-python-keyring-lib). Once this plugin and its prerequisites are installed, you can add your password to the keyring using this bit of interactive Python: 

	$ ~/oprint/bin/python
	>>> import yagmail
	>>> yagmail.register("SMTP username", "SMTP password")

For some accounts, your SMTP username is your complete "username@domain.com" address.

## Acknowledgements

Loosely based on [OctoPrint-Pushbullet](https://github.com/OctoPrint/OctoPrint-Pushbullet). 

Uses [yagmail](https://github.com/kootenpv/yagmail) to send email.

## License

Licensed under the terms of the [AGPLv3](http://opensource.org/licenses/AGPL-3.0).
