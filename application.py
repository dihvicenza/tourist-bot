from flask import Flask, render_template, jsonify, request, make_response
from numpy import result_type  # BSD License
import pg8000
import torch
import overpy
from libraries.model import NeuralNet
import nltk
from libraries.nltk_utilities import bag_of_words, tokenize

# StdLibs
import random
import json

###################################################
#Programmato da Alex Prosdocimo e Matteo Mirandola#
###################################################



application = Flask(__name__)


@application.route("/")  #Index
def index():
    return make_response(render_template("index.html"))

@application.route("/tourist")
def tourist():
    return make_response(render_template("tourist.html"))


@application.route("/cities", methods=["POST"])
def getCities():
    with open("static/jsons/comuni.json", "r") as file:
        response = json.load(file)
        return jsonify(response)

# API: Richiede obbligatoriamente i campi city e tipo. Tutti gli altri campi sono opzionali. Se i campi opzionali non sono specificiati sono, si includono tutte le opzioni
# Generatore di query al database per ottenere gli alloggi
@application.route("/getAll", methods=["POST"])
def execAllQuery():
    if "city" not in request.form or "tipo" not in request.form:
        return "400 Bad Request"
    try:
        #Costruzione della query.
        #Se il campo tipologia è == % allora non inserisce il constrain per tipologia di alloggio
        #Aggiunge i constrain successivi solo se nella richiesta esiste una specificazione true/false per quel campo 
        query = f"SELECT * FROM alloggio WHERE comune='{request.form['''city''']}'"
        if(request.form["tipo"] != "%"):
            query += f" and tipologia='{request.form['''tipo''']}'"
        if("piscina" in request.form):
            query += f" and piscina={request.form['''piscina''']}"
        if("ac" in request.form):
            query += f" and ac={request.form['''ac''']}"
        if("parcheggio" in request.form):
            query += f" and parcheggio={request.form['''parcheggio''']}"
        if("ristorante" in request.form):
            query += f" and ristorante={request.form['''ristorante''']}"
        if("animali" in request.form):
            query += f" and animali={request.form['''animali''']}"
        if("parcogiochi" in request.form):
            query += f" and parcogiochi={request.form['''parcogiochi''']}"
        if("sauna" in request.form):
            query += f" and sauna={request.form['''sauna''']}"
        if("palestra" in request.form):
            query += f" and palestra={request.form['''palestra''']}"
        query += ";"

        #Connessione al database
        #Cambiare dati del server adeguatamente, adattare nel caso non si stia usando postgresSQL
        conn = pg8000.connect(host="pg1.cfhdttxorzlt.eu-south-1.rds.amazonaws.com", port=5432,
                                database="tourist_bot", user="tourist_bot_admin", password="daUqe%z*qqj&C7n.oR8iX,]4")        
        cur = conn.cursor()
        cur.execute(query)
        result = cur.fetchall()
        response = []
        #fecassoc del mysql per ottenere le righe e costruire il dizionario di risposte
        provincia = ""
        for row in result:
            dicty = {}
            dicty['id'] = row[0]
            dicty['nome'] = row[1]
            dicty['indirizzo'] = row[3]
            dicty['stelle'] = row[5]
            if row[6] != "":
                dicty['sito'] = row[6]
            if row[7] != "":
                dicty['telefono'] = row[7]
            if row[8] != "":
                dicty['email'] = row[8]
            dicty['lat'] = row[17]
            dicty['lon'] = row[18]
            provincia = row[19]

            response.append(dicty)
        #La risposta è un dizionario di dizionari
        response = {"data": response, "provincia":provincia, "comune": request.form['''city''']}
        #Chiusura connessione al database
        cur.close()
        conn.close()
        return jsonify(response) #Ritorno json del dizionario
    except:
        return "500 Internal Server Error" 


