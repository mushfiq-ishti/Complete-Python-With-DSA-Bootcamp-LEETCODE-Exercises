class Node:
    def __init__(self,data):
        self.data = data
        self.next = None

class LinkedList:
    def __init__(self):
        self.head = None

    def insertAtHead(self,data):
        new_node = Node(data)  
        new_node.next = self.head  
        self.head = new_node  

    def insertAtIndex(self,data,index):
        if(index ==0):
            newNode = Node(data)
            newNode.next = self.head
            self.head = newNode
            return 
        if(self.head == None):
            print("Index is out of bounds")
            return head
    
        self.head.next = insert_node(self.head.next,index-1,data)
        #return head

    def removeAtindex(self,index):
        if self.head is None:
            print("List is empty")
            return

        if index == 0:
            self.head = self.head.next
            return

        temp = self.head
        position = 0

        while temp and position < index - 1:
            temp = temp.next
            position += 1

        if temp is None or temp.next is None:
            print("Index out of bounds")
            return

        temp.next = temp.next.next
        
    def searchByValue(self, value):
        temp = self.head
        position = 0
        while temp:
            if temp.data == value:
                return position  # Return index where value is found
            temp = temp.next
            position += 1
        return -1  # Value not found

    def searchByIndex(self, value):
        if self.head is None or index<0:
            return None
        if index==0:
            return self.head.data
        return search_by_index(self.head.next,index-1)

    def updateNode(self, newValue, index):
        temp = self.head
        position = 0
        while temp:
            if position == index:
                temp.data = newValue  # Updating node value
                return
            temp = temp.next
            position += 1
        print("Index out of bounds")

    def print_LL(self):
        temp = self.head
        while temp:
            print(temp.data, end=" -> ")
            temp = temp.next
        print("None")  # Indicating end of linked list

    def length_LL(self):
        temp = self.head
        count = 0
        while temp:
            count += 1
            temp = temp.next
        return count


ll1 = LinkedList()

ll1.insertAtHead(3)
