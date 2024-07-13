# Intro
Based on [Jekyll](https://jekyllrb.com/)

# Run
`bundle exec jekyll serve`

# Sources
- `dc_Hollander.json` (IT/EN Text)
  - extracted from https://dante.princeton.edu/pdp
  - The English translation of the Comedy is a new translation by Robert Hollander and Jean Hollander. Inferno was published by Doubleday/Anchor in 2000, Purgatorio in 2003; Paradiso in 2007.
  - format:
    ```json
    {
        'hell':
            1: {
                'IT': {
                    1: 'line 1 IT canto 1',
                    2: ...,
                    136: ...,
                },
                'EN': {
                    1: 'line 1 EN canto 1',
                    2: ...,
                    136: ...,
                },
            },
            ...,
            34: {...}
        'purgatory': {
            1: {...},
            ...
            33: {...},
        },
        'paradise': {
            1: {...},
            ...
            33: {...},
        },
    }
    ```