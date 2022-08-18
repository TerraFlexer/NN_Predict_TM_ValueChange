# NN_Predict_TM_ValueChange
## Neuron network predicting player's TransferMarkt new value after season based on his performance during it.
Players' stats for season are collected from fbref.com using parsing.py, transfermarkt database with players and their values are taken from kaggle.com
data_unite.py uses functions from parser.py for different seasons, unite all necessary data in the final.csv which is input data for network.
