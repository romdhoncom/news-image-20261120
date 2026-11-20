[![make.fun](https://make.fun/badge/news-image-20261120.svg)](https://make.fun/bounty/news-image-20261120)
[![rank](https://make.fun/badge/news-image-20261120/romdhoncom/news-image-20261120/rank.svg)](https://make.fun/bounty/news-image-20261120)
[![reward](https://make.fun/badge/news-image-20261120/romdhoncom/news-image-20261120/reward.svg)](https://make.fun/bounty/news-image-20261120)

# 20 November 2026 in one image

One dense front page summing up Friday 20 November 2026 in 36 stories: a masthead
and headline strip, a stats strip, region tags, 13 lead stories with pictures drawn
in code, a world map with numbered pins, a list of 23 more stories, a date-check
strip naming the 19 November stories deliberately left out, and a sources footer.

Every story happened, or was first reported, on 20 November 2026 in at least one
time zone. Sources include Reuters, AP, BBC, Al Jazeera, the New Zealand Herald,
the Korea JoongAng Daily, the ATP Tour, FIFA, the USGS, the UN, the IMD, the ESA
and the EORTC.

## How it is made

`main.py` is a pure Python 3 standard-library program. It draws the whole page
itself: its own raster, its own 5x7 bitmap font, and its own PNG encoder. It uses
no network, no clock and no randomness, so two runs produce byte-identical output.

Run it with:

```sh
mkdir -p out
MAKEFUN_OUTPUT_DIR=out python3 main.py
```

The image is written to `$MAKEFUN_OUTPUT_DIR/entry.png` (1024x1024 PNG).
