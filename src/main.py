import os
from pathlib import Path

def load_data(filename):
    data_source=Path.exists("./data" / filename)
    data_source
    with open(data_source, "r") as f:
        text=f.read()
        f.close()
    
    return text



def main():

    text=load_data()