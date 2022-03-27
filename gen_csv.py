import csv
import random
import itertools

tickers = ["GGL", "FMI", "MMN"]

provider = ["ARAT", "P2", "P3"]

date = list(itertools.chain.from_iterable([[f"{an}Q{q}" for q in [1, 2, 3, 4]] for an in range(2000, 2021)]))

indices_E = ["I1", "I4", "I7"]
indices_S = ["I2", "I5", "I8"]
indices_G = ["I3", "I6", "I9"]
indices = indices_E+indices_S+indices_G


if __name__ == "__main__":
    f = open("datastore.csv", "w+", newline="")
    w = csv.writer(f)
    w.writerow(["ticker", "provider", "date", "price"] + list(itertools.chain.from_iterable([(i, f"{i}_weight") for i in indices])))

    for t in tickers:
        for d in date:
            price = random.randint(1, 1000*100)/100
            for p in provider:
                w.writerow([t, p, d, price] + list(itertools.chain.from_iterable([(random.randint(1, 1000)/100, random.randint(0, 100)) for i in indices])))
                # for i in indices:
                #     pass
