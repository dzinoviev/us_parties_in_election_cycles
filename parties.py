import pandas as pd
import networkx as nx

# Read data from Wikipedia
SOURCE = "https://en.wikipedia.org/wiki/List_of_United_States_presidential_election_results_by_state"
table = pd.read_html(SOURCE)[0]

# Clean up the table
data = table.T.set_index(0).T.iloc[:,:-1].set_index("State")\
                                         .dropna(how='all').iloc[:-1]
data = data.drop('State')
data = data.dropna(axis=1, how='all')
data.columns = [1789] + list(range(1792, 2021, 4))
# There was no party-based election that year
# But you can still keep the column. 
# REMOVE EITHER OF THESE TWO LINES
df.loc[df[1824] != 'X', 1824] = 'DR'
data.drop(1824, axis=1)

# Calculate similarities between cycles
parts=[]
for year1, year2 in zip(data.columns, data.columns[1:]):
    s = data.groupby([year1,year2]).size()\
                                   .reset_index()\
                                   .rename(columns={year1: 'n1', year2: 'n2'})
    s['n1'] += " (" + str(year1) + ")"
    s['n2'] += " (" + str(year2) + ")"
    s[0] /= s[0].sum() # Normalize
    parts.append(s)

# Create a directed weighted network of parties/years
G = nx.from_pandas_edgelist(pd.concat(parts).rename(columns={0: 'weight'}),
                            'n1', 'n2', 'weight', create_using=nx.DiGraph)
# Add network attributes
nx.set_node_attributes(G, {n: int(n.split(" ")[1][1:-1]) for n in G}, "year")
nx.set_node_attributes(G, {n: n.split(" ")[0] for n in G}, "party")
counts = data.apply(lambda x:
                    x.value_counts()).stack().astype(int).reset_index()
nx.set_node_attributes(G, {f"{x[0]} ({x[1]})":
                           x[2] for x in counts.values}, "s")

# Save the results
nx.write_graphml(G,"parties.graphml")
