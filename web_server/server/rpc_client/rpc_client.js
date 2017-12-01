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
    console.log('Node RPC response: getAverageListingPrices');
    console.log(response);
    callback(response);
  });
}

function getListings(region, callback) {
  client.request('getListings', [region], function(err, error, response) {
    if (err) throw err;
    console.log('Node RPC response: getListings');
    console.log(JSON.stringify(response));
    callback(response);
  });
}

module.exports = {
  getAverageListingPrices: getAverageListingPrices,
  getListings: getListings
};