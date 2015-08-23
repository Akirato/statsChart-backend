import nltk,csv,pickle,os
import threading,MySQLdb
import tweepy
import codecs
listCompanies = {'Apple': ('Apple',['apple','#apple','Apple'],'AAPL'),'CocaCola': ('CocaCola',['coke','#coke','#cocacola','cocacola'],'KO')}

def twitter(tags):
    auth = tweepy.OAuthHandler('xgRxSH2oS55V96dlfmyke14Ex','BHT6R608D8fZlNEhmzVVxaPPy5iS9LKUsaTZXfwNp6N6AQGmjX')
    auth.set_access_token('3012016202-Bcs4IGJYSMvBAShm7x6q9tOZfPfVgdoVpGQ6uel','QaXI4oRn1HncW1GwOtQTenRDHEvey1nZWonmfEiofCGUp')
    api = tweepy.API(auth)
    allTweets = []
    for tag in tags:
        try:
            count = 0
            for tweet in tweepy.Cursor(api.search,
                           q=tag,
                           count=16,
                           result_type="recent",
                           include_entities=True,
                           lang="en").items():
                allTweets.append(tweet.text)
                count+=1
                if count>=16:
                    break
        except:
            return allTweets
    return allTweets

def get_words_in_tweets(tweets):
    all_words = []
    for (words, sentiment) in tweets:
        all_words.extend(words)
    return all_words

def get_word_features(wordlist):
    wordlist = nltk.FreqDist(wordlist)
    word_features = wordlist.keys()
    return word_features

def extract_features(document,word_features):
    document_words = set(document)
    features = {}
    for word in word_features:
        features['contains(%s)' % word] = (word in document_words)
    return features

def sentiment(sentence,tags):
    fp0 = open('fkk0.csv','rb')
    fp4 = open('fkk4.csv','rb')
    reader0 = csv.reader( fp0, delimiter=',', quotechar='"', escapechar='\\' )
    reader4 = csv.reader( fp4, delimiter=',', quotechar='"', escapechar='\\' )
    raw_tweets = []
    i,j=0,0
    for row in reader0:
        raw_tweets.append([row[5],row[0]])
        if j>1000:
	    break
        j+=1
    for row in reader4:
        raw_tweets.append([row[5],row[0]])
        if i>1000:
	    break
        i+=1
    tweets = []
    for (words, sentiment) in raw_tweets:
        words_filtered = [e.lower() for e in words.split() if len(e) >= 3]
        tweets.append((words_filtered, sentiment))
    word_features = get_word_features(get_words_in_tweets(tweets))
    classifier = pickle.load(open("FSsentimentTrained.pickle",'rb'))
    tweet = sentence
    if isinstance(tweet,str):
        return (0 if classifier.classify(extract_features(tweet.split(),word_features)) == "0" else 1)
    
    elif isinstance(tweet,list) and tags == None:
        pos,neg=0,0
        try:
            openfile = codecs.open('/home/www-data/web2py/twitterData','a',encoding = 'utf-8')
            openfile.close()
        except:
            openfile = codecs.open('/home/www-data/web2py/twitterData','w',encoding = 'utf-8')
            openfile.close()

        for i in tweet:
            if classifier.classify(extract_features(i.split(),word_features)) == "0":
                try:
                    openfile = codecs.open('/home/www-data/web2py/twitterData','a',encoding = 'utf-8')
                    openfile.write(i+'\n'+'Negative'+'\n')
                    openfile.close()
                except:
                    pass
                neg+=1
            else:
                try:
                    openfile = codecs.open('/home/www-data/web2py/twitterData','a',encoding = 'utf-8')
                    openfile.write(i+'\n'+'Positive'+'\n')
                    openfile.close()
                except:
                    pass

                pos+=1
        return (pos,neg)

    elif isinstance(tweet,list) and tags != None:
        pos,neg=0,0
        for i in tweet:
            flag = 0
            for tag in tags:
                if tag in tweet:
                    flag=1
                    break
            if flag==1:
                try:
                    openfile = codecs.open('/home/www-data/web2py/ccextrData','a',encoding = 'utf-8')
                    openfile.close()
                except:
                    openfile = open('/home/www-data/web2py/ccextrData','w')
                    openfile.close()
                if classifier.classify(extract_features(i.split(),word_features)) == "0":
                    try:
                        openfile = codecs.open('/home/www-data/web2py/ccextrData','a',encoding = 'utf-8')                  
                        openfile.write(i+"\n"+'Negative'+'\n')
                        openfile.close()
                    except:
                        pass

                    neg+=1
                else:
                    try:
                        openfile = codecs.open('/home/www-data/web2py/ccextrData','a',encoding = 'utf-8')
                        openfile.write(i+"\n"+'Positive'+'\n')       
                        openfile.close()
                    except:
                        pass
                    pos+=1
        return (pos,neg)
 
def writeTwitter():
    global listCompanies
    threading.Timer(float(720.0*len(listCompanies)), writeTwitter).start()
    for i in listCompanies.keys():
        feel = sentiment(twitter(listCompanies[i][1]),None)
        pos = feel[0]
        neg = feel[1]
        conn = MySQLdb.connect(host= "localhost",
                  user="root",
                  passwd="iamroot",
                  db="statschart")
        x = conn.cursor()
        insertsql = "INSERT INTO twitterstats(company,positive,negative) VALUES ('" +str(listCompanies[i][0])+"',"+ str(pos)+","+str(neg)+");"
        try:
            x.execute(insertsql)
            conn.commit()
        except:
            conn.rollback()
        conn.close()
       
if  __name__ == "__main__":
     writeTwitter()
