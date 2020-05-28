import re
import math
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from os.path import dirname, join
import pprint

class TextSummarization(object):

    def __init__(self):
        self.document = ""
        self.splitted_documents = []
        self.template_doc = []
        self.stopwordText = []
        self.stemmer = None
        self.cleaned_documents = []
        self.terms = []
        self.term_vector_space_model = []
        self.term_frequency = []
        self.idf = []
        self.weight_term_frequency = []
        self.document_vector_space_model = []
        self.sentence_weight = []
        self.sorted_sentence_weight = []
        self.used_index = []
        self.summarized_documents = []
        self.setup()
        self.pp = pprint.PrettyPrinter()

    def setup(self):
        f = open(join(dirname(__file__), 'stopword.txt'))
        self.stopwordText=f.read().split('\n')
        f.close()
        stemmerFactory = StemmerFactory()
        self.stemmer = stemmerFactory.create_stemmer()

    def summarize(self,document, summarized_level = 2):
        self.document = document
        self.template_doc = self.document.split(". ")
        self.splitted_documents = self.document.lower().split(". ")
        self.cleaned_documents = self.clean_documents()
        self.terms = self.find_terms()
        self.term_vector_space_model = self.create_term_vector_space_model()
        self.term_frequency = self.find_term_frequency()
        self.idf = self.find_idf()
        self.document_vector_space_model = self.create_document_vector_space_model()
        self.sentence_weight = self.find_sentence_weight()
        self.sorted_sentence_weight = self.sentence_weight.copy()
        self.sorted_sentence_weight.sort(reverse = True)
        self.used_index = self.find_used_index(summarized_level)
        self.summarized_documents = self.get_sentence_by_index()
        self.show_details(summarized_level)
        return self.summarized_documents

    def show_details(self,summarized_level):
        print("Terms")
        self.pp.pprint(self.terms)
        print("\nTerm Vector Space Model")
        self.pp.pprint(self.term_vector_space_model)
        print("\nTerm Frequency")
        self.pp.pprint(self.term_frequency)
        print("\nIDF")
        self.pp.pprint(self.idf)
        print("\nDocument Vector Space Model")
        self.pp.pprint(self.document_vector_space_model)
        print("\nSentence Weight")
        self.pp.pprint(self.sentence_weight)
        print("\nUsed Index take only 1 /%2d documents" %(summarized_level))
        self.pp.pprint(self.document_vector_space_model)
        print()

    def clean_documents(self):
        cleaned_documents = []
        for sentence in self.splitted_documents:
            cleaned_documents.append(self.clean_sentence(sentence))
        return cleaned_documents

    def clean_sentence(self,sentence):
        number_removed = re.sub('[^a-zA-Z]', ' ', sentence)
        lower_case_sentence = number_removed.lower()
        stemmed_docs = self.stemmer.stem(lower_case_sentence)
        words = stemmed_docs.split()
        stopwords = self.stopword(words)
        return words
    
    def stopword(self,arrayText):
        for word in self.stopwordText:
            for text in arrayText:
                if text == word:
                    arrayText.remove(word)
        return arrayText

    def countWord(self,term, document):
        count = 0
        for word in document:
            if term == word:
                count+=1
        return count

    def find_terms(self):
        terms = []
        for sentence in self.cleaned_documents:
            for word in sentence:
                if word not in terms:
                    terms.append(word)
        return terms

    def dft_counter(self,numbers):
        count = 0
        for num in numbers:
            if num != 0:
                count+=num
        return count

    def create_term_vector_space_model(self):
        term_vector_space_model = {}
        for term in self.terms:
            t = []
            for sentence in self.cleaned_documents:
                df = self.countWord(term,sentence)
                tf_dokumen = self.find_wtf(df)
                t.append(tf_dokumen)
            term_vector_space_model[term] = t
        return term_vector_space_model

    def find_term_frequency(self):
        term_frequency = []
        for term in self.terms:
            term_frequency.append(self.dft_counter(self.term_vector_space_model[term]))
        return term_frequency

    def find_wtf(self, df):
        weight_term_frequency = 0 if df == 0 else 1+math.log(df,10)
        return weight_term_frequency

    def find_idf(self):
        idf = []
        for tf in self.term_frequency:
            temp = math.log(len(self.splitted_documents)/tf,10)
            idf.append(temp)
        return idf

    def create_document_vector_space_model(self):
        document_vector_space_model = {}
        for x in range(len(self.term_vector_space_model[self.terms[0]])):
            temp=[]
            for term in self.terms:
                temp.append((self.term_vector_space_model[term][x]))
            document_vector_space_model[x] = temp
        return document_vector_space_model

    def find_sentence_weight(self):
        sentence_weight = []
        for x in range(len(self.term_vector_space_model[self.terms[0]])):
            s = 0
            for y in range(len(self.idf)):
                s = s + float(self.document_vector_space_model[x][y]) * float(self.idf[y])
            sentence_weight.append(s)
        return sentence_weight

    def find_used_index(self, summarized_level):
        index = []
        for ww in self.sorted_sentence_weight:
            index.append(self.sentence_weight.index(ww)+1)
        used_index = []
        take = int(len(self.splitted_documents)/summarized_level)
        for x in range(take):
            used_index.append(index[x])
        used_index.sort()
        return used_index

    def get_sentence_by_index(self):
        summarized_documents = ''
        for id in self.used_index:
            summarized_documents = summarized_documents + self.template_doc[id-1] +'. '
        return summarized_documents

if __name__ == "__main__":
    document = "Sekarang saya sedang suka memasak. Masak kesukaan saya sekarang adalah nasi goreng. Cara memasak nasi goreng adalah nasi digoreng. Nasi goreng dapat dimakan dengan berbagai macam lauk. Lauk kesukaan saya adalah telur goreng untuk dimakan bersama nasi goreng. Selain itu lauk ayam goreng juga enak untuk dimakan bersama nasi goreng"
    a = TextSummarization()
    print(a.summarize(document))