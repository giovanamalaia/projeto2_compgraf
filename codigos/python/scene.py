class Scene:
    def __init__(self, root):
        self.root = root
        self.engines = []

    def GetRoot(self):
        return self.root

    def AddEngine(self, engine):
        self.engines.append(engine)

    def Update(self, dt):
        for e in self.engines:
            e.Update(dt)

    def Render(self, camera):
        from state import State
        st = State(camera)
        self.root.Render(st)

    def FindNodeByName(self, name):
        return self._find_node_recursive(self.root, name)

    def _find_node_recursive(self, node, name):
        if hasattr(node, "name") and node.name == name:
            return node
        if hasattr(node, "nodes"):
            for child in node.nodes:
                result = self._find_node_recursive(child, name)
                if result:
                    return result
        return None