# API: Richiede i campi sentence e city in POST
@application.route("/chatbot", methods=["GET", "POST"])
def chatbot():
    try:
        if request.method == "GET":
            return render_template("chat.html")
        else:
            if "sentence" in request.form and "city" in request.form:
                risposta = {
                    "tag": "",
                    "message": "",
                    "data": []
                }

                #NON TOCCARE IL CODICE SOTTOSTANTE
                #DELICATO E MOLTO TECNICO, SI RISCHIA DI ROMPERE TOTALMENTE LA FUNZIONALITA CHATBOT
                #Il codice sottostante analizza una frase in lingua inglese, suddividendola in pezzi più piccoli
                #detti token. In seguito, la frase trasformata in token viene fatta passare attraverso la rete neurale.
                #Questa determina l'intento della frase (ne capisce il senso) e produce una risposta.
                #Il programma analizza questa risposta ed esegue la corretta query ad overpass e ne ritorna i risultati al client
                sentence = tokenize(request.form["sentence"])
                x = bag_of_words(sentence, all_words)
                x = x.reshape(1, x.shape[0])

                x = torch.from_numpy(x)

                output = model(x)
                _, predicted = torch.max(output, dim=1)
                tag = tags[predicted.item()]
                probs = torch.softmax(output, dim=1)
                prob = probs[0][predicted.item()]
                with open('static/jsons/intents.json', 'r') as f:
                    intents = json.load(f)
                if sentence[0] == 'help':
                    risposta['tag'] = 'help'
                    risposta['message'] = f"help"
                    return risposta
                elif prob.item() > 0.75:
                    try:
                        amenitytag = ['hospital', 'nightclub' 'fast_food', 'restaurant', 'library', 'bicycle_parking', 'bicycle_rental', 'boat_rental', 'car_rental',
                                      'charging_station', 'parking', 'atm', 'pharmacy', 'casino', 'cinema', 'theatre', 'drinking_water', 'toilets', 'internet_cafe', 'post_office',
                                      'gym', 'fuel', 'bar']
                        tourismtag = ['museum', 'attraction', 'aquarium', 'caravan_site',
                                      'gallery', 'picnic_site', 'theme_park', 'viewpoint', 'zoo']
                        leisuretag = ['park', 'beach_resort', 'swimming_pool']
                        buildingtag = ['cathedral', 'church']
                        naturaltag = ['water']
                        shoptag = ['mall']

                        for intent in intents['intents']:
                            if tag == intent['tag']:
                                risposta['tag'] = tag
                                risposta['message'] = f'{random.choice(intent["responses"])}'
                        if tag in amenitytag:
                            tmp = StructQuery(request.form['city'], tag, 'amenity')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta
                        elif tag in tourismtag:
                            tmp = StructQuery(request.form['city'], tag, 'tourism')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta

                        elif tag in leisuretag:
                            tmp = StructQuery(request.form['city'], tag, 'leisure')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta

                        elif tag in buildingtag:
                            tmp = StructQuery(request.form['city'], tag, 'building')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta

                        elif tag in naturaltag:
                            tmp = StructQuery(request.form['city'], tag, 'natural')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta

                        elif tag in shoptag:
                            tmp = StructQuery(request.form['city'], tag, 'shop')
                            if(tmp == []):
                                risposta['message'] = "There are no available results"
                                return risposta
                            else:
                                risposta['data'] = tmp
                                return risposta
                        else:
                            return risposta
                    except:
                        risposta["message"] = "Please slow down! You are doing to many requests!"
                        return 
                else:
                    risposta['tag'] = 'missunderstanding'
                    risposta['message'] = f"I can't understand you. Please repeat"
                    return risposta
            else:
                return "400 Bad Request"
    except Exception as e:
        return "500 Internal Server Error"

@application.route("/final") #Final page
def final():
    return make_response(render_template("final.html"))

