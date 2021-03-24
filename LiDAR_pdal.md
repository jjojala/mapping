# Pistepilviaineiston käsittely PDAL-ohjelmistolla

## Laserkeilausaineiston yhdistäminen

Aineistojen yhdistäminen on erityisesti tarpeen, jos siitä aiotaan tehdä käyrämuotoista. Yhdistämisen myötä käyriin
ei synny erillisten aineistojen rajoille katkoa. Yhdistäminen tapahtuu `las2las` -komennolla:

```
> pdal merge MML\M4211E4.laz MML\M4211F3.laz MML\M4211E4+F3.laz
```

## Laserkeilausaineiston leikkaaminen alueella

Kuten kartta-aineistossa, myös laserkeilausaineistossa haluamme yleensä keskittyä vain kartoitettavaa aluetta
kattavaan aineistoon. Rajaus onnistuu komennolla `lasclip`:

```
> ogrinfo rajaus.shp rajaus -fid 0 -q -nomd | findstr POLYGON > rajaus.wkt
> set /p rajaus=<rajaus.wkt
> pdal translate -i MML\M4211E4+F3_ground.laz -o MML\Kaitajarvi_ground.laz ^
			-f crop --filters.crop.polygon="%rajaus%"
```

## Laserkeilausaineiston yksinkertaistaminen

Yksinkertaistamista voidaan tehdä useilla eri tavoilla. Tässä käytetään "thin" -menetelmää, jossa aineiston kattama
alue jaetaan oletusarvoisesti neliömetrin kokoisiin ruutuihin. Kustakin ruudusta valitaan vain se piste, jonka
korkeus (Z-attribuutti) on alin. Jos siis neliömetrin kokoiselta alueelta on useita ruutuja, olemme kiinnostuneita
vain matalimmasta.

```
> pdal ...
```

Yksinkertaistamisen etuna on se, että lopputuloksesta suodattuu pois merkityksettömät pienet korkeusvaihtelut.
Suodatetusta aineistosta tuotettu korkeuskäyrä on siten siistimpi ja vastaa paremmin suunnistuskartan valmistuksen
tarpeita.

MML:n laserkeilausaineistolla yksinkertaistaminen ei tunnu vaikuttavan kovin merkittävästi lopputulokseen.
Seikka saattaa johtua siitä, että MML:n aineistossa pisteiden tiheys ei ole kovin suuri (keskimäärin 0,5
pistettä/m2, joista kaikki eivät ole maapisteitä).

## Laserkeilausaineiston muuttaminen käyräviivaksi

Pistepilviaineiston muuttaminen käyräviivaksi tapahtuu kahdessa vaiheessa:
1. Luodaan pistepilviaineistosta *digitaaliseksi maastomalliksi* (*DTM*).
2. Muutetaan digitaalinen maastomalli vektorimuotoiseksi käyrämalliksi.

Digitaalinen maastomalli *DTM* (*Digital Terrain Model*) kuvaa maanpinnan muodon
käytännössä GeoTIF -muotoisena "kuvana", jonka jokaiseen kuvapisteeseen liittyy
sijainti- ja korkeustieto.

```
> pdal translate -i MML\Kaitajarvi_ground.laz -o MML\Kaitajarvi_dem.tif ^
			-w gdal --writers.gdal.resolution=2.0 --writers.gdal.radius=10 ^
			--writers.gdal.window_size=1 --writers.gdal.output_type="idw"
```

Syöte- ja tulostiedostot kuvataan yleisillä `-i` ja `-o` -optioilla. 


```
> gdal_contour -i 0.5 -a "elev" MML\Kaitajarvi_dem.tif Kaitajarvi_contours05.shp
```
