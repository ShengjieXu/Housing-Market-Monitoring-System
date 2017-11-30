var jayson = require('jayson');
var config = require('../config/config.json');

// create a client
var client = jayson.client.http({
  port: config.rpc.server.port,
  hostname: config.rpc.server.hostname
});

function getAverageListingPrices(callback) {
  client.request('getAverageListingPrices', [], function(err, error, response) {
    if (err) throw err;
    console.log(response);
    callback(response);
  });
}

module.exports = {
  getAverageListingPrices
};