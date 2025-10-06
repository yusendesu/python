import random

def readfile():
    global name_list
    with open("name.txt") as file:
        name_list = [line.strip() for line in file]

def select(num):
    name = random.sample(name_list, num)
    return name

def main():
    readfile()
    mode = int(input("choose a mode(1,2,3):"))
    match mode:
        case 1:
            names = select(1)
        case 2:
            names = select(3)
        case 3:
            names = select(9)
    print(*names)

if __name__ == "__main__":
    main()