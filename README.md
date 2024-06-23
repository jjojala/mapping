# Suunnistuskartan pohja-aineiston valmistelu avoimista aineistoista OOM:lle

## Ohjelmat

Kaikki käytetyt ohjelmat ovat ilmaisia. Käyttöympäristönä näissä ohjeissa on Windows, mutta tarvittavat ohjelmat
toimivat useissa eri ympäristöissä.

* [OpenOrienteering Mapper](https://www.openorienteering.org/), eli kotoisasti "OOM"
* [OSGeo4W](https://trac.osgeo.org/osgeo4w/) on Windows -ympäristöön koottu  ilmainen 
ohjelmistokokonaisuus kartta-aineiston käsittelyyn. OSGeo4W:stä sisältää todella monipuoliset 
työkalut, mutta tässä ohjeessa tarvitaan ainoastaan paketit `gdal`, `gdal-python`, `pdal` sekä 
`gdal203dll`, `shell` (ja ohjelmistopäivitysten myöhempään ylläpitoon `setup`) ja lisäksi ne
automaattisesti asentuvat paketit, joista em. ovat riippuvaisia.
  
Lisäksi tarvitset:
* MML:n MTK --> ISOM2017 -translaatiotaulukon [MTK-ISOM2017.crt](https://github.com/jjojala/mapping/raw/master/MTK-ISOM2017.crt), sekä
* Korkeuskäyrien luokitteluun tarkoitetun [`contours.py` -komennon](contours.py)

## Alueen rajaus

Aloitetaan alueen rajaamisella. Se onnistuu esimerkiksi 
[geojson.io](https://geojson.io/) -palvelussa. Käyttääksesi palvelua et tarvitse 
käyttäjätunnusta.

Valitse karttanäkymän oikeasta laidasta *Draw a polygon* -työkalu ja rajaa sillä kartoitettava 
alue. Tallenna alue *Shapefile* (ESRi Shapefile) -muodossa valikon *Save->Shapefile* 
-toiminnolla.

![geojson.net](images/geojsonio.png)

Pura ladattu tiedosto esimerkiksi tekemääsi hakemistoon `geojson.net`.

geojson.net -palvelu käyttää WGS-84, eli EPSG:4326 -koordinaattijärjestelmää. Sen sijaan maanmittauslaitos käyttää
kaikissa aineistoissaa ETRS-TM35FIN, eli EPSG:3067 -koordinaattijärjestelmää. Jäljempänä oletetaan, että rajaus
annetaan ETRS-TM35FIN -muodossa, joten rajaus on tarpeen muuttaa ETRS-TM35FIN -muotoon.

Käynnistä OSGeo4W Shell (komentotulkki) esimerkiksi Windows:n *Start* -valikon kautta ja muuta aluerajaus MML:n käyttämään koordinaatistoon:

```
> ogr2ogr -t_srs EPSG:3067 Kaitajärvi_rajaus.shp geojson.net\layers\POLYGON.shp
```

Älä sulje *OSGeo4W shell*:iä komennon jälkeen (myöhemmin tässä ohjeessa suoritettavat komennot ajetaan
samasta ikkunasta).

## Aineistot

Tarvittavat avoimet aineistot saadaan seuraavista palveluista:
* [Maanmittauslaitoksen (MML) avoimien aineistojen tiedostopalvelu](https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta)
* [MapAnt](https://mapant.fi/)
* [OpenStreetMap](https://www.openstreetmap.org/)

### Maanmittauslaitoksen (MML) avoimet aineistot

Lataa MML:n avoimet aineistot palvelusta:
  https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta

Valitse vasemmassa reunassa noudettavan materiaalin tyyppi yksi kerraallaan ja klikkaa sen jälkeen haluamaasi aluetta.
Lista noudettavasta materiaalista muodostuu oikeaan reunaan. Noudettavia materiaaleja ovat:
* JPEG2000 -muotoiset ortoilmakuvat
* laserkeilaus-, eli pistepilviaineisto (mielellään stereomalliluokiteltu)
* Maastotietokanta, kaikki kohteet
* kiinteistörekisterikartta, vektori, kaikki kohteet

![MML](images/MML.png)

Tee lataustilaus ja odota, että saat sähköpostiisi latauslinkin. Lataa aineistot ja kopioi ne esimerkiksi tekemääsi
hakemistoon `MML`. Pura zip -paketit vastaavan nimiseen hakemistoon, esim. `MML\M4211R.shp.zip` --> `MML\M4211R.shp`

### MapAnt

Hae MapAnt -kartta palvelusta https://www.mapant.fi/. Tuonti käynnistetään *Export* -toiminnolla, jonka jälkeen
hiirellä rajataan kartalta noudettava suorakaiteenmuotoinen alue. Käytä tuonnissa tarkinta lähennystasoa (Zoom=9)
ja muotona georeferoitua PNG:tä (Format="Georeferenced PNG"):

![MapAnt](images/mapant.png)

Pura ladattu zip-tiedosto esimerkiksi tekemääsi hakemistoon `MapAnt`.

### OpenStreetMap (OSM)

OSM -palvelu löytyy osoitteesta https://openstreetmap.org/. Aineiston voi rajata ja tuoda karttanäkymästä *Export* -toiminnolla.
Kopioi ladattu `map.osm` hakemistoon `OSM`.

![OSM](images/OSM.png)

## Aineiston valmistelu

### MapAnt -kartan valmistelu

Rajataan kartoitettava alue:

```
> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
            -co COMPRESS=JPEG -co WORLDFILE=YES MapAnt\MapAnt.png Kaitajarvi_MapAnt.tif
```

Tässä vaiheessa on luontevaa luoda OOM -kartta ja tuoda sinne edellä synnytetty `Kaitajarvi_MapAnt.tif` taustakartaksi
georeferointeineen ja erannon asetuksineen (kts. pikakartan valmistusohjetta). Maanmittauslaitos tuottaa Ilmatieteenlaitoksen erantomittausten pohjalta [erantokarttaa](https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/kartat/erantokartta), jonka mukaan eranto kannattaa OOM:ssä asettaa.

### Ortoilmakuvien valmistelu

Yhdistetään kuvat (jos useita):

```
> gdalwarp MML\M4211E.jp2 MML\M4211F.jp2 MML\M4211E+F.tif
```

... ja rajataan kartoitettavaan alueeseen (kuten MapAnt -kartta):

```
> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
            -co COMPRESS=JPEG -co WORLDFILE=YES MML\M4211E+F.tif Kaitajarvi_Orto.tif
```

Tässä vaiheessa on jälleen hyvä avata syntynyt `Kaitajarvi_Orto.tif` luotavan kartan taustakartaksi.

### Kiinteistörajojen valmistelu ja tuonti

Rajataan kiinteistötiedot:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_kiinteistorajat.gml MML\M4211E\M4211E_kiinteistoraja.shp
```

Lopputuloksena syntyvä `Kaitajarvi_kiinteistorajat.gml` voidaan tuoda _taustakarttana_ OMAP-karttaan.

### OpenStreetMap -kartan valmistelu ja tuonti

OSM -kartta ei käytä MML:n käyttämää koordinaattijärjestelmää, joten se pitää ensin muuttaa:

```
> ogr2ogr -t_srs EPSG:3067 OSM\map.gml OSM\map.osm
```

Muutoksen jälkseen rajataan materiaali kartoitettavaan alueeseen:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_osm.gml OSM\map.gml
```

Lopputuloksenä syntyvä `Kaitajarvi_osm.gml` on yleensä mielekästä avata taustakarttana. Tällöin taustakartan
avaulla piirretään taustakartan halutut kohteet myös OOM-karttaan.

Jos OSM-kartta sisältää huomattavan paljon kartalle sellaisenaan tuotavia kohteita (esimerkiksi polkuja), voi olla
mielekästä tuoda OSM-kartta OOM-karttaan sellaisenaan. Tuotuun karttaan sovelletaan sellaisenaan `OSM-ISOM2017.crt`
-translaaatiotaulua.

### Maastotietokannan valmistelu ja tuonti

Useista Shapefileistä koostuva maastotietokanta (purettu zip:stä) yhdistetään yhdeksi GML-tiedostoksi:

```
> ogrmerge -o MML\M4211R.gml MML\M4211R.shp\*.shp
```

... ja rajataan:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_mtk.gml MML\M4211R.gml
```

Lopputuloksena syntyvä `Kaitajarvi_mtk.gml` tuodaan OOM -karttaan. Maastotietokannan symbolit muutetaan OMAP -symboleiksi
lataamalla `MTK-ISOM2017.crt` -tiedosto. Hyödyttömiä symboleita voi tässä vaiheessa poistaa tai piilottaa.

### Laserpistepilven valmistelu ja tuonti

Jos pistepilvitiedostoja on useita, yhdistetään ne:

```
> pdal merge MML\M4211E4.laz MML\M4211F3.laz MML\M4211E4+F3.laz
```

Kartan korkeuskuvauksen kannalta vain maanpintaa kuvaavat "ground", eli "class 2" -pisteet
tarvitaan. Muut, esimerkiksi kasvillisuutta tai vesistöjä kuvaavat pisteet suodatetaan pois:

```
> pdal translate -i MML\M4211E4+F3.laz -o MML\M4211E4+F3_ground.laz ^
			-f range --filters.range.limits="Classification[2:2]"
```

Pistepilviaineiston rajaaminen kattamaan vain tarvittava alue edellyttää rajausta 
*WKT* (Well Known Text) -muodossa:

```
> ogrinfo rajaus.shp rajaus -fid 0 -q -nomd | findstr POLYGON > rajaus.wkt
> set /p rajaus=<rajaus.wkt
```
(Rajauksen pitää olla alle 1024 merkkiä! Rajaukseen käytetyn tason nimi on tässä `rajaus`. Nimi on johdettu *Shapefile* tiedoston nimestä.)
 
Tämän jälkeen tarvittava materiaali voidaan rajata:

```
> pdal translate -i MML\M4211E4+F3_ground.laz -o MML\Kaitajarvi_ground.laz ^
			-f crop --filters.crop.polygon="%rajaus%"
```
(pdal ei salli skandimerkistön käyttöä tiedoston nimissä!)

Seuraavaksi rajausta, maanpitaa kuvaavasta pistepilvestä tehdään *DTM* (Digital Terrain Model):

```
> pdal translate -i MML\Kaitajarvi_ground.laz -o MML\Kaitajarvi_dem.tif ^
			-w gdal --writers.gdal.resolution=0.2 --writers.gdal.radius=3 ^
			--writers.gdal.window_size=1 --writers.gdal.output_type="idw"
```
(Digital Elevation Model, DEM on yleisnimi erilaisille pintamalleille. Maanpinnan pinnanmuotoja
kuvaava DTM on eräs DEM:n muoto.)

> [!TIP]
> MML:n uudella 5p/m<sup>2</sup> -materiaalilla voi olla mielekästä tehdä kaksi DEM-mallia: toinen kartalle
> tulevien käyrien piirtämiseen (kts. ohjeet jatkossa), jolloin resoluutio voi olla kenties hieman
> karkeampi, esim. 0.5 ... 1.0 (muiden parametrien säilyessä ennallaan). Toista mallia käytetään
> pohja-aineistona esim. kivien ja jyrkänteiden tunnistamiseen. Tällöin resoluutio voi olla 0.2,
> radius 1.0 ja window_size=0 (ei välttämättä pyritä yhtenäiseen viivaan). Tarkka käyrästö vie paljon tilaa,
> joten voi olla mielekästä muuttaa se OOM:llä jpg-muotoon.
>
> Tarkemmasta DEM-mallista voi tuottaa myös rinnevarjostuskuvan:
> ```
> > gdaldem dem.tif hillshade.jpg -co worldfile=yes
> ```
> ja niin ikään hyödyllisen TRI (Terrain Roughiness Index) -kuvan:
> ```
> > gdaldem TRI dem.tif tri.tif -co worldfile=yes
> ```
>
> Em. tri.tif ei ole nykyisellään luettavissa OOM:ään. Asian voi korjata konvertoimalla tiedoston
> jpg-muotoon esim. ilmaisella Paint.Net -ohjelmalla.

Lopuksi muutetaan lopputulos käyräviivaksi (puolen metrin käyrävälein):

```
> gdal_contour -i 0.5 -a "elev" MML\Kaitajarvi_dem.tif Kaitajarvi_contours05.shp
```

Syntynyt `Kaitajarvi_contours05.shp` sisältää korkeuskäyrät puolen metrin käyrävälillä.

Seuraavaksi onkin päätettävä kartassa käytettävä käyräväli ja johtokäyrien tasot. Komennolla:

```
> python contours.py -info MML\Kaitajarvi_contours05.shp
```

... saat yhteenvedon korkeusvaihtelusta ja taulukon, jossa on kuvattu miten monta käyräsymbolia milläkin korkeustasolla esiintyy:

```
Elevation range: 107.50 - 155.00m:
        Elevation | count
        -----------------------
        107.50m   |    3
        108.75m   |    2
        ...
        ...
        150.00m   |   17
        151.25m   |   21
        152.50m   |    9
        153.75m   |    4
        155.00m   |    1
```

Esimerkiksi tässä tapauksessa alueen korkeus vaihtelee välillä 107,5 - 155m ja on siis 47,5m. Jos (ja kun) käyräväliksi
valitaan viisi metriä, johtokäyrätasoja mahtuu vaihteluvälille kaksi (koska joka viides korkeuskäyrä on johtokäyrä), 
ylemmän ollessa esimerkiksi tasolla 145m. ISOM 2017 suosittelee johtokäyrätason valinnaksi "*merkittävimpien rinteiden
keskitason*".

Nyt, kun tiedetään käyräväli (5m) ja vähintään yksi käytetettävä johtokäyrän korkeustaso (145m), voidaan tehdä käyrien luokittelu:

```
> python contours.py -tag 145 5 MML\Kaitajarvi_contours05.shp Kaitajarvi_contours05.gml
```

Lopputulos `Kaitajarvi_contours05.gml` voidaan lisätä OOM -karttaan "Tuo" -toiminnolla. Tuodut käyräsymbolit muutetaan
OMAP -symboleiksi lataamalla `MTK-ISOM2017.crt` -tiedosto. Lopullisesta kartasta pois jäävät kartoituksen avuksi tarkoitetut
tukikäyrät esitetään purppuralla oletussymbolilla, mutta niitä varten kannattaa käsin tehdä esim. 0,03mm leveä tumman vihreä
käyräsymboli. Kokonaan niitä ei kannata poistaa, sillä tukikäyrät ovat mm. maastossa hyvin tarpeellisia.

![OOM](images/OOM.png)

... ja koko kartta edellä kuvattujen mekaanisten vaiheiden jäljiltä:
[Kaitajarvi](https://github.com/jjojala/mapping/raw/master/images/Kaitajarvi_raw.pdf)

## Entä sitten?

Ennen maastoon ryntäämistä voi, ja kannattaa pohja-aineiston kanssa vähän jumpata, esimerkiksi:

* OSM -pohjista kannattaa tarkistaa mahdollisia kartalle kuvattavia kohteita. OSM-pohjissa on erityisesti taajamien liepeillä
  MTK:ta kattavampaa tietoa esimerkiksi poluista.
* Ortoilmakuvia kannattaa verrata kiinteistörajoihin. Jos ilmakuvasta näkyy hakkuu, joka näyttäisi rajautuvan kiinteistörajaan,
  kyseessä on melkoisella varmuudella myös maastossa selvästi erottuva kuvioraja. Ilmakuvista voi näkyä myös muita
  MTK-materiaalista puuttuvia kohteita.
* Myös MapAnt -karttaa kannattaa verrata kiinteistörajoihin. Jos MapAnt -kartassa aukko tai tiheikkö rajautuu kiinteistörajaan,
  kyseessä todennäköisesti on maastossa selvästi erottuva kuvioraja - erityisesti jos sama raja erottuu vielä ortoilmakuvassakin.
* Taajama- ja esimerkiksi mökkialueilla kiinteistörajojen perusteella voi kuvata tonttivihreät. Tässä on tosin huomattava, että
  isoilla, metsäisillä tonteilla koko tontti ei ole välttämättä kiellettyä aluetta.
* Korkeuskäyriä voi trimmailla melkein loputtomiin. Useimmat laserpohjista otetut käyrän mutkat eivät erotu maastossa, joten
  yleensä on aika turvallista pelkistää ja suoristaa käyräviivoja jo ennen maastotyötä - tosin maastossa käynnin jälkeen
  voi tulla yllätyksiäkin ja joskus jonkun muodon korostaminen maastokäynnin jälkeen tuntuu ilmeiseltä.

On myös muita avoimia materiaaleja:
* Esimerkiksi [Bing Aerial](https://www.bing.com/maps/aerial), [Google Maps](https://www.google.com/maps/) -ilmakuvista
  voi toisinaan näkyä jotakin sellaista, joka ei MML:n ortoilmakuvista irtoa. Kaikista palveluista kuvia ei saa georeferoituna,
  joten kohteiden todellisen sijainnin kanssa kannattaa olla tarkkana. Toisinaan kuvat voivat olla myös huomattavan vanhoja.
  Myös esimerkiksi kunnilta saattaa saada alueesta ilmakuvia.
* [Google Street View:n](https://mapstreetview.com/) avulla voit tsekkailla tien reunat
  ([esimerkki](https://github.com/jjojala/mapping/raw/master/images/GoogleStreetView.png)
  ja sama [livenä](https://mapstreetview.com/#10ksus_e4fmr_3n.a_0g42))
* Kuntien kaavakartat.
* [Vanhat painetut kartat](http://vanhatpainetutkartat.maanmittauslaitos.fi/) -palvelusta kannattaa kaivaa vanhoja karttoja.
  Vanhat kartat eivät ole georeferoituja ja niissä on (ennen vuotta 2003) myös eri projektio. Tästä syystä ne kannattaa
  asemoida aina kulloinkin käsiteltävän alueen perusteella paikalleen ennen käyttöä. Kun asemoinnin tekee huolella,
  vanhoista kartoista irtoaa yllättävän hyvää tietoa. Esimerkiksi nykyisin maastossa kuviorajoina erottuvat jo vuosia sitten
  paketoitujen peltojen reunat saa kätevästi poimittua vanhoista kartoista.
* [Strava Global Heatmap](https://www.strava.com/heatmap) -palvelusta voi nähdä Strava -käyttäjien yleisimmin käyttämiä
  GPS-jälkiä. Jäljistä on mahdollista piirtää esimerkiksi yleisesti käytetyt ulkoilureitit.
* Metsäkeskuksen metsänkäyttöilmoitukset. Kannattaa tutustua jo ennalta: [Metsäkeskuksen karttapalvelut](https://www.metsaan.fi/karttapalvelut) ja [Metsänkäyttöilmoitukset](https://www.arcgis.com/apps/MapSeries/index.html?appid=e8c03f73165b44aa8edb276e11ca2d2c)
* Aiemmat suunnistuskartat, luonnollisesti.

Työpöydän ääressä valmisteltu kartta voi näyttää esimerkiksi 
[tältä](https://github.com/jjojala/mapping/raw/master/images/Kaitajarvi.pdf). 
Sitten vaan maastoon tarkistamaan pohjatyön tulosta, korjaamaan ja täydentämään...

(Vertailun vuoksi kartta vuodelta 1993 löytyy [täältä](https://github.com/jjojala/mapping/raw/master/images/Kaitajarvi_1993.png),
Copyright 1993 (C) Tampereen Yritys).
