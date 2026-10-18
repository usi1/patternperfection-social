# Pattern Perfection – weekly social content guide

This is the brief for the weekly scheduled task that creates the next week's Instagram + Facebook posts.
The style was approved by the owner on 2026-10-19 (see `weeks/2026-10-19.json` as the reference week).

## Brand
- Pattern Perfection sells **digital sewing patterns** (instant download): https://www.patternperfection.store/collections/all
- Products: Coat, Corset Dress, Dress, Hoodie, Lapel Skirt, Summer Dress, Summer Suit, Summer Bundle 5 in 1.
  Check the shop page each week before mentioning a product; only mention products that are listed.
- Sizes **XS–XL**, **US and UK** sizing standards. Detailed step-by-step instructions. Audience: beginners and up.
- Audience is English-speaking (UK + US). Write in **English** (British spelling is fine: "cosy", "colour").
- Tone: upbeat, encouraging, practical, direct. Short sentences. A few emojis, never more than one per line.
- Instagram handle: @pattern_perfection.
- Never invent discount codes, prices, reviews or statistics. Don't mention a discount code unless the owner confirms it.

## Weekly rotation (published 15:00 Europe/Rome)
| Day | Format | Series label | Content |
|---|---|---|---|
| Monday | carousel, exactly 5 slides | `Sewing basics` | cover + 3 numbered points + cta |
| Wednesday | single, 1 slide (`single_tip`) | `Fabric tip` | one practical fabric tip |
| Friday | carousel, exactly 5 slides | `Fit & sizing` | cover + 3 numbered points + cta, linked to XS–XL US/UK sizing |
| Sunday | single, 1 slide (`question`) | `Community` | a question that invites comments and connects to a product (e.g. Coat, Hoodie) |

Before choosing topics, read every file in `weeks/` and **never repeat a topic** already used.

## Spec format (`weeks/<monday-date>.json`)
Copy the structure of `weeks/2026-10-19.json` exactly. Per post: `date`, `format` (`carousel`|`single`), `series`,
`topic`, `slides`, `caption_ig`, `caption_fb`.

Slide types and fields:
- `cover`: `title` (≤ 9 words), `subtitle` (≤ 25 words), optional `icon`
- `point`: `number`, `title` (≤ 6 words), optional `icon`, `body` (≤ 40 words)
- `cta`: `title` (≤ 6 words), `body` (≤ 22 words), `button` (e.g. `patternperfection.store` or `Shop the patterns`)
- `single_tip`: `title` (≤ 9 words), optional `icon`, `body` (≤ 40 words)
- `question`: `title` (≤ 14 words), `body` (≤ 20 words), `prompt` (≤ 5 words, no arrow characters)

Icons available: `grainline`, `fold`, `notch`, `dart`, `grade`, `lengthen`, `dots`, `tape`, `wash`, `scissors`,
`hanger`, `size`, `question`. Only use these names; pick one that genuinely illustrates the point, or omit it.
Don't use emoji or special arrow characters inside slide text (the fonts can't render them); emojis are fine in captions.

## Captions
- `caption_ig`: hook line, 2–4 short paragraphs, a call to action (save / comment), then **at most 5 hashtags**
  on the last line. Max 2,200 characters. No links (Instagram doesn't make them clickable; say "link in bio").
- `caption_fb`: shorter, adapted (not identical) to Instagram, no hashtags or at most 2, and include the shop link
  https://www.patternperfection.store/collections/all when relevant.

## Build
```
python3 generator/render.py weeks/<monday>.json      # validates + renders posts/<date>/NN.jpg
python3 generator/records.py weeks/<monday>.json     # prints the Make data store records
```
Look at the rendered images before publishing: no text overlapping, nothing cut off, nothing touching the footer.
If something overflows, shorten the text and re-render.
