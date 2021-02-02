from .alerts import Alerts


class piSupportNotifications:

	def __init__(self, logger):
		self._logger = logger
		self._alerts = Alerts(self._logger)
		self._layers = []

	def handle_piSupportData(self, settings, event_payload):
		server_url = settings.get(["server_url"])
		if not server_url or not server_url.strip():
			# No FCM server has been defined so do nothing
			return -1

		tokens = settings.get(["tokens"])
		if len(tokens) == 0:
			# No Android devices were registered so skip notification
			return -2

		# anything bad happening?
		# payload data: {'raw_value': 0, 'current_undervoltage': False, 'past_undervoltage': False, 'current_overheat': False, 'past_overheat': False, 'current_issue': False, 'past_issue': False}
		if event_payload["current_undervoltage"] is True or event_payload["current_overheat"] is True:
			self._logger.info("We got current_undervoltage/current_overheat problems")
		else:
			return -3

		# For each registered token we will send a push notification
		# We do it individually since 'printerID' is included so that
		# Android app can properly render local notification with
		# proper printer name
		used_tokens = []
		last_result = None
		for token in tokens:
			fcm_token = token["fcmToken"]
			printerID = token["printerID"]

			# Ignore tokens that already received the notification
			# This is the case when the same OctoPrint instance is added twice
			# on the Android app. Usually one for local address and one for public address
			if fcm_token in used_tokens:
				continue
			# Keep track of tokens that received a notification
			used_tokens.append(fcm_token)

			if 'printerName' in token and token["printerName"] is not None:
				# We can send non-silent notifications (the new way) so notifications are rendered even if user
				# killed the app
				printer_name = token["printerName"]
				url = server_url

				#send_alert_code(self, fcm_token, url, printer_id, printer_name, event_code, image=None, event_param=None):

				last_result = self._alerts.send_alert_code(fcm_token, url, printerID, printer_name,
														   "test-message", None, None)

		return last_result