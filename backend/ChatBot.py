import nltk
from nltk.corpus import stopwords
from nltk import word_tokenize,pos_tag
import string
import requests
import random
from fuzzywuzzy import fuzz
from nltk.stem import WordNetLemmatizer

PRIVATE_THRESHOLD=50
VALID_THRESHOLD=0.3

python_related_keywords=[
    'programming', 'language', 'scripting', 'interpreter', 'compiler', 'function',
    'class', 'object', 'module', 'package', 'library', 'variable', 'list', 'dictionary',
    'tuple', 'set', 'loop', 'conditional', 'exception', 'file', 'input', 'output',
    'string', 'integer', 'float', 'boolean', 'data', 'type', 'documentation', 'algorithm',
    'structure', 'recursion', 'inheritance', 'polymorphism', 'encapsulation',
    'abstraction', 'decorator', 'generator', 'list','comprehension', 'lambda','function',
    'django','flask', 'connect', 'code','coding','cod',
    'exception', 'virtual','environment','venv', 'package', 'web','scraping','framework','odoo',
    'REST','API', 'JSON', 'database', 'SQL', 'SQLite', 'Pandas', 'NumPy',
    'Matplotlib', 'SciPy', 'TensorFlow', 'machine','learning', 'artificial','intelligence','ml','ai','dl','natural','language','processing','nlp'
    'deep','async', 'await', 'coroutine',
    'concurrency', 'threading', 'multithreading', 'multiprocessing', 'logging',
    'unit testing', 'debugging', 'profiling', 'scripting', 'automation', 'gui',
    'regular','expression', 'serialization', 'deserialization', 'network',
    'socket', 'http','https', 'XML', 'HTML', 'CSS', 'JavaScript', 'development',
    'desktop','application', 'file','handling', 'analysis', 'visualization',
    'vision', 'image', 'audio', 'game','hosting'
     'Internet','Things', 'embedded','systems', 'cybersecurity',
    'cloud','computing', 'virtualization', 'containers', 'Big','RESTful',
    'version','control', 'Git', 'GitHub', 'command','line','interface', 'CLI', 'automation',
    'CI/CD', 'continous','integration','development','deployment','management', 'manipulation', 'extraction',
    'cleansing', 'transformation', 'mining', 'aggregation',
     'storage', 'retrieval', 'analytics',
    'modeling', 'warehousing', 'integration', 'ETL', 'pipelines','preprocessing'
    'governance', 'security', 'privacy', 'ethics', 'science','maths','mathematics','computer','integrity','oops'
    'engineering', 'architecture', 'exploration', 'querying', 'query', 'queries',
    'validation',  'normalization', 'wrangling','get','post','put','delete',
     'classification', 'clustering', 'prediction',
    'forecasting', 'storytelling', 'reporting', 'insights',
    'driven','decision', 'solutions',
    'backup', 'restore', 'synchronization', 'migration',
    'compression', 'encryption', 'transmission',
    'quality', 'auditing','python','design','beautiful','intriguing','beautifulsoup'
    'monitoring', 'scalability', 'elasticity', 'replication',
    'recovery', 'resilience', 'masking', 'anonymization','decryption','hashing','socket','chat','call']

greetings=['hey','hi','hello','namaste']

python_related_keywords=[word.lower() for word in python_related_keywords]
discarded_languages=['java','c','c++','ruby','c#','dotnet','.net']
private_questions={'company \'s mission vision ?':'','product service company offer':'','long company operation':''}

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('averaged_perceptron_tagger')

def has_punct(question):
  return any([s in string.punctuation for s in question])

def determine_py_ques(question):
  append_string="Determine which coding language is used in this code. Return None if there is no code. The answer should only contain one word:"
  prompt=append_string+question
  messages={}
  messages['role']='user'
  messages['content']=prompt
  lom=[]
  lom.append(messages)
  API_URL='https://api.openai.com/v1/chat/completions'
  API_KEY='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'
  headers={"Content-Type":'application/json','Authorization':f'Bearer {API_KEY}'}
  data={'model':"gpt-3.5-turbo",'temperature':0.7,"max_tokens":10,"messages":lom}
  resp=requests.post(API_URL,headers=headers,json=data)
  print(resp.json())
  if resp.status_code==200:
    ans=resp.json()['choices'][0]['message']['content']
    print(ans)
    if 'python' in ans.lower():
      return True
    elif 'none' in ans.lower():
      return True
    else:
      return False
  else:
    return False


