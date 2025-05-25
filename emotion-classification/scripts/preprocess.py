import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import squarify
from wordcloud import WordCloud
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
from sklearn.feature_extraction.text import CountVectorizer

df = pd.read_csv('data/raw/emotion_dataset.csv', header=None, names=['comment', 'emotion_label', 'id'])  # Format: comment,emotion_label
#df = pd.read_csv('data/raw/emotion_dataset.csv')  # Format: comment,emotion_label
print(df.head())
print(df.info())

print(df.isnull().sum())
print(f"Total samples: {len(df)}")



# Get counts for each emotion class
emotion_counts = df['emotion_label'].value_counts()

########################
# plt.figure(figsize=(12, 10))  # Tall plot for horizontal bars
# sns.barplot(
#     y=emotion_counts.index, 
#     x=emotion_counts.values, 
#     orient='h',
#     palette="viridis"
# )
# plt.ylabel('Emotion Class')
# plt.xlabel('Count')
# plt.title('Distribution of Emotion Classes')

# plt.tight_layout()  # Ensures labels are not cut off
# plt.savefig('emotion_class_distribution.png', dpi=300)  # Save the plot
# plt.show()
########################

plt.figure(figsize=(16, 6))
top_n = 20
sns.barplot(
    x=emotion_counts.index[:top_n],
    y=emotion_counts.values[:top_n],
    palette="viridis"
)
plt.xticks(rotation=75, ha='right')
plt.xlabel('Emotion Class')
plt.ylabel('Count')
plt.title(f'Distribution of Top {top_n} Emotion Classes')
plt.tight_layout()
plt.savefig('eda/plots/top20_emotion_class_distribution.png', dpi=300)
#plt.show()

# # Frequency table for emotion classes
# label_counts = df['emotion_label'].value_counts()
# print(label_counts)
# plt.figure(figsize=(12, max(6, 0.25*len(label_counts))))  # Adjust height for many labels
# sns.barplot(
#     y=label_counts.index,
#     x=label_counts.values,
#     orient='h',
#     palette='viridis'
# )
# plt.ylabel('Emotion Label')
# plt.xlabel('Frequency')
# plt.title('Frequency of All Emotion Classes')
# plt.tight_layout()
# plt.savefig('eda/plots/all_emotion_class_distribution.png', dpi=300)
# #plt.show()


# plt.figure(figsize=(12, max(6, 0.25*len(label_counts))))  # Adjust height for many labels
# sns.barplot(
#     y=label_counts.index,
#     x=label_counts.values,
#     orient='h',
#     palette='viridis'
# )
# plt.ylabel('Emotion Label')
# plt.xlabel('Frequency')
# plt.title('Frequency of All Emotion Classes')
# plt.tight_layout()
# plt.savefig('eda/plots/all_emotion_class_distribution2.png', dpi=300)
# #plt.show()


# num_classes = len(label_counts)
# half = num_classes // 2

# # First half
# plt.figure(figsize=(12, max(6, 0.25*half)))
# sns.barplot(
#     y=label_counts.index[:half],
#     x=label_counts.values[:half],
#     orient='h',
#     palette='viridis'
# )
# plt.title('Frequency of Emotion Classes (Part 1)')
# plt.tight_layout()
# plt.savefig('eda/plots/emotion_classes_part1.png', dpi=300)
# #plt.show()

# # Second half
# plt.figure(figsize=(12, max(6, 0.25*(num_classes-half))))
# sns.barplot(
#     y=label_counts.index[half:],
#     x=label_counts.values[half:],
#     orient='h',
#     palette='viridis'
# )
# plt.title('Frequency of Emotion Classes (Part 2)')
# plt.tight_layout()
# plt.savefig('eda/plots/emotion_classes_part2.png', dpi=300)
# #plt.show()





# label_counts = df['emotion_label'].value_counts()
# cum_pct = label_counts.cumsum() / label_counts.sum() * 100

# plt.figure(figsize=(14, 6))
# plt.bar(label_counts.index, label_counts.values)
# plt.plot(label_counts.index, cum_pct, color='red', marker='o')
# plt.xticks(rotation=90, fontsize=8)
# plt.ylabel('Frequency')
# plt.title('Pareto Plot: Emotion Class Frequency and Cumulative %')
# plt.tight_layout()
# plt.savefig('eda/plots/emotion_classes_pareto.png', dpi=300)
# #plt.show()

# label_counts = df['emotion_label'].value_counts()
# plt.figure(figsize=(16, 8))
# squarify.plot(sizes=label_counts.values, label=label_counts.index, alpha=.8)
# plt.axis('off')
# plt.title('Treemap of Emotion Label Distribution')
# plt.savefig('eda/plots/emotion_classes_treemap.png', dpi=300)



label_counts = df['emotion_label'].value_counts()
wc = WordCloud(width=1200, height=600, background_color='white')
wc.generate_from_frequencies(label_counts)
plt.figure(figsize=(16, 8))
plt.imshow(wc, interpolation='bilinear')
plt.axis('off')
plt.title('Word Cloud of Emotion Classes')
plt.savefig('eda/plots/emotion_classes_wordcloud.png', dpi=300)


# label_counts = df['emotion_label'].value_counts()
# plt.figure(figsize=(14, max(6, 0.25*len(label_counts))))
# plt.stem(label_counts.index, label_counts.values)
# plt.xticks(rotation=90)
# plt.ylabel('Frequency')
# plt.title('Lollipop Plot of Emotion Classes')
# plt.tight_layout()
# plt.savefig('eda/plots/emotion_classes_lollipop.png', dpi=300)




nltk.download('stopwords')
nltk.download('wordnet')

stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def preprocess(text):
    text = re.sub(r'[^a-zA-Z\s]', '', text)      # Remove non-letters
    tokens = text.lower().split()
    tokens = [lemmatizer.lemmatize(w) for w in tokens if w not in stop_words]
    return ' '.join(tokens)

df['clean_comment'] = df['comment'].apply(preprocess)
print(df.head())
print(df.info())


bow = CountVectorizer(max_features=3000)
X_bow = bow.fit_transform(df['clean_comment']).toarray()


tfidf = TfidfVectorizer(max_features=3000)
X_tfidf = tfidf.fit_transform(df['clean_comment']).toarray()

ngram = TfidfVectorizer(ngram_range=(1,2), max_features=3000)
X_ngram = ngram.fit_transform(df['clean_comment']).toarray()


np.save('data/processed/X_bow.npy', X_bow)
np.save('data/processed/X_tfidf.npy', X_tfidf)
np.save('data/processed/X_ngram.npy', X_ngram)
np.save('data/processed/y.npy', df['emotion_label'].to_numpy())

joblib.dump(bow, 'data/processed/bow_vectorizer.joblib')
joblib.dump(tfidf, 'data/processed/tfidf_vectorizer.joblib')
joblib.dump(ngram, 'data/processed/ngram_vectorizer.joblib')