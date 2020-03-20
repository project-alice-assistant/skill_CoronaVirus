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
			country = self.getConfig('defaultCountryCode').upper()
		else:
			country = session.slotValue('Country')

		params = {'global': 'stats'} if country == 'EARTH' else {'countryTotal': country}

		try:
			req = requests.get(
				url='https://thevirustracker.com/free-api',
				params=params
			)
		except Exception as e:
			self.logError(f'Request failed: {e}')
			req: Optional[Response] = None

		if not req or req.status_code != 200:
			self.logError('API access failed')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		try:
			answer = req.json()
			print(answer)
		except:
			answer = None

		if not answer or 'countrydata' not in answer:
			self.logError('No data in API answer')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		if len(answer['countrydata']) > 1:
			found = dict()
			for worldCountry in answer['countrydata']:
				if worldCountry['info']['code'] == country:
					found = worldCountry
					break

			if not found:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text='noData', replace=[session.slotRawValue('Country')])
				)
				return
		else:
			found = answer['countrydata'][0]

		text = self.randomTalk(text='situation', replace=[
				found['info']['title'],
				found['total_cases'],
				found['total_deaths'],
				found['total_recovered'],
				found['total_new_cases_today'],
				found['total_new_deaths_today'],
				found['total_serious_cases']
			])

		self.endDialog(
			sessionId=session.sessionId,
			text=text
		)
