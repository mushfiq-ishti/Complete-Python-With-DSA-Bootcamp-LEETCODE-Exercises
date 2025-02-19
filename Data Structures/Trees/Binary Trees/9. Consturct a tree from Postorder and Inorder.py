class BinaryTreeNode:
    def __init__(self,data):
        self.data = data
        self.left = None
        self.right = None
def construct_tree_from_inorder_and_postorder(inorder,postorder):
    n=len(inorder)
    def construct_tree_from_inorder_and_postorder_helper(inorder,postorder,inS=0,inE=n-1,poS=0,poE=n-1):
        if(inS>inE or poS>poE): # Base Condition
            return None
        
        root_data = postorder[poE] 
        root = BinaryTreeNode(root_data)
        inorder_rootIndex=-1
        
        for i,elem in enumerate(inorder):
            if elem==root_data:
                inorder_rootIndex=i
                break
        if inorder_rootIndex==-1:
            error("Check input")
            return None
    
        l_inS=inS
        l_inE=inorder_rootIndex-1
        l_poS=poS
        l_poE=(l_inE - l_inS) + l_poS
    
        r_inS= inorder_rootIndex+1
        r_inE= inE
        r_poS=l_poE+1
        r_poE=poE-1
    
        root.left= construct_tree_from_inorder_and_postorder_helper(inorder,postorder,l_inS,l_inE,l_poS,l_poE)
        root.right= construct_tree_from_inorder_and_postorder_helper(inorder,postorder,r_inS,r_inE,r_poS,r_poE)
    
        return root
    
    
    return construct_tree_from_inorder_and_postorder_helper(inorder,postorder)
    
postorder=[4,5,2,6,3,1]
inorder=[4,2,5,1,3,6]
root=construct_tree_from_inorder_and_postorder(inorder,postorder)
print_binary_tree(root)