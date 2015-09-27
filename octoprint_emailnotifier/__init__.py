# coding=utf-8
from __future__ import absolute_import
import os
import octoprint.plugin
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
			
			# Notification title and body templates may include any
			# event payload properties associated with the event.
			# http://docs.octoprint.org/en/master/events/index.html#available-events
			# Elapsed times are formatted as H:M:S instead of seconds.
			
			notifications={
				"FileSelected": dict(
					enabled=True,
					title="Selected {filename}",
					body="{file} selected for printing. {__now}",
					snapshot=False
				),
				"PrintDone": dict(
					enabled=True,
					title="Print complete: {file}",
					body="{file} done in {time}.",
					snapshot=True
				),
				"MovieDone": dict(
					enabled=True,
					title="Timelapse rendered: {movie_basename}",
					body="Timelapse of printing {gcode} saved as {movie}.",
					snapshot=False
				)
			}
		)
	
	def get_settings_version(self):
		return 2
	
	def on_settings_migrate(self, target, current):
		if current == 1:
			
			# retain smtp/recipient settings
				
			# remove original notification settings
			self._settings.set(["enabled"], None)
			self._settings.set(["include_snapshot"], None)
			self._settings.set(["message_format"], None)
			
			# reset event notifications to new defaults
			self._settings.set(["notifications"], self.get_settings_defaults().get('notifications'))

			self._settings.save()
			
	#~~ TemplatePlugin

	def get_template_configs(self):
		return [
			dict(type="settings", name="Email Notifier", custom_bindings=False)
		]

	#~~ EventPlugin
	
	def on_event(self, event, payload):
		
		# Is there a notification registered for this event?
		notification = self._settings.get(['notifications']).get(event)
		if notification is None:
			return
		
		# Is this notification enabled?
		if not notification.get('enabled', False):
			return
		
		# Consider integrating or re-implementing these standard event properties, which I don't *think* are issued to plugin handlers:
		# https://github.com/foosel/OctoPrint/blob/1c6b0554c796f03ed539397daa4b13c44d05a99d/src/octoprint/events.py#L325
		
		# Convert elapsed times from raw seconds to readable durations.
		if 'time' in payload:
			import datetime
			import octoprint.util
			time = octoprint.util.get_formatted_timedelta(datetime.timedelta(seconds=payload["time"]))
		
		# Generate notification message from template.
		# (**locals() makes event payload properties accessible)
		title = notification.get('title').format(**locals())
		content = [notification.get('body').format(**locals())]

		# Should this notification include a webcam snapshot?
		# If so, attempt to attach it to the message content.
		if notification.get('snapshot', False):
			snapshot_url = self._settings.globalGet(["webcam", "snapshot"])
			if snapshot_url:
				try:
					import urllib
					snapfile, headers = urllib.urlretrieve(snapshot_url)
				except Exception as e:
					self._logger.exception("Snapshot error (sending email notification without image): %s" % (str(e)))
				else:
					content.append({snapfile: "snapshot.jpg"})
		
		# Send and log.
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

				# update method: pip
				pip="https://github.com/anoved/OctoPrint-EmailNotifier/archive/{target_version}.zip",
				dependency_links=False
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

