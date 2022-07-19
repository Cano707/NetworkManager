1. Routen für unterschiedliche Funktionskategorien 

2. Funktionskategorien nennen und beschreiben

3. Route -> diverse Endpoints für die Funktionskategorie

4. Unterscheidung gleicher Pfade durch Request-Typ

5. Klassen als Routen definition

### Grundlegende Struktur der Endpoints

Zur Interaktion mit der Anwendung stehen Endpoints zur Verfügung, die über die gängigen HTTP-Requests GET, POST, PUT und DELETE angesprochen werden können. Die API-Schnittstellen werden je nach Funktion kategorierst und unter den für sie definierten Routen zugänglich gemacht. 

Als Route ist ein Endpoint zu verstehen, an dem weitere Endpoints angehängt werden. So ist eine Organisation und somit eine übersichtlichere Struktur umsetzbar. Wenn beispielsweise`localhost:8000` die Domain ist, so ist die Route `localhost:8000/crud/` und folglich ein möglicher Endpoint `localhost:8000/crud/create`, über ein POST-Request die Möglichkeit bietet eine Objekt zu erstellen. 

Alle Routen und deren Endpoints werden global unter der Route `/app/v1` bekannt gemacht. Diese soll nicht nur die derzeitige Version der API Schnittstellen vermitteln, sondern auch eine zukünftige Versionierung vereinfachen.

#### Versionierung und Erweiterung der API

Hierzu ist lediglich unter dem Ordnerpfad `./app/api/` eine neuer Ordner mit der entsprechenden Version zu erstellen. 







Da in Zukunft eine erweiterte Version dieser Applikation bzw. der API zu erwarten ist, wurde die Hauptroute als `/app/v1` definiert, unter der alle weiteren Routen zu erreichen sind. So wird eine Versionierung der API ermöglicht

Die Funktionskategorien und deren Endpoints sind hierbei die folgenden:

- **about**: Bietet Endpoints für die Erfragung von unterstützten Herstellern, Gerätetypen und Gerätemodellen.
  
  - 

- **device**: Bietet Endpints für CRUD-Operationen, um ein Gerät hinzuzufügen, zu verändern, zu erfragen und zu löschen.

- **connect**: Bietet Endpoints um eine Verbindung mit einem Gerät aufzubauen bzw. sich von diesem zu trennen.

- **command**: Bietet Endpoints um Befehle an das gewählte Gerät zu schicken und - wenn gewünscht - zu konfigurieren.






