from sentence_transformers import SentenceTransformer, util

# Загружаем модель
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

# Примеры
emb1 = model.encode("Привет, мир!", convert_to_tensor=True)
emb2 = model.encode("Скриптоника – огонь", convert_to_tensor=True)

# Считаем косинусное сходство
print("cosine:", float(util.cos_sim(emb1, emb2)))
