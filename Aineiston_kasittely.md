# Karttamateriaalin käsittely

[OSGeo4W](https://trac.osgeo.org/osgeo4w/) sisältämä *GDAL - Geospatial Data Abstraction Library*
[www.gdal.org](https://www.gdal.org) sisältää karttatiedon käsittelykirjaston ja koko joukon
valmiita komentorivikomentoja. Tässä yhteydessä käsitellään joitakin ohjeessa käytettyjä komentoja
hieman tarkemmin.

## Vektoriaineiston käsittely

### Koordinaattimuunnos

Aika tavallista on, että aineisto käyttää käsittelyn kannalta hankalaa koordinaattijärjestelmää.
Esimerkiksi [geojson.io](https://geojson.io) -palvelusta tehdyt lataukset eivät käytä
Maanmittauslaitoksen käyttämää ETRS-TM35FIN (eli EPSG:3067) -koordinaattijärjestelmää. Niinpä
geojson.io -palvelusta saatu koordinaattijärjestelmä pitää muuttaa EPSG:3067 -koordinaatistoon:

```
> ogr2ogr -t_srs EPSG:3067 rajaus.shp geojson.io\layers\POLYGON.shp
```

, jossa `-t_srs EPSG:3067` määrittää, että *kohdetiedoston* koordinaattijärjestelmä tulee olemaan EPSG:3067.
`rajaus.shp` on tulostiedosto ja `geojson.io\layers\POLYGON.shp` on lähdetiedosto.

### Alueen rajaaminen toisella alueella

Kartta-aineistot sisältää paljon tietoa ja vie siksi paljon tilaa ja on hidas käsitellä. Siksi ylimääräinen
aieneisto on hyvä leikata pois jo käsittelyn alkuvaiheessa. Vektoriaineiston osalta homma hoituu `ogr2ogr`
-komennolla:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_osm.gml OSM\map.osm
```

Komennossa *rajaava* muoto on annettu `-clipsrc rajaus.shp` -optiolla. `Kaitajarvi_osm.gml` on rajattu
lopputulos ja `OSM\map.osm` on lähtöaineisto, jota halutaan rajata. Tässä on hyvä huomioida, että `ogr2ogr`
osaa automaattisesti käsitellä tiedostojen tyypin, kunhan vakiintuneita tiedostojen tarkenteita käytetään.

### Aineistojen yhdistely

Joskus on tarvetta saada useita eri vektoriaineistoja yhdistettyä ja tämähän onnistuu tietenkin `ogrmerge` -komennolla.
Klassinen esimerkki on Maanmittauslaitoksen maastotietokannan koostaminen yhteen tiedostoon:

```
> ogrmerge -o MML\M4211R.gml MML\M4211R.shp\*.shp
```

Komento on aika itsestään selvä, `-o MML\M4211R.gml` on yhdistämisen lopputuloksena syntyvä kohdetiedosto.
`MML\M4211R.shp\*.shp` taas sisältää kaikki "shp-tiedostot", joita ko. hakemistossa on.

Yhdistämisessä on syytä huomioida kohdetiedoston muoto. Esimerkiksi *ESRI Shapefile* (shp-tiedosto) edellyttää,
että kaikissa yhdistettävissä tiedostoissa esitettävä *geometria* on sama, ja niihin liittyvät attribuutit ovat
samat. MML:n tapauksessa attribuutit ovat (käytännössä) samat, mutta muotoja on erilaisia (alueita, pisteitä,
polygoneja). Näin ollen kohdetiedosto ei voi maastotietokannan tapauksessa olla Shapefile.

Edelleen, esimerkiksi DXF-tiedosto ei tue yleisesti maastotietokannassa käytettyjä käyttäjän määrittelemiä
attribuutteja. Siksi myöskään DXF -muotoinen kohdetiedosto ei ole sopiva, ellei voida hyväksyä attribuuttien
menetystä.

GML:n (Geographical Markup Language) osalta tällaisia rajoitetta ei ole, mutta XML-pohjaisena se vie moniin
muotoihin verrattuna paljon levytilaa. Alueen rajauksen jälkeen tilankäyttö ei ole enää yleensä ongelma ja niin
näissä ohjeissa on melko yleisesti päädytty käyttämään GML-muotoa.

## Rasteriaineiston käsittely

Rasteriaineistoihin lasketaan kaikenlaiset kuvat. Muoto voi olla esimerkiksi TIF, JPG, PNG. Tässä ohjeessa
yleensä aina georeferoidussa, eli maantieteelliseen sijaintiin sidotussa muodossa.

### Rasteriaineiston yhdistäminen

Kuvia voidaan yhdistää komennolla `gdalwarp`. Klassinen esimerkki ovat Maanmittauslaitoksen ortoilmakuvat:

```
> gdalwarp MML\M4211E.jp2 MML\M4211F.jp2 MML\M4211E+F.tif
```

Komento yhdistää `M4211E.jp2` ja `M4211F.jp2` -tiedostot yhdeksi `M4211E+F.tif` -tiedostoksi. Huomaa, että
samalla kuvien muoto muuttuu JPEG2000 -muodosta TIFF -muotoon.

### Alueen rajaaminen toisella alueella

Varsinkin edellisessä esimerkissä esitetyt MML:n JPEG2000 -muotoiset ortoilmakuvat ovat valtavan kokoisia. Varsinkin
huokeassa, maastokäytössä olevassa Android -laitteessa niiden sutjakka pyörittely edellyttää turhan poistamista.
Se onnistuu `gdalwarp` -komennolla:

```
> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
           -co COMPRESS=JPEG -co WORLDFILE=YES MML\M4211E+f.tif Kaitajarvi_Orto.tif
```

Optio `-cutline rajaus.shp` sisältää rajauksessa käytettävän alueen. Optio `-crop_to_cutline` ohjaa komentoa 
heittämään pois rajauksen ulkopuolisen aineiston. `-dstalpha` tekee poistetusta osasta läpinäkyvän (ilman sitä
ulkopuolinen alue näkyy mustana). Optio `-s_srs EPSG:3067` kertoo, että lähdetiedostossa käytetty koordinaatisto
on EPSG:3067, kuten MML:n aineistossa aina. `-co` -optiot kertovat, että lopputulos pakataan käyttäen JPEG -pakkausta
ja että kohdetiedoston lisäksi luodaan "World-file". Lopuksi kerrotaan, että lopputuloksena syntyvä rajattu kuva
kirjoitetaan tiedostoon `Kaitajarvi_Orto.tif`.

World-file sisältää kuvan kulmien maantieteelliset koordinaatit. Tämä on kuitenkin periaatteessa turhaa, koska TIFF 
tässä tapuksessa sisätää jos itsessään koordinaattitiedon. Optiota on kuitenkin käytetty, koska OOM ei ymmärrä lukea
kuvaa georeferoituna, ellei world-fileä ole. Option käytöstä tulee komennon ajon aikana virheilmoitus, mutta siitä
ei tarvitse välittää.

## LiDAR-, eli pistepilvi- tai laserkeilausaineiston käsittely

### Pistepilviaineiston yhdistäminen

Aineistojen yhdistäminen on erityisesti tarpeen, jos siitä aiotaan tehdä käyrämuotoista. Yhdistämisen myötä käyriin
ei synny erillisten aineistojen rajoille katkoa. Yhdistäminen tapahtuu `las2las` -komennolla:

```
> las2las.exe -i MML\M4211E4.laz MML\M4211F3.laz -merged -o MML\M4211E4+F3.laz
```

Option `-i` jälkeen voidaan luetella syötteen tiedostot. Optio `-merged` kertoo, että tiedostot on tarkoitus yhdistää.
Lopuksi optiolla `-o` kerrotaan, että yhdistämisen lopputulos kirjoitetaan tiedostoon `MML\M4211E4+F3.laz`.

### Pistepilviaineiston leikkaaminen alueella

Kuten kartta-aineistossa, myös pistpilviaineistossa haluamme yleensä keskittyä vain kartoitettavaa aluetta
kattavaan aineistoon. Rajaus onnistuu komennolla `lasclip`:

```
> lasclip.exe -i MML\M4211E4+F3.laz -o MML\Kaitajarvi.laz -poly rajaus.shp -v
```

Optiolla `-i` ja `-o` kerrotaan syöte- ja tulostiedostot. Optiolla `-poly rajaus.shp` taas kertoo, että rajaukseen
käytetään muotoa tiedostossa `rajaus.shp`. Muodon tulee olla suljettu polygoni (eli lenkki) ja tiedostossa käytetyn
koordinaatiston tulee olla sama kuin syötetiedoston koordinaatiston. MML:n aineistolla koordinaatisto on poikkeuksestta
ETRS-TM35FIN, eli EPSG:3067. 

Optio `-v` antaa suorituksen aikana tavallista enemmän tietoa suorituksen etenemisestä.

### Pistepilviaineiston yksinkertaistaminen

Yksinkertaistamista voidaan tehdä useilla eri tavoilla. Tässä käytetään "thin" -menetelmää, jossa aineiston kattama
alue jaetaan oletusarvoisesti neliömetrin kokoisiin ruutuihin. Kustakin ruudusta valitaan vain se piste, jonka
korkeus (Z-attribuutti) on alin. Jos siis neliömetrin kokoiselta alueelta on useita ruutuja, olemme kiinnostuneita
vain matalimmasta.

```
> lasthin.exe -i MML\Kaitajarvi.laz -o MML\Kaitajarvi_thinned_class2.laz -keep_class 2
```

Lisäksi komento suodattaa aineistosta kaikki muut pisteet, paitsi ne, joiden luokka on 2. Luokka 2 viittaa
"maapisteisiin" (ground). Esimerkiksi kasvillisuudelleen on oma luokka, mutta niistä ei olla tässä kiinostuneita.

Yksinkertaistamisen etuna on se, että lopputuloksesta suodattuu pois merkityksettömät pienet korkeusvaihtelut.
Suodatetusta aineistosta tuotettu korkeuskäyrä on siten siistimpi ja vastaa paremmin suunnistuskartan valmistuksen
tarpeita.

Eri parametreillä ja optioilla voi olla runsaastikin vaikutusta lopputulosken laatuun ja sopivuuteen kartoitustyöhön.
Aihealuetta lienee syytä tutkailla lisää...

### Pistepilviaineiston muuttaminen käyräviivaksi

(Melkein) viimeinen vaihe ennen pistepilvitiedon siirtymistä OOM:ään kartoituksen pohjaksi on muuttaa se käyräviivaksi.
Homma hoituu `las2iso.exe` -komennolla:

```
> las2iso.exe -i MML\Kaitajarvi_thinned_class2.laz -o MML\Kaitajarvi_contours05.shp ^
              -iso_every 0.5 -keep_class 2 -clean 8 -simplify 4 -smooth 5
```

Syöte- ja tulostiedostot kuvataan yleisillä `-i` ja `-o` -optioilla. Optiolla `-iso_every 0.5` kerrotaan, että
käyräväli halutaan 0,5:n *yksikön* välein. Yksi yksikkö on pistepilven korkeusattribuutin arvo 1,0, jonka koko
riippuu aineistosta. MML:n tapauksessa se on johdonmukaisesti yksi metri. Tuumajärjestelmää käyttävissä maissa
se voisi olla esimerkiksi jalka.

Optio `-keep_class 2` kertoo, että tulostiedostoon jätetään vain luokan 2 pisteitä. Pistepilviaineistossa pisteet
luokitellaan. Luokka 2 on "maapiste" (muita ovat esim. kasvillisuus).

`-clean 8` kertoo, että alle 8 *segmenttiä* pitkät käyrät jätetään pois lopputuloksesta. Yhden segmentin käyrä
on sellainen, joka koostuu kahdesta pisteestä ja niitä yhdistävästä käyräviivasta. Kahden segmentin käyrä koostuu
kolmesta pisteestä ja niitä yhdistävästä viivasta jne. Keskimäärin MML:n aineistossa pistetiheys on 1,4 pistettä/m2,
joten pyöreästi n. alle 6m pitkät käyrät pudotetaan pois. Periaatteessa tällaisia käyriä ei esiinny kuin kumpareissa,
jolloin halkaisijaltaan noin alle parimetriset kumpareet jäävät pois.

`-simplify 4` tarkoittaa, että käyräviivalla toisistaan neljän tai alle neljän *yksikön* päässä olevat pisteet pelkistetään
yhdeksi pisteeksi. Yksikkö mielletään samoin, kuin `-iso_every` -option yhteydessä. MML:n materiaalilla kyse on siis
alle neljän metrin etäisyydellä toisistaan olevista pisteistä. 

`-smooth 5` on huonosti dokumentoitu optio. ...
