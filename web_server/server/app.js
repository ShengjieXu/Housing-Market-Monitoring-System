var express = require('express');
var path = require('path');

var config = require('./config/config.json');
var _ = require('./models/main.js').connect(config.mongoDbUri);

var indexRouter = require('./routes/index');
var restRouter = require('./routes/rest')

var app = express();

app.use(express.static(path.join(__dirname, '../listing-map/build/')))
app.use('/', indexRouter)
app.use('/api/v1', restRouter)
app.use((req, res, next) => {
  res.sendFile('index.html', { root: path.join(__dirname, '../listing-map/build/') })
})

module.exports = app;
