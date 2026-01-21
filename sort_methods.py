def printSortedList(list: list, sortedCount: int) -> None:
    text = ""
    for index in range(len(list)):
        if index != sortedCount:
            text += f"{list[index]}, "

        else:
            if sortedCount != 0:
                text += f"{list[index]}|"
            else:
                text += f"отсортированый массив => {list[index]}, "
    print(text)


def bubble_sort(list: list) -> list:
    count = 1
    sortedCount = len(list) - 1
    while count != 0:
        count = 0
        for index in range(len(list)):
            if index < len(list) - 1:
                if list[index] > list[index + 1]:
                    list[index] += list[index + 1]
                    list[index + 1] = list[index] - list[index + 1]
                    list[index] = list[index] - list[index + 1]
                    count += 1
        if count != 0:
            sortedCount -= 1
        else:
            sortedCount = 0
        printSortedList(list, sortedCount)
    return list


def shell_sort(list: list[int]) -> list[int]:
    last_index = len(list)
    step = len(list) // 2
    while step > 0:
        for i in range(step, last_index, 1):
            j = i
            delta = j - step
            while delta >= 0 and list[delta] > list[j]:
                list[delta], list[j] = list[j], list[delta]
                j = delta
                delta = j - step
        step //= 2
    return list
