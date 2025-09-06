from app import db, create_app
from app.models.question import Questions

trivia = [
    {"id": 1, "question": "Which planet in our solar system is known for its prominent ring system?", "answer": "Saturn"},
    {"id": 2, "question": "What is the chemical symbol for gold?", "answer": "Au"},
    {"id": 3, "question": "In which city is the famous Louvre Museum located?", "answer": "Paris"},
    {"id": 4, "question": "What is the tallest mammal in the world?", "answer": "Giraffe"},
    {"id": 5, "question": "Which element has the atomic number 1?", "answer": "Hydrogen"},
    {"id": 6, "question": "Who wrote the play 'Romeo and Juliet'?", "answer": "William Shakespeare"},
    {"id": 7, "question": "What is the capital of Australia?", "answer": "Canberra"},
    {"id": 8, "question": "How many continents are there on Earth?", "answer": "Seven"},
    {"id": 9, "question": "What is the main ingredient in traditional Japanese miso soup?", "answer": "Miso (fermented soybean paste)"},
    {"id": 10, "question": "Which gas do plants absorb from the atmosphere during photosynthesis?", "answer": "Carbon dioxide"}
]

app = create_app()

with app.app_context():
    for item in trivia:
        q = Questions()
        q.question = item['question']
        q.answer = item['answer']
        db.session.add(q)
    db.session.commit()

