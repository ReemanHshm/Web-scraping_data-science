from flask import Flask, jsonify, render_template
from pymongo import MongoClient, TEXT
from bson import ObjectId
from datetime import datetime, timedelta
app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["almayadeen"]
collection = db["articles"]

@app.route("/")
def home():
    return "Welcome to the Home Page!"


@app.route("/articles_count", methods=["GET"])
def articles_count():
    return jsonify(collection.count_documents(filter={}))


#1
@app.route("/top_keywords_chart")
def top_keywords_chart():
    return render_template("top_keywords_chart.html")

@app.route("/top_keywords", methods=["GET"])
def top_keywords():
    pipeline = [
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)
@app.route("/articles_by_top_keyword_count", methods=["GET"])
def articles_by_top_keyword_count():
    pipeline = [
        {"$group": {"_id": {"$size": "$keywords"}, "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit" : 5}
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#2
@app.route("/top_authors_chart")
def top_authors_chart():
    return render_template("top_authors_chart.html")
@app.route("/top_authors", methods=["GET"])
def top_authors():
    pipeline = [
        {"$group": {"_id": "$author", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#3
@app.route("/articles_by_date_chart")
def articles_by_date_chart():
    return render_template("articles_by_date_chart.html")
@app.route("/articles_by_date", methods=["GET"])
def articles_by_date():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$dateToString": {
                        "format": "%Y-%m-%d",
                        "date": {"$dateFromString": {"dateString": "$published_time"}},
                    }
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#4
@app.route("/articles_by_word_count_chart")
def articles_by_word_count_chart():
    return render_template("articles_by_word_count_chart.html")
@app.route("/articles_by_word_count", methods=["GET"])
def articles_by_word_count():
    pipeline = [
        {"$group": {"_id": {"$toInt": "$word_count"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


#5
@app.route("/articles_by_language_chart")
def articles_by_language_chart():
    return render_template("articles_by_language_chart.html")
@app.route("/articles_by_language", methods=["GET"])
def articles_by_language():
    pipeline = [
        {"$group": {"_id": "$lang", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#6
@app.route("/articles_by_classes_chart")
def articles_by_classes_chart():
    return render_template("articles_by_classes_chart.html")
@app.route("/articles_by_classes", methods=["GET"])
def articles_by_classes():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "category"}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#7
@app.route("/recent_articles_chart")
def recent_articles_chart():
    return render_template("recent_articles_chart.html")
@app.route("/recent_articles", methods=["GET"])
def recent_articles():
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "url": 1,
                "title": 1,
                "keywords": 1,
                "published_time": {
                    "$dateFromString": {"dateString": "$published_time"}
                },
            }
        },
        {"$sort": {"published_time": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#8
@app.route("/articles_by_keyword_chart")
def articles_by_keyword_chart():
    return render_template("articles_by_keyword_chart.html")
@app.route("/articles_by_keyword/<keyword>", methods=["GET"])
def articles_by_keyword(keyword):
    pipeline = [
        {"$match": {"keywords": {"$in": [keyword]}}},
        {"$project": {"_id": 0, "title": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)
@app.route("/articles_grouped_by_keywords_count", methods=["GET"])
def articles_grouped_by_keywords_count():
    pipeline = [
        {"$group": {"_id": {"$size": "$keywords"}, "titles": {"$push": "$title"}}},
        {"$sort": {"_id": -1}},
        {"$project": {"titles": {"$slice": ["$titles", 5]}}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


#9
@app.route("/articles_by_author_chart")
def articles_by_author_chart():
    return render_template("articles_by_author_chart.html")
@app.route("/articles_by_author/<author_name>", methods=["GET"])
def articles_by_author(author_name):
    pipeline = [
        {"$match": {"author": author_name}},
        {
            "$project": {
                "_id": 0,
                "url": 1,
                "title": 1,
                "keywords": 1,
                "published_time": 1,
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#10
@app.route("/top_classes_chart")
def top_classes_chart():
    return render_template("top_classes_chart.html")
@app.route("/top_classes", methods=["GET"])
def top_classes():
    pipeline = [
        {"$unwind": "$classes"},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#11
@app.route("/article_details_chart")
def article_details_chart():
    return render_template("article_details_chart.html")
@app.route("/article_details/<postid>", methods=["GET"])
def article_details(postid):
    postid = ObjectId(postid)
    pipeline = [
        {"$match": {"_id": postid}},
        {
            "$project": {
                "_id": 0,
                "url": 1,
                "title": 1,
                "keywords": 1,
                "published_time": 1,
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#12
@app.route("/articles_with_videos_chart")
def articles_with_videos_chart():
    return render_template("articles_with_videos_chart.html")


@app.route('/articles_by_video_count', methods=['GET'])
def articles_by_video_count():
    # Count articles with and without videos
    articles_with_videos = collection.count_documents({'video_duration': {'$exists': True, '$ne': None}})
    articles_without_videos = collection.count_documents({'video_url': {'$exists': False}})-articles_with_videos

    return jsonify({
        'with_videos': articles_with_videos,
        'without_videos': articles_without_videos
    })

@app.route("/articles_with_video", methods=["GET"])
def articles_with_video():
    pipeline = [
        {"$match": {"video_duration": {"$ne": None}}},
        {"$project": {"_id": 0, "title": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#13
@app.route("/articles_by_year_chart")
def articles_by_year_chart():
    return render_template("articles_by_year_chart.html")


@app.route("/articles_by_year/<int:year>", methods=["GET"])
def articles_by_year(year):
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$eq": [
                        {
                            "$year": {
                                "$dateFromString": {"dateString": "$published_time"}
                            }
                        },
                        year,
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": {
                    "$year": {"$dateFromString": {"dateString": "$published_time"}}
                },
                "count": {"$sum": 1},
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


@app.route("/articles_grouped_by_year", methods=["GET"])
def articles_grouped_by_year():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "$year": {"$dateFromString": {"dateString": "$published_time"}}
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id": -1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#14
@app.route("/longest_articles_chart")
def longest_articles_chart():
    return render_template("longest_articles_chart.html")

@app.route("/longest_articles", methods=["GET"])
def longest_articles():
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "word_count": {"$toInt": "$word_count"},
            }
        },
        {"$sort": {"word_count": -1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#15
@app.route("/shortest_articles_chart")
def shortest_articles_chart():
    return render_template("shortest_articles_chart.html")

@app.route("/shortest_articles", methods=["GET"])
def shortest_articles():
    pipeline = [
        {"$match": {"$expr": {"$ne": [{"$toInt": "$word_count"}, 0]}}},
        {
            "$project": {
                "_id": 0,
                "title": 1,
                "word_count": {"$toInt": "$word_count"},
            }
        },
        {"$sort": {"word_count": 1}},
        {"$limit": 10},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#16
@app.route("/articles_by_keyword_count", methods=["GET"])
def articles_by_keyword_count():
    pipeline = [
        {"$group": {"_id": {"$size": "$keywords"}, "articles_count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#17
@app.route("/articles_with_thumbnail_chart")
def articles_with_thumbnail_chart():
    return render_template("articles_with_thumbnail_chart.html")
@app.route("/articles_with_thumbnail", methods=["GET"])
def articles_with_thumbnail():
    pipeline = [
        {"$match": {"thumbnail": {"$ne": None}}},
        {"$project": {"_id": 0, "title": 1, "thumbnail": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#18
@app.route("/articles_updated_after_publication_chart")
def articles_updated_after_publication_chart():
    return render_template("articles_updated_after_publication_chart.html")

@app.route("/articles_updated_after_publication", methods=["GET"])
def articles_updated_after_publication():
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$gt": [
                        {"$dateFromString": {"dateString": "$last_updated"}},
                        {"$dateFromString": {"dateString": "$published_time"}},
                    ]
                }
            }
        },
        {"$project": {"_id": 0, "title": 1, "published_time": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route('/articles_updated_after_publication_count', methods=['GET'])
def articles_updated_after_publication_count():
    pipeline = [
        {
            "$match": {
                "last_updated": {"$exists": True, "$ne": None},
                "published_time": {"$exists": True, "$ne": None}
            }
        },
        {
            "$addFields": {
                "is_updated": {
                    "$cond": [
                        {"$gt": ["$last_updated", "$published_time"]},
                        "Updated",
                        "Not Updated"
                    ]
                }
            }
        },
        {
            "$group": {
                "_id": "$is_updated",
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by status
        }
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#19
@app.route("/articles_grouped_by_coverage_perYear", methods=["GET"])
def articles_grouped_by_coverage_perYear():
    pipeline = [
        {
            "$project": {
                "year": {
                    "$year": {"$dateFromString": {"dateString": "$published_time"}}
                },
                "classes": "$classes",
            }
        },
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "category"}},
        {
            "$group": {
                "_id": {"year": "$year", "coverage": "$classes.value"},
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "count": -1}},
        {
            "$group": {
                "_id": "$_id.year",
                "coverages": {
                    "$push": {"category": "$_id.coverage", "count": "$count"}
                },
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/articles_by_coverage/<coverage>", methods=["GET"])
def articles_by_coverage(coverage):
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "coverage", "classes.value": coverage}},
        {"$project": {"_id": 0, "title": 1, "author": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#20
@app.route("/popular_keywords_last_X_days_chart")
def popular_keywords_last_X_days_chart():
    return render_template("popular_keywords_last_X_days_chart.html")
@app.route("/popular_keywords_last_X_days/<int:day>", methods=["GET"])
def popular_keywords_last_X_days(day):
    date_X_days_ago = datetime.utcnow() - timedelta(days=day)
    print(date_X_days_ago)
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$gte": [
                        {"$dateFromString": {"dateString": "$published_time"}},
                        date_X_days_ago,
                    ]
                }
            }
        },
        {"$unwind": "$keywords"},
        {"$group": {"_id": "$keywords", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 15},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#21
@app.route("/articles_by_month_chart")
def articles_by_month_chart():
    return render_template("articles_by_month_chart.html")
@app.route("/articles_by_month/<int:year>/<int:month>", methods=["GET"])
def articles_by_month(year, month):
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {
                        "$year": {"$dateFromString": {"dateString": "$published_time"}}
                    },
                    "month": {
                        "$month": {"$dateFromString": {"dateString": "$published_time"}}
                    },
                },
                "count": {"$sum": 1},
            }
        },
        {"$match": {"_id.year": year, "_id.month": month}},
        {
            "$project": {
                "_id": 0,
                "year": "$_id.year",
                "month": "$_id.month",
                "count": 1,
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/articles_grouped_by_month", methods=["GET"])
def articles_grouped_by_month():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "year": {
                        "$year": {"$dateFromString": {"dateString": "$published_time"}}
                    },
                    "month": {
                        "$month": {"$dateFromString": {"dateString": "$published_time"}}
                    },
                },
                "count": {"$sum": 1},
            }
        },
        {"$sort": {"_id.year": 1, "_id.month": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#22
@app.route("/articles_by_word_count_range/<int:min>/<int:max>", methods=["GET"])
def articles_by_word_count_range(min, max):
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$and": [
                        {"$gte": [{"$toInt": "$word_count"}, min]},
                        {"$lte": [{"$toInt": "$word_count"}, max]},
                    ]
                }
            }
        },
        {"$project": {"_id": 0, "title": 1, "word_count": 1}},
        {"$sort": {"word_count": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#23
@app.route("/articles_with_specific_keyword_count_chart")
def articles_with_specific_keyword_count_chart():
    return render_template("articles_with_specific_keyword_count_chart.html")
@app.route("/articles_with_specific_keyword_count/<int:count>", methods=["GET"])
def articles_with_specific_keyword_count(count):
    pipeline = [
        {"$match": {"$expr": {"$eq": [{"$size": "$keywords"}, count]}}},
        {"$project": {"_id": 0, "title": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#24
@app.route("/articles_by_specific_date/<date>", methods=["GET"])
def articles_by_specific_date(date):
    date_format = "%Y-%m-%d"
    date = str(datetime.strptime(date, date_format).date())

    pipeline = [
        {
            "$project": {
                "_id": 0,
                "published_time": {
                    "$dateFromString": {"dateString": "$published_time"}
                },
            }
        },
        {
            "$match": {
                "$expr": {
                    "$eq": [
                        {
                            "$dateToString": {
                                "date": "$published_time",
                                "format": date_format,
                            }
                        },
                        date,
                    ]
                }
            }
        },
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#25
@app.route("/articles_containing_text_chart")
def articles_containing_text_chart():
    return render_template("articles_containing_text_chart.html")
@app.route("/articles_containing_text/<text>", methods=["GET"])
def articles_containing_text(text):
    collection.create_index([("full_text", TEXT)])
    pipeline = [
        {"$match": {"$text": {"$search": text}}},
        {"$project": {"_id": 0, "title": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#26
@app.route("/articles_with_more_than/<int:word_count>", methods=["GET"])
def articles_with_more_than(word_count):
    pipeline = [
        {"$match": {"$expr": {"$gte": [{"$toInt": "$word_count"}, word_count]}}},
        {"$project": {"_id": 0, "title": 1, "word_count": {"$toInt": "$word_count"}}},
        {"$sort": {"word_count": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#27
@app.route("/articles_grouped_by_coverage", methods=["GET"])
def articles_grouped_by_coverage():
    pipeline = [
        {"$unwind": "$classes"},
        {"$match": {"classes.mapping": "coverage"}},
        {"$group": {"_id": "$classes.value", "count": {"$sum": 1}}},
        {"$sort": {"count": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#28
@app.route("/articles_last_24_hours_chart")
def articles_last_24_hours_chart():
    return render_template("articles_last_24_hours_chart.html")

@app.route('/articles_published_last_24_hours_count', methods=['GET'])
def articles_published_last_24_hours_count():
    # Define the time range for the last 24 hours
    now = datetime.utcnow()
    last_24_hours = now - timedelta(hours=24)

    # Aggregate count of articles published in the last 24 hours
    pipeline = [
        {
            "$match": {
                "published_time": {"$gte": last_24_hours}
            }
        },
        {
            "$group": {
                "_id": {
                    "$dateToString": {"format": "%Y-%m-%d %H:%M:%S", "date": "$published_time"}
                },
                "count": {"$sum": 1}
            }
        },
        {
            "$sort": {"_id": 1}  # Sort by publication time
        }
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

@app.route("/articles_last_X_hours/<int:hour>", methods=["GET"])
def articles_last_X_hours(hour):
    date_X_hours_ago = datetime.utcnow() - timedelta(hours=hour)
    pipeline = [
        {
            "$match": {
                "$expr": {
                    "$gte": [
                        {"$dateFromString": {"dateString": "$published_time"}},
                        date_X_hours_ago,
                    ]
                }
            }
        },
        {"$project": {"title": 1, "_id": 0}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

#29
@app.route("/articles_by_title_length_chart")
def articles_by_title_length_chart():
    return render_template("articles_by_title_length_chart.html")
@app.route("/articles_by_title_length", methods=["GET"])
def articles_by_title_length():
    pipeline = [
        {"$group": {"_id": {"$strLenCP": "$title"}, "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}},
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)


#30
@app.route("/most_updated_articles_chart")
def most_updated_articles_chart():
    return render_template("most_updated_articles_chart.html")
@app.route('/most_updated_articles', methods=['GET'])
def most_updated_articles():
    pipeline = [
        {
            "$match": {
                "last_updated": {"$exists": True}
            }
        },
        {
            "$group": {
                "_id": "$title",
                "update_count": {"$sum": 1}
            }
        },
        {
            "$sort": {"update_count": -1}  # Sort by number of updates, descending
        },
        {
            "$limit": 10  # Limit to top 10 most updated articles
        }
    ]
    result = list(collection.aggregate(pipeline))
    return jsonify(result)

if __name__ == "__main__":
    app.run(debug=True)
