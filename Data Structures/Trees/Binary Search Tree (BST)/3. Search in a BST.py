from predefinedBSTs import create_predefined_bsts_manual

root1,root2,root3 = create_predefined_bsts_manual()

class BSTNode:
    def __init__(self,data):
        self.data = data
        self.left = None
        self.right = None
def search_in_BST(root,value):
    if root is None:
        return False
    if root.data==value:
        return True
    if root.data>value:
        ans=search_in_BST(root.left,value)
    if root.data<value:
        ans=search_in_BST(root.right,value)
    return ans

search_in_BST(root1,69)