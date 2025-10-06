with open("name.txt", "r+") as file:
    list1 = [line.strip() for line in file]
print(list1)