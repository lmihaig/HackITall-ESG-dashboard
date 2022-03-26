import csv
import random
import itertools

tickers = ["GGL", "FMI", "MMN"]

provider = ["ARAT", "P2", "P3"]

date = ["2017Q1", "2017Q2", "2017Q3", "2017Q4", "2018Q5"]

indices_E=["I1"]
indices_S=["I2"]
indices_G=["I3"]
# ["I1", "I2", "I3"]
indices=indices_E+indices_S+indices_G


# index_weight=[random.randint(1,1000)/100 for i in indices]


if __name__ =="__main__":
    f=open("datastore.csv", "w+", newline="")
    w=csv.writer(f)
    w.writerow(["ticker", "provider", "date", "price"]+ list(itertools.chain.from_iterable([ (i,f"{i}_weight") for i in indices])))

    for t in tickers:
        for d in date:
            price=random.randint(1,1000*100)/100
            for p in provider:
                w.writerow([t,p,d, price]+ list(itertools.chain.from_iterable([(random.randint(1,1000)/100, random.randint(0,100)) for i in indices])))
                # for i in indices:
                #     pass
