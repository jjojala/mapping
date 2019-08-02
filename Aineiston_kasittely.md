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

Useimmat vektoriaineiston tiedostomuodot sisältävät tiedon käytetystä koordinaattijärjestelmästä. Tästä syystä
sitä ei tarvitse yleensä erikseen antaa. Tarvittaessa se voidaan antaa `-s_srs` -optiolla. Muutoksen yhteydessä
kohdetiedostoa ei lähtötilanteessa ole, jonka vuoksi se annetaan erikseen.

### Alueen rajaaminen toisella alueella

Kartta-aineisto sisältää paljon tietoa ja siitä johtuen kuluttaa paljon tilaa ja on hidas käsitellä. Näin ollen epäkiinnostavat
alueet kannattaa leikata pois jo käsittelyn alkuvaiheessa. Vektoriaineiston osalta homma hoituu `ogr2ogr`
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
että kaikissa yhdistettävissä tiedostoissa olevien karttaobjektien *geometriatyyppi* (piste, polygon tai alue) on sama,
ja objekteihin liittyvien *attribuuttien* nimet ja tyypit ovat samat. MML:n tapauksessa attribuutit ovat (käytännössä)
samat, mutta geometriamuotoja on erilaisia (alueita, pisteitä, polygoneja). Näin ollen kohdetiedosto ei voi
maastotietokannan tapauksessa olla Shapefile.

Edelleen, esimerkiksi DXF-tiedosto ei tue yleisesti maastotietokannassa käytettyjä käyttäjän määrittelemiä
attribuutteja. Siksi myöskään DXF -muotoinen kohdetiedosto ei ole sopiva, ellei voida hyväksyä attribuuttien
menetystä.

GML:n (Geographical Markup Language) osalta tällaisia rajoitetta ei ole, mutta XML-pohjaisena se vie moniin
muotoihin verrattuna paljon levytilaa. Alueen rajauksen jälkeen tilankäyttö ei ole enää yleensä ongelma ja niin
näissä ohjeissa on melko yleisesti päädytty käyttämään GML-muotoa.

## Rasteriaineiston käsittely

Rasteriaineistoihin lasketaan kaikenlaiset kuvat. Muoto voi olla esimerkiksi TIF, JPG, PNG. Tässä ohjeessa
yleensä aina georeferoidussa, eli maantieteelliseen sijaintiin sidotussa muodossa. Useimmissa rasteriaineistoissa
georeferointi, eli käytännössä kuvan kulmapisteiden maantieteelliset sijainnit, esitetään erillisessä
ns. *World -tiedostossa*. World-tiedoston nimi on yleensä johdettu kuvatiedoston nimestä: jos kuvatiedosto
on `Kaitajarvi_Orto.jpg`, voi world -tiedoston nimi olla `Kaitajarvi_Orto.wld`. Joissakin rasteriaineistoissa
georeferointi voi olla upotettuna kuvatiedoston sisään. Näin on esimerkiksi ns. GeoTIF -muotoisessa TIFF -tiedostossa.

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
on EPSG:3067, kuten MML:n aineistossa aina on. `-co` -optiot kertovat, että lopputulos pakataan käyttäen JPEG -pakkausta
ja että kohdetiedoston lisäksi luodaan World -tiedosto. Lopuksi kerrotaan, että lopputuloksena syntyvä rajattu kuva
kirjoitetaan tiedostoon `Kaitajarvi_Orto.tif`.

World -tiedosto sisältää kuvan kulmien maantieteelliset koordinaatit. Tämä on kuitenkin tässä tapauksessa turhaa, koska
syntyvä `Kaitajarvi_Orto.tif` sisältää jo itsessään koordinaattitiedon. Optiota on kuitenkin käytetty, koska OOM ei ymmärrä lukea
kuvaa georeferoituna, ellei world -tiedostoa ole. Option käytöstä tulee komennon ajon aikana virheilmoitus, mutta siitä
ei tarvitse välittää.