@application.route("/getCityCoords", methods=["POST"])
def getCoords():
    api = overpy.Overpass(url="https://overpass.kumi.systems/api/interpreter")
    query = ""
    print(request.form['city'])
    if(request.form['city'].lower() == "vicenza"):
        query= f'''
        [out:json];
        (node["name"="{request.form['city']}"]["place"= "city"];);
        out center meta;
        '''
    else:
        query= f'''
        [out:json];
        (node["name"="{request.form['city']}"]["place"= "town"];);
        out center meta;
        '''

    result = api.query(query)
    list_of_node_tags = []
    for node in result.nodes:
        node.tags['latitude'] = node.lat
        node.tags['longitude'] = node.lon
        node.tags['id'] = node.id
        list_of_node_tags.append(node.tags)
    list_of_node_tags[0]['latitude'] = str(list_of_node_tags[0]['latitude'])
    list_of_node_tags[0]['longitude'] = str(list_of_node_tags[0]['longitude'])
    return list_of_node_tags[0]


#Query ad Overpass.
#Il parametr city per ora sarà sempre Vicenza poichè il programma gestisce solo il territorio vicentino.
#queryparam è la categoria generale di oggetto da trovare (solitamente Turismo, Passatempo, Negozio...)
#tag specifica il tipo di oggetto che si sta cercando (ad esempio Museo è una specificazione di Turismo)
#Le query possono durare un po', perchè il database di OpenStreetMap è molto grande.
def StructQuery(city, tag, queryparam):
    api = overpy.Overpass(url="https://overpass.kumi.systems/api/interpreter")

    addre = ''

    query = f'''
    [out:json];
    area["name"="{city}"]->.searchArea;
    node
        ["{queryparam}"="{tag}"]
        (area.searchArea);
    out;'''

    result = api.query(query)

    list_of_node_tags = []
    for node in result.nodes:
        node.tags['latitude'] = node.lat
        node.tags['longitude'] = node.lon
        node.tags['id'] = node.id
        list_of_node_tags.append(node.tags)
    tmp = 0
    data = []
    for struct in list_of_node_tags:
        dictionout = {
            'name': '',
            'address': '',
            'opening_hours': '',
            'phone': '',
            'lat': '',
            'lon': '',
            'cost': '',
            'website': ''
        }
        if 'name' in struct:
            dictionout['name'] = struct['name']
        if 'addr:street' in struct:
            addre = struct['addr:street']
            if 'addr:housenumber' in struct:
                addre += ', ' + struct['addr:housenumber']
            if 'addr:postcode' in struct:
                addre += ', ' + struct['addr:postcode']
            dictionout['address'] = addre
        if 'opening_hours' in struct:
            dictionout['opening_hours'] = struct['opening_hours']
        if 'phone' in struct:
            dictionout['phone'] = struct['phone']
        if 'latitude' in struct:
            tmp = struct['latitude']
            dictionout['lat'] = str(tmp)
        if 'longitude' in struct:
            tmp = struct['longitude']
            dictionout['lon'] = str(tmp)
        if 'cost' in struct:
            dictionout['cost'] = struct['cost']
        if 'website' in struct:
            dictionout['website'] = struct['website']
        data.append(dictionout)
    return data

#########
#Startup#
#########

#Inizializazione rete neurale. Viene scaricato il tokenizer e viene impostata la cpu come dispositivo di elaborazione
def BotInitialize():
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    nltk.download('punkt')
    FILE = 'data.pth'
    data = torch.load(FILE)

    input_size = data['input_size']
    hidden_size = data['hidden_size']
    output_size = data['output_size']
    all_words = data['all_words']
    model_state = data['model_state']
    tags = data['tags']

    model = NeuralNet(input_size, hidden_size, output_size).to(device)
    model.load_state_dict(model_state)
    model.eval()
    return all_words, model, tags


all_words, model, tags = BotInitialize()

if __name__ == '__main__':
    application.run(debug=True, port=80)


####Powered by Requiem####