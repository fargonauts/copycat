from workspaceStructure import WorkspaceStructure


class Replacement(WorkspaceStructure):
    def __init__(self, objectFromInitial, objectFromModified, relation):
        from context import context as ctx
        WorkspaceStructure.__init__(self, ctx)
        self.objectFromInitial = objectFromInitial
        self.objectFromModified = objectFromModified
        self.relation = relation
