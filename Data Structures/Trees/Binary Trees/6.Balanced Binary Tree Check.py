# Definition for a binary tree node.
class TreeNode:
     def __init__(self, val=0, left=None, right=None):
         self.val = val
         self.left = left
         self.right = right

def isBalanced(root):
    if root is None:
        return True,0 #isbalanced,height
    left_balanced,left_height=isBalanced(root.left)
    right_balanced,right_height=isBalanced(root.right)
    current_balanced=left_balanced and right_balanced and abs(left_height-right_height)<=1
    current_height=1+max(left_height,right_height)
    return current_balanced,current_height

boolean,height=isBalanced(root2)
print(boolean)