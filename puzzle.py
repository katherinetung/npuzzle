def string_is_int(s):
    try:
        s=int(s)
    except ValueError:
        print("Error in file")
        exit()
    return int(s)

# Taken from last year
def LoadWords(scrabble_dictionary_path):
    file1 = open(scrabble_dictionary_path, 'r')
    tiles = []
    dim = file1.readline()
    dim = string_is_int(dim)
    while True:
        line = file1.readline()
        if not line:
            break
        line = line.split("\t")
        line = list(map(string_is_int, line))
        tiles.append(line)
        print(tiles)
    return tiles

# Called from command line like "word_games.py scrabble.txt"
if __name__ == '__main__':
  scrabble_dict_path = "/Users/katherinetung/npuzzle/example.txt"
  all_words = LoadWords(scrabble_dict_path)
  print(all_words)
  """str='\t\t'
  x=str.split("\t")
  print(x)"""