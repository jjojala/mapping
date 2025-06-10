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

## Valmistelut

Tehdään kansio projektille haluttuun paikkaan, esim. `Documents\Kaitajarvi` ja sen alle seuraavat kansiot:
```
Documents\
	+ Kaitajarvi\
		+ tmp\		-- tänne tuodaan tilapäistiedostot
		+ field\	-- tänne luodaan karttatiedosto ja tuodaan kaikki kartanteon
				-- aikana tallennettavat, pysyvät tiedostot
```

Kun valmistelu on valmis, voi `tmp` -kansion halutessaan poistaa.

### Alueen rajaus

Aloitetaan alueen rajaamisella. Se onnistuu esimerkiksi 
[geojson.io](https://geojson.io/) -palvelussa. Käyttääksesi palvelua et tarvitse 
käyttäjätunnusta.

Valitse karttanäkymän oikeasta laidasta *Draw a polygon* -työkalu ja rajaa sillä kartoitettava 
alue. Tallenna alue *Shapefile* (ESRi Shapefile) -muodossa valikon *Save->Shapefile* 
-toiminnolla.

![geojson.net](images/geojsonio.png)

Pura ladattu tiedosto esimerkiksi tekemääsi hakemistoon `tmp`.

geojson.net -palvelu käyttää WGS-84, eli EPSG:4326 -koordinaattijärjestelmää. Sen sijaan maanmittauslaitos käyttää
kaikissa aineistoissaa ETRS-TM35FIN, eli EPSG:3067 -koordinaattijärjestelmää. Jäljempänä oletetaan, että rajaus
annetaan ETRS-TM35FIN -muodossa, joten rajaus on tarpeen muuttaa ETRS-TM35FIN -muotoon.

Käynnistä OSGeo4W Shell (komentotulkki) esimerkiksi Windows:n *Start* -valikon kautta ja muuta aluerajaus MML:n käyttämään koordinaatistoon
(alla, ja jatkossa oletus on, että komennot suoritetaan kansiossa `Documents\Kaitajarvi`):

```
> ogr2ogr -t_srs EPSG:3067 field\rajaus.gpkg tmp\layers\POLYGON.shp -nln rajaus
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

Valitse noudettavan materiaalin tyyppi yksi kerraallaan ja klikkaa sen jälkeen haluamaasi aluetta.
Lista noudettavasta materiaalista muodostuu oikeaan reunaan. Noudettavia materiaaleja ovat:
* orto- ja vääräväri-kuvat (JP2000 -formaatti)
* laserkeilaus-, eli pistepilviaineisto (mielellään stereomalliluokiteltu, laz-formaatti)
* Maastotietokanta, kaikki kohteet (GeoPackage, gpkg -muoto)
* kiinteistörekisterikartta, vektori, kaikki kohteet (GeoPackage)

![MML](images/MML.png)

Tee lataustilaus ja odota, että saat sähköpostiisi latauslinkin. Lataa aineistot ja kopioi ne esimerkiksi tekemääsi
hakemistoon `tmp`. Pura zip -paketit. *Huom!* Orto- ja väärävärikuvat ovat saman nimisiä, joten tallenna ne omiin 
alahakemistoihinsa `tmp\orto\` ja `tmp\vaaravari`.

### MapAnt

Hae MapAnt -kartta palvelusta https://www.mapant.fi/. Tuonti käynnistetään *Export* -toiminnolla, jonka jälkeen 
hiirellä rajataan kartalta noudettava suorakaiteenmuotoinen alue. Käytä tuonnissa tarkinta mahdollista lähennystasoa
(vaihtelee tuotavan alueen koon mukaan) ja muotona georeferoitua PNG:tä (Format="Georeferenced PNG"):

![MapAnt](images/mapant.png)

Pura ladattu zip-tiedosto `tmp` -kansioon.

### OpenStreetMap (OSM)

OSM -palvelu löytyy osoitteesta https://openstreetmap.org/. Aineiston voi rajata ja tuoda karttanäkymästä *Export* -toiminnolla.
Kopioi ladattu `map.osm` hakemistoon `tmp`.

![OSM](images/OSM.png)

## Aineiston valmistelu

### MapAnt -kartan valmistelu

Rajataan kartoitettava alue:

```
> gdalwarp -cutline field\rajaus.gpkg -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
            -co COMPRESS=JPEG tmp\MapAnt.png field\MapAnt.tif
```

Tässä vaiheessa on luontevaa luoda OOM -kartta ja tuoda sinne edellä synnytetty `field\MapAnt.tif` taustakartaksi
georeferointeineen ja erannon asetuksineen (kts. pikakartan valmistusohjetta). Maanmittauslaitos tuottaa Ilmatieteenlaitoksen erantomittausten pohjalta [erantokarttaa](https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/kartat/erantokartta), jonka mukaan eranto kannattaa OOM:ssä asettaa.

### Ortoilmakuvien valmistelu

Yhdistetään ja rajataan kuvat:

```
> gdalbuildvrt tmp\orto-merged.vrt tmp\orto\M4211E.jp2 tmp\orto\M4211F.jp2
> gdalwarp -cutline field\rajaus.gpkg -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
           -co compress=JPEG tmp\orto-merged.vrt field\Orto.tif
```
> [!TIP]
> Pieniä rasteritiedostoja voi yhdistää myös komennolla `gdalwarp`:
> ```
> > gdalwarp tmp\orto\M4211E.jp2 tmp\orto\M4211F.jp2 tmp\orto-merged.tif
> ```

Tässä vaiheessa on jälleen hyvä avata syntynyt `field\Orto.tif` luotavan kartan taustakartaksi.

### Kiinteistörajojen valmistelu ja tuonti

Rajataan kiinteistörajat:

```
> ogr2ogr -clipsrc field\rajaus.gpkg field\Kiinteistorajat.gpkg ^
	tmp\kiinteistorekisterikartta.gpkg KiinteistorajanSijaintitiedot
```

Lopputuloksena syntyvä `field\Kiinteistorajat.gpkg` voidaan tuoda _taustakarttana_ OMAP-karttaan.

### OpenStreetMap -kartan valmistelu ja tuonti

OSM -kartta ei käytä MML:n käyttämää koordinaattijärjestelmää, joten se pitää muuttaa samalla kun rajataan alue:

```
> ogr2ogr -t_srs EPSG:3067 -clipsrc field\rajaus.gpkg field\OSM.gpkg tmp\map.osm
```

Lopputuloksenä syntyvä `Osm.gpkg` on yleensä mielekästä avata taustakarttana. Tällöin taustakartan
avaulla piirretään taustakartan halutut kohteet myös OOM-karttaan.

Jos OSM-kartta sisältää huomattavan paljon kartalle sellaisenaan tuotavia kohteita (esimerkiksi polkuja), voi olla
mielekästä tuoda OSM-kartta OOM-karttaan sellaisenaan. Tuotuun karttaan sovelletaan sellaisenaan `OSM-ISOM2017.crt`
-translaaatiotaulua.

### Maastotietokannan valmistelu ja tuonti

Rajataan maastotietokanta:

```
> ogr2ogr -clipsrc field\rajaus.gpkg tmp\mtk_rajattu.gpkg tmp\maastotietokanta_kaikki.gpkg
```

Lopputuloksena syntyvä `tmp\mtk_rajattu.gpkg` tuodaan OOM -karttaan. Maastotietokannan symbolit muutetaan OMAP -symboleiksi
lataamalla `MTK-ISOM2017.crt` -tiedosto. Hyödyttömiä symboleita voi tässä vaiheessa poistaa tai piilottaa.

> [!TIP]
> Käytännössä voi myös käyttää OMAP:n "Etsi ..." -toimintoa ja hakea symbolityyppi kerrallaan kaikki tässä vaiheessa purppuralla
> kuvatut lopulliseen karttaan halutut objektit ja muuttaa ne OOM:n "Vaihda symbolia" -toiminnolla halutuksi suunnistuskarta symboliksi.
> Vaikka erilaisia symboleja on varsin paljon, on työ silti varsin kohtuullinen (ehkä kehitän tähän jossain kohtaa jotakin...).

### Laserpistepilven valmistelu ja tuonti

Jos pistepilvitiedostoja on useita, yhdistetään ne:

```
> pdal merge tmp\M4211E4.laz tmp\M4211F3.laz tmp\merged.laz
```

Kartan korkeuskuvauksen kannalta vain maanpintaa kuvaavat "ground", eli "class 2" -pisteet
tarvitaan. Muut, esimerkiksi kasvillisuutta tai vesistöjä kuvaavat pisteet suodatetaan pois:

```
> pdal translate -i tmp\merged.laz -o tmp\merged_ground.laz ^
			-f range --filters.range.limits="Classification[2:2]"
```

Pistepilviaineiston rajaaminen kattamaan vain tarvittava alue edellyttää rajausta 
*WKT* (Well Known Text) -muodossa:

```
> ogrinfo field\rajaus.gpkg rajaus -q -nomd | findstr POLYGON > tmp\rajaus.wkt
> set /p rajaus=<tmp\rajaus.wkt
```
(Rajauksen pitää olla alle 1024 merkkiä! Rajaukseen käytetyn tason nimi on tässä `rajaus`. Nimi on johdettu *Shapefile* tiedoston nimestä.)
 
Tämän jälkeen tarvittava materiaali voidaan rajata:

```
> pdal translate -i tmp\merged_ground.laz -o tmp\ground.laz ^
			-f crop --filters.crop.polygon="%rajaus%"
```
(pdal ei salli skandimerkistön käyttöä tiedoston nimissä!)

Seuraavaksi rajausta, maanpitaa kuvaavasta pistepilvestä tehdään *DEM* (Digital Elevation Model):

```
> pdal translate -i tmp\ground.laz -o tmp\dem.tif ^
			-w gdal --writers.gdal.resolution=0.2 --writers.gdal.radius=3 ^
			--writers.gdal.window_size=1 --writers.gdal.output_type="idw"
```

Lopuksi DEM muutetaan käyräviivaksi (puolen metrin käyrävälein):

```
> gdal_contour -i 0.5 -a "elev" tmp\dem.tif tmp\contours05.gpkg
```

> [!TIP]
> MML:n uudella 5p/m<sup>2</sup> -materiaalilla voi olla mielekästä tehdä kaksi DEM-mallia: toinen kartalle
> tulevien käyrien kuvaamiseen (kts. ohjeet jatkossa) ja toinen pohja-aineistoksi maastotyössä, esim. kivien,
> jyrkänteiden ja pienten maaston muotojen kuvaamiseen.
>
> Käyrien kuvaamiseen karkeampi:
> ```
> > pdal translate -i tmp\ground.laz -o tmp\dem.tif ^
>			  -w gdal --writers.gdal.resolution=1.0 --writers.gdal.radius=3.0 ^
> 			  --writers.gdal.window_size=1 --writers.gdal.output_type="idw"
> ```
>
> Pohja-aineistoksi tarkempi:
> ```
> > pdal translate -i tmp\ground.laz -o tmp\dem_dense.tif ^
> 			  -w gdal --writers.gdal.resolution=0.2 --writers.gdal.radius=1.0 ^
>			  --writers.gdal.window_size=0 --writers.gdal.output_type="idw"
> > gdal_contour -i 0.5 -a "elev" tmp\dem_dense.tif tmp\contours05_dense.gpkg
> ```
> 
> Varsinkin MML:n tarkemmalla laseraineistolla voi kannattaa tehdä myös käyristä tarkempi
> kuvatiedosto, jota on helpompi käyttää tausta-aineistona:
> ```
> > gdal_rasterize -a "elev" -tr 0.5 0.5  -ot Byte tmp\contours05_dense.gpkg ^
> 			  field\Contours05_dense.tif -co compress=JPEG
> ```
> Rasteroitu kuva kannattaa jälkikäsitellä, esim. ilmaisella Paint.NET -ohjelmalla seuraavasti:
> 1. Käyttäen "Magic Wand" -työkalua, valitse Shift -nappi pohjassa kuva-alueen ulkopuolinen musta piste (kohta, jossa ei ole käyräinformaatiota)
> 2. Poista ko. tieto "Del" -napilla (näistä alueista tulee läpinäkyviä), jäljelle jää vain käyrät
> 3. Muuta käyrien väri yhdeksi väriksi: "Adustments" -> "Levels" ja säädetään molempiin "Input" -kenttiin arvo 255.
> 4. Tallenna formaatissa, joka tukee Alpha -kanavia (läpinäkyviä alueita), esim. alkuperäinen TIF (JPEG), jossa samalla säilyy myös georeferointi .
>
>
> DEM-mallista voi tuottaa myös rinnevarjostuskuvan (multidirectional - varjostus useasta suunnasta):
> ```
> > gdaldem hillshade tmp\dem_dense.tif field\Hillshade.tif -multidirectional -co compress=JPEG
> ```
> 
> ja niin ikään hyödyllisen TRI (Terrain Roughiness Index) -kuvan:
> ```
> > gdaldem TRI tmp\dem_dense.tif tmp\tri-data.tif -co compress=DEFLATE -co predictor=2
> > gdal_translate -scale 0 0.4 -ot Byte tmp\tri-data.tif field\Tri.tif -co compress=JPEG
> ```

Syntynyt `tmp\contours05.gpkg` sisältää korkeuskäyrät puolen metrin käyrävälillä.

Lopputulos `tmp\contours05.gpkg` voidaan lisätä OOM -karttaan "Tuo" -toiminnolla. Tuonnin jälkeen OOM:n "Tag Editor" -ikkunassa
näkee kulloinkin valittuna olevan, tässä vaiheessa purppuralla viivalla kuvatun käyrän korkeuden merenpinnasta "elev" -attribuutissa.

Tämän jälkeen:
* Päätetään johtokäyrien taso. Kuvausohjeen mukaan johtokäyrä -symbolilla tulee kuvata korkeuskäyrä _"merkittävien rinteiden puolestavälistä"_.
* Valitaan johtokäyriksi muutettavat symbolit "Etsi..." -ikkunassa hakemalla symboleita, joissa attribuutti "elev" on valittu korkeustaso ("Etsi kaikki"). Kun ko. symbolit on valittuna, valitaan symboli-ikkunasta haluttu symboli ja painetaan "vaihda symboli" -nappia.
* ... toistetaan kaikille johtokäyrä, korkeuskäyrä ja apukäyrä -tasoille

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
* Metsäkeskuksen metsänkäyttöilmoitukset. Kannattaa tutustua jo ennalta: [Metsäkeskuksen karttapalvelut](https://www.metsaan.fi/karttapalvelut) ja [Metsänkäyttöilmoitukset](https://metsakeskus.maps.arcgis.com/apps/MapSeries/index.html?appid=e8c03f73165b44aa8edb276e11ca2d2c)
* Aiemmat suunnistuskartat, luonnollisesti.

Työpöydän ääressä valmisteltu kartta voi näyttää esimerkiksi 
[tältä](https://github.com/jjojala/mapping/raw/master/images/Kaitajarvi.pdf). 
Sitten vaan maastoon tarkistamaan pohjatyön tulosta, korjaamaan ja täydentämään...

(Vertailun vuoksi kartta vuodelta 1993 löytyy [täältä](https://github.com/jjojala/mapping/raw/master/images/Kaitajarvi_1993.png),
Copyright 1993 (C) Tampereen Yritys).
