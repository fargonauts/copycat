from workspaceStructure import WorkspaceStructure

class Replacement(WorkspaceStructure):
	def __init__(self, objectFromInitial, objectFromModified, relation):
		WorkspaceStructure.__init__(self)
		self.objectFromInitial = objectFromInitial
		self.objectFromModified = objectFromModified
		self.relation = relation

