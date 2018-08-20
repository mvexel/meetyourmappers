# Meet Your Mappers

Meet Your Mappers (MYM) is a simple tool to retrieve a list of active mappers around you. This can come in handy when you want to invite people to a mapping party or another local OSM event you are organizing. Or perhaps you have just always wondered who else is mapping a lot in your area.

MYM does that, and only that, for you. It will not give you detailed breakdowns of what everyone mapped and where, there are great tools out there for that already, like Simon Legner's Whodidit, Wille Marcel's OSMCha and Pascal Neis's Who's Around Me.

## Usage

This is a bit of a hack so you need to do a few steps. Please help make this tool easier to use by contributing improvements if you can!

**The OSM data needed to get you your answers is retrieved from Overpass. Please be mindful of this and don't try to request answers for huge areas.**

1. Search for your town, county or equivalent on OSM
2. Note down or copy the OSM ID of the boundary relation. 

A boundary relation ID is currently the only input method, so if your area of interest does not have that, you're out of luck. 

3. Go to [mym.rtijn.org](https://mym.rtijn.org/)
4. Paste the relation ID in the input box
5. Click 'Go'

Next, MYM will retrieve the OSM data for your area from Overpass and analyze it. This may take up to a minute or so, depending on the amount of data.

When it's done, You see a table with users. By default they are sorted by magic, which is an attempt to group users into classes. 

### Standalone usage
If you have OSM files on your local machine and you want to run the tool on those, follow these steps:

* Create the virtual environment and install dependencies (see below under Installation > Development)
* run `python3 meetyourmappers/osm.py YOUR_OSM_DATA_FILE > out.json`

The file can be any format osmium supports. 

## Installation


### Development

* Clone the repository
* Install dependencies (Flask, osmium, requests) in a virtual environment
* If you want to test data downloads, set `data_dir` and `data_alias` to `data` and create a directory `data` in the application directory.
* `run.sh`

### Production

* Clone the repository
* Create a data directory, `chown` to www-data
* Configure Apache (see example)
* Set up a `cron` job to empty the data directory periodically, something like `0 * * * * find /var/www/data/ -type f -mmin +60 -delete`

## Development

MYM uses the following technologies:

* Python
* Flask
* PyOsmium
* JQuery
* DataTables

If you encounter a bug or have an idea for improvement, please file it as an issue before you start working on it, so we can discuss (unless it's something really trivial).

Javascript is not really my thing so forgive me for that mess.
