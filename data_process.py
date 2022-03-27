import pandas as pd
import itertools
from scipy.optimize import curve_fit
from gen_csv import indices_E, indices_S, indices_G

datastore = pd.read_csv("datastore.csv")
# print(datastore[["ticker", "provider", "date", "I1"]])

general_col = ["ticker", "provider", "date"]
E_col = list(itertools.chain.from_iterable([(i, f"{i}_weight") for i in indices_E]))
S_col = list(itertools.chain.from_iterable([(i, f"{i}_weight") for i in indices_S]))
G_col = list(itertools.chain.from_iterable([(i, f"{i}_weight") for i in indices_G]))


def get_index_coloumns(row): return ([i[:-7] for i in row.index if "_weight" in i])
def get_index_weight_coloumns(row): return ([i for i in row.index if "_weight" in i])

def next_date(date):
    year,q=map(int,date.split("Q"))
    q+=1
    if(q==5):
        q=1
        year+=1
    return f"{year}Q{q}"

# Function to curve fit to the data
def func(x, a, b, c, d): return a * (x ** 3) + b * (x ** 2) + c * x + d
# Initial parameter guess, just to kick off the optimization
guess = (0.5, 0.5, 0.5, 0.5)

def ce_face_functia_ta(rows):
    indices = get_index_coloumns(rows)
    weights = get_index_weight_coloumns(rows)

    return sum(map(lambda x: x[0]*x[1], zip(rows[indices], rows[weights])))/sum(rows[weights])


def get_price(ticker):
    b = pd.DataFrame(data=datastore, columns=["ticker", "date", "price"])
    b = b[b['ticker'] == ticker]
    return b


def get_factor(ticker, cols):
    b = pd.DataFrame(data=datastore, columns=general_col+cols)
    b = b[b['ticker'] == ticker]

    b['factor'] = c = b.apply(ce_face_functia_ta, axis=1)  # raw=False

    c = b.groupby(general_col[2]).mean()
    return c.reset_index()

def extrapolate_next_year(original):
    last_date=original.iloc[-1]['date']

    new_dates=[]
    for i in range(4):
        last_date=next_date(last_date)
        new_dates.append(last_date)
    original=original[['date','factor']]#.iloc[-35:]
    new=pd.concat([original ,pd.DataFrame(new_dates, columns=["date"])], ignore_index=True)
    # print(new)
    # print(new.index)
    # https://stackoverflow.com/questions/22491628/extrapolate-values-in-pandas-dataframe/35959909#35959909
    col_params = {}

    # Curve fit each column
    col='factor'
    # Get x & y
    x = original.index.astype(float).values
    y = original[col].values
    # print(x,y,guess)
    # Curve fit column and get curve parameters
    params = curve_fit(func, x, y, guess)
    # Store optimized parameters
    col_params[col] = params[0]
    # print(params)

    col='factor'
    # Extrapolate each column

    # Get the index values for NaNs in the column
    x = new[pd.isnull(new[col])].index.astype(float).values
    # Extrapolate those points with the fitted function
    new[col][x] = func(x, *col_params[col])

    # print(new)

    return new#.interpolate(method="spline", order=2, limit_are="outside")

# a=get_factor("GGL", S_col)


def get_E(ticker): return get_factor(ticker, E_col)
def get_S(ticker): return get_factor(ticker, S_col)
def get_G(ticker): return get_factor(ticker, G_col)


def get_ESG(ticker):
    E = get_E(ticker).rename(columns={"factor": "E"})
    S = get_S(ticker).rename(columns={"factor": "S"})
    G = get_G(ticker).rename(columns={"factor": "G"})
    ESG = E['date']  # .reset_index()

    ESG = pd.concat([ESG, E['E'], S['S'], G['G']], axis=1)
    ESG['ESG'] = (E['E']+S['S']+G['G'])/3

    return ESG


def get_index_percentage(row):
    indices = get_index_coloumns(row)

    index_df = pd.DataFrame({
        "index": indices,
        "value": [row[i]*row[i+"_weight"] for i in indices]
    })

    index_df["value"] = index_df["value"].div(row['factor']).div(sum([row[i+"_weight"] for i in indices]))

    return index_df


if __name__ == "__main__":
    a = get_G("GGL")
    print(a)

    print(extrapolate_next_year(a))
    # print(get_index_percentage(a.iloc[-1]))
    # print(get_ESG("GGL"))
