import os
import re
import sys
import copy
import MeCab

def get_sample():
    return "rhyme<br>detect"

def parse_sentence(sentence):
    m = MeCab.Tagger()
    return m.parse(sentence).split("\n")

def remove_escape_word(sentence_list):
    
    for word_attr in copy.copy(sentence_list):
        if len(word_attr.split(",")) == 1:
            sentence_list.remove(word_attr)
    return sentence_list

def fetch_kana(sentence):
    
    parsed_sentence = parse_sentence(sentence)
    cleaned_parsed_sentence = remove_escape_word(parsed_sentence)
    #kana_sentence = [word_attr.split(",")[8] if len(word_attr.split(",")) == 9 else word_attr.split(",")[0].split("\t")[0] for word_attr in cleaned_parsed_sentence]
    origin_sentence_list = []
    kana_sentence = []
    kana_to_origin_point_list = []
    is_origin_top_list = []
    for (i ,word_attr) in enumerate(cleaned_parsed_sentence):
        if len(word_attr.split(",")) == 9:
            kana_word = word_attr.split(",")[8]
        else:
            kana_word = word_attr.split(",")[0].split("\t")[0]
        origin_sentence_list.append(word_attr.split(",")[0].split("\t")[0])
        kana_sentence.append(kana_word)
        for j in range(len(kana_word)):
            is_origin_top_list.append(True if j == 0 else False)
            kana_to_origin_point_list.append(i)
    return origin_sentence_list, kana_sentence, kana_to_origin_point_list, is_origin_top_list

def kana_to_vowel(kana_sentence, lower_kana_list, kana_to_vowel_dict):
    vowel_sentence = []
    vowel_to_kana_point_list = []
    is_vowel_word_top_list = []
    kana_length = 0
    print(kana_sentence)
    for word in kana_sentence:
        vowel_word = ""
        for (i, char) in enumerate(list(word)):
            print(char)
            if char in lower_kana_list:
                vowel_word = vowel_word[:-1] + kana_to_vowel_dict[char]
                vowel_to_kana_point_list[-1][1] = kana_length + i
            elif vowel_word != '' and ((vowel_word[-1] == 'オ' and  char == 'ウ') or (vowel_word[-1] == 'エ' and char == 'イ')) :
                vowel_word += ''
                vowel_to_kana_point_list[-1][1] = kana_length + i
            elif char in ['ッ', 'ン', 'ー']:
                vowel_word += ''
                vowel_to_kana_point_list[-1][1] = kana_length + i
            else:
                vowel_word += kana_to_vowel_dict[char]
                vowel_to_kana_point_list.append([kana_length+i, kana_length+i])
            is_vowel_word_top_list.append(True if i == 0 else False)
        vowel_sentence.append(vowel_word)
        kana_length += len(word)
    return vowel_sentence, vowel_to_kana_point_list, is_vowel_word_top_list

def search(keyword, sentence, tolerance=0):
    """

    """
    match_list = re.finditer(keyword, sentence)
    if match_list:
        for match in match_list:
            print(match.start())

def get_duplicated_index(vowels, vowels_list):
    return [i for i, _vowels in enumerate(vowels_list) if _vowels == vowels]


def search_n_gram(sentence, is_kana_top_list, n_gram=2, tolerance=0):
    """
    """
    n_gram_elements = []
    for i in range(len(sentence) - (n_gram - 1)):
        n_gram_elements.append(sentence[i:i+(n_gram)])
    
    vowels_index_dict = {}
    for vowels in set(n_gram_elements):
        candidate = get_duplicated_index(vowels, n_gram_elements)
        if len(candidate) >= 2:
            for (i, vowel_index) in enumerate(candidate):
                if not is_kana_top_list[vowel_index]:
                    candidate.pop(i)
            if len(candidate) >= 2:
                vowels_index_dict[vowels] = candidate
    return vowels_index_dict

def get_kana_point(vowel_to_kana_point_list, point, n_gram):
    return vowel_to_kana_point_list[point][0], vowel_to_kana_point_list[point+n_gram-1][1]

def get_kana_word(kana_sentence, vowel_to_kana_point_list, point, n_gram):
    begin_point, end_point = get_kana_point(vowel_to_kana_point_list, point, n_gram)
    return kana_sentence[begin_point:end_point+1]

