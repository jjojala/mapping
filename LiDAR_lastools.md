# Pistepilviaineiston käsittely LAStools:lla

## Laserkeilausaineiston yhdistäminen

Aineistojen yhdistäminen on erityisesti tarpeen, jos siitä aiotaan tehdä käyrämuotoista. Yhdistämisen myötä käyriin
ei synny erillisten aineistojen rajoille katkoa. Yhdistäminen tapahtuu `las2las` -komennolla:

```
> las2las.exe -i MML\M4211E4.laz MML\M4211F3.laz -merged -keep_class 2 -o MML\M4211E4+F3_ground.laz
```

Option `-i` jälkeen voidaan luetella syötteen tiedostot. Optio `-merged` kertoo, että tiedostot on tarkoitus yhdistää.
Optiolla `-keep_class 2` ilmaistaan, että lopputulokseen poimitaan vain maanpinnaksi (ground, luokka 2) luokitellut
pisteet. Lopuksi optiolla `-o` kerrotaan, että yhdistämisen lopputulos kirjoitetaan tiedostoon `MML\M4211E4+F3_ground.laz`.

## Laserkeilausaineiston leikkaaminen alueella

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

## Laserkeilausaineiston yksinkertaistaminen

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

## Laserkeilausaineiston muuttaminen käyräviivaksi

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
