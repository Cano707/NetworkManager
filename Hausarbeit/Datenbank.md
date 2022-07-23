Für das Backend wurde die NOSQL Datenbank MongoDB gewählt.

MongoDB ist ein nicht-relationales Datenbank-Mangement-System, welches hohe Flexibilität hinsichtlich der Datenspeicherung bietet [IBM_MONGODB] .

Der Grund für die Wahl dieser Datenbank liegt darin, dass in der Zukunft eine rege Weiterentwicklung erwartet wird. Diese Weiterentwicklungen können neue `fields` mit sich bringen, deren Einbettung in die bestehende Datenbank leicht umsetzbar und keine Umstrukturierung der Tabelle erfordern, wie es bei SQL Datenbanken der Fall wäre. 

Ein weiterer Vorteil bei einer NOSQL Datenbank ist die Möglichkeit problemlos verschachtelte Daten einzufügen. So ist es beispielsweise möglich unter dem Key `ssh` die für eine SSH-Verbindung notwendigen Daten abzulegen. 

NOSQL biete des Weiteren die Möglichkeit einer agilen Softwareentwicklung, die sich - im Rahmen dieses Projektes - als eine Erfordernis herausgestellt hat. 

Die Initialisierung der Datenbank erfolgt über das Skript `initializer.py`, welches die unter Datenbank `networkmanager` die Collections `router` und `switch` anlegt. 

Die Collections werden für jeden Gerättypen erstellt, welches der Ordnerstruktur folgt, die auch innerhalb des Programmes für die Speicherung der Gerätemodelle entspricht.

Ein beispielhafter Eintrag innerhalb der Collection `router` könnte wie folgt aussehen:

```json
{
    _id: ObjectId("62d5b5f20c6586ee4191b1e4"),
    key: 'test',
    config: [],
    hostname: 'test',
    model: '1800 series',
    secret: '',
    serial: { username: '', password: '', device_type: '' },
    ssh: { username: '', password: '', host: '', port: '', device_type: '' },
    telnet: { username: '', password: '', host: '', port: '', device_type: '' },
    vendor: 'cisco'
  }
```

Hier ist die _id ein von MongoDB automatisch generierter Key, der für unsere Zwecke keine festgelegte Rolle spielt. Das Feld `key` ist der vom Nutzer eindeutig definierte Schlüssel für die sogennanten `documents` bzw. für die Geräte. Die derzeitige Konfiguration des Gerätes wird unter dem Schlüssen `config` als eine Liste vom Strings hinterlegt. Der Hostname, das Model, der Hersteller (engl. Vendor) und das Secret werden in den gleichnamigen Feldern gespeichert.  Informationen bzgl. der Herstellung von Verbindungen werden in einem seperaten `document` und diese wiederum verschachtelt in den bestehenden Eintrag unter dem key hinterlegt, die dem Verbindungstyp entspricht. 





MongoDB - JSON --> FastAPI - JSON
