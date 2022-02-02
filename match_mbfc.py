# match_mc_mbfc.py
# description: provided a Media Cloud zip, check articles against existing Media
#              Bias Fact Check outlets

# imports
import os
import csv
import sys
import json
import lzma
import tarfile
import pandas as pd
from progress.bar import ChargingBar, Bar

def get_all_files(dir):
    dir_contents = os.listdir(dir)
    files_list = list()

    for item in dir_contents:
        full_path = os.path.join(dir, item)
        if os.path.isdir(full_path): files_list = files_list + get_all_files(full_path)
        else: files_list.append(full_path)

    return files_list


def match_mbfc(mbfc_file, articles_folder, outfile):
    start_loading = False

    # open Media Bias Fact Check outlets file
    mbfc_outlets = pd.read_csv(mbfc_file).T.to_dict()

    # open tarfiles and decompress 
    content = tarfile.open(articles_folder)
    all_lines = content.getmembers()

    # charging bar for progress 
    bar = ChargingBar('Filtering MC w/ MBFC', max = len(all_lines)) # for progress reporting

    out_p = open(outfile, 'w')
    writer = csv.DictWriter(out_p, ['guid', 'media_id', 'stories_id', 'collect_date', 'url', 'title', 'Name', 'Bias', 'article_url'])
    writer.writeheader()

    for line in all_lines:
        # decompress all files in .tar.xz folder
        decompressed_line = content.extractfile(line)
        try:
            line_content = decompressed_line.readline()
            json_line = json.loads(line_content)
        except: 
            if not start_loading: 
                start_loading = True
            else: print('LOAD ERROR')
            bar.next()
            continue
        
        all_articles = []
        # filter articles: for each outlet, check whether an article url starts with the outlet url
        # annotate filtered articles: merge outlet information w/ article information
        for outlet in mbfc_outlets:
            def join_dict(article):
                merged = article | outlet
                merged['article_url'] = article['url']
                return merged
            outlet = mbfc_outlets[outlet]
            outlet_url = outlet['url']
            filtered_articles = list(filter(lambda article_url: article_url['url'].startswith(outlet_url), json_line))
            annotated_articles = list(map(join_dict, filtered_articles))

            all_articles.extend(annotated_articles)
        
        # if there are filtered/annotated articles, write to csv file
        if len(all_articles) > 0: 
            writer.writerows(all_articles)
            
        bar.next()
    bar.finish()
    out_p.close()

         
def main():
    mbfc_outlet_file = "mbfc_outlets.csv"
    folder_name = sys.arv[1]
    #folder_name = "articles/pl.tar.xz"
    outfile_name = "mbfc_matched_" + folder_name.split('/')[1].split('.')[0] + '.csv'


    match_mbfc(mbfc_file=mbfc_outlet_file, articles_folder=folder_name, outfile=outfile_name)

if __name__ == "__main__":
    main()