def get_origin_point(kana_to_origin_point_list, vowel_to_kana_point_list, vowel_point, n_gram):
    vowel_begin_point, vowel_end_point = get_kana_point(vowel_to_kana_point_list, vowel_point, n_gram)
    return kana_to_origin_point_list[vowel_begin_point], kana_to_origin_point_list[vowel_end_point]

def get_origin_word(origin_sentence_list, kana_sentence, kana_to_origin_point_list, vowel_to_kana_point_list, vowel_point, n_gram):
    vowel_begin_point, vowel_end_point = get_kana_point(vowel_to_kana_point_list, vowel_point, n_gram)
    origin_begin_point, origin_end_point = kana_to_origin_point_list[vowel_begin_point], kana_to_origin_point_list[vowel_end_point]
    return origin_sentence_list[origin_begin_point:origin_end_point+1]


def read_kana_to_vowel_dict(path):
    kana_to_vowel_dict = {}
    with open(path, "r") as f:
        read_lines = f.readlines()
    for line in read_lines:
        kana_to_vowel_dict[line.split(" ")[0]] = line.split(" ")[1].split("\n")[0]
    return kana_to_vowel_dict

def read_lower_kana_list(path):
    lower_kana_list = []
    with open(path, "r") as f:
        read_lines = f.readlines()
    for line in read_lines:
        lower_kana_list.append(line.split("\n")[0])
    return lower_kana_list

def rhyme_detect(input_text):
    kana_to_vowel_dict = read_kana_to_vowel_dict("data/kana_to_vowel_table.txt")
    lower_kana_list = read_lower_kana_list("data/lower_kana_table.txt")
    origin_sentence_list, kana_sentence_list, kana_to_origin_point_list, is_origin_top_list = fetch_kana(input_text)
    kana_sentence = ""
    for kana in kana_sentence_list:
        kana_sentence += kana
    vowel_sentence_list, vowel_to_kana_point_list, is_vowel_word_top_list = kana_to_vowel(kana_sentence_list, lower_kana_list, kana_to_vowel_dict)
    vowel_sentence = ""
    for vowel in vowel_sentence_list:
        vowel_sentence += vowel
    output = ""
    for i in range(10):
        n_gram = i + 3
        rhyme_dict = search_n_gram(vowel_sentence, is_vowel_word_top_list, n_gram=n_gram)
        for vowel_rhyme in rhyme_dict:
            sentence_list = origin_sentence_list.copy()
            output += "----{}----<br>".format(vowel_rhyme)
            if any(rhyme_dict):
                for vowel_point in rhyme_dict[vowel_rhyme]:
                    begin_point, end_point = get_origin_point(kana_to_origin_point_list, vowel_to_kana_point_list, vowel_point, n_gram)
                    sentence_list[begin_point] = '<span style="color:red">{}'.format(sentence_list[begin_point])
                    sentence_list[end_point] = '{}</span>'.format(sentence_list[end_point])
                output += "{}<br>".format("".join(sentence_list))
                output += "{}<br>".format(get_origin_word(origin_sentence_list, kana_sentence, kana_to_origin_point_list, vowel_to_kana_point_list, vowel_point, n_gram=n_gram))
    return output



if __name__ == "__main__":
    kana_to_vowel_dict = read_kana_to_vowel_dict("../data/kana_to_vowel_table.txt")
    lower_kana_list = read_lower_kana_list("../data/lower_kana_table.txt")
    sentence = "学校では生徒会長でも女子からされない性の対象"
    origin_sentence_list, kana_sentence_list, kana_to_origin_point_list, is_origin_top_list= fetch_kana(sentence)
    print(kana_sentence_list)
    kana_sentence = ""
    for kana in kana_sentence_list:
        kana_sentence += kana
    vowel_sentence_list, vowel_to_kana_point_list, is_vowel_word_top_list = kana_to_vowel(kana_sentence_list, lower_kana_list, kana_to_vowel_dict)
    print(vowel_sentence_list)
    vowel_sentence = ""
    for vowel in vowel_sentence_list:
        vowel_sentence += vowel
    
    rhyme_dict = search_n_gram(vowel_sentence, is_vowel_word_top_list, n_gram=5)
    for vowel_rhyme in rhyme_dict:
        print("-----{}-----".format(vowel_rhyme))
        for vowel_point in rhyme_dict[vowel_rhyme]:
            #print(get_kana_word(kana_sentence, vowel_to_kana_point_list, vowel_point, n_gram=4))
            print(get_origin_word(origin_sentence_list, kana_sentence, kana_to_origin_point_list, vowel_to_kana_point_list, vowel_point, n_gram=4))


