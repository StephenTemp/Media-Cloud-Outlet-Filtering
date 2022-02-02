# match_abyz.py
# description: provided the folder of ABYZ outlets, match it to Media Cloud articles

# imports
from cmath import isnan
import os
import sys
import csv
import json
import tarfile
import pandas as pd
from progress.bar import ChargingBar

# function: get_all_files()
# description: from the crawled folders, export csv readable document of outlets
def get_all_files(dir):
    dir_contents = os.listdir(dir)
    files_list = list()

    for item in dir_contents:
        full_path = os.path.join(dir, item)
        if os.path.isdir(full_path): files_list = files_list + get_all_files(full_path)
        else: files_list.append(full_path)

    return files_list

# function: folders_to_csv()
# description: crawl 'articles' folder and export as simple csv file
def folders_to_csv(input_folder = "abyz"):
    # get json files from "abyz" directory
    all_files = get_all_files(input_folder)
    json_files = list(filter(lambda file: file.endswith('.json'), all_files))

    # list of outlets
    outlets = list()

    for file in json_files:
        file_p = open(file)
        json_data = json.load(file_p)
        outlets.extend(json_data)

    # write outlets to file
    output_file = open("abyz_outlets.csv", "w")
    outlet_writer = csv.DictWriter(output_file, outlets[0].keys())
    outlet_writer.writeheader()
    outlet_writer.writerows(outlets)

def clean_data(data):
    return list(filter(lambda article: isinstance(article['url'], str), data))


# function: match_mc_outlets()
# description: provided the "abyz" outlets file and media clouds "articles" directory
def filter_mc_outlets(abyz_file, folder, outfile):
    start_loading = False
    mc_folder = "articles/" + folder + ".tar.xz"

    # open abyz file
    abyz_outlets = pd.read_csv(abyz_file)
    abyz_outlets = abyz_outlets.T.to_dict()

    # open tarfiles and decompress 
    content = tarfile.open(folder)
    all_lines = content.getmembers()

    all_articles = []
    # charging bar for progress 
    bar = ChargingBar('Filtering ' + folder + ' MC w/ ABYZ', max = len(all_lines)) # for progress reporting
    
    out_p = open(outfile, 'w')
    writer = csv.DictWriter(out_p, ['guid', 'media_id', 'stories_id', 'collect_date', 'url', 'title', 'index', 'greater region', 'sub-region', 'local, national or foreign', 'name', 'media type', 'media focus', 'language', 'article_url'])
    writer.writeheader()
    for line in all_lines:
        # decompress and load article jsons
        decompressed_line = content.extractfile(line)
        try:
            line_content = decompressed_line.readline()
            json_line = json.loads(line_content)
            cleaned_data = clean_data(json_line)
        except: 
            # error with loading line
            if not start_loading: 
                start_loading = True
                continue
            else: 
                print('LOAD ERROR')
                sys.exit()

        for outlet in abyz_outlets:
            def join_dict(article):
                merged = article | outlet
                merged['article_url'] = article['url']
                return merged
            outlet = abyz_outlets[outlet]
            if not isinstance(outlet['url'], str): continue
            outlet_url = outlet['url']
            filtered_articles = list(filter(lambda article_url: article_url['url'].startswith(outlet_url), cleaned_data))
            annotated_articles = list(map(join_dict, filtered_articles))

            all_articles.extend(annotated_articles)
        
        # if there are filtered/annotated articles, write to csv file
        if len(all_articles) > 0: 
            writer.writerows(all_articles)

        bar.next()
    bar.finish()
    outfile.close()

def main():
    # folders_to_csv()
    abyz_outlet_file = "abyz_outlets.csv"
    # folder_name = sys.argv[1]
    folder_name = "articles/pl.tar.xz"
    outfile_name = "abyz_matched_" + folder_name.split('/')[1].split('.')[0] + '.csv'

    filter_mc_outlets(abyz_file = abyz_outlet_file, folder=folder_name, outfile=outfile_name)

if __name__ == "__main__":
    main()