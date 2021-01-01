from nltk.corpus import wordnet as wn
import pandas as pd
import spacy
import re
import random

nlp = spacy.load("en_core_web_sm")

def initiate():

  key = {
    "_": "+REQ",
    ",": "+OPT"
  }

  frame = "\((.*)\)"
  frame1 = "\(([a-z]*,[a-z]*)\)"
  path = "C:\\Users\jake\OneDrive\Documents\Python Scripts\\verbs.txt"
  file_text = open(path, "r")
  raw_text = file_text.read()[9142:].split("\n\n;;")

  words = {}
  names_list = []

  count = 1
  for entry in raw_text: 
    data = entry.split(":")[2:]
    if (data[0][0:8] == "DEF_WORD"):
      name = data[0][10:-3]
      del data[0]
    else:
      for i in data:
        if "DEF_WORD" in i:
          data[0] = i
          break
        else:
          del(i)
      name = data[0][10:-3]
      names_list.append(name)
  
    if name in words or name[0:-1] in words:
      count += 1
      name += str(count)
    else:
      count = 1

    for element in data:
      thetas = []
      if element[0:11] == "THETA_ROLES":
        theta = element[17:-5]
        except_parenth = re.search(frame1, theta)
        if except_parenth:
          test_string = re.split(frame1, theta)[0]
          for letter in key:
            theta = theta.replace(letter, key[letter])
        else:
          for letter in key:
            theta = theta.replace(letter, key[letter])
        roles = theta[1:].split("+")
        index = 1
        
        for i in roles:
          if re.search(frame, i):
            if re.search(frame1, i):
              parenth = except_parenth.group()
              i = i.replace(parenth, "")[1:]
            else:
              parenth = re.search(frame, i).group()
              i = i.replace(parenth, "")[1:]
          else:
            if except_parenth:
              parenth = except_parenth.group()
            else:
              parenth = None
          req = i[0:3]
          if req[0:2] == "EQ":
            req = "REQ"
            place = 2
          elif req[0:2] == "PT":
            req = "OPT"
            place = 2
          else:
            place = 3

          if except_parenth:
            if "(" in i[place:]:
              end = i.find("(") 
            elif ")" in i[place:]:
              continue
            else:
              end = False
          else:
            end = False

          if parenth == "()":
            if i[place:] == "src":
              parenth = "(from)"
            elif i[place:] == "goal":
              parenth = "(to/toward)"
            elif i[place:] == "pred":
              parenth = "(to/toward)"
            elif i[place:] == "perc":
              parenth = "(to/toward)"
            elif i[place:] == "loc":
              parenth = "(at/in/on)"
            elif i[place:] == "mod-poss":
              parenth = "(with/in/of/from/for)" #check me
            elif i[place:] == "ben":
              parenth = "(for)"
            elif i[place:] == "instr":
              parenth = "(with/by/of/on)"
            elif i[place:] == "purp":
              parenth = "(for)"
            elif i[place:] == "mod-loc":
              parenth = "(around/from/down)"
            elif i[place:] == "mod-pred":
              parenth = "(as)"
          
          if end:
            thetas.append([index, i[place:end], req, parenth])
          else:
            thetas.append([index, i[place:], req, parenth])
          index +=1
        
        if len(thetas) == 1 or thetas[1][2] == "OPT":
          if thetas[0][1] == "th":
            vtype = "unaccusative"
          else:
            vtype = "intransitive"
        elif len(thetas) > 1:
          if len(thetas) >= 3:
            if thetas[2][2] == "REQ":
              vtype = "ditransitive"
            else:
              vtype = "transitive"
          else:
            vtype = "transitive"
        words[name] = {"type": vtype, "sm_roles": thetas}
        if words[name]["sm_roles"][0][1] == "prop":
          del words[name]
        break
  collocate_data = pd.read_csv("collocates1.csv").drop(0)
  return words, collocate_data, names_list

words, collocate_data, names_list = initiate()

