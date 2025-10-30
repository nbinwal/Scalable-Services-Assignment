const express = require('express');
const bodyParser = require('body-parser');
const { MongoClient, ObjectId } = require('mongodb');

const app = express();
app.use(bodyParser.json());

const mongoUrl = process.env.MONGO_URL || 'mongodb://mongo:27017';
const dbName = process.env.MONGO_DB || 'bookstore';
let db;

MongoClient.connect(mongoUrl, { useUnifiedTopology: true })
  .then(client => {
    db = client.db(dbName);
    console.log('Review connected to MongoDB');
  })
  .catch(err => { console.error(err); process.exit(1); });

app.post('/books/:id/reviews', async (req, res) => {
  const bookId = req.params.id;
  const review = { bookId, ...req.body, createdAt: new Date() };
  const result = await db.collection('reviews').insertOne(review);
  res.status(201).json({ id: result.insertedId, ...review });
});

app.get('/books/:id/reviews', async (req, res) => {
  const bookId = req.params.id;
  const reviews = await db.collection('reviews').find({ bookId }).toArray();
  res.json(reviews);
});

app.listen(3001, () => console.log('Review service listening on 3001'));