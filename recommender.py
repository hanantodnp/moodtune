# recommender.py
import pandas as pd

class Recommender:
    def __init__(self, csv_path="models/indexed_tracks.csv"):
        self.csv_path = csv_path
        self.df = pd.read_csv(csv_path, low_memory=False)
        # normalize
        if 'mood' in self.df.columns:
            self.df['mood'] = self.df['mood'].astype(str).str.capitalize()
        # ensure popularity column name
        if 'popularity' in self.df.columns and 'popularity_track' not in self.df.columns:
            self.df.rename(columns={'popularity':'popularity_track'}, inplace=True)
        # create groups
        self.groups = {m: g.reset_index(drop=True) for m, g in self.df.groupby('mood')}


    def get_moods(self):
        return sorted(self.df['mood'].unique())
    

    def recommend_by_mood(self, mood, top_n=10, method='popularity'):
        mood = str(mood).capitalize()
        if mood in self.groups:
            df = self.groups[mood]
        else:
            df = self.df
        if method == 'popularity' and 'popularity_track' in df.columns:
            out = df.sort_values('popularity_track', ascending=False).head(top_n)
        elif method == 'valence_energy':
            # rank by valence*energy
            if 'valence' in df.columns and 'energy' in df.columns:
                df['score'] = df['valence'].fillna(0)*df['energy'].fillna(0)
                out = df.sort_values('score', ascending=False).head(top_n)
            else:
                out = df.sample(min(top_n,len(df)))
        else:
            out = df.sample(min(top_n,len(df)))
        return out.to_dict(orient='records')
    

    def sample_by_mood(self, mood, n=10):
        mood = str(mood).capitalize()
        if mood in self.groups:
            return self.groups[mood].sample(min(n, len(self.groups[mood]))).to_dict(orient='records')
        return self.df.sample(n).to_dict(orient='records')