## Laserkeilausaineiston käsittely

Laserkeilaus-, eli [LiDAR](https://fi.wikipedia.org/wiki/Lidar) -aineisto koostuu pisteistä (tästä nimitys pistepilvi).
Kukin piste sisältää erinäistä tietoa, josta tärkeimmät ovat:
* pisteen maantieteelliset koordinaatit (MML:n materiaalissa käytetään aina ETRS-TM35FIN, eli EPSG:3067 koordinaattijärjestelmää),
* Z-koordinaatin, eli pisteen korkaus merenpinnasta (metrejä, desimaaliluku) ja
* pisteen *luokka*, joista tärkein on maanpintaa (ground) kuvaava luokka 2.

Laserkeilausaineiston käsittely on mahdollista esimerkiksi [LAStools](https://rapidlasso.com/lastools/) -paketin työkaluilla,
joiden käyttö ei-kaupalliseen käyttöön on ilmaista. Isoilla aineistoilla osa LASTools:n työkaluista lisää tuottamaansa
aineistoon virhekohinaa, jonka ei käytännössä ole havaittu vaikuttavan kartoitustyöhön. Hankkimalla LASTools:n lisenssin,
pääsee virhekohinasta eroon. 

Maanmittauslaitos luokittelee pisteet (*luokka*) ensin automaattisesti (automaattiluokiteltu aineisto) ja myöhemmin
stereomallin avulla (stereomalliluokiteltu). Jälkimmäinen on täsmällisempi, mutta se ei ole yhtä nopeasti saatavilla
kuin automaattiluokiteltu aineisto. Jos (ja kun) laserkeilausaineistoa käytetään nimenomaan korkeuskuvauksen tuottamiseen,
stereomalliluokiteltu lienee lähes aina parempi vaihtoehto. Maanmpinnan muodot kun eivät jatkuvasti vaihtele. Maanmittaulaitoksen
laserkeilausaineiston tarkempi kuvaus on saatavilla 
[täällä](https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/asiantuntevalle-kayttajalle/tuotekuvaukset/laserkeilausaineisto). 

### Laserkeilausaineiston yhdistäminen

Aineistojen yhdistäminen on erityisesti tarpeen, jos siitä aiotaan tehdä käyrämuotoista. Yhdistämisen myötä käyriin
ei synny erillisten aineistojen rajoille katkoa. Yhdistäminen tapahtuu `las2las` -komennolla:

```
> las2las.exe -i MML\M4211E4.laz MML\M4211F3.laz -merged -keep_class 2 -o MML\M4211E4+F3_ground.laz
```

Option `-i` jälkeen voidaan luetella syötteen tiedostot. Optio `-merged` kertoo, että tiedostot on tarkoitus yhdistää.
Optiolla `-keep_class 2` ilmaistaan, että lopputulokseen poimitaan vain maanpinnaksi (ground, luokka 2) luokitellut
pisteet. Lopuksi optiolla `-o` kerrotaan, että yhdistämisen lopputulos kirjoitetaan tiedostoon `MML\M4211E4+F3_ground.laz`.

### Laserkeilausaineiston leikkaaminen alueella

Kuten kartta-aineistossa, myös laserkeilausaineistossa haluamme yleensä keskittyä vain kartoitettavaa aluetta
kattavaan aineistoon. Rajaus onnistuu komennolla `lasclip`:

```
> lasclip.exe -i MML\M4211E4+F3_ground.laz -o MML\Kaitajarvi_ground.laz -poly rajaus.shp -v
```

Optiolla `-i` ja `-o` kerrotaan syöte- ja tulostiedostot. Optiolla `-poly rajaus.shp` taas kertoo, että rajaukseen
käytetään muotoa tiedostossa `rajaus.shp`. Muodon tulee olla suljettu polygoni (eli lenkki) ja tiedostossa käytetyn
koordinaatiston tulee olla sama kuin syötetiedoston koordinaatiston. MML:n aineistolla koordinaatisto on poikkeuksestta
ETRS-TM35FIN, eli EPSG:3067. 

Optio `-v` antaa suorituksen aikana tavallista enemmän tietoa suorituksen etenemisestä.

### Laserkeilausaineiston yksinkertaistaminen

Yksinkertaistamista voidaan tehdä useilla eri tavoilla. Tässä käytetään "thin" -menetelmää, jossa aineiston kattama
alue jaetaan oletusarvoisesti neliömetrin kokoisiin ruutuihin. Kustakin ruudusta valitaan vain se piste, jonka
korkeus (Z-attribuutti) on alin. Jos siis neliömetrin kokoiselta alueelta on useita ruutuja, olemme kiinnostuneita
vain matalimmasta.

```
> lasthin.exe -i MML\Kaitajarvi_ground.laz -o MML\Kaitajarvi_ground_thinned.laz
```

Yksinkertaistamisen etuna on se, että lopputuloksesta suodattuu pois merkityksettömät pienet korkeusvaihtelut.
Suodatetusta aineistosta tuotettu korkeuskäyrä on siten siistimpi ja vastaa paremmin suunnistuskartan valmistuksen
tarpeita.

MML:n laserkeilausaineistolla `lasthin` -komennolla tehtävä yksinkertaistaminen - ainakaan oletusarvoilla - ei tunnu
vaikuttavan kovin merkittävästi lopputulokseen. Seikka saattaa johtua siitä, että MML:n aineistossa pisteiden tiheys
ei ole kovin suuri (keskimäärin 0,5 pistettä/m2, joista kaikki eivät ole maapisteitä).

### Laserkeilausaineiston muuttaminen käyräviivaksi

(Melkein) viimeinen vaihe ennen laserkeilausaineiston siirtymistä OOM:ään kartoituksen pohjaksi on muuttaa se käyräviivaksi.
Homma hoituu `las2iso.exe` -komennolla:

```
> las2iso.exe -i MML\Kaitajarvi_ground_thinned.laz -o MML\Kaitajarvi_contours05.shp ^
              -iso_every 0.5 -clean 8 -simplify 4 -smooth 5
```

Syöte- ja tulostiedostot kuvataan yleisillä `-i` ja `-o` -optioilla. Optiolla `-iso_every 0.5` kerrotaan, että
käyräväli halutaan 0,5:n *yksikön* välein. Yksi yksikkö on pistepilven korkeusattribuutin arvo 1,0, jonka koko
riippuu aineistosta. MML:n tapauksessa se on johdonmukaisesti yksi metri. Tuumajärjestelmää käyttävissä maissa
se voisi olla esimerkiksi jalka.

`-clean 8` kertoo, että alle 8 *segmenttiä* pitkät käyrät jätetään pois lopputuloksesta. Yhden segmentin käyrä
on sellainen, joka koostuu kahdesta pisteestä ja niitä yhdistävästä käyräviivasta. Kahden segmentin käyrä koostuu
kolmesta pisteestä ja niitä yhdistävästä viivasta jne. MML:n aineistossa keskimääräinen pisteiden välinen etäisyys on 1,4m,
joten pyöreästi n. alle 11m pitkät käyrät pudotetaan pois. Periaatteessa tällaisia käyriä ei esiinny kuin kumpareissa,
jolloin halkaisijaltaan noin alle nelimetriset kumpareet jäävät pois.

`-simplify 4` tarkoittaa, että käyräviivalla toisistaan neljän tai alle neljän *yksikön* päässä olevat pisteet pelkistetään
yhdeksi pisteeksi. Yksikkö mielletään samoin, kuin `-iso_every` -option yhteydessä. MML:n materiaalilla kyse on siis
alle seitsemän metrin etäisyydellä toisistaan olevista pisteistä. 

`-smooth 5` on huonosti dokumentoitu optio. ...
