var client = require('./rpc_client');

client.getAverageListingPrices(function(response) {
  console.assert(response.length >= 7);
});