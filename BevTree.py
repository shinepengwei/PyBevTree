class BevNodePrecondition(object):
    def external_condition(self, input_par):
        pass


class BevNodePreconditionTRUE(BevNodePrecondition):
    def external_condition(self, input_par):
        return True


class BevNodePreconditionFALSE(BevNodePrecondition):
    def external_condition(self, input_par):
        return False


class BevNodePreconditionNOT(BevNodePrecondition):
    def __init__(self, lhs):
        self.lhs = lhs

    def external_condition(self, input_par):
        return not self.lhs.external_condition(input_par)


RUN_STATUS_EXECUTING = 0
RUN_STATUS_FINISH = 1


class BevNode(object):
    def __init__(self, parent_node, node_precondition, name=None):
        self.parent_node = parent_node
        if not self.parent_node is None:
            self.parent_node.add_child_node(self)
        self.node_precondition = node_precondition
        self.name = name
        self.child_nodes = []

    def add_child_node(self, node):
        self.child_nodes.append(node)

    def _do_evaluate(self, input_par):
        return True

    def evaluate(self, input_par):
        return (self.node_precondition is None or self.node_precondition.external_condition(input_par)) and self._do_evaluate(input_par)

    def tick(self, input_par, out_par):
        return self._do_tick(input_par, out_par)

    def _do_tick(self, input_par, out_par):
        return RUN_STATUS_FINISH


class BevNodeTerminal(BevNode):
    def __init__(self, parent_node, node_precondition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)

    def _do_tick(self, input_par, out_par):
        self._do_execute(input_par, out_par)

    def _do_execute(self, input_par, out_par):
        pass


class BevNodePrioritySelector(BevNode):
    def __init__(self, parent_node, node_precondition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)
        self.current_select_index = -1

    def _do_evaluate(self, input_par):
        for index, child in enumerate(self.child_nodes):
            if child.evaluate(input_par):
                self.current_select_index = index
                print "BevNodePrioritySelector:" + str(index)
                return True
        return False

    def _do_tick(self, input_par, out_par):
        self.child_nodes[self.current_select_index].tick(input_par,out_par)

