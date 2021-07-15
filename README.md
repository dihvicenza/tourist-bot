# Tourist Bot: Portale automatico di assistenza al turismo

[Link al sito](http://touristbot.app.digitalinnovationhubvicenza.it/)

Tourist Bot è una webapp programmata in Python, con frontend in HTML/CSS/JavaScript, che permette di aiutare turisti ad preparare la loro vacanza perfetta, tramite anche il supporto di una intelligenza artificiale che possa conversare con loro. Vengono utilizzati dati open per ogni parte dell'applicazione


> Il progetto è parte del Programma Operativo Regionale del Fondo Europeo di Sviluppo Regionale (POR FESR 2014 - 2020) del Veneto, nell'ambito del bando dell'azione 231 volto alla "costituzione di Innovation Lab diretti al consolidamento/sviluppo del network Centri P3@-Palestre Digitali e alla diffusione della cultura degli Open Data."

  ![](/static/assets/logos.png)
  

## Installazione
Per installare la webapp è necessario un server con Python 3.8 installato. Le librerie necessarie per il funzionamento della webapp sono segnate nel file `requirements.txt` che può essere passato come parametro a pip. Infine, basta impostare che il file `application.py` venga avviato automaticamente all'avvio del server.

Bisogna inoltre modificare le impostazioni del database nel codice: attualmente essere si riferiscono ad un database che non sarà accessibile dall'esterno, in quanto gestito da DIH. Un database PostgreSQL è preferibile, ma modificando la funzione getAll è possibile sostituirlo con qualunque database SQL. I dati da creare nella tabella alloggio sono contenuti all'interno del file `hotelTable.csv`

Per permettere il corretto funzionamento dell'applicazione, è necessario un server di media potenza (l'ambiente che abbiamo utilizzato ha 4GB di RAM e 2 vCPU di velocità fino a 2.5GHz)

## Aggiornamento dei dataset

Gli unici dati da aggiornare sono quelli riguardanti ai centri di accoglienza turistica nel Veneto. Questi si possono aggiornare semplicemente caricando i dati dal portale opendata al database tramite script creato da zero o manualmente tramite il portale di visualizazione del database. Gli altri dati sono ottenuti automaticamente da OpenStreetMap ad ogni richiesta
