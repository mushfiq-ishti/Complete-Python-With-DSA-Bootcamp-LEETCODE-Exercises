def mergeSort_linkedList(head):
  if head is None or head.next is None: #base case if none or 1 elem is present
    return head
  if head.next.next is None: #base case if two elems are present
    if head.data > head.next.data:
      temp=head.data
      head.data=head.next.data
      head.next.data=temp
    return head
  if head.next.next.next is None: #base case if 3 elems are present
    p1=head
    p2=head.next
    p3=head.next.next
    if p1.data > p2.data:
      temp=p1.data
      p1.data=p2.data
      p2.data=temp
    if p2.data > p3.data:
      temp=p2.data
      p2.data=p3.data
      p3.data=temp
    if p1.data > p2.data:
      temp=p1.data
      p1.data=p2.data
      p2.data=temp
    return head

  def find_middle(head):

    # TODO: Implement this function
    if head is None or head.next is None:
      return head
    slow=head
    fast=head
    while fast!=None and fast.next!=None:
      slow=slow.next
      fast=fast.next.next
    return slow

  def merge_two_sorted_LL(head1,head2):
    if head1 is None:
      return head2
    if head2 is None:
      return head1

    finalHead = None
    finalTail = None

    while head1 is not None and head2 is not None:
      if(head1.data < head2.data):
        if(finalHead == None):
          finalHead = head1
          finalTail = head1
        else:
          finalTail.next = head1
          finalTail = head1
        head1 = head1.next
      else:
        if(finalHead == None):
          finalHead = head2
          finalTail = head2
        else:
          finalTail.next = head2
          finalTail = head2
        head2 = head2.next

    if head1 is not None:
      finalTail.next = head1

    if head2 is not None:
      finalTail.next = head2

    return finalHead

  mid=find_middle(head)
  head1=head
  head2=mid.next
  mid.next=None

  head1=mergeSort_linkedList(head1)
  head2=mergeSort_linkedList(head2)

  return merge_two_sorted_LL(head1,head2)

a=createLLFromList([69,96,7,6,5,4,3,2,1,0,-1,-2,25])
print_LL(a)
b=mergeSort_linkedList(a)
print_LL(b)