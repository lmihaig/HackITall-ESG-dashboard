import csv
import random
import itertools


tickers = ["GGL", "FMI", "MMN", "FLOP", "PGP", "SSH", "OSPF", "LSAC", "DDD", "CASL", "IRAM", "MLK", "PIN", "ASM", "PIP", "SPRP"]


provider = ["ARAT", "ISS", "MSCI", "ETHOS", "MRATE"]

date = list(itertools.chain.from_iterable([[f"{an}Q{q}" for q in [1, 2, 3, 4]] for an in range(2000, 2021)]))

indices_E = ["Greenhouse Gas Emissions", "Carbon Footprint", "Energy Consumption Intensity", "Production of hazardous waste"]
indices_S = ["Equal representation", "Discrimination", "Personal data security and privacy"]
indices_G = ["Bribery and corruption", "Accountability/rule of law", "Disclosures and practices"]
indices = indices_E+indices_S+indices_G


if __name__ == "__main__":
    f = open("datastore.csv", "w+", newline="")
    w = csv.writer(f)
    w.writerow(["ticker", "provider", "date", "price"] + list(itertools.chain.from_iterable([(i, f"{i}_weight") for i in indices])))

    last_value={ t:{i:random.randint(1, 1000)/100 for i in indices} for t in tickers}

    for t in tickers:
        for d in date:
            price = random.randint(1, 1000*100)/100
            last_value={ t:{i:last_value[t][i]*random.randint(50, 150)/100 for i in indices} for t in tickers}
            for p in provider:

                w.writerow([t, p, d, price] + list(itertools.chain.from_iterable([(last_value[t][i]*random.randint(95, 105)/100, random.randint(0, 100)) for i in indices])))
                # for i in indices:
                #     pass
