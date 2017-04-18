from workspaceStructure import WorkspaceStructure


class Replacement(WorkspaceStructure):
    def __init__(self, ctx, objectFromInitial, objectFromModified, relation):
        WorkspaceStructure.__init__(self, ctx)
        self.objectFromInitial = objectFromInitial
        self.objectFromModified = objectFromModified
        self.relation = relation
