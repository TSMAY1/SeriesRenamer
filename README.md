This code is intended to take the contents of a directory, and rename them by series name, season number, and episode number. 

The format should be the following: SeriesName - SXX - EXX

Example Directory 1:

Directory = "[Judas] SaiHito - S01E01v2", "[Judas] SaiHito - S01E02v2", "[Judas] SaiHito - S01E03v2", "[Judas] SaiHito - S01E04v2", "[Judas] SaiHito - S01E02v2"

Example Directory 2:

Directory = "Heated Rivalry S01E01", Heated Rivalry S01E02", Heated Rivalry S01E03", "Heated Rivalry S01E04", "Heated Rivalry S01E05"

Example Directory 3:

Directory = "The Great (2020) - S01E01 - The Great (1080p BluRay x265 Silence)", "The Great (2020) - S01E02 - The Beard (1080p BluRay x265 Silence)", "The Great (2020) - S01E03 - And You Sir, Are No Peter the Great (1080p BluRay x265 Silence)", "The Great (2020) - S01E04 - Moscow Mule (1080p BluRay x265 Silence)", "The Great (2020) - S01E05 - War and Vomit (1080p BluRay x265 Silence)" 

I'm thinking of using a mix of regex and indexing. I might need variations depending on the formatting of the initial list. Ideally I want to create something versatile that can be used in different situations.

Would it be better for my purposes to inclube an input asking me to type the Series Name? Since I might want to rename what it currently calls itself. It could potentially ask "Would you like to rename?" at the beginning of the function, and then do either option.

