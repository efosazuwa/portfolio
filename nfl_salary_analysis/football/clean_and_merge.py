import numpy as np
import pandas as pd
import re

def create_player_df(player):
    keys = [x for x in player if x not in ['birthday', 'name', 'weight', 'height', 'draft'] and len(player[x])>0]
    j = []
    for z in keys:
        print z
        l=[]
        for x in player[z]:
            dic = {}
            for p in player[z][x]:
                dic = merge_dicts(dic,p)
            for key in dic.keys():
                dic[key] = [''.join(dic[key])]
            l.append(pd.DataFrame(dic))
        j.append(pd.concat(l))
    jj = []
    for x in j:
        x['Name'] = player['name'][0]
        if 'year_id' in x.columns:
            x = x[x['year_id']!=''].copy()
            x['year'] = x['year_id'].apply(lambda y: re.findall('(\d+|[*+]+)', y)[0])
            # x['year'] = x[x['year_id']!='']['year_id'].apply(lambda y: re.findall('(\d+|[*+]+)', y)[0])
            if x['year_id'].apply(len).mean()>4:
                x['honours'] = x['year_id'].apply(lambda y: (re.findall('(\d+|[*+]+)', y)+[None])[1])
            del x['year_id']
        jj.append(x)
    for name, df in zip(keys, jj):
        df.name = name


    # Merge
    # ###Experimental reduce(lambda x, y: pd.merge(x, y, on=[z for z in x.columns if z
    # j = reduce(lambda x, y: x.join(y, on='year'), j)
    return jj

def rename_playoff_dfs(dfs):
    playoff_dfs = ['rushing_and_receiving_playoffs', 'passing_playoffs', 'defense_playoffs', "receiving_and_rushing_playoffs", "returns_playoffs"]

    for x in dfs:
        if x.name in playoff_dfs:
           x.rename(index=str, columns=merge_dicts({y: "{}_".format('playoffs')+y for y in x.columns if y not in ['Name', 'age', 'year']}, {"Name": "Name", "age": "age", "year": "year"}), inplace=True)

def merge_dfs(dfs):
    t = [x for x in dfs if x.name !="all_pro"]
    t = sorted(t, key=len, reverse=True)

    for x in t:
        x.set_index('year', inplace=True)

    df = reduce(lambda x, y: pd.merge(x, y[y.columns.difference(x.columns)], left_index=True, right_index=True, how='outer'), t)

    all_pro_df = [x for x in dfs if x.name =="all_pro"]
    if all_pro_df:
        all_pro_df = all_pro_df[0]
        del all_pro_df['Name']
        all_pro_df = all_pro_df.pivot('year', 'voters')
        df = pd.merge(df, all_pro_df, left_index=True, right_index=True, how='outer')
    return df

def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

if __name__ == '__main__':
    # HOw to extract a list of
    lis = []
    np.random.seed(30)
    for player in np.random.choice(data, 500, replace=False):
        print player['name']
        j = cm.create_player_df(player)
        cm.rename_playoff_dfs(j)
        df = cm.merge_dfs(j)
        for x in ['birthday', 'weight', 'height', 'draft']:
            if player[x]:
                df[x] = ''.join(player[x])
            else:
                df[x] = None
        lis.append(df)
    a = pd.concat(lis)
