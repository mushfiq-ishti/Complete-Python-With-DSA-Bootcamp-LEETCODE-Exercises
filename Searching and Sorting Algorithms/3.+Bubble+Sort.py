def bubble_sort(arr):
    n = len(arr)

    for i in range(0,n-1):
        for j in range(n-1-i):
            if(arr[j] > arr[j+1]):
                arr[j],arr[j+1] = arr[j+1],arr[j]
                
    return arr


unsorted_list = [1,10,64,34,25,12,22]
sorted_list = bubble_sort(unsorted_list)
print(sorted_list)