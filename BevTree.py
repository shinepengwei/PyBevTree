# -*- coding: utf-8 -*-
# 节点运行状态：运行中/运行完成
NODE_STATUS_EXECUTING = 0
NODE_STATUS_FINISH = 1


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
        return (self.node_precondition is None or self.node_precondition.external_condition(
            input_par)) and self._do_evaluate(input_par)

    def tick(self, input_par, out_par):
        return self._do_tick(input_par, out_par)

    def _do_tick(self, input_par, out_par):
        return NODE_STATUS_EXECUTING

    #切换，从一个运行节点切换到另一个节点运行
    def transition(self, input_par):
        self._do_transition(input_par)

    def _do_transition(self,input_par):
        pass


class BevNodeTerminal(BevNode):
    def __init__(self, parent_node, node_precondition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)

    def _do_tick(self, input_par, out_par):
        return self._do_execute(input_par, out_par)

    def _do_execute(self, input_par, out_par):
        pass


class BevNodePrioritySelector(BevNode):
    '''
        优先级选择节点
    '''

    def __init__(self, parent_node, node_precondition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)
        self.current_select_index = -1

    def _do_evaluate(self, input_par):
        for index, child in enumerate(self.child_nodes):
            if child.evaluate(input_par):
                if index != self.current_select_index:
                    child.transition(input_par)
                self.current_select_index = index
                print "BevNodePrioritySelector:" + str(index)
                return True
        return False

    def _do_tick(self, input_par, out_par):
        return self.child_nodes[self.current_select_index].tick(input_par, out_par)

    def _do_transition(self, input_par):
        if self.current_select_index != -1:
            self.child_nodes[self.current_select_index].transition(input_par)
        self.current_select_index = -1



'''
一般来说，序列节点最后一个子节点应该是可重复的（没有结束），比如攻击分为：[移动过来，挥砍]，挥砍就应该是可重复的。
如果最后一个子节点结束，有两种处理方式：（``错误``）1.evaluate返回false。2evaluate返回true，但是tick.啥都不做。
处理方式：相当于重新进入。
'''


class BevNodeSequence(BevNode):
    '''
        序列节点
    '''

    def __init__(self, parent_node, node_precondition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)
        self.current_select_index = -1

    # 判断当前执行的节点是否符合条件
    def _do_evaluate(self, input_par):
        if self.current_select_index == -1:
            self.current_select_index = 0
        return self.child_nodes[self.current_select_index].evaluate(input_par)

    def _do_tick(self, input_par, out_par):
        if self.current_select_index >= len(self.child_nodes):# 重新来过
            self.current_select_index = 0
        if self.child_nodes[self.current_select_index].tick(input_par, out_par) == NODE_STATUS_FINISH:
            self.child_nodes[self.current_select_index].transition(input_par)
            self.current_select_index += 1
            if self.current_select_index >= len(self.child_nodes):
                return NODE_STATUS_FINISH
        return self.child_nodes[self.current_select_index].tick(input_par, out_par)

    def _do_transition(self, input_par):
        if self.current_select_index != -1:
            self.child_nodes[self.current_select_index].transition(input_par)
        self.current_select_index = -1



'''
结束条件：and或者or
比如逃跑有两个并行子节点【run和嘘声】，只要run结束，那么逃跑就结束。or的关系。
'''
PARALLAX_FINISH_CON_OR = 0
PARALLAX_FINISH_CON_AND = 0


class BevNodeParallelNode(BevNode):
    '''
        并行节点
    '''

    def __init__(self, parent_node, node_precondition, finish_condition, name):
        BevNode.__init__(self, parent_node, node_precondition, name)
        self.finish_condition = finish_condition
        self.statuses = []

    def add_child_node(self, node):
        BevNode.add_child_node(self, node)
        self.statuses.append(NODE_STATUS_EXECUTING)

    # 依次调用所有的子节点的Evaluate方法，若所有的子节点都返回True，则自身也返回True，否则，返回False
    def _do_evaluate(self, input_par):
        for child in self.child_nodes:
            if not child.evaluate(input_par):
                return False
        return True

    def _do_tick(self, input_par, out_par):
        if self.finish_condition == PARALLAX_FINISH_CON_OR:
            for child in self.child_nodes:
                if child.tick(input_par, out_par) == NODE_STATUS_FINISH:
                    return NODE_STATUS_FINISH
            return NODE_STATUS_EXECUTING
        else:
            ret = NODE_STATUS_FINISH
            for index, child in enumerate(self.child_nodes):
                if self.statuses[index] == NODE_STATUS_EXECUTING:
                    if child.tick(input_par, out_par) == NODE_STATUS_EXECUTING:
                        ret = NODE_STATUS_EXECUTING
                    else:
                        self.statuses[index] = NODE_STATUS_FINISH
            return ret

    def _do_transition(self,input_par):
        for i,child in enumerate(self.child_nodes):
            self.statuses[i] = NODE_STATUS_EXECUTING
            child.transition(input_par)
