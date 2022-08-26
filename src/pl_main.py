import pandas as pd
import random
import time
import json

def run_palm(n,dobj):

    random.seed(9001)
    choice = random.randint(0, 2)

    if choice == 0:
        value = random.sample(range(100, 1000), n)

    elif choice == 1:

        if n % 2 == 0:
            a, b = n/2, n/2
        else:
            a, b = int(n/2), int(n/2) + 1

        value = random.sample(range(500, 1000), a)
        value += random.sample(range(100, 500), b)

    else:

        if n % 3 == 0:
            a, b, c = n/3, n/3, n/3
        elif n % 2 == 0:
            a, b, c = int(n/3), int(n/3) + 1, int(n/3) + 1
        else:
            a, b, c = int(n/3), int(n/3), int(n/3) + 1

        value = random.sample(range(700, 1000), a)
        value += random.sample(range(400, 700), b)
        value += random.sample(range(100, 400), c)


    value1 = [int((x-100)/9) for x in value]

    color = [round((1/(n-1))*x, 3) for x in range(n)]

    legend=["set {}".format(x) for x in range(1, n+1)]

    df=pd.DataFrame(list(zip(legend, value1, color)),
                columns=['legend', 'value', 'color'])


    time.sleep(4)
    return json.loads(df.to_json(orient='records'))


if __name__ == "__main__":
    print(run_palm(5,"z"))