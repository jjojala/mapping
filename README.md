# Suunnistuskartan pohja-aineiston valmistelu avoimista aineistoista OOM:lle

## Ohjelmat

Kaikki käytetyt ohjelmat ovat ilmaisia. Käyttöympäristönä on Windows.

* _OpenOrienteering Mapper_, eli kotoisasti "OOM" (https://www.openorienteering.org/)
* OSGeo4W (https://trac.osgeo.org/osgeo4w/) on Windows -ympäristöön koottu ohjelmistokokonaisuus kartta-aineiston käsittelyyn
  * oikeasti paketista tarvitaan vain Python ja GDAL, mutta paketin mukana tulee paljon, paljon muutakin mahdollisesti myöhemmin
    käyttökelpoista ohjelmistoa
* LASTools (https://rapidlasso.com/)
  * Käytettävä ilmaisversio mm. aiheuttaa pientä poikkeamaa laserpistepilven koordinaatteihin. Se on tästä huolimatta 
  riittävän tarkka tässä esitettyyn käyttötarkoitukseen. LAStools tulee jossakin muodossa myös OSGeo4W:n mukana, mutta
  ainakaan tätä kirjoitettaessa se ei toiminut odotetusti.
  
Lisäksi tarvitset MML:n MTK --> ISOM2017 -translaatiotaulukon
([MTK-ISOM2017.crt](https://github.com/jjojala/mapping/raw/master/MTK-ISOM2017.crt)) ja LASTools:n jäljiltä käyrät sisältävän
Shapefile:n rikastamiseen ja käyrien luokitteluun tarkoitetun skriptinpätkän
([contours.py](https://github.com/jjojala/mapping/raw/master/contours.py)).

Translaatiotaulu on sovitettu MML:n maastotietokannan (MTK) ja OOM:n ISOM2017 -symbolisetin kanssa toimivaksi. OCAD ei
tietääkseni tue yhtä monipuolista translaatiomallia, eikä OCAD näin ollen voi suoraan niellä MTK:n kohteita yhtä kattavasti
kuin OOM. Toisaalta, kaikilta osin MTK ei ole suoraviivaisesti edes mäpättävissä suunnistuskartan symboleihin.

MML:n MTK:n symbolit, eli "kuvausohje" löytyy täältä:
https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/asiantuntevalle-kayttajalle/tuotekuvaukset/maastotietokanta-0

Laserkeilaus, eli LiDAR -aineistosta ("pistepilven") tuotettujen Käyrien rikastamiseen tarkoitettu `contours.py` perustuu (mm)
OSGeo4W:n mukana tulevaan Python - ympäristöön terästettynä karttatiedon käsittelyyn tarkoitetulla kirjastolla (GDAL). Työkalu
luokittelee käyrät korkeustason mukaan korkeuskäyriin, johtokäyriin, apukäyriin ja korkeuskuvauksen tekemistä kuvaaviin
tukikäyriin ('UTIL').

## Aineistot

Tarvittavat avoimet aineistot saadaan seuraavista palveluista:
* Maanmittauslaitoksen (MML) _avoimien aineistojen tiedostopalvelu_ (https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta)
* MapAnt (https://mapant.fi/)
* OpenStreetMap (hptts://www.openstreetmap.org/)

Lisäksi kartoitettava alue rajataan palvelulla geojson.io (https://geojson.io/):

### Maanmittauslaitoksen (MML) avoimet aineistot

Aineistot voit ladata MML:n _avoimien aineistojen tiedostopalvelusta_:
  https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta

MML:n tiedostpalvelusta noudettavat materiaalit:
* JPEG2000 -muotoiset ortoilmakuvat
* laserkeilaus-, eli pistepilviaineisto (mielellään stereomalliluokiteltu)
* kiinteistörekisterikartta, vektori, kaikki kohteet

![MML](images/MML.png)

Kopioi ladatut aineistot esimerkiksi hakemistoon `MML`. Pura zip -paketit vastaavan nimiseen hakemistoon,
esim. `MML\M4211R.shp.zip` --> `MML\M4211R.shp`

### MapAnt

MapAnt -palvelusta (https://www.mapant.fi/) haetaan kartoitettavan alueen kattava karttapala
"Export" -toiminnolla (Zoom=9, Format="Georeferenced PNG"):

![MapAnt](images/mapant.png)

### OpenStreetMap (OSM)

OSM -palvelu löytyy osoitteesta https://openstreetmap.org/ Aineiston voi rajata ja tuoda karttanäkymästä "Export" -toiminnolla.
Kopioi ladattu `map.osm` hakemistoon `OSM`.

![OSM](images/OSM.png)

## Aineiston alustava valmistelu

### Alueen rajaus

Kartoitettava alue rajataan palvelussa http://geojson.io/#map=2/20.0/0.0 Polygonina raj ttu alue tallennetaan Shapefile -muodossa:

![geojson.io](images/geojsonio.png)

Pura ladattu tiedosto esimerkiksi hakemistoon `geojson.io`.

Käynnistä OSGeo4W -komentotulkki ja muuta aluerajaus MML:n käyttämään koordinaatistoon:

```
> ogr2ogr -t_srs EPSG:3067 rajaus.shp geojson.io\layers\POLYGON.shp
```

### MapAnt -kartan valmistelu

Pura palvelusta tuotu MapAnt.zip esimerkiksi hakemistoon `MapAnt` ja rajaa siitä tarvitsemasi osa:

```
> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
            -co COMPRESS=JPEG -co WORLDFILE=YES MapAnt\MapAnt.png Kaitajarvi_MapAnt.tif
```

Tässä vaiheessa on luontevaa luoda OOM -kartta ja tuoda sinne edellä synnytetty `Kaitajarvi_MapAnt.tif` taustakartaksi
georeferointeineen ja karttapohjoisen asetuksineen (kts. pikakartan valmistusohjetta).

### Ortoilmakuvien valmistelu

Yhdistetään kuvat (jos useita):

```
> gdalwarp MML\M4211E.jp2 MML\M4211F.jp2 MML\M4211E+F.tif
```

... ja rajataan kartoitettavaan alueeseen (kuten MapAnt -kartta):

```
> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 ^
            -co COMPRESS=JPEG -co WORLDFILE=YES MML\M4211E+f.tif Kaitajarvi_Orto.tif
```

Tässä vaiheessa on jälleen hyvä avata syntynyt `Kaitajarvi_Orto.tif` luotavan kartan taustakartaksi.

### Kiinteistörajojen valmistelu ja tuonti

Rajataan kiinteistötiedot:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_kiinteistorajat.gml MML\M4211E\M4211E_kiinteistoraja.shp
```

Lopputuloksena syntyvä `Kaitajarvi_kiinteistorajat.gml` voidaan tuoda _taustakarttana_ OMAP-karttaan.

### OpenStreetMap -kartan valmistelu ja tuonti

Rajataan materiaali alueellisesti:

```
> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_osm.gml OSM\map.osm
```

Lopputuloksenä syntyvä `Kaitajarvi_osm.gml` on yleensä mielekästä avata taustakarttana. Tällöin taustakartan
avaulla piirretään taustakartan halutut kohteet myös OOM-karttaan.

Jos OSM-kartta sisältää huomattavan paljon kartalle sellaisenaan tuotavia kohteita (esimerkiksi polkuja), voi olla
mielekästä tuoda OSM-kartta OOM-karttaan sellaisenaan. Tuotuun karttaan sovelletaan sellaisenaan `OSM-ISOM2017.crt`
-translaaatiotaulua.

### Maastotietokannan valmistelu ja tuonti

Useista Shapefileistä koostuva maastotietokanta (purettu zip:stä) yhdistetään yhdeski GML-tiedostoksi:

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

Jos pistepilvitiedostoja on useita, yhdistellään ne:

```
> las2las.exe -i MML\M4211E4.laz MML\M4211F3.laz -merged -o MML\M4211E4+F3.laz
```

... rajataan materiaali vain tarvittavaan alueeseen:

```
> lasclip.exe -i MML\M4211E4+F3.laz -o MML\Kaitajarvi.laz -poly rajaus.shp -v
```

... pelkistetään pistepilveä ja valitaan siihen vain "ground" (class 2) pisteet:

```
> lasthin.exe -i MML\Kaitajarvi.laz -o MML\Kaitajarvi_thinned_class2.laz -keep_class 2
```

... ja muutetaan lopputulos käyräviivaksi (puolen metrin käyrävälein):

```
> las2iso.exe -i MML\Kaitajarvi_thinned_class2.laz -o MML\Kaitajarvi_contours05.shp ^
               -iso_every 0.5 -keep_class 2 -clean 8 -simplify 4 -smooth 5
```

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
valitaan viisi metriä, johtokäyrätasoja mahtuu vaihteluvälille kaksi, ylemmän ollessa esimerkiksi tasolla 145m.

Nyt, kun tiedetään käyräväli (5m) ja vähintään yksi käytetettävä johtokäyrän korkeustaso (145m), voidaan tehdä käyrien luokittelu:

```
> python contours.py -tag 145 5 MML\Kaitajarvi_contours05.shp Kaitajarvi_contours05.gml
```

Lopputulos `Kaitajarvi_contours05.gml` voidaan lisätä OOM -karttaan "Tuo" -toiminnolla. Tuodut käyräsymbolit muutetaan
OMAP -symboleiksi lataamalla `MTK-ISOM2017.crt` -tiedosto. Lopullisesta kartasta pois jäävät kartoituksen avuksi tarkoitetut
tukikäyrät esitetään purppuralla oletussymbolilla, mutta niitä varten kannattaa käsin tehdä esim. 0,03mm leveä tumman vihreä
käyräsymboli. Kokonaan niitä ei kannata poistaa, sillä tukikäyrät ovat mm. maastossa hyvin tarpeellisia.

![OOM](images/OOM.png)

