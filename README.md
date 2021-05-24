# chomsky

#sample_json folder contains JSONS
cp download.json sample_json/Bot-Json_mod.json

#RUN Configuration Generation from json 
source activate rasa
python generate_rasa_config.py

#Rasa configuration generation files
cd rasa_config

#Run BOT Server

#Disable telemetry
rasa telemetry disable
#Run rasa x 
rasa x

#Run action Server
rasa run actions -vv






