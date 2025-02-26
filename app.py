from flask import Flask, request, jsonify
from Bio import Entrez
import datetime

app = Flask(__name__)

Entrez.email = "your_email@example.com"
current_year = datetime.datetime.now().year
min_year = current_year - 4  # بررسی مقالاتی که آخرین مرور سیستماتیک آنها 4+ سال پیش است

def get_old_systematic_reviews(keyword):
    search_term = f"systematic review AND {keyword}"
    handle = Entrez.esearch(db="pubmed", term=search_term, retmax=50)
    record = Entrez.read(handle)
    handle.close()

    id_list = record["IdList"]
    handle = Entrez.efetch(db="pubmed", id=id_list, retmode="xml")
    records = Entrez.read(handle)
    handle.close()

    topics = []
    for article in records["PubmedArticle"]:
        title = article["MedlineCitation"]["Article"]["ArticleTitle"]
        try:
            pub_date = article["MedlineCitation"]["Article"]["Journal"]["JournalIssue"]["PubDate"]
            pub_year = int(pub_date.get("Year", "0"))
        except:
            pub_year = 0

        if pub_year > 0 and pub_year <= min_year:
            topics.append({"title": title, "year": pub_year})

    return topics

@app.route("/search", methods=["GET"])
def search():
    keyword = request.args.get("keyword")
    if not keyword:
        return jsonify({"error": "Please provide a keyword"}), 400
    results = get_old_systematic_reviews(keyword)
    return jsonify(results)

if __name__ == "__main__":
    app.run(debug=True)
