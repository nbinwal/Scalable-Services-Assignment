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
    console.log('Catalog connected to MongoDB');
  })
  .catch(err => {
    console.error('Mongo connect error', err);
    process.exit(1);
  });

// create book
app.post('/books', async (req, res) => {
  const book = req.body; // expect { title, author, price }
  const result = await db.collection('books').insertOne(book);
  res.status(201).json({ id: result.insertedId, ...book });
});

// list books
app.get('/books', async (req, res) => {
  const books = await db.collection('books').find().toArray();
  res.json(books);
});

// get book by id
app.get('/books/:id', async (req, res) => {
  const id = req.params.id;
  const book = await db.collection('books').findOne({ _id: new ObjectId(id) });
  if (!book) return res.status(404).json({ message: 'not found' });
  res.json(book);
});

app.listen(3000, () => console.log('Catalog service listening on 3000'));