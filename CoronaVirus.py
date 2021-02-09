from typing import Optional

import requests
from requests import Response

from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class CoronaVirus(AliceSkill):
	"""
	Author: Psycho
	Description: Information about the spread of the virus, worldwide
	"""


	@IntentHandler('GetCoronaVirusSpreadInfo')
	def getCoronaVirusSpreadInfo(self, session: DialogSession, **_kwargs):
		if 'Country' not in session.slots:
			country = self.getConfig('defaultCountryCode').lower()
		else:
			country = session.slotValue('Country').lower()

		req: Optional[Response] = None
		try:
			headers = {'Accept': '*/*', 'User-Agent': 'request'}
			req = requests.get(
				url=f'https://api.covid19api.com/live/country/{country}',
				headers=headers
			)
		except Exception as e:
			self.logError(f'Request failed: {e}')

		if not req or req.status_code != 200:
			self.logError('API access failed')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		try:
			answer = req.json()
		except:
			answer = None

		if not answer:
			self.logError('No data in API answer')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		text = self.randomTalk(text='situation', replace=[
			answer[-1]['Country'],
			answer[-1]['Confirmed'],
			answer[-1]['Deaths'],
			answer[-1]['Recovered'],
			answer[-1]['Confirmed'] - answer[-2]['Confirmed'],
			answer[-1]['Deaths'] - answer[-2]['Deaths']
		])

		self.endDialog(
			sessionId=session.sessionId,
			text=text
		)