def get_pos_tag(tag):
  tag=tag[0].upper()
  markings={
      'J':nltk.corpus.wordnet.ADJ,
      'N':nltk.corpus.wordnet.NOUN,
      'V':nltk.corpus.wordnet.VERB,
      'R':nltk.corpus.wordnet.ADV
  }
  return markings.get(tag,nltk.corpus.wordnet.NOUN)

def preprocessquestion(question):
  stop_words=set(stopwords.words('english'))
  custom_words=set(['describe','write','define','make','please','create','give','details','brief','detail','introduce','introduction','cant','dont','shant','wont','cannot','donot','can','do','should','willnot','wouldnot','will','would'])
  stop_words.update(custom_words)
  tokenized=word_tokenize(question)
  filtered_words=[tokens.lower() for tokens in tokenized if tokens.lower() not in stop_words]

  filtered_words=[word.lower() for word in filtered_words if word not in string.punctuation]
  #print(filtered_words)

  pos_tags=pos_tag(filtered_words)

  lemmatizer=WordNetLemmatizer()
  root_words=[lemmatizer.lemmatize(word,pos=get_pos_tag(tag)) for word,tag in pos_tags]
  preprocessed_qsn=' '.join(root_words)
  return preprocessed_qsn

def determine_private(question):
  best_score=0
  best_match=None
  for qs in private_questions.keys():
    ratio=fuzz.partial_ratio(qs.lower(),question.lower())
    if ratio>best_score:
      best_score=ratio
      best_match=qs
  return best_score, best_match

def valid_scoring(question):
  validity_score=0
  qlist=question.split(' ')
  tagged_words=pos_tag(qlist)
  for word,tag in tagged_words:
    if tag=='NNP':
      validity_score=validity_score+1
    elif word in python_related_keywords:
      validity_score=validity_score +1
    elif word in greetings:
      validity_score=validity_score+1
    elif word in discarded_languages:
      return 0.0
  final_score=validity_score/len(qlist)
  return final_score

def generate_response(question):
  messages={}
  messages['role']='user'
  messages['content']=question
  lom=[]
  lom.append(messages)
  API_ENDPOINT = "https://api.openai.com/v1/chat/completions"
  API_KEY="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"
  headers={"Content-Type":'application/json','Authorization':f'Bearer {API_KEY}'}
  data={'model':"gpt-3.5-turbo",'temperature':0.7,"max_tokens":1000,"messages":lom}
  resp=requests.post(API_ENDPOINT,headers=headers,json=data)
  if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]['content']
  else:
    print(resp.json())
    raise Exception("ChatGPT API request failed!")
def determine_dsicard(question):
  q=question.split(' ')
  return any(ques.lower() in discarded_languages for ques in q) 
def get_output_from_preprocessed_question(question):
  pq=preprocessquestion(question)
  bs,bm=determine_private(pq)
  print('Preprocessed Question ',pq)
  print('Private Score ',bs)
  print('Private Match ',bm)
  if bs>PRIVATE_THRESHOLD:
    return private_questions[bm]
  else:
    valid_score=valid_scoring(pq)
    print("Valid Score ",valid_score)
    if valid_score>=VALID_THRESHOLD:
      response=generate_response(pq)
      return response
    else:
      return "Sorry This Is Not My Expertise"
    
def get_output(question):
  disc_ques=determine_dsicard(question)
  if disc_ques:
    ans='Sorry this is not my expertise'
  else:
      hp=has_punct(question)
      print(hp)
      if hp:
        detpy=determine_py_ques(question)
        print(detpy)
        if detpy:
           ans=get_output_from_preprocessed_question(question)
        else:
           ans='Sorry This Is Not My Expertise'
      else:
             ans=get_output_from_preprocessed_question(question)
  return ans 


if __name__=='__main__':
  print('Chatbot: How can I Help You Today!? *Enter E to exit* \n')
  inp=input("User: ")
  while inp.lower()!='e':
    resp=get_output(inp)
    print('\n Chatbot: '+resp+'\n')
    inp=input('User: ')
  exit()
