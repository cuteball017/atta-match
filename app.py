from flask import Flask, request, jsonify
from langchain_openai import OpenAIEmbeddings
from pinecone import Pinecone
import os

app = Flask(__name__)

# 환경 변수
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# 임베딩 및 Pinecone 초기화
embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)

@app.route("/webhook", methods=["POST"])
def handle():
    data_list = request.get_json()

    # 단일 객체로 보내는 경우에도 리스트로 처리
    if isinstance(data_list, dict):
        data_list = [data_list]

    items_to_upsert = []

    for data in data_list:
        # 포함할 필드만 연결해서 텍스트로 만듦
        text = " / ".join([
            str(data.get("name", "")),
            str(data.get("brand", "")),
            str(data.get("color", "")),
            str(data.get("feature", "")),
            str(data.get("place", "")),
            str(data.get("img_url", "")),
            str(data.get("created_at", "")),
            str(data.get("category", ""))
        ])

        vector = embeddings.embed_query(text)

        items_to_upsert.append({
            "id": str(data.get("id")),
            "values": vector,
            "metadata": {
                "name": data.get("name"),
                "brand": data.get("brand"),
                "color": data.get("color"),
                "feature": data.get("feature"),
                "place": data.get("place"),
                "img_url": data.get("img_url"),
                "created_at": data.get("created_at"),
                "category": data.get("category"),
                "text": text  # ✅ 검색용 필드 반드시 추가
            }
        })

    # Pinecone에 한번에 저장
    index.upsert(items_to_upsert)

    return jsonify({"status": "ok", "count": len(items_to_upsert)})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)




# from flask import Flask, request, jsonify
# from langchain_openai import OpenAIEmbeddings
# from pinecone import Pinecone
# import os

# app = Flask(__name__)

# OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
# PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME")

# embeddings = OpenAIEmbeddings(api_key=OPENAI_API_KEY)
# pc = Pinecone(api_key=PINECONE_API_KEY)
# index = pc.Index(PINECONE_INDEX_NAME)

# @app.route("/webhook", methods=["POST"])
# def handle():
#     data = request.get_json()
#     text = f"{data.get('name')} / {data.get('place')} / {data.get('feature')}"
#     vector = embeddings.embed_query(text)
#     index.upsert([{
#         "id": str(data["id"]),
#         "values": vector,
#         "metadata": {
#             "name": data["name"],
#             "place": data["place"],
#             "feature": data["feature"]
#         }
#     }])
#     return jsonify({"status": "ok"})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=8000)
