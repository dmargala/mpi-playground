#!/usr/bin/env python

def main():

    # say hello
    print(f"Hello!")

    # iterate over tasks
    for i in range(3):

        # generate data
        numbers = list(range(i*10, (i+1)*10))
        print(f"({i}) numbers = {numbers}")

        # compute total
        total = 0
        for value in numbers:
            total += value

        # print result
        print(f"({i}) total = {total}")


if __name__ == "__main__":
    main()
