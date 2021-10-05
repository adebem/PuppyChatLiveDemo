# tree.py
# simple node class for the sentence tree structure
# properties:
#     rule (word type or parent rule)
#     left (word/phrase if the rule is a word type, child rule otherwise)
#     right child node (None if the rule is a word type, child rule otherwise)
# Anthony de Bem 2021

class Node:
    # initialization requires the rule and left properties.
    # the right property is optional (tree leaves will only need to store a word/phrase in the left property)
    def __init__(self, rule, left, right=None):
        self.rule = rule
        self.left = left
        self.right = right

        if (left and type(left) == Node) and (right and type(right) == Node):
            self.len = max(left.length(), right.length()) + 1  # length of the node's deepest branch
        elif type(left) == Node:
            self.len = left.length() + 1  # length of the left child node's deepest branch
        else:
            self.len = 0  # the node is a leaf or a singular node

    def __str__(self):
        if type(self.left) == str:
            return self.left
        else:
            return self.rule

    # getters for rule, left, right, len
    def rule(self):
        return self.rule

    def left(self):
        return self.left

    def right(self):
        return self.right

    def length(self):
        return self.len

    # recursively constructs a list of leaf nodes in the order of the original sentence
    def leaves(self):
        leaves = []

        if type(self.left) == str:
            return [(self.rule, self.left)]
        else:
            leaves += self.left.leaves()
            if self.right:
                leaves += self.right.leaves()

        return leaves
