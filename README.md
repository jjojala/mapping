# Suunnistuskartan pohja-aineiston valmistelu avoimista aineistoista OOM:llä

## Ohjelmat

Kaikki käytetyt ohjelmat ovat ilmaisia. Käyttöympäristönä on Windows.

* _OpenOrienteering Mapper_, eli kotoisasti "OOM" (https://www.openorienteering.org/)
* OSGeo4W (https://trac.osgeo.org/osgeo4w/) on Windows -ympäristöön koottu ohjelmistokokonaisuus kartta-aineiston käsittelyyn
  * oikeasti paketista tarvitaan vain Python ja GDAL, mutta paketin mukana tulee _paljon_ muutakin mahdollisesti myöhemmin käyttökelpoista
* LASTools (https://rapidlasso.com/)
  * Käytettävä ilmaisversio mm. aiheuttaa pientä poikkeamaa laserpistepilven koordinaatteihin. Se on tästä huolimatta 
  riittävän tarkka tässä esitettyyn käyttötarkoitukseen.

## Aineistot

Tarvittavat avoimet aineistot saadaan seuraavista palveluista:
* Maanmittauslaitoksen (MML) _avoimien aineistojen tiedostopalvelu_ (https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta)
* MapAnt (https://mapant.fi/)
* OpenStreetMap (hptts://www.openstreetmap.org/)

Lisäksi kartoitettava alue rajataan palvelulla geojson.io (https://geojson.io/)

### Maanmittauslaitoksen (MML) avoimet aineistot

Aineistot voit ladata MML:n _avoimien aineistojen tiedostopalvelusta_:
  https://tiedostopalvelu.maanmittauslaitos.fi/tp/kartta

MML:n tiedostpalvelusta noudettavat materiaalit:
* JPG2000 -muotoiset ortoilmakuvat
* laserkeilaus-, eli pistepilviaineisto (mielellään stereomalliluokiteltu)
* kiinteistörekisterikartta, vektori, kaikki kohteet

Kopioi ladatut aineistot esimerkiksi hakemistoon `MML`. Pura zip -paketit vastaavan nimiseen hakemistoon,
esim. `MML\M4211R.shp.zip` --> `MML\M4211R.shp`

### MapAnt

MapAnt -palvelusta (https://www.mapant.fi/) haetaan kartoitettavan alueen kattava karttapala
"Export" -toiminnolla (Zoom=9, Format="Georeferenced PNG"). 

## Aineiston alustava valmistelu

### Alueen rajaus

Kartoitettava alue rajataan palvelussa http://geojson.io/#map=2/20.0/0.0 Polygonina raj ttu alue tallennetaan Shapefile -muodossa.
Pura ladattu tiedosto esimerkiksi hakemistoon `geojson.io`.

Käynnistä OSGeo4W -komentotulkki ja muuta aluerajaus MML:n käyttämään koordinaatistoon:

`> ogr2ogr -t_srs EPSG:3067 rajaus.shp geojson.io\layers\POLYGON.shp`

### MapAnt -kartan valmistelu

Pura palvelusta tuotu MapAnt.zip esimerkiksi hakemistoon `MapAnt` ja rajaa siitä tarvitsemasi osa:

`> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 -co COMPRESS=JPEG -co WORLDFILE=YES MapAnt\MapAnt.png Kaitajarvi_MapAnt.tif`

Tässä vaiheessa on luontevaa luoda OOM -kartta ja tuoda sinne edellä synnytetty `Kaitajarvi_MapAnt.tif` taustakartaksi
georeferointeineen ja karttapohjoisen asetuksineen (kts. pikakartan valmistusohjetta).

### Ortoilmakuvien valmistelu

Yhdistetään kuvat (jos useita):
`> gdalwarp MML\M4211E.jp2 MML\M4211F.jp2 MML\M4211E+F.tif`

... ja rajataan kartoitettavaan alueeseen (kuten MapAnt -kartta):

`> gdalwarp -cutline rajaus.shp -crop_to_cutline -dstalpha -s_srs EPSG:3067 -co COMPRESS=JPEG -co WORLDFILE=YES MML\M4211E+f.tif Kaitajarvi_Orto.tif`

Tässä vaiheessa on jälleen hyvä avata syntynyt `Kaitajarvi_Orto.tif` luotavan kartan taustakartaksi.

### Maastotietokannan valmistelu ja tuonti

Useista Shapefileistä koostuva maastotietokanta (purettu zip:stä) yhdistetään yhdeski GML-tiedostoksi:

`> ogrmerge -o MML\M4211R.gml MML\M4211R.shp\*.shp`

... ja rajataan:

`> ogr2ogr -clipsrc rajaus.shp Kaitajarvi_mtk.gml MML\M4211R.gml`

Lopputuloksena syntyvä `Kaitajarvi_mtk.gml` tuodaan OOM -karttaan. Maastotietokannan symbolit muutetaan OMAP -symboleiksi
lataamalla github.com/jjojala/mapping/MTK-ISOM2017.crt -tiedostoa. Hyödyttömiä symboleita voi tässä vaiheessa poistaa tai
piilotella.

### Laserpistepilven valmistelu ja tuonti

Jos pistepilvitiedostoja on useita, yhdistellään ne:

`> las2las.exe -i MML\M4211E4.laz MML\M4211F3.laz -merged -o MML\M4211E4+F3.laz`

... rajataan materiaali vain tarvittavaan alueeseen:

`> lasclip.exe -i MML\M4211E4+F3.laz -o MML\Kaitajarvi.laz -poly rajaus.shp -v`

... pelkistetään pistepilveä ja valitaan siihen vain "ground" (class 2) pisteet:

`> lasthin.exe -i MML\Kaitajarvi.laz -o MML\Kaitajarvi_thinned_class2.laz -keep_class 2`

... ja muutetaan lopputulos käyräviivaksi:

`> las2iso.exe -i MML\Kaitajarvi_thinned_class2.laz -o Kaitajarvi.shp -iso_every 0.5 -keep_class 2 -clean 8 -simplify 4 -smooth 5`

Lopuksi vähän magiaa:

`> python contours.py ...`
