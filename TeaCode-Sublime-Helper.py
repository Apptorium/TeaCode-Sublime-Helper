import sublime, sublime_plugin, os.path, subprocess, json

class ExpandWithTeacodeCommand(sublime_plugin.TextCommand):

	def getCursorPosition(self):
		for region in self.view.sel():
			if region.empty():
				return region

		return self.view.sel()[0]

	def setCursorPosition(self, position):
		sel = self.view.sel()
		sel.clear()
		region = sublime.Region(position, position)
		sel.add(region)

	def insertText(self, edit, text):
		self.view.insert(edit, self.getCursorPosition().begin(), text)

	def getTextRangeFromBegginingOfLineToCursor(self):
		for region in self.view.sel():
			if region.empty():
				range = self.view.line(region)
				return range

		return self.view.line(region)

	def getTextFromBeginningOfLineToCursor(self):
		range = self.getTextRangeFromBegginingOfLineToCursor()
		return self.view.substr(range)

	def replaceText(self, edit, text, cursorPosition):
		range = self.getTextRangeFromBegginingOfLineToCursor()
		self.view.replace(edit, range, text)

		self.setCursorPosition(range.begin() + cursorPosition)

	def handleJson(self, jsonObject, edit):
		if jsonObject is None:
			return

		j = json.loads(jsonObject)
		
		if j is None:
			return

		text = j['text']

		if text is None:
			return

		cursorPosition = j['cursorPosition']
		self.replaceText(edit, text, cursorPosition)

	def run(self, edit):
		filename = self.view.file_name()

		if filename is None:
			filename = ""

		extension = os.path.splitext(filename)[1][1:]

		text = self.getTextFromBeginningOfLineToCursor()

		command = ["osascript", "-l", "JavaScript", "-e", "Application('TeaCode').expandAsJson('" + text + "', { 'extension': '" + extension + "' })"]
		session = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
		stdout, stderr = session.communicate()

		if stderr:
			sublime.message_dialog("Could not run TeaCode. Please make sure it's installed. You can download the app from www.apptorium.com/teacode")
			return

		self.handleJson(stdout, edit)
