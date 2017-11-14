# coding=utf-8
from __future__ import absolute_import
import os
import octoprint.plugin
import yagmail
import flask
import tempfile
from email.utils import formatdate

from email.utils import formatdate
from flask.ext.login import current_user

class EmailNotifierPlugin(octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.TemplatePlugin,
                          octoprint.plugin.AssetPlugin,
                          octoprint.plugin.SimpleApiPlugin):

	#~~ AssetPlugin
	def get_assets(self):
		return dict(
			js=["js/emailnotifier.js"]
		)


	#~~ SettingsPlugin

	def get_settings_defaults(self):
		# matching password must be registered in system keyring
		# to support customizable mail server, may need port too
		return dict(
			enabled=False,
			recipient_address="",
			mail_server="",
			mail_port="",
			mail_tls=False,
			mail_ssl=False,
			mail_username="",
			mail_useralias="",
			include_snapshot=True,
			message_format=dict(
				title="Print job complete",
				body="{filename} done printing after {elapsed_time}" 
			)
		)
	
	def get_settings_version(self):
		return 1

	def on_settings_load(self):
		data = octoprint.plugin.SettingsPlugin.on_settings_load(self)

		# only return our restricted settings to admin users - this is only needed for OctoPrint <= 1.2.16
		restricted = ("mail_server", "mail_port", "mail_tls", "mail_ssl","mail_username", "recipient_address", "mail_useralias")
		for r in restricted:
			if r in data and (current_user is None or current_user.is_anonymous() or not current_user.is_admin()):
				data[r] = None

		return data

	def get_settings_restricted_paths(self):
		# only used in OctoPrint versions > 1.2.16
		return dict(admin=[["mail_server"], ["mail_port"], ["mail_tls"], ["mail_ssl"], ["mail_username"], ["recipient_address"], ["mail_useralias"]])

	#~~ TemplatePlugin

	def get_template_configs(self):
		return [
			dict(type="settings", name="Email Notifier", custom_bindings=True)
		]

	#~~ EventPlugin
	
	def on_event(self, event, payload):
		if event != "PrintDone":
			return
		
		if not self._settings.get(['enabled']):
			return
		
		filename = os.path.basename(payload["file"])
		
		import datetime
		import octoprint.util
		elapsed_time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=payload["time"]))
		
		tags = {'filename': filename, 'elapsed_time': elapsed_time}
		subject = self._settings.get(["message_format", "title"]).format(**tags)
		message = self._settings.get(["message_format", "body"]).format(**tags)
		body = [message]
		
		try:
			self.send_notification(subject, body, self._settings.get(['include_snapshot']))
		except Exception as e:
			# If the email wasn't sent, report problems appropriately.
			self._logger.exception("Email notification error: %s" % (str(e)))
		else:
			# If the mail was sent, report the success.
			self._logger.info("Print notification emailed to %s" % (self._settings.get(['recipient_address'])))


	def get_update_information(self):
		return dict(
			emailnotifier=dict(
				displayName="EmailNotifier Plugin",
				displayVersion=self._plugin_version,

				# version check: github repository
				type="github_release",
				user="anoved",
				repo="OctoPrint-EmailNotifier",
				current=self._plugin_version,

				# update method: pip
				pip="https://github.com/anoved/OctoPrint-EmailNotifier/archive/{target_version}.zip",
				dependency_links=False
			)
		)

	#~~ SimpleApiPlugin

	def get_api_commands(self):
		return dict(
			testmail=[]
		)

	def on_api_command(self, command, data):
		if command == "testmail":

			subject = "OctoPrint Email Notifier Test"
			body = ["If you received this email, your email notification configuration in OctoPrint is working as expected."]
			snapshot = bool(data["snapshot"])

			try:
				self.send_notification(subject, body, snapshot)
			except Exception as e:
				self._logger.exception("Email notification error: %s" % (str(e)))
				return flask.jsonify(success=False, msg=str(e))

			# If we got here, everything is good.
			self._logger.info("Test notification emailed to %s" % (self._settings.get(['recipient_address'])))
			return flask.jsonify(success=True)

		# If it's not testmail, then we don't know what it is.
		else:
			return flask.make_response("Unknown command", 400)


	# Helper function to reduce code duplication.
	# If snapshot == True, a webcam snapshot will be appended to body before sending.
	def send_notification(self, subject="OctoPrint notification", body=[""], snapshot=True):

		# If a snapshot is requested, let's grab it now.
		if snapshot:
			snapshot_url = self._settings.global_get(["webcam", "snapshot"])
			if snapshot_url:
				try:
					import urllib
					filename, headers = urllib.urlretrieve(snapshot_url, tempfile.gettempdir()+"/snapshot.jpg")
				except Exception as e:
					self._logger.exception("Snapshot error (sending email notification without image): %s" % (str(e)))
				else:
					body.append(yagmail.inline(filename))

		# Exceptions thrown by any of the following lines are intentionally not
		# caught. The callers need to be able to handle them in different ways.
		mailer = yagmail.SMTP(user={self._settings.get(['mail_username']):self._settings.get(['mail_useralias'])}, host=self._settings.get(['mail_server']),port=self._settings.get(['mail_server_port']), smtp_starttls=self._settings.get(['mail_server_tls']), smtp_ssl=self._settings.get(['mail_server_ssl']))
		emails = [email.strip() for email in self._settings.get(['recipient_address']).split(',')]
		mailer.send(to=emails, subject=subject, contents=body, headers={"Date": formatdate()})


__plugin_name__ = "Email Notifier"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = EmailNotifierPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

