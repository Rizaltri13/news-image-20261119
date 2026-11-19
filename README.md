# The World Today — Thursday 19 November 2026 in one image

[![make.fun](https://make.fun/badge/news-image-20261119.svg)](https://make.fun/bounty/news-image-20261119)
[![Rank](https://make.fun/badge/news-image-20261119/Rizaltri13/news-image-20261119/rank.svg)](https://make.fun/bounty/news-image-20261119)
[![Reward](https://make.fun/badge/news-image-20261119/Rizaltri13/news-image-20261119/reward.svg)](https://make.fun/bounty/news-image-20261119)

A make.fun bounty entry for
[news-image-20261119](https://make.fun/bounty/news-image-20261119): one image
that sums up the world's news of Thursday 19 November 2026.

## The program

`main.py` (Python 3, standard library only, no network) draws a 1024×1024
newspaper front page — masthead "THE WORLD TODAY", a red date band, a large
hero panel for the lead story, six illustrated story tiles, and a bottom
ticker of shorter items — and encodes it as a PNG with a hand-rolled encoder
(`zlib` + `struct`). Every letter comes from a small hand-typed 5×7 bitmap
font and every picture is drawn from code, so the output is fully
deterministic: two runs produce byte-identical files.

Run it with:

```sh
MAKEFUN_OUTPUT_DIR=out python3 main.py   # writes out/entry.png
```

## The day's stories

- **Lead — Trump, Xi and Putin meet in China.** The three leaders shake
  hands in Shenzhen at a regional summit; Xi hugged Trump on the tarmac on
  arrival, and a trilateral meeting is expected on Thursday.
  (Sources: BBC, NYT)
- **Crimean Bridge attacked again.** Russia says the bridge was attacked
  again, in reports on 19 November. (Source: BBC)
- **Anthropic IPO: $81.3bn, biggest ever.** The Claude-maker raises $81.3bn
  in the biggest IPO of all time, poised for a stock-market debut worth more
  than $1.4tn. (Sources: NYT, BBC)
- **Jeffries set to be first Black House Speaker.** Democrats nominate
  Hakeem Jeffries, set to become the first African-American Speaker of the
  US House. (Sources: NYT, BBC)
- **Voyager 1 hits one light-day.** After almost 50 years in space, NASA's
  Voyager 1 reaches a record one light-day from Earth. (Source: BBC)
- **GTA VI rollout begins.** Gamers enter Vice City as Grand Theft Auto VI
  begins its global rollout. (Source: BBC)
- **Israel ground operation in Gaza.** Israeli troops and tanks advance
  across the Gaza ceasefire line in a rare ground operation.
  (Source: Al Jazeera)
- **Ticker:** Van Gogh painting sells for a record $190.4m · Myanmar faces a
  historic genocide verdict at the UN court over the Rohingya · Cyclone Akvan
  nears India's east coast (Machilipatnam–Puri) · EU proposes a €45bn Ukraine
  loan · Estonia plans to close its border with Russia.
  (Sources: BBC, Al Jazeera, NDTV)
