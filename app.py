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

# ✅ 전역 id 카운터 시작값
id_counter = 220

@app.route("/webhook", methods=["POST"])
def handle():
    global id_counter  # 전역 변수 사용 선언

    data_list = request.get_json()

    if isinstance(data_list, dict):
        data_list = [data_list]

    items_to_upsert = []

    for data in data_list:
        # ✅ 현재 ID 설정 및 증가
        current_id = str(id_counter)
        id_counter += 1

        # 포함할 필드 연결
        text = " / ".join([
            current_id,
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
            "id": current_id,  # ✅ Pinecone의 ID
            "values": vector,
            "metadata": {
                "id": current_id,  # ✅ 검색 결과에서도 ID 확인 가능
                "name": data.get("name"),
                "brand": data.get("brand"),
                "color": data.get("color"),
                "feature": data.get("feature"),
                "place": data.get("place"),
                "img_url": data.get("img_url"),
                "created_at": data.get("created_at"),
                "category": data.get("category"),
                "text": text
            }
        })

    # Pinecone에 한번에 저장
    index.upsert(items_to_upsert)

    return jsonify({"status": "ok", "count": len(items_to_upsert), "start_id": id_counter - len(data_list)})

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
