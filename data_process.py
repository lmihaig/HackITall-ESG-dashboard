import pandas as pd
import itertools
from gen_csv import indices_E, indices_S, indices_G

datastore=pd.read_csv("datastore.csv")
# print(datastore[["ticker", "provider", "date", "I1"]])

general_col=["ticker", "provider", "date"]
E_col=list(itertools.chain.from_iterable([ (i,f"{i}_weight") for i in indices_E]))
S_col=list(itertools.chain.from_iterable([ (i,f"{i}_weight") for i in indices_S]))
G_col=list(itertools.chain.from_iterable([ (i,f"{i}_weight") for i in indices_G]))

def ce_face_functia_ta(rows):
    # print(rows[3:][0])
    # indices=rows.index[3::2]
    # weights=rows.index[4::2]
    indices=rows[3::2]
    weights=rows[4::2]
    # help(rows)
    # print(sum(map(*,zip(indices,weights)))/sum(weights))
    return sum(map(lambda x:x[0]*x[1] ,zip(indices,weights)))/sum(weights)


def get_factor(ticker, cols):
    b=pd.DataFrame(data=datastore, columns= general_col+cols)
    b=b[b['ticker']== ticker]

    b['factor']=c=b.apply(ce_face_functia_ta, axis=1)#raw=False

    c=b.groupby(general_col[2]).mean()
    return c.reset_index()

# a=get_factor("GGL", S_col)

def get_E(ticker): return get_factor(ticker, E_col)
def get_S(ticker): return get_factor(ticker, S_col)
def get_G(ticker): return get_factor(ticker, G_col)

def get_ESG(ticker):
    E=get_E(ticker).rename(columns={"factor":"E"})
    S=get_S(ticker).rename(columns={"factor":"S"})
    G=get_G(ticker).rename(columns={"factor":"G"})
    ESG=E['date']#.reset_index()

    ESG=pd.concat([ESG, E['E'], S['S'], G['G']], axis=1)
    ESG['EGS']=E['E']+S['S']+G['G']

    return ESG

def get_index_percentage(row):
    indices=([i[:-7] for i in row.index if "_weight" in i])

    index_df=pd.DataFrame({
        "index": indices,
        "value": [row[i]*row[i+"_weight"] for i in indices]
    })

    index_df["value"]=index_df["value"].div(row['factor']).div(sum([row[i+"_weight"] for i in indices]))

    return index_df

if __name__ == "__main__":
    a=get_G("GGL")
    print(a)

    # print(get_index_percentage(a.iloc[-1]))
    # print(get_ESG("GGL"))
