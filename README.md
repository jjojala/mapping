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

### MapAnt

MapAnt -palvelusta (https://www.mapant.fi/) haetaan kartoitettavan alueen kattava karttapala
"Export" -toiminnolla (Zoom=9, Format="Georeferenced PNG")

## Aineiston alustava valmistelu

### Alueen rajaus

Kartoitettava alue rajataan palvelussa http://geojson.io/#map=2/20.0/0.0 Polygonina rajattu alue tallennetaan Shapefile -muodossa.
Pura ladattu tiedosto haluamaasi hakemistoon.

Käynnistä OSGeo4W -komentotulkki ja muuta aluerajaus MML:n käyttämään koordinaatistoon:

`ogr2ogr -t_srs EPSG:3067 rajaus.shp layers\POLYGON.shp`

