# coding=utf-8
from __future__ import absolute_import
import os
import octoprint.plugin
from octoprint.events import Events	
import yagmail

class EmailNotifierPlugin(octoprint.plugin.EventHandlerPlugin,
                          octoprint.plugin.SettingsPlugin,
                          octoprint.plugin.TemplatePlugin):
	
	#~~ SettingsPlugin

	def get_settings_defaults(self):
		# matching password must be registered in system keyring
		# to support customizable mail server, may need port too
		return dict(
			recipient_address="",
			mail_server="",
			mail_username="",
			include_snapshot=True,
			enabled=False
		)
	
	def get_settings_version(self):
		return 1

	#~~ TemplatePlugin

	def get_template_configs(self):
		return [
			dict(type="settings", name="Email Notifier", custom_bindings=False)
		]

	#~~ EventPlugin
	
	def on_event(self, event, payload):
		
		if event != Events.PRINT_DONE:
			return
		
		if not self._settings.get(['enabled']):
			return
		
		filename = os.path.basename(payload["file"])
		
		import datetime
		import octoprint.util
		elapsed = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=payload["time"]))
		
		message = "%s print complete in %s" % (filename, elapsed)
		title = "Print Job Done"
		
		content = [message]
		
		if self._settings.get(['include_snapshot']):
			snapshot_url = self._settings.globalGet(["webcam", "snapshot"])
			if snapshot_url:
				try:
					import urllib
					filename, headers = urllib.urlretrieve(snapshot_url)
				except Exception as e:
					self._logger.exception("Snapshot error (sending email notification without image): %s" % (str(e)))
				else:
					content.append(filename)
		
		try:
			mailer = yagmail.SMTP(user=self._settings.get(['mail_username']), host=self._settings.get(['mail_server']))
			mailer.send(to=self._settings.get(['recipient_address']), subject=title, contents=content, validate_email=False)
		except Exception as e:
			# report problem sending email
			self._logger.exception("Email notification error: %s" % (str(e)))
		else:
			# report notification was sent
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

				# update method: pip w/ dependency links
				pip="https://github.com/anoved/OctoPrint-EmailNotifier/archive/{target_version}.zip",
				dependency_links=True
			)
		)

__plugin_name__ = "Email Notifier"

def __plugin_load__():
	global __plugin_implementation__
	__plugin_implementation__ = EmailNotifierPlugin()

	global __plugin_hooks__
	__plugin_hooks__ = {
		"octoprint.plugin.softwareupdate.check_config": __plugin_implementation__.get_update_information
	}

