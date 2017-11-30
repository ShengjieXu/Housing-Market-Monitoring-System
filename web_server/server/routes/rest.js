var express = require('express');
var rpc_client = require('../rpc_client/rpc_client');
var router = express.Router();

router.get('/markets/stats/:type', function(req, res, next) {
  var type = req.params['type'];
  console.log('markets/stats/' + type + ' get called');

  rpc_client.getAverageListingPrices(function(response) {
    res.json(response);
  });
});

module.exports = router;
