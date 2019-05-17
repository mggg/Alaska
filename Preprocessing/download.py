import os

import geopandas
import us
import wasabi

printer = wasabi.Printer()


def download_shapefile(state_name):
    state = us.states.lookup(state_name)

    output_file = f"./shapefiles/{state.name}/{state.name}.shp"
    os.mkdir(f"./shapefiles/{state.name}")
    with printer.loading("Downloading {}...".format(state.name)):
        url = (
            f"https://www2.census.gov/geo/tiger/TIGER2018/SLDL/"
            f"tl_2018_{state.fips}_sldl.zip"
        )
        df = geopandas.read_file(url)
        df.to_file(output_file)
    printer.good("Downloaded {} to {}!".format(state_name, output_file))


def download_states(states):
    for state in states:
        download_shapefile(state)


if __name__ == "__main__":
    states = [
        "Alaska",
        "Iowa",
        "Montana",
        "Ohio",
        "Wisconsin",
        "Illinois",
        "Minnesota",
        "Nevada",
        "Oregon",
        "Wyoming",
    ]
    download_states(states)
