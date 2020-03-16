import requests

from core.ProjectAliceExceptions import SkillStartingFailed
from core.base.model.AliceSkill import AliceSkill
from core.dialog.model.DialogSession import DialogSession
from core.util.Decorators import IntentHandler


class CoronaVirus(AliceSkill):
	"""
	Author: Psycho
	Description: Information about the spread of the virus, worldwide
	"""

	def onStart(self):
		super().onStart()
		if not self.getConfig('apiKey'):
			raise SkillStartingFailed('Missing API key')


	@IntentHandler('GetCoronaVirusSpreadInfo')
	def getInfo(self, session: DialogSession, **_kwargs):
		if 'Country' not in session.slots:
			country = self.getConfig('country').title()
		else:
			country = session.slotValue('Country')

		if country == "United States":
			country = "US"

		req = requests.get(
			url='https://covid-19-coronavirus-statistics.p.rapidapi.com/v1/stats',
			params={
				'country': country
			},
			headers={
				'X-RapidAPI-Key': self.getConfig('apiKey')
			}
		)

		if req.status_code != 200:
			self.logError('API access failed')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		answer = req.json()

		if not answer or 'data' not in answer or 'covid19Stats' not in answer['data']:
			self.logError('No data in API answer')
			self.endDialog(
				sessionId=session.sessionId,
				text=self.randomTalk(text='error')
			)
			return

		if len(answer['data']['covid19Stats']) > 1:
			found = dict()
			for worldCountry in answer['data']['covid19Stats']:
				if worldCountry['country'] == country:
					found = worldCountry
					break

			if not found:
				self.endDialog(
					sessionId=session.sessionId,
					text=self.randomTalk(text='noData', replace=[country])
				)
				return
		else:
			found = answer['data']['covid19Stats'][0]

		self.endDialog(
			sessionId=session.sessionId,
			text=self.randomTalk(text='situation', replace=[
				country,
				found['confirmed'],
				found['deaths'],
				found['recovered']
			])
		)
