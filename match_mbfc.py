# match_mc_mbfc.py
# description: provided a Media Cloud zip, check articles against existing Media
#              Bias Fact Check outlets

# imports
import os
import csv
import json
import lzma
import tarfile
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
    mbfc_fp = open(mbfc_file)
    mbfc_outlets = json.load(mbfc_fp)

    # open tarfiles and decompress 
    content = tarfile.open(articles_folder)
    all_lines = content.getmembers()

    # charging bar for progress 
    bar = ChargingBar('Filtering MC w/ MBFC', max = len(all_lines)) # for progress reporting

    with open(outfile, 'a') as out_p:
        for line in all_lines:
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


                
            '''
            for article in json_line:
                
                article_url = article['url']
                for outlet in mbfc_outlets: 
                    if outlet['link'] in article_url:
                        classified_article = article.copy()
                        classified_article['mbfc_bias'] = outlet['bias']
                        classified_article['outlet'] = outlet['name']

                        # write line to file
                        json.dump(classified_article, out_p)
                        out_p.write('\n')
            '''
            bar.next()
        bar.finish()

         
def main():
    mbfc_outlet_file = "mbfc_outlets.json"
    folder_name = "articles/zh.tar.xz"

    match_mbfc(mbfc_file=mbfc_outlet_file, articles_folder=folder_name, outfile="matched_mbfc_zh.json")

if __name__ == "__main__":
    main()