def find_nouns(verb):
  from selenium import webdriver
  from selenium.webdriver.common.keys import Keys

  from selenium.webdriver.common.by import By
  from selenium.webdriver.support.ui import WebDriverWait
  from selenium.webdriver.support import expected_conditions as EC

  path = "C:\\Users\jake\OneDrive\Documents\Python Scripts\chromedriver.exe"
  driver = webdriver.Chrome(path)



  driver.get("https://www.english-corpora.org/iweb/")

  while True:
    try:
      driver.switch_to.frame("controller")
      top_button = driver.find_element_by_id("link1")
      top_button.click()
      driver.switch_to.default_content()
      driver.switch_to.frame("x1")
      button_path = "/html/body/table/tbody/tr[2]/td[2]/table/tbody/tr[1]/td/a[2]"
      button = driver.find_element_by_xpath(button_path)
      button.click()
      element_path = '//*[@id="p"]'
      element = driver.find_element_by_xpath(element_path)
      element.send_keys(verb)
      element.send_keys(Keys.RETURN)
      driver.switch_to.default_content()
      driver.implicitly_wait(1)
      break
    except Exception:
      driver.switch_to.default_content()
      pass
  while True:
    try:
      driver.switch_to.frame("x2")
      nouns_path = "/html/body/table[1]/tbody/tr[2]/td[3]/table[4]/tbody/tr[1]/td[2]/p"
      nouns_list = driver.find_element_by_xpath(nouns_path)
      nouns = [noun for noun in nouns_list.text.split(", ")]
      if nouns != ['']:
        driver.quit()
        break
      else:
        driver.switch_to.default_content()
        pass
    except Exception:
      driver.switch_to.default_content()
      pass
  return nouns

def lookup(verb):
  doc = nlp(verb)
  for token in doc:
    if token.pos_ == "VERB":
      verb = token.lemma_
      break
  try:
      words[verb]
  except KeyError:
      verb = "!NF!"
  return verb

def return_all_forms(verb):
  forms = []
  frame = "%s[2-9]*" % verb
  matches = re.findall(frame, " ".join(words))
  if matches:
    for i in matches:
      if i in words and i not in forms:
        forms.append(i)
  return forms
      
def find_patterns(verb, lang="e"):

  verb = lookup(verb)

  # 主 謂 賓 定 狀 補

  key_c = {
    "subject": "主詞",
    "dobj": "直接受詞",
    "iobj": "間接受詞",
    "src": "起點",
    "goal": "指向",
    "ben": "人",
    "loc": "地點",
    "instr": "工具",
    "perc": "刺激", #check
    "pred": "補語",
    "poss": "名詞",
    "prop": "小句",
    "mod-poss": "名詞",
    "mod-loc": "地方",
    "mod-prop": "動詞",
    "purp": "間接受詞",
    "mod-pred": "補語",
    "info": "小句"
  }

  key_e = {
    "subject": "Subject",
    "dobj": "Direct Object",
    "iobj": "Indirect Object",
    "src": "Starting Point",
    "goal": "End Point",
    "ben": "Noun",
    "loc": "Location",
    "instr": "Something",
    "perc": "Perceiver",
    "pred": "Complement",
    "poss": "Noun",
    "prop": "Verb",
    "mod-poss": "Noun",
    "mod-loc": "Location",
    "mod-prop": "Verb",
    "purp": "Reason",
    "mod-pred": "Complement",
    "info": "Clause"
  }
  

  if lang == "c":
    dic = key_c
  elif lang == "e":
    dic = key_e
  words_all = return_all_forms(verb)
  frames = []
  data = []
  sentences = {"patterns":[], "nouns": None}
  for x in words_all:
    data.append(words[x])
  for word in data:
    if word["type"] == "unaccusative":
      word["sm_roles"][0] = dic["subject"]
      word["sm_roles"].insert(1, verb.upper())
    elif word["type"] == "intransitive":
      if word["sm_roles"][0][1] in ("ag", "exp") and word["sm_roles"][0][2] == "REQ":
        word["sm_roles"][0] = dic["subject"]
        word["sm_roles"].insert(1, verb.upper())
    elif word["type"] == "transitive":
      if word["sm_roles"][0][1] in ("ag", "exp", "th", "perc"):
        if word["sm_roles"][1][1] in ("th", "exp", "perc"):
          word["sm_roles"][1] = dic["dobj"]
        word["sm_roles"][0] = dic["subject"]
        word["sm_roles"].insert(1, verb.upper())
    elif word["type"] == "ditransitive":
      if word["sm_roles"][0][1] in ("ag", "exp", "th") and word["sm_roles"][0][2] == "REQ":
        if word["sm_roles"][1][1] in ("th", "exp", "perc"):
          word["sm_roles"][1] = dic["dobj"]
        if word["sm_roles"][1][1] == "goal":
          word["sm_roles"][1] = dic["iobj"]
        if word["sm_roles"][2][1] == "th":
          word["sm_roles"][2] = dic["dobj"]
        word["sm_roles"][0] = dic["subject"]
        word["sm_roles"].insert(1, verb.upper())
    for entry in word["sm_roles"]:
      if type(entry) == list:
        if entry[1] in dic.keys():
          place = word["sm_roles"].index(entry)
          word["sm_roles"][place] = dic[entry[1]]
          if entry[3] != None:
            word["sm_roles"].insert((place), entry[3])
  for entry in data:
    if entry["sm_roles"][0] != "Subject":
      del entry
    elif entry["sm_roles"] not in sentences["patterns"]:
      sentences["patterns"].append(entry["sm_roles"])
  # sentences["nouns"] = [i for i in find_nouns(verb)]
  return sentences

