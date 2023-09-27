import urllib.parse
import requests
import random
import csv
import re
import sys
import os

search_history = {}
song_limit = 20

def main():
    while True:
        print("\n")
        artist = input("Artist to Search (type 'exit' to quit): ")
        if artist == "exit":
            sys.exit("\nExiting...")
        artist = error_check(artist)
        data_pull(artist, song_limit, search_history)
        search_save(search_history)
        finish()

def error_check(input_to_check):
    if not re.match(r"\S", input_to_check) or re.match(r"\W", input_to_check):
        sys.exit("\nInvalid Characters")

    string_adj = [string.capitalize() for string in input_to_check.split()]
    return " ".join(string_adj)

def data_pull(artist_request, limit, data, num=50):
    song_list = []
    sample_size = min(10, num)
    invalid_msg = "\nInvalid Artist, Try Again\n"
    
    encoded_artist = urllib.parse.quote(artist_request)
    response = requests.get(f"https://itunes.apple.com/search?entity=song&limit={num}&term={encoded_artist}")
    j_display = response.json()
    tracks = [result['trackName'] for result in j_display["results"]]
    
    if not tracks:
        print(invalid_msg)
        main()

    random_tracks = random.sample(tracks, sample_size)
    song_list.extend(random_tracks)

    song_list = list(set(song_list))
    fault_location = search_filter(artist_request, song_list)
    song_list = index_delete(song_list, fault_location)
    
    try:
        song_list = song_list[:limit]
    except TypeError:
        print(invalid_msg)
        main()

    search_history["results"] = {artist_request: song_list}
    for song in song_list:
        print(song)

def search_filter(artist, song_list):
    fault_location = []
    search_keys = set([artist, artist.capitalize(), artist.upper(), artist.lower()])
    for index, song in enumerate(song_list):
        if any(re.match(search_key, song) for search_key in search_keys):
            fault_location.append(index)
    return fault_location

def index_delete(song_list, indexes_to_delete):
    for index in sorted(indexes_to_delete, reverse=True):
        del song_list[index]
    return song_list

def search_save(data):
    with open("songs.csv", "a", encoding='utf-8', newline="") as csvfile:
        csvwriter = csv.writer(csvfile)
        if csvfile.tell() == 0:
            csvwriter.writerow(["Artist", "Song"])  # Writing header
        for key, value in data['results'].items():
            for song in value:
                csvwriter.writerow([key.encode('utf-8'), song.encode('utf-8')])

def read_save():
    print("Previous Search Results:\n")
    with open("songs.csv", "r", encoding='utf-8') as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            print(row)

def finish():
    while True:
        redo = input("\nSearch Again? (y/n): ").lower()
        if redo == "y":
            print("\033[H\033[J")
            main()
        elif redo == "n":
            print("\033[H\033[J")
            read_save()
            os.remove("songs.csv")
            sys.exit("\nExiting...")
        elif redo == "exit":
            sys.exit("\nExiting...")

if __name__ == "__main__":
    main()
