# GymSplit

## Sovelluksen toiminnot
- Käyttäjä pystyy luomaan tunnuksen ja kirjautumaan sisään sovellukseen.
- Käyttäjä pystyy lisäämään, muokkaamaan ja poistamaan treeniohjelmia.
- Käyttäjä näkee omat ja muiden lisäämät treeniohjelmat.
- Käyttäjä pystyy valitsemaan treeniohjelmalle luokittelun.
- Käyttäjä pystyy arvioimaan treeniohjelmia.
- Käyttäjä pystyy etsimään treeniohjelmia luokittelun perusteella.
- Sovelluksessa on käyttäjäsivut, jotka näyttävät tilastoja ja käyttäjän lisäämät treeniohjelmat, lähetetyt arvostelut.

## Suuren tietomäärän käsittely
Sovellukseen lisätyn sivutuksen ja tietokantaan lisätyn indeksin takia, suurien tietomäärien käsittely ei juurikaan hidasta sovellusta.

Seuraavat testit ovat toteutettu seed.py luomalla testidatalla, parametreillä:
- `user_count = 1000`
- `post_count = 10^5`
- `vote_count = 10^6`

elapsed time: 0.001 s
127.0.0.1 - - [02/May/2025 18:31:36] "GET /?offset=50&limit=10 HTTP/1.1" 200 -
elapsed time: 0.001 s
127.0.0.1 - - [02/May/2025 18:31:36] "GET /static/main.css HTTP/1.1" 200 -
elapsed time: 0.004 s
127.0.0.1 - - [02/May/2025 18:32:17] "GET /post/55 HTTP/1.1" 200 -
elapsed time: 0.0 s
127.0.0.1 - - [02/May/2025 18:32:17] "GET /static/main.css HTTP/1.1" 200 -

## Sovelluksen asennus

Asenna `flask`-kirjasto:

```
$ pip install flask
```

Luo tietokannan taulut ja lisää alkutiedot:

```
$ sqlite3 database.db < schema.sql
$ sqlite3 database.db < init.sql
```

Voit käynnistää sovelluksen näin:

```
$ flask run
```