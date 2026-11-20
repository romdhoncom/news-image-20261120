[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/romdhoncom/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/romdhoncom/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# One Day on Earth — Friday 20 November 2026

A newspaper front page that sums up Friday 20 November 2026 in one image.
`main.py` (pure Python 3 standard library, no network, no clock, no
randomness) draws it in code — own raster, own 5x7 bitmap font, own PNG
encoder — and writes `entry.png` (1024x1024) to `$MAKEFUN_OUTPUT_DIR`
(default `/output`). Two runs produce byte-identical output.

## The six stories

1. **Kyiv bridges hit overnight** — Russian ballistic missiles damaged three
   bridges over the Dnipro; Mayor Klitschko reported fires across the capital.
2. **Asia markets rout** — worst week since 2020; Taiwan fell 16% in a week,
   its worst since 1991, as the AI trade unwound.
3. **GTA VI: $2.36bn day** — an estimated 24.6 million copies sold on launch
   day (Sensor Tower estimate; Take-Two has not confirmed figures).
4. **Sydney terror charge** — an Australian man charged with terrorism
   offences on Friday after a police raid in Sydney.
5. **Boat capsizes off Senegal: 4 dead** — at least 50 people were aboard the
   migrant boat near Yenne; the search goes on.
6. **13,000 rally in Tokyo** — crowds outside the National Diet protest
   plans to revise Japan's pacifist constitution.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
