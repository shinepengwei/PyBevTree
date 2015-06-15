# -*- coding: utf-8 -*-
from BevTree import *
import time

class InputParam(object):
    def __init__(self):
        self.count = 0
        self.show = True


class CON_Reached(BevNodePrecondition):
    def __init__(self, num):
        self.num = num

    def external_condition(self, input_par):
        if input_par.count > self.num:
            return True
        return False

class TerminalRevert(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "ADD")

    def _do_execute(self, input_par, output_par):
        output_par.show = not input_par.show
        print("TerminalRevert:" + str(output_par.show))


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

        return NODE_STATUS_EXECUTING

class TerminalAddTo(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition,num):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "NodeAddTo")
        self.num = num

    def _do_execute(self, input_par, output_par):
        output_par.count = input_par.count + 1
        print("NodeAddTo" + str(self.num) + " count:" + str(output_par.count))
        if output_par.count >= self.num :
            return NODE_STATUS_FINISH
        return NODE_STATUS_EXECUTING

class NodeAddTo10(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "NodeAddTo10")

    def _do_execute(self, input_par, output_par):
        output_par.count = input_par.count + 1
        print("NodeAddTo10 count:" + str(output_par.count))
        if output_par.count >= 10 :
            return NODE_STATUS_FINISH
        return NODE_STATUS_EXECUTING

class NodeAddTo20(BevNodeTerminal):
    def __init__(self, parent_node, node_precondition):
        BevNodeTerminal.__init__(self, parent_node, node_precondition, "NodeAddTo20")

    def _do_execute(self, input_par, output_par):
        output_par.count = input_par.count + 1
        print("NodeAddTo20 count:" + str(output_par.count))
        if output_par.count >= 20:
            return NODE_STATUS_FINISH
        return NODE_STATUS_EXECUTING

def test0():
    root = BevNodePrioritySelector(None, None, "Root")
    NODE_Add(root, BevNodePreconditionNOT(CON_Reached(10)))
    NODE_Minus(root, CON_Reached(10))
    input_par = InputParam()
    output_par = InputParam()
    while True:
        time.sleep(0.1)
        if root.evaluate(input_par):
            root.tick(input_par, output_par)
            input_par.count = output_par.count

def test1():
    root = BevNodePrioritySelector(None, None, "Root")
    seq = BevNodeSequence(root,BevNodePreconditionNOT(CON_Reached(25)), "seq")
    NodeAddTo10(seq, None)
    NODE_Add(seq, None)
    NODE_Add(root, BevNodePreconditionNOT(CON_Reached(40)))
    input_par = InputParam()
    output_par = InputParam()
    while True:
        time.sleep(0.1)
        if root.evaluate(input_par):
            root.tick(input_par, output_par)
            input_par.count = output_par.count

def test2():
    root = BevNodePrioritySelector(None, None, "Root")
    seq = BevNodeSequence(root,BevNodePreconditionNOT(CON_Reached(25)), "seq")
    NodeAddTo10(seq, None)
    NODE_Add(seq, None)
    parallax = BevNodeParallelNode(root, BevNodePreconditionTRUE(), PARALLAX_FINISH_CON_OR, "parallax")
    TerminalAddTo(parallax, None, 40)
    TerminalRevert(parallax, None)
    input_par = InputParam()
    output_par = InputParam()
    while True:
        time.sleep(0.1)
        if root.evaluate(input_par):
            root.tick(input_par, output_par)
            input_par.count = output_par.count
            input_par.show = output_par.show


if __name__ == '__main__':
    test2()



