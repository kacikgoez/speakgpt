import pandas as pd
from threading import Semaphore


class KeyManager:

    '''
        API key manager I've intended to use for ElevenLabs, so I could have, not worth using because they'll
         block your IP ¯\_(ツ)_/¯
    '''

    def __init__(self, default="./keys.csv"):
        self.df = pd.read_csv(default)
        self.dict = {}
        for _, row in self.df.iterrows():
            self.dict[row[0]] = [row[0], int(row[1]), Semaphore(2)]

    def get_key(self, string: str):
        for index, row in self.df.iterrows():
            # Enough words left according to CSV?
            if int(row[1]) > len(string):
                if self.dict[row[0]][2].acquire(blocking=False):
                    # Given CSV [api key, number of words left] -> update number of words:
                    self.df.iloc[index, 1] = int(
                        self.df.iloc[index, 1]) - len(string)
                    self.df.to_csv("./test.csv", index=False)
                    # Returns API key and semaphore
                    return self.dict[row[0]][0], self.dict[row[0]][2]
        return "API-KEY", Semaphore(1)
