from flask import Flask, render_template, request, redirect, url_for
from flask_pymongo import PyMongo
from bson.objectid import ObjectId

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/plant_app"
mongo = PyMongo(app)

def initialize_db():
    # Check if the collection is empty
    if mongo.db.plants.count_documents({}) == 0:
        # Sample plants data with images
        sample_plants = [
            {
                'name': 'Monstera',
                'photo_url': 'https://images.unsplash.com/photo-1587142964580-9785c14c14b5?ixlib=rb-1.2.1&auto=format&fit=crop&w=700&q=60',
                'date_planted': '2022-01-15',
                'variety': 'Deliciosa'
            },
            {
                'name': 'Snake Plant',
                'photo_url': 'https://images.unsplash.com/photo-1587049352834-0e313cbdda91?ixlib=rb-1.2.1&auto=format&fit=crop&w=700&q=60',
                'date_planted': '2021-05-30',
                'variety': 'Laurentii'
            },
            {
                'name': 'Fiddle Leaf Fig',
                'photo_url': 'https://images.unsplash.com/photo-1560347876-aeef00ee58a1?ixlib=rb-1.2.1&auto=format&fit=crop&w=700&q=60',
                'date_planted': '2023-03-25',
                'variety': 'Lyrata'
            }
        ]
        mongo.db.plants.insert_many(sample_plants)
        print("Sample plants added to the database.")

@app.route('/')
def plants_list():
    plants = mongo.db.plants.find()
    return render_template('plants_list.html', plants=plants)

@app.route('/plant/<plant_id>')
def detail(plant_id):
    plant = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    return render_template('detail.html', plant=plant)

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        new_plant = {
            'name': request.form.get('name'),
            'photo_url': request.form.get('photo_url'),
            'date_planted': request.form.get('date_planted'),
            'variety': request.form.get('variety')
        }
        result = mongo.db.plants.insert_one(new_plant)
        return redirect(url_for('detail', plant_id=result.inserted_id))
    return render_template('create.html')

@app.route('/plant/<plant_id>/edit', methods=['GET', 'POST'])
def edit(plant_id):
    plant = mongo.db.plants.find_one({'_id': ObjectId(plant_id)})
    if request.method == 'POST':
        updated_plant = {
            'name': request.form.get('name'),
            'photo_url': request.form.get('photo_url'),
            'date_planted': request.form.get('date_planted'),
            'variety': request.form.get('variety')
        }
        mongo.db.plants.update_one({'_id': ObjectId(plant_id)}, {'$set': updated_plant})
        return redirect(url_for('detail', plant_id=plant_id))
    return render_template('edit.html', plant=plant)

@app.route('/plant/<plant_id>/delete', methods=['POST'])
def delete(plant_id):
    mongo.db.plants.delete_one({'_id': ObjectId(plant_id)})
    return redirect(url_for('plants_list'))

@app.route('/plant/<plant_id>/harvest', methods=['POST'])
def harvest(plant_id):
    harvest_info = {
        'date': request.form.get('date'),
        'yield': request.form.get('yield')
    }
    mongo.db.plants.update_one(
        {'_id': ObjectId(plant_id)},
        {'$push': {'harvests': harvest_info}}
    )
    return redirect(url_for('detail', plant_id=plant_id))

if __name__ == '__main__':
    initialize_db()  # Initialize the database with sample data
    app.run(debug=True)
