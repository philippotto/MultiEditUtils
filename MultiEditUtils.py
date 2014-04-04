import sublime, sublime_plugin


class JumpToLastRegionCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		selection = self.view.sel()
		lastRegion = selection[-1]
		cursorPosition = lastRegion.begin()
		selection.clear()
		selection.add(sublime.Region(cursorPosition))



class AddLastSelectionCommand(sublime_plugin.TextCommand):

	def run(self, edit):

		helper = Helper.getOrConstructHelperForView(self.view)
		lastSelections = helper.lastSelections

		if len(lastSelections) < 2:
			return

		currentSelection = self.view.sel()
		oldSelectionHash = Helper.hashSelection(currentSelection)

		for region in lastSelections[-1]:
			helper.ignoreSelectionCommand = True
			currentSelection.add(region)

		newSelectionHash = Helper.hashSelection(currentSelection)

		lastSelections.pop(-1)

		nothingChanged = oldSelectionHash == newSelectionHash
		if nothingChanged:
			# Rerun if the previous selection was only a subset of the current selection.
			self.run(edit)



class SelectionListener(sublime_plugin.EventListener):

	def on_selection_modified(self, view):

		helper = Helper.getOrConstructHelperForView(view)
		lastSelections = helper.lastSelections

		if helper.ignoreSelectionCommand:
			helper.ignoreSelectionCommand = False
			return

		currentSelection = view.sel()

		if self.isComplexSelection(currentSelection):

			currentRegions = [region for region in currentSelection]
			selectionWasExpanded = lastSelections and self.isSubsetOf(currentSelection, lastSelections[-1])

			if selectionWasExpanded:
				# Override the last entry since the selection was expanded.
				lastSelections[-1] = currentRegions
			else:
				lastSelections.append(currentRegions)


	def isComplexSelection(self, selection):
		# A "complex selection" is a selection which is not empty or has multiple regions.

		regionCount = len(selection)
		firstRegionLength = len(selection[0])

		return regionCount > 1 or firstRegionLength > 0


	def isSubsetOf(self, selectionA, selectionB):
		# Check if selectionA is a subset of selectionB.

		return all(selectionA.contains(region) for region in selectionB)



class Helper:

	viewToHelperMap = {}

	def __init__(self):

		# The SelectionCommand should be ignored if it was triggered by AddLastSelectionCommand.
		self.ignoreSelectionCommand = False
		self.lastSelections = []


	@staticmethod
	def getOrConstructHelperForView(view):

		mapping = viewToHelperMap
		viewID = view.id()

		if not viewID in mapping.keys():
			mapping[viewID] = Helper()

		helper = mapping[viewID]
		return helper


	@staticmethod
	def hashSelection(selection):

		return str([region for region in selection])