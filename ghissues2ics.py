#!/usr/bin/env python2
# -*- coding: utf-8 -*-
#
#  ghissues2ics.py
#
#  Robert Chmielowiec 2011
#  robert@chmielowiec.net
#
#  depends:
#  * python-vobject


import vobject
import json
from datetime import datetime
from urllib2 import urlopen


date = lambda x: datetime.strptime(x, "%Y-%m-%dT%H:%M:%SZ")

class GitHubIssues(object):
	"""Params:
	repo_name	string	existing GitHub repo
	milestone	int		you can check it on milestone page
	state		string	valid values: 'open', 'close'; default: 'open'
	assignee	string	GitHub username
	mentioned	string	same as above
	"""

	repo = ""

	def __init__(self, repo_name, milestone=None, state=None, assignee=None,
		mentioned=None):

		# check whether the repo_name variable has a valid syntax
		if len(repo_name.split('/')) != 2:
			exit("Wrong repo syntax!")

		# API v3, get only opened issues
		self.url = "https://api.github.com/repos/%s/issues?" % \
			repo_name

		if state:
			if state not in ("open", "closed"):
				raise RuntimeError("only 'open' or 'closed' values are valid")
			self.url += "state=%s&" % state

		if milestone:
			self.url += "milestone=%d&" % milestone

		if assignee:
			self.url += "assignee=%s&" % assignee

		if mentioned:
			self.url += "mentioned=%s" % mentioned

		self.repo = repo_name

	def get(self):
		# download the json data
		self.data = urlopen(self.url).read()

		# decode json data into python object
		return json.loads(self.data)

class iCalendar:

	def __init__(self, list):
		if not list:
			raise RuntimeError("You must define at least one GitHubIssue \
				object")


		self.cal = vobject.iCalendar()

		for issues in list:
			if type(issues) != GitHubIssues:
				raise RuntimeError("All arguments have to be GitHubIssues \
					objects")

			for issue in issues.get():
				todo = self.cal.add('vtodo')

				todo.add('summary').value = issue['title']
				todo.add('description').value = issue['body']
				# FIXME: repo name as a location? any better ideas?
				todo.add('location').value = issues.repo

				created = date(issue['created_at'])
				todo.add('dtstart').value = \
				todo.add('dtstamp').value = \
				todo.add('created').value = created

				todo.add('last-modified').value = date(issue['updated_at'])

				# if the issue has a milestone with due on date
				if issue['milestone']:
					if not issue['milestone']['due_on']:
						continue

					todo.add('due').value = date(issue['milestone']['due_on'])

	def serialize(self):
		return self.cal.serialize()

if __name__ == '__main__':
	teerace_chaosk = GitHubIssues("chaosk/teerace", assignee="chmielu")

	list = [teerace_chaosk,]

	cal = iCalendar(list)
	print cal.serialize()