def get_examples(verb):
  examples = []
  for synset in wn.synsets(verb, pos=wn.VERB):
    for sentence in synset.examples():
      doc = nlp(sentence)
      for token in doc:
        if token.lemma_ == verb:
          examples.append(sentence)
  return examples

def find_collocates(word, word_pos, coll_pos, thres=0.6, num=8):
  collocates = {}
  collocate_data["[% coll < node]"] = [float(i) for i in collocate_data["[% coll < node]"]]
  if word in [i for i in collocate_data.lemma]:
    selection = collocate_data[collocate_data.lemma == word][collocate_data.lemPoS == word_pos][collocate_data.collPoS==coll_pos][collocate_data.coll != "FALSE"]
    # if coll_pos == "n":
    #   collocates["before"] = list(selection[selection["[% coll < node]"] >= thres]["coll"][0:num])
    #   collocates["after"] = list(selection[selection["[% coll < node]"] <= thres]["coll"][0:num])
    # else:
    collocates["words"] = list(selection["coll"][0:num])
  else:
    selection = collocate_data[collocate_data.coll == word][collocate_data.lemPoS == coll_pos][collocate_data.lemma != "FALSE"].sort_values(by=["freq"], ascending=False)
    # collocates["before"] = list(selection[selection["[% coll < node]"] >= thres]["lemma"][0:num])
    # collocates["after"] = list(selection[selection["[% coll < node]"] <= thres]["lemma"][0:num])
    # word_list = {}
    # for i in selection["lemma"]:
    #   print(i.freq)
    # print(word_list)
    # selection_else = collocate_data[collocate_data.coll == word][collocate_data.collPoS == word_pos][collocate_data.lemPoS != "n"].sort_values(by=["freq"], ascending=False)
    collocates["words"] = list(selection["lemma"][0:num])
    # collocates["before"], collocates["after"] = [], []

  return collocates

def get_frames(word, word_pos):
  frames = {}
  nouns = find_collocates(word, word_pos, "n")
  # frames["主"], frames["賓"] = nouns["before"], nouns["after"]
  frames["Nouns"] = find_collocates(word, word_pos, "n")["words"]
  # frames["賓"] = get_collocates(word, word_pos, "n")["words"]
  frames["Adjectives"] = find_collocates(word, word_pos, "j")["words"]
  frames["Adverbs"] = find_collocates(word, word_pos, "r")["words"]
  frames["Verbs"] = find_collocates(word, word_pos, "v")["words"]
  if len(frames["Nouns"]) + len(frames["Adjectives"]) + len(frames["Adverbs"]) + len(frames["Verbs"]) == 0:
      return "!ND!" 
  else:
    return frames


def get_patterns(verb):
  patterns = []
  verb = lookup(verb)
  data = find_patterns(verb)
  for pattern in data["patterns"]:
    patterns.append(" + ".join(str(v) for v in pattern))
  return patterns

def get_all_data(verb):
  verb = lookup(verb)
  if verb == "!NF!":
      return "!NF!"
  else:
      data = {}
      data["Usage"] = get_patterns(verb)
      collocates = get_frames(verb, "v")
      if collocates != "!ND!":
        data["Collocates"] = get_frames(verb, "v")
      examples = get_examples(verb)
      if len(examples) != 0:
        data["Example Sentences"] = get_examples(verb)
      return data

from flask import render_template, flash, redirect, request
from app import app
from app.forms import WordForm

@app.route("/")
@app.route("/index", methods=["POST", "GET"])
def index():
    global form
    form = WordForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            return redirect("/data")
    else:
      return render_template("word.html", form = form, rand = random.choice(names_list))

@app.route("/data", methods=["POST", "GET"])
def data():
    word_data = get_all_data(request.form.get("word"))
    return render_template("data.html", word_data=word_data)