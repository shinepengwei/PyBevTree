from BevTree import *
import time

class InputParam(object):
    def __init__(self):
        self.count = 0


class CON_Reached_TEN(BevNodePrecondition):
    def external_condition(self, input_par):
        if input_par.count > 100:
            return True
        return False


class NODE_Add(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "ADD")

    def _do_execute(self, input_par, output_par):
        output_par.count = input_par.count + 1
        print("NODE_Add count:" + str(output_par.count))


class NODE_Minus(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "MINUS")

    def _do_execute(self, input_par, output_par):
        output_par.count = input_par.count - 1
        print("NODE_Minus count:" + str(output_par.count))


def TEST1():
    root = BevNodePrioritySelector(None, None, "Root")
    NODE_Add(root, BevNodePreconditionNOT(CON_Reached_TEN()))
    NODE_Minus(root, CON_Reached_TEN())
    input_par = InputParam()
    output_par = InputParam()
    while True:
        time.sleep(0.1)
        if root.evaluate(input_par):
            root.tick(input_par, output_par)
            input_par.count = output_par.count


TEST1()
