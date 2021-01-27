#!/usr/bin/env python

def main():

    # say hello
    print(f"Hello!")

    for i in range(3):
        # generate data
        data = list(range((i+1)*10))

        # compute total
        total = 0
        for value in data:
            total += value

        # print result
        print(f"({i}) total = {total}")



if __name__ == "__main__":
    